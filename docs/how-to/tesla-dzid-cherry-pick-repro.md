# Tesla dzid Cherry-Pick Repro and Validation

Date: 2026-04-21

This runbook captures the exact Tesla-focused dzid port state that was validated in WSL, plus the checks needed to reproduce it.

## Scope

Validated features:
- invalidLkasSetting soft-disable handling in selfdrived events
- gas-override longitudinal behavior in controls
- Tesla cruise override handling in carstate/teslacan
- Tesla coop steering stack from dzid Tesla path

Validated test result:
- `opendbc/safety/tests/test_tesla.py`: PASS (`377 passed`, `73 skipped`) in WSL

## Important Environment Note

Use Linux/WSL for validation. Windows PowerShell is not reliable for this safety test flow because `libsafety` compiles with `cc`.

## Commit Sources

Reference map: `../dzid-port-map.md`

Superproject commits used:
- `9fcb9f96e7` (Tesla autopilot/autopark fix)
- `3a8f3d3ee7` (long control active on gas override)
- `dda70fbd41` (Tesla coop steering UI text)

Opendbc commits used:
- `a371575bcf` (Tesla autopilot/autopark fix)
- `c08817ec96` (allow accel with gas)
- `3c3b826bdf` (jerk ramp after gas override)
- `66c8c70da6` (angle-based cooperative steering stack)

## Critical Integration Fix (Required)

After porting, ensure this fix exists in:
- `opendbc_repo/opendbc/safety/modes/tesla.h`

Required condition:

```c
!(controls_allowed || controls_allowed_lateral)
```

Do NOT use `is_lat_active()` in this file; that symbol is undefined in this tree and breaks safety test compilation.

## Repro Steps

Fast path (automated):

```bash
bash scripts/validate-tesla-dzid-port.sh
```

Optional flags:
- `--no-setup` skips `source opendbc_repo/setup.sh` before tests (use when env is already prepared)
- `--no-tests` runs only file-content checks

Manual path:

1) Apply Tesla cherry-picks in your working branch (superproject + `opendbc_repo`) using the commit list above.

2) Confirm the critical fix is present in `opendbc_repo/opendbc/safety/modes/tesla.h`.

3) In WSL, run Tesla safety validation:

```bash
cd opendbc_repo
source ./setup.sh
pytest -c pyproject.toml --rootdir=. --confcutdir=. opendbc/safety/tests/test_tesla.py -q
```

4) Confirm gas-override logic in superproject:
- `selfdrive/controls/controlsd.py`
  - `CC.longActive` should not be blocked by `overrideLongitudinal`
  - `freeze_integrator=override_longitudinal` should be passed to long control update

5) Confirm Tesla override logic in opendbc:
- `opendbc_repo/opendbc/car/tesla/carstate.py`
  - `cruise_override = cruise_state in ("OVERRIDE")`
- `opendbc_repo/opendbc/car/tesla/teslacan.py`
  - override-aware set speed behavior
  - jerk ramp reset while override is active

## In-Car Test Preconditions

Set `DisengageOnAccelerator` to OFF before testing gas-override-long behavior.

Reason:
- `selfdrive/selfdrived/selfdrived.py` adds `pedalPressed` on gas rising edge when this toggle is ON, which triggers user disable and masks the override-long behavior.

## Quick Regression Checklist

- safety test compiles and passes in WSL
- no `is_lat_active()` usage in `opendbc_repo/opendbc/safety/modes/tesla.h`
- `controlsd.py` retains override-integrator freeze wiring
- `carstate.py` and `teslacan.py` retain cruise override handling
