# tesla feature cherry-picks and combo workflow

This runbook is the source of truth for maintaining Tesla feature branches and rebuilding `t-combo` in a repeatable way.

## branch model

- `t-baseline`: clean Tesla base branch synced from `origin/t-baseline`
- `t-lkas-bypass`: Tesla LKAS bypass and FSD14 failsafe behavior
- `t-steer-ratio-test`: Tesla steer-ratio test behavior
- `t-can-toggle`: CAN streaming developer toggle from `wpmed92/sunnydash`
- `t-combo`: integration branch that combines the three feature branches above

## branch hygiene

- Start each feature branch from `t-baseline`
- Keep feature branches feature-scoped (no local-only helper scripts or personal notes)
- Keep trees clean before cherry-picking: `git status --short --branch`
- Use `--ff-only` pulls to avoid accidental merge commits in maintenance branches

## create or refresh `t-can-toggle`

```bash
git switch t-baseline
git pull --ff-only origin t-baseline
git switch -c t-can-toggle
git fetch "https://github.com/wpmed92/sunnypilot.git" sunnydash
git cherry-pick 59e4f4cb5b4c68ca565a42a9c36be066530ddd55
git push -u origin t-can-toggle
```

If `t-can-toggle` already exists locally, use `git switch t-can-toggle` instead of `git switch -c t-can-toggle`.

## rebuild `t-combo` from feature branches

1. Start from `t-baseline`.
2. Cherry-pick feature commits from each feature branch in order.
3. Push `t-combo`.

```bash
git switch t-combo
git pull --ff-only origin t-combo

# LKAS/failsafe feature commits
git log --reverse --oneline t-baseline..t-lkas-bypass -- opendbc_repo

# Steer-ratio feature commits
git log --reverse --oneline t-baseline..t-steer-ratio-test -- selfdrive/controls/controlsd.py opendbc_repo

# CAN toggle feature commits
git log --reverse --oneline t-baseline..t-can-toggle -- selfdrive/ui/mici/layouts/settings/developer.py
```

Cherry-pick the commit SHAs from those three log commands in this order:

1. `t-lkas-bypass`
2. `t-steer-ratio-test`
3. `t-can-toggle`

Then push:

```bash
git push origin t-combo
```

## verification checklist

- `git status --short --branch` is clean on both `t-can-toggle` and `t-combo`
- `git log --oneline origin/t-combo..t-combo` only shows intended new commits
- `git show --name-status --oneline -1` on `t-combo` shows the expected last integration change
