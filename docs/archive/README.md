# Archive

This directory contains **archived documentation and materials** from historical investigations, refactoring efforts, and superseded documentation. These files are preserved for reference but are no longer actively maintained.

---

## Directory Structure

```
docs/archive/
├── README.md                          # This file
├── ci-cd/                             # Archived CI/CD documentation
├── troubleshooting/                   # API debugging investigation materials
├── GITHUB_ACTIONS_IMPROVEMENTS.md     # CI/CD improvements summary (Jan 2026)
├── INSTALLER_FIXES_SUMMARY.md         # Installer diagnostic infrastructure (Jan 2026)
├── INSTALLER_FIX_VERIFIED.md          # Installer fix verification (Jan 2026)
├── architecture.md.old                # Superseded architecture docs
├── requirements.md.old                # Superseded requirements docs
├── specifications.md.old              # Superseded specifications docs
└── peer-review.md                     # Historical peer review notes
```

---

## CI/CD Documentation Archive

**Archive Date:** January 6, 2026
**Reason:** Workflow consolidation rendered these documents obsolete

### What Happened

The GitHub Actions workflows were consolidated from **7 workflows** down to **3 workflows**, achieving a 60-70% reduction in CI minutes.

| Old Architecture | New Architecture |
|------------------|------------------|
| `cross-platform-ci.yml` | `main-ci.yml` (consolidated) |
| `backend-ci.yml` | `main-ci.yml` (consolidated) |
| `frontend-ci.yml` | `main-ci.yml` (consolidated) |
| `windows-build.yml` | `platform-builds.yml` |
| `macos-build.yml` | `platform-builds.yml` |
| `dependabot-tests.yml` | `main-ci.yml` (consolidated) |
| `docs-ci.yml` | `docs-ci.yml` (unchanged) |

### Archived Files

| File | Original Purpose |
|------|------------------|
| `ci-cd/ci-cd-v1.md` | General CI/CD overview (outdated workflow references) |
| `ci-cd/cross-platform-ci-v1.md` | Cross-platform matrix testing strategy |

### Current Documentation

For up-to-date CI/CD documentation, see **[GitHub Actions Overview](../technical/github-actions-overview.md)**.

---

## Windows Installer Documentation Archive

**Archive Date:** January 7, 2026
**Reason:** Root-level PR summaries consolidated into existing documentation

### What Happened

Three root-level summary files were created during the Windows installer debugging effort. These have been archived because:

1. The actual fix is documented in **[Troubleshooting: exe-launch-failure.md](../troubleshooting/exe-launch-failure.md)**
2. Testing procedures are documented in **[installer/windows/TESTING.md](../../installer/windows/TESTING.md)**
3. Root cause analysis is in **[windows-installer-root-cause-analysis.md](../testing/windows-installer-root-cause-analysis.md)**

### Archived Files

| File | Original Purpose |
|------|------------------|
| `GITHUB_ACTIONS_IMPROVEMENTS.md` | Summary of CI/CD workflow improvements |
| `INSTALLER_FIXES_SUMMARY.md` | Summary of diagnostic infrastructure added |
| `INSTALLER_FIX_VERIFIED.md` | Verification that production exe fix worked |

### Key Fix (for reference)

The production exe crash was caused by uvicorn's logging configuration attempting to call `sys.stdout.isatty()` when `sys.stdout` is `None` in frozen executables with `console=False`.

**Solution:** Add `log_config=None` to uvicorn.Config():

```python
config = uvicorn.Config(
    app,
    host="127.0.0.1",
    port=PORT,
    log_level="info",
    access_log=False,
    log_config=None,  # CRITICAL: Disable uvicorn logging config when frozen
)
```

### Current Documentation

For up-to-date installer troubleshooting, see **[Troubleshooting: exe-launch-failure.md](../troubleshooting/exe-launch-failure.md)**.

---

## API Troubleshooting Archive

**Investigation Period:** January 4-5, 2026
**Status:** RESOLVED

### Problem

Ambient Weather API returned `429 Too Many Requests` errors inconsistently, preventing reliable data collection.

### Root Cause

Sequential API calls with only **400ms delay** violated Ambient Weather's **1 API call/second** rate limit.

### Solution

Updated `weather_app/api/client.py` to enforce **1.1-second delay** between sequential calls.

```python
# Before (WRONG)
time.sleep(0.4)  # Too fast! Triggers rate limiting

# After (CORRECT)
time.sleep(1.1)  # Respects 1 call/second limit
```

### Archived Files

| Directory/File | Contents |
|----------------|----------|
| `troubleshooting/investigation-summary.md` | Complete investigation summary |
| `troubleshooting/phase-1-results.md` | Basic connectivity testing |
| `troubleshooting/phase-2-results.md` | Frequency tolerance testing |
| `troubleshooting/cooldown-test-results.md` | 30-second recovery period discovery |
| `troubleshooting/backend-diagnostic-findings.md` | Diagnostic script results |
| `troubleshooting/api-debugging-plan.md` | Original debugging plan |
| `troubleshooting/ambient-weather-debugging-next-steps.md` | Investigation next steps |

### Lessons Learned

1. **Read API documentation carefully** - Ambient Weather clearly states "1 call/second" limit
2. **Measure actual delays** - Code review revealed 400ms vs 1000ms timing mismatch
3. **Don't assume account tiers** - Free tier was sufficient when used correctly
4. **Systematic investigation** - Phased approach helped isolate the issue

---

## Test Scripts Archive

Related experimental scripts are archived in `tests/archive/api-debugging/`. These diagnostic scripts were used during the API rate limiting investigation.

See [tests/archive/](../../tests/archive/) for the complete list of archived test scripts.

---

## Superseded Documentation

| File | Superseded By |
|------|---------------|
| `architecture.md.old` | `docs/architecture/overview.md` |
| `requirements.md.old` | `docs/product/requirements.md` |
| `specifications.md.old` | Various files in `docs/product/` and `docs/architecture/` |

---

## Usage Warning

**These materials are NOT maintained and may not reflect current architecture.**

- API endpoints may have changed
- Database schema may be different
- Workflow configurations are outdated
- Dependencies may be outdated

**For current documentation:** See [docs/README.md](../README.md) for the documentation index.

---

**Last Updated:** January 7, 2026
