# GitHub Actions CI/CD Overview

**Status:** ✅ Streamlined (January 2026)
**Last Updated:** January 6, 2026
**Phase:** Phase 2 - Optimized Multi-Platform Testing

---

## Overview

The Weather App uses a **streamlined two-workflow strategy** to ensure comprehensive testing and build validation across all target platforms with **60-70% fewer GitHub Actions minutes** compared to the previous architecture:

1. **Main CI** (`main-ci.yml`) - Primary quality gate for all code changes
2. **Platform Builds** (`platform-builds.yml`) - Platform-specific installers and artifacts
3. **Docs CI** (`docs-ci.yml`) - Documentation validation (unchanged)

---

## Architecture Improvements (January 2026)

### Before: 7 Workflows with Massive Redundancy

```
┌─────────────────────────────────────────────────────────────────┐
│  PREVIOUS ARCHITECTURE (7 workflows, ~150-300 min per PR)       │
├─────────────────────────────────────────────────────────────────┤
│  ❌ cross-platform-ci.yml  → Multi-platform tests                │
│  ❌ backend-ci.yml          → Python tests (duplicate!)          │
│  ❌ frontend-ci.yml         → React tests (duplicate!)           │
│  ❌ windows-build.yml       → Windows tests + installer          │
│  ❌ macos-build.yml         → macOS tests                        │
│  ❌ dependabot-tests.yml    → Dependabot-only tests              │
│  ✅ docs-ci.yml             → Documentation validation           │
└─────────────────────────────────────────────────────────────────┘

Problems:
- Same tests ran 2-3 times across different workflows
- Linting ran separately in backend-ci.yml and cross-platform-ci.yml
- Security scans ran twice
- Confusing failure reports (same test failed in multiple places)
- Wasted ~200+ Actions minutes per PR
```

### After: 3 Workflows, Zero Redundancy

```
┌─────────────────────────────────────────────────────────────────┐
│  NEW ARCHITECTURE (3 workflows, ~50-80 min per PR)               │
├─────────────────────────────────────────────────────────────────┤
│  ✅ main-ci.yml           → All standard CI (tests, lint, security)│
│  ✅ platform-builds.yml   → Platform-specific builds only         │
│  ✅ docs-ci.yml           → Documentation validation (unchanged)  │
└─────────────────────────────────────────────────────────────────┘

Benefits:
✅ 60-70% reduction in GitHub Actions minutes
✅ No duplicate test runs
✅ Faster CI (10-15 min vs. 25+ min)
✅ Cleaner failure reports
✅ Easier maintenance (update linting rules in one place)
✅ Path filtering (workflows only run if relevant files changed)
```

---

## Workflow Details

### 1. Main CI (`main-ci.yml`)

**Purpose:** Primary quality gate for all code changes

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Jobs:**

| Job | Runs On | Purpose | Duration |
|-----|---------|---------|----------|
| `backend-tests` | Ubuntu, Windows, macOS (matrix) | Multi-platform Python testing | ~5-8 min |
| `backend-lint` | Ubuntu only | Code quality (Ruff, Black, isort, mypy) | ~2-3 min |
| `frontend-tests` | Ubuntu only | React/TypeScript lint, type check, build | ~3-4 min |
| `security-scan` | Ubuntu only (after backend-tests) | Safety + Bandit security scans | ~2-3 min |
| `api-integration` | Ubuntu only (after backend-tests) | FastAPI endpoint tests | ~2-3 min |

**Matrix Strategy:**
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
  python-version: ['3.11']  # Primary version for all platforms
  include:
    # Additional Python versions tested on Ubuntu only
    - os: ubuntu-latest
      python-version: '3.10'
    - os: ubuntu-latest
      python-version: '3.12'
```

**Path Filtering:**
- Only runs if backend files changed (weather_app/, tests/, requirements.txt, pyproject.toml)
- Frontend tests only run if web/ directory changed
- Skips unnecessary runs (e.g., doc-only changes)

**Key Features:**
- ✅ Parallel execution (all jobs run simultaneously)
- ✅ Smart path filtering
- ✅ Coverage reporting to Codecov (Ubuntu + Python 3.11 only)
- ✅ DuckDB and FastAPI validation on all platforms

---

### 2. Platform Builds (`platform-builds.yml`)

**Purpose:** Platform-specific builds, installers, and validations

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Jobs:**

| Job | Runs On | Purpose | Duration |
|-----|---------|---------|----------|
| `windows-installer` | Windows only | PyInstaller .exe build + Windows-specific tests | ~8-12 min |
| `macos-app` | macOS only | macOS app bundle preparation + Mac-specific tests | ~5-7 min |
| `frontend-build-artifacts` | Ubuntu, Windows, macOS (matrix) | Multi-platform frontend builds | ~4-6 min |

**Windows-Specific Validations:**
- Console encoding tests (emoji support: ✅ 📊 🌡️ 💧)
- System tray icon compatibility (PIL + pystray)
- Windows path handling
- PowerShell integration
- **PyInstaller .exe build** (only on `main` branch pushes)

**macOS-Specific Validations:**
- macOS system information (`sw_vers`)
- File system compatibility
- Native path handling
- Future: `.app` bundle creation

**Installer Builds:**
- Windows .exe only builds on `push` to `main` branch (not on every PR)
- Uses `installer/windows/weather_app_debug.spec`
- Uploads artifact with 30-day retention
- macOS .app bundle: Disabled until Phase 3 deployment

**Artifacts:**
- `windows-installer-exe-<sha>` - WeatherApp.exe (30-day retention)
- `frontend-dist-<os>-<sha>` - Frontend builds (7-day retention)

---

### 3. Docs CI (`docs-ci.yml`)

**Purpose:** Documentation validation (unchanged from previous architecture)

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'docs/**'
      - 'README.md'
      - '.claude/**'
      - '.github/workflows/docs-ci.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'docs/**'
      - 'README.md'
      - '.claude/**'
      - '.github/workflows/docs-ci.yml'
```

**Jobs:**
- `markdown-lint` - Markdown linting
- `link-check` - Broken link detection
- `adr-validation` - ADR format validation
- `spell-check` - Spell checking
- `doc-structure` - Documentation structure validation
- `accessibility-docs-check` - Accessibility standards verification

---

## Workflow Relationships

### Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PUSH/PULL REQUEST                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
     ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
     │   Main CI      │ │  Platform    │ │  Docs CI     │
     │  (PRIMARY)     │ │   Builds     │ │  (if docs)   │
     └────────────────┘ └──────────────┘ └──────────────┘
            │                  │                 │
    ┌───────┴─────────┐        │                 │
    ▼                 ▼        ▼                 ▼
┌─────────┐     ┌─────────┐ ┌─────────┐    ┌─────────┐
│ Backend │     │Frontend │ │ Windows │    │Markdown │
│ Tests   │     │ Build   │ │ .exe    │    │ Lint    │
│(3 OS x  │     │(Ubuntu) │ │(main    │    │         │
│ 3 Py)   │     │         │ │ only)   │    │         │
└────┬────┘     └─────────┘ └─────────┘    └─────────┘
     │
     ▼
┌─────────────┐
│ Linting     │
│ Security    │
│ API Tests   │
└─────────────┘
```

### Dependencies Between Jobs

**Main CI:**
- `security-scan` requires `backend-tests` to pass first
- `api-integration` requires `backend-tests` to pass first
- All other jobs run in parallel

**Platform Builds:**
- All jobs run independently and in parallel
- No dependencies (can fail independently)

---

## Performance Comparison

### CI Minutes Usage

| Scenario | Old Architecture | New Architecture | Savings |
|----------|------------------|------------------|---------|
| **Per PR (all tests)** | 150-300 minutes | 50-80 minutes | **60-70%** |
| **Per PR (backend only)** | 100-150 minutes | 30-50 minutes | **65%** |
| **Per PR (docs only)** | 3-5 minutes | 3-5 minutes | 0% (unchanged) |

### Wall Clock Time

| Scenario | Old Architecture | New Architecture |
|----------|------------------|------------------|
| **Full PR** | 25-40 minutes | 10-15 minutes |
| **Backend only** | 15-25 minutes | 8-12 minutes |
| **Docs only** | 3-5 minutes | 3-5 minutes |

**Why faster?**
- No duplicate test runs
- Better parallelization
- Smarter path filtering
- Linting runs once (not 2-3 times)

---

## Artifact Management

### What Gets Uploaded

| Workflow | Artifact Name | Contents | Retention |
|----------|---------------|----------|-----------|
| **Main CI** | _(none)_ | Coverage → Codecov only | N/A |
| **Platform Builds** | `windows-installer-exe-<sha>` | WeatherApp.exe | 30 days |
| **Platform Builds** | `frontend-dist-ubuntu-<sha>` | web/dist/ (Ubuntu build) | 7 days |
| **Platform Builds** | `frontend-dist-windows-<sha>` | web/dist/ (Windows build) | 7 days |
| **Platform Builds** | `frontend-dist-macos-<sha>` | web/dist/ (macOS build) | 7 days |

### Downloading Artifacts

**From GitHub UI:**
1. Go to Actions tab → Select workflow run
2. Scroll to "Artifacts" section
3. Download desired artifact

**From CLI (gh):**
```bash
# List recent workflow runs
gh run list --workflow=platform-builds.yml --limit 5

# Download Windows installer
gh run download <run-id> -n windows-installer-exe-<sha>

# Download frontend build
gh run download <run-id> -n frontend-dist-ubuntu-<sha>
```

---

## Path Filtering Details

### Main CI Path Filters

**Backend Tests:**
```yaml
if: |
  contains(github.event.head_commit.modified, 'weather_app/') ||
  contains(github.event.head_commit.modified, 'tests/') ||
  contains(github.event.head_commit.modified, 'requirements.txt') ||
  contains(github.event.head_commit.modified, 'pyproject.toml') ||
  github.event_name == 'pull_request'
```

**Frontend Tests:**
```yaml
if: |
  contains(github.event.head_commit.modified, 'web/') ||
  github.event_name == 'pull_request'
```

**Effect:** CI only runs if relevant files changed, saving Actions minutes.

---

## Branch Protection Rules

### Recommended Settings

Configure in **Settings → Branches → Branch Protection Rules** for `main`:

```yaml
Require status checks to pass before merging: ✅
  Required checks:
    - Main CI / backend-tests (ubuntu-latest, 3.11)
    - Main CI / backend-lint
    - Main CI / frontend-tests
    - Platform Builds / windows-installer (optional)
    - Platform Builds / macos-app (optional)

Require branches to be up to date before merging: ✅
Require pull request reviews before merging: ✅ (1 reviewer)
```

**Note:** Platform builds are optional (can merge even if they fail), but Main CI must pass.

---

## Debugging Failed Workflows

### Common Failure Patterns

| Symptom | Likely Cause | Where to Look |
|---------|--------------|---------------|
| Backend tests fail on Windows only | Path separators, encoding | `main-ci.yml` → backend-tests (Windows) |
| Backend tests fail on all platforms | Logic error, test issue | `main-ci.yml` → backend-tests (all) |
| Frontend build fails | TypeScript error, dependency | `main-ci.yml` → frontend-tests |
| Linting fails | Code style violation | `main-ci.yml` → backend-lint |
| Security scan fails | Vulnerable dependency | `main-ci.yml` → security-scan |
| Windows installer fails | PyInstaller config | `platform-builds.yml` → windows-installer |
| macOS build fails | macOS-specific issue | `platform-builds.yml` → macos-app |

### Reproduce Locally

```bash
# Backend tests
pytest tests/ -v -m "not requires_api_key"

# Frontend build
cd web && npm ci && npm run build

# Linting
ruff check weather_app/
black --check weather_app/
cd web && npm run lint

# Type checking
mypy weather_app/
cd web && npx tsc -b --noEmit

# Security scans
safety check
bandit -r weather_app/

# Windows installer (Windows only)
cd installer/windows
pyinstaller weather_app_debug.spec
```

---

## Migration Guide (From Old to New)

### If You Had Custom Workflows

**Old workflow references:**
```yaml
# ❌ Old (no longer exists)
needs: [cross-platform-ci]
```

**New workflow references:**
```yaml
# ✅ New
needs: [backend-tests]  # From main-ci.yml
```

### Updating CI Badges

**Old badges:**
```markdown
[![Cross-Platform CI](https://github.com/USER/Weather-App/actions/workflows/cross-platform-ci.yml/badge.svg)](...)
[![Backend CI](https://github.com/USER/Weather-App/actions/workflows/backend-ci.yml/badge.svg)](...)
[![Windows Build](https://github.com/USER/Weather-App/actions/workflows/windows-build.yml/badge.svg)](...)
```

**New badges:**
```markdown
[![Main CI](https://github.com/USER/Weather-App/actions/workflows/main-ci.yml/badge.svg)](https://github.com/USER/Weather-App/actions/workflows/main-ci.yml)
[![Platform Builds](https://github.com/USER/Weather-App/actions/workflows/platform-builds.yml/badge.svg)](https://github.com/USER/Weather-App/actions/workflows/platform-builds.yml)
[![Docs CI](https://github.com/USER/Weather-App/actions/workflows/docs-ci.yml/badge.svg)](https://github.com/USER/Weather-App/actions/workflows/docs-ci.yml)
```

---

## Future Enhancements

### Planned Improvements

1. **Conditional Platform Builds**
   - Only run Windows installer on tags (not every PR)
   - Only run macOS build on main branch

2. **Deploy Previews**
   - Auto-deploy frontend to Vercel/Netlify on PR
   - Temporary backend deployment for testing

3. **Performance Benchmarks**
   - Track API response times
   - Monitor bundle size growth
   - Database query performance

4. **Release Automation**
   - Auto-create releases on version tags
   - Generate changelog from commits
   - Publish artifacts to GitHub Releases

---

## Troubleshooting

### Common Issues

**Issue:** "workflow does not exist" error
**Solution:** Old workflow was removed. Update references to use `main-ci.yml` or `platform-builds.yml`

**Issue:** Path filtering not working
**Solution:** Ensure you're using `github.event_name == 'pull_request'` fallback

**Issue:** Windows installer not building on PR
**Solution:** By design - only builds on `push` to `main` branch

**Issue:** Tests running even though I only changed docs
**Solution:** Check path filter syntax in `if:` conditions

---

## Related Documentation

- **Workflows README**: [.github/workflows/README.md](../../.github/workflows/README.md)
- **CI/CD Guide**: [docs/technical/ci-cd.md](ci-cd.md)
- **Testing Guide**: [docs/testing/refactoring-test-plan.md](../testing/refactoring-test-plan.md)
- **Contributing**: [docs/CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Quick Reference

### Validate Workflow Syntax

```bash
# Install actionlint
brew install actionlint  # macOS
# or
scoop install actionlint  # Windows

# Validate all workflows
actionlint .github/workflows/*.yml
```

### Manual Workflow Trigger

1. Go to Actions tab → Select workflow
2. Click "Run workflow" dropdown
3. Select branch → "Run workflow"

### Check CI Status

```bash
# View recent runs
gh run list --limit 10

# View specific workflow
gh run list --workflow=main-ci.yml

# Watch a run
gh run watch <run-id>
```

---

**Last Updated:** January 6, 2026
**Architecture Version:** 2.0 (Streamlined)
**Status:** ✅ Production Ready
