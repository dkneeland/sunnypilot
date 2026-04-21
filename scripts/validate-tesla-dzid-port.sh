#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

RUN_TESTS=1

for arg in "$@"; do
  case "$arg" in
    --no-tests)
      RUN_TESTS=0
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: $0 [--no-tests]"
      exit 1
      ;;
  esac
done

if [[ "$(uname -s)" != "Linux" ]]; then
  echo "This script is intended for Linux/WSL (current: $(uname -s))."
  exit 1
fi

ok() {
  echo "[PASS] $1"
}

fail() {
  echo "[FAIL] $1"
  exit 1
}

require_contains() {
  local file="$1"
  local pattern="$2"
  local note="$3"
  if grep -qE "$pattern" "$file"; then
    ok "$note"
  else
    fail "$note"
  fi
}

require_absent() {
  local file="$1"
  local pattern="$2"
  local note="$3"
  if grep -qE "$pattern" "$file"; then
    fail "$note"
  else
    ok "$note"
  fi
}

echo "Validating Tesla dzid port checks..."

require_absent "opendbc_repo/opendbc/safety/modes/tesla.h" "is_lat_active\(" "No undefined is_lat_active() in tesla safety mode"
require_contains "opendbc_repo/opendbc/safety/modes/tesla.h" "\!\(controls_allowed \|\| controls_allowed_lateral\)" "tesla safety gating uses controls_allowed/controls_allowed_lateral"

require_contains "selfdrive/controls/controlsd.py" "CC\.longActive = CC\.enabled and \(self\.CP\.openpilotLongitudinalControl or not self\.CP_SP\.pcmCruiseSpeed\)" "longActive not blocked by overrideLongitudinal"
require_contains "selfdrive/controls/controlsd.py" "freeze_integrator=override_longitudinal" "Integrator freeze wired during longitudinal override"

require_contains "opendbc_repo/opendbc/car/tesla/carstate.py" "self\.cruise_override = cruise_state in \(\"OVERRIDE\"\)" "Tesla cruise override state detected"
require_contains "opendbc_repo/opendbc/car/tesla/teslacan.py" "set_speed = 0 if \(accel < 0 and not cruise_override\) else V_CRUISE_MAX" "Long command set speed follows override logic"
require_contains "opendbc_repo/opendbc/car/tesla/teslacan.py" "self\.jerk = 0 if cruise_override else" "Jerk ramp reset during override"

if [[ "$RUN_TESTS" -eq 1 ]]; then
  echo "Running Tesla safety tests in opendbc_repo..."
  pushd "opendbc_repo" > /dev/null
  uv run python -m unittest discover -s opendbc/safety/tests -p test_tesla.py -v
  popd > /dev/null
  ok "Tesla safety tests completed"
else
  echo "Skipping tests (--no-tests)."
fi

echo "Tesla dzid port validation complete."
