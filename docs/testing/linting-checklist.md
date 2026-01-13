# Linting Checklist

**Date Created:** January 13, 2026
**Status:** AUTOMATED via pre-commit hooks

---

## Pre-commit Hooks (Now Automated)

This project now uses the `pre-commit` framework to automatically run linting before every commit. This replaces the need to manually run linting commands.

### What Runs Automatically

Every `git commit` now runs these checks:

| Hook | Purpose |
|------|---------|
| `check-added-large-files` | Block files > 1MB |
| `check-yaml` | Validate YAML syntax |
| `detect-private-key` | Block private keys |
| `trailing-whitespace` | Fix trailing spaces |
| `end-of-file-fixer` | Ensure files end with newline |
| `no-env-files` | Block .env, credentials.json, secrets.py |
| `ruff` | Python linting (auto-fix enabled) |
| `black` | Python formatting (auto-fix enabled) |
| `isort` | Import sorting (auto-fix enabled) |

### Setup for New Developers

```bash
# Install pre-commit (already in requirements.txt)
pip install -r requirements.txt

# Install the git hooks
pre-commit install

# Verify it works
pre-commit run --all-files
```

### How It Works

1. You make code changes
2. You run `git add .` and `git commit -m "message"`
3. Pre-commit hooks run automatically
4. If issues are found:
   - Auto-fixable issues (formatting) are fixed automatically
   - You need to `git add .` again to include the fixes
   - Re-run `git commit`
5. If all hooks pass, commit proceeds

### Manual Commands (Optional)

You can still run checks manually if needed:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run black --all-files

# Skip hooks in emergency (not recommended)
git commit --no-verify -m "message"
```

---

## CI Alignment

The pre-commit hooks mirror what CI checks (from [main-ci.yml](../../.github/workflows/main-ci.yml)):

| CI Check (Line) | Pre-commit Hook |
|-----------------|-----------------|
| `ruff check` (138) | `ruff` |
| `black --check` (141) | `black` |
| `isort --check-only` (144) | `isort` |

This means: **If pre-commit passes locally, CI will pass.**

---

## Excluded Directories

The following directories are excluded from linting (special files):

- `tests/archive/` - Archived experimental code
- `installer/` - PyInstaller hooks with intentional import ordering
- `tests/data/` - Test data generation scripts

---

## Troubleshooting

### "Hook failed" but no obvious error

Run with verbose output:
```bash
pre-commit run --all-files --verbose
```

### Pre-commit not running on commit

Re-install the hooks:
```bash
pre-commit install
```

### Need to update hook versions

```bash
pre-commit autoupdate
```

---

## Historical Context

Before pre-commit was set up, every commit pushed to this PR failed CI because linting wasn't run locally. The pattern was:

1. Push code → CI fails on linting
2. Push fix commit → CI fails again
3. Push another fix → Finally passes

This wasted CI minutes and created noisy commit history. Pre-commit hooks prevent this by catching issues before they're committed.
