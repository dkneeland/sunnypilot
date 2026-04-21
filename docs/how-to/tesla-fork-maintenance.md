# Tesla Fork Maintenance Instruction Set

Date: 2026-04-21

This is the maintenance playbook for your Tesla dzid-port fork so you can keep it reproducible and easy to update.

## What Was Cleansed in This Session

- Created a real working branch in `opendbc_repo` (it was detached HEAD):
  - `tesla-baseline`
- Kept the validated integration fix in place:
  - `opendbc_repo/opendbc/safety/modes/tesla.h` uses `!(controls_allowed || controls_allowed_lateral)`
- Added reproducible validation tooling/docs:
  - `scripts/validate-tesla-dzid-port.sh`
  - `docs/how-to/tesla-dzid-cherry-pick-repro.md`
- Created GitHub fork for opendbc and rewired submodule remotes:
  - `origin` -> `https://github.com/dkneeland/opendbc.git`
  - `upstream` -> `https://github.com/sunnypilot/opendbc.git`
- Pushed feature branches so both repos now have remote tracking:
  - superproject `tesla-baseline` -> `origin/tesla-baseline`
  - submodule `tesla-baseline` -> `origin/tesla-baseline`

## Fork Model (Important)

You are maintaining two repos together:

1) Superproject: `sunnypilot`
2) Submodule: `opendbc_repo`

Always remember: the superproject only stores a pointer to an opendbc commit. If that opendbc commit is not pushed to a reachable remote, the setup is not reproducible.

## One-Time Setup

1. Fork `sunnypilot` to your GitHub account.
2. Fork `opendbc` to your GitHub account.
3. In `sunnypilot`, set remotes:
   - `origin` -> your fork
   - `upstream` -> `sunnypilot/sunnypilot`
4. In `opendbc_repo`, set remotes:
   - `origin` -> your opendbc fork (recommended)
   - `upstream` -> `sunnypilot/opendbc` (or whichever upstream you track)

## Branch Strategy

- Superproject baseline branch: `tesla-baseline`
- Opendbc baseline branch: `tesla-baseline`
- Feature test branches:
  - `tesla-lkas-bypass`
  - `tesla-steer-ratio-test`
  - `tesla-combined`
- Never do Tesla port work directly on `master` in either repo.

## Daily Maintenance Workflow

1. Sync superproject base:
```bash
git fetch upstream
git switch master
git pull --ff-only upstream master
```

2. Rebase your Tesla branch:
```bash
git switch tesla-baseline
git rebase master
```

3. Sync opendbc branch similarly:
```bash
git -C opendbc_repo fetch upstream
git -C opendbc_repo switch master
git -C opendbc_repo pull --ff-only upstream master
git -C opendbc_repo switch tesla-baseline
git -C opendbc_repo rebase master
```

4. Run validation:
```bash
bash scripts/validate-tesla-dzid-port.sh
```

5. In-car validation precondition:
   - Ensure `DisengageOnAccelerator` is OFF when testing gas-override-long behavior.

## Commit and Push Order (Critical)

Always do this order:

1. Commit in `opendbc_repo` first.
2. Push `opendbc_repo` branch first.
3. Then commit superproject changes (including the updated submodule pointer).
4. Push superproject branch.

This prevents broken submodule pointers.

## Quick Commands to Check Hygiene

```bash
git status --short --branch
git -C opendbc_repo status --short --branch
git -C opendbc_repo branch --show-current
```

Expected:
- superproject on your Tesla feature branch
- opendbc on `tesla-baseline` (not detached)

## Suggested Tagging for Known-Good States

After a validated run:

```bash
git tag -a tesla-dzid-v1 -m "Validated Tesla dzid port"
git push origin tesla-dzid-v1
```

Use incrementing tags (`v2`, `v3`) after each stable rebase/update.

## Recovery Tips

- If opendbc is detached again, recreate/switch branch before editing:
```bash
git -C opendbc_repo switch -c tesla-baseline
```
- If tests fail after rebase, run file checks first:
```bash
bash scripts/validate-tesla-dzid-port.sh --no-tests
```
