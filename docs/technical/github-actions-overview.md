# GitHub Actions CI/CD Overview

**Status:** ✅ Streamlined (January 2026)
**Last Updated:** January 7, 2026
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
    paths:
      - 'weather_app/**'
      - 'installer/**'
      - 'web/**'
      - 'requirements.txt'
      - 'setup.py'
      - 'pyproject.toml'
      - 'package.json'
      - '.github/workflows/platform-builds.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      # Same paths as push
```

**Jobs:**

| Job | Runs On | Purpose | Duration |
|-----|---------|---------|----------|
| `windows-installer` | Windows only | PyInstaller .exe builds (production + debug) + Windows-specific tests | ~8-12 min |
| `macos-app` | macOS only | PyInstaller .app bundles (production + debug) + macOS-specific tests | ~8-12 min |

**Windows-Specific Validations:**
- Console encoding tests (emoji support: ✅ 📊 🌡️ 💧)
- System tray icon compatibility (PIL + pystray)
- Windows path handling
- PowerShell integration
- **PyInstaller .exe builds** (production + debug, on all PRs and pushes)

**macOS-Specific Validations:**
- macOS system information (`sw_vers`)
- File system compatibility
- Native path handling
- **PyInstaller .app bundle builds** (production + debug, on all PRs and pushes)

**Installer Builds:**
- Windows .exe builds on all PRs and pushes to main/develop
  - Production: `installer/windows/weather_app.spec` → `WeatherApp.exe`
  - Debug: `installer/windows/weather_app_debug.spec` → `WeatherApp_Debug.exe` (with console)
- macOS .app bundle builds on all PRs and pushes to main/develop
  - Production: `installer/macos/weather_app.spec` → `WeatherApp.app`
  - Debug: `installer/macos/weather_app_debug.spec` → `WeatherApp_Debug.app` (with console)

**Artifacts:**
- `windows-installer-<sha>` - WeatherApp.exe production build (7 days for PRs, 30 days for main)
- `windows-installer-debug-<sha>` - WeatherApp_Debug.exe with console (7 days for PRs, 30 days for main)
- `macos-app-bundle-<sha>` - WeatherApp.app production build (7 days for PRs, 30 days for main)
- `macos-app-bundle-debug-<sha>` - WeatherApp_Debug.app with console (7 days for PRs, 30 days for main)

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
| **Platform Builds** | `windows-installer-<sha>` | WeatherApp.exe (production) | 7 days (PR) / 30 days (main) |
| **Platform Builds** | `windows-installer-debug-<sha>` | WeatherApp_Debug.exe (with console) | 7 days (PR) / 30 days (main) |
| **Platform Builds** | `macos-app-bundle-<sha>` | WeatherApp.app (production) | 7 days (PR) / 30 days (main) |
| **Platform Builds** | `macos-app-bundle-debug-<sha>` | WeatherApp_Debug.app (with console) | 7 days (PR) / 30 days (main) |

### Production vs Debug Builds

| Build Type | Console | Use Case |
|------------|---------|----------|
| **Production** | Hidden | Normal use - clean UI without console window |
| **Debug** | Visible | Troubleshooting - shows logs and error messages in console |

Debug builds also set `USE_TEST_DB=true`, `LOG_LEVEL=DEBUG`, and `DEBUG_MODE=true` via runtime hooks.

### Downloading Artifacts

**From GitHub UI:**
1. Go to Actions tab → Select workflow run
2. Scroll to "Artifacts" section
3. Download desired artifact

**From CLI (gh):**
```bash
# List recent workflow runs
gh run list --workflow=platform-builds.yml --limit 5

# Download Windows production installer
gh run download <run-id> -n windows-installer-<sha>

# Download Windows debug installer
gh run download <run-id> -n windows-installer-debug-<sha>

# Download macOS production app
gh run download <run-id> -n macos-app-bundle-<sha>

# Download macOS debug app
gh run download <run-id> -n macos-app-bundle-debug-<sha>
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
pyinstaller weather_app.spec        # Production
pyinstaller weather_app_debug.spec  # Debug

# macOS app bundle (macOS only)
cd installer/macos
pyinstaller weather_app.spec        # Production
pyinstaller weather_app_debug.spec  # Debug
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

## Quality Gates

### Pull Request Requirements

Before a PR can be merged to `main`, it must:

1. **Pass all CI workflows** ✅
   - Main CI (all jobs: backend-tests, backend-lint, frontend-tests, security-scan, api-integration)
   - Platform Builds (optional: windows-installer, macos-app)
   - Documentation CI (if docs changed)

2. **Code coverage** (recommended)
   - Backend: ≥80% coverage
   - Frontend: ≥80% coverage

3. **Code review** (manual)
   - At least one approval from code owner
   - All conversations resolved

4. **No security vulnerabilities**
   - Safety and Bandit scans pass or warnings are reviewed/accepted

---

## Local Development

### Running Tests Locally

Before pushing, run these commands locally to catch issues early:

#### Backend Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov pytest-asyncio ruff black isort mypy

# Run tests with coverage
pytest tests/ -v --cov=weather_app -m "not requires_api_key"

# Run linting
ruff check weather_app/ tests/ --exclude tests/archive
black --check weather_app/ tests/ --exclude tests/archive
isort --check-only weather_app/ tests/ --skip tests/archive
mypy weather_app/

# Auto-fix formatting
black weather_app/ tests/ --exclude tests/archive
isort weather_app/ tests/ --skip tests/archive
```

#### Frontend Tests
```bash
cd web

# Install dependencies
npm ci

# Run tests
npm run test

# Run linting
npm run lint

# Type check
npx tsc -b --noEmit

# Build production bundle
npm run build

# Auto-fix formatting
npm run lint -- --fix
```

#### Documentation Checks
```bash
# Install markdownlint-cli (if not installed)
npm install -g markdownlint-cli

# Lint markdown files
markdownlint '**/*.md' --ignore node_modules --ignore web/node_modules

# Check links (requires markdown-link-check)
npm install -g markdown-link-check
find docs -name "*.md" -exec markdown-link-check {} \;
```

---

## Troubleshooting

### Common CI Failures

#### Backend Issues

**Issue:** "Black formatting failed"
**Cause:** Code not formatted with Black
**Fix:**
```bash
black weather_app/ tests/ --exclude tests/archive
git add .
git commit --amend --no-edit
git push --force-with-lease
```

**Issue:** "Ruff linting errors"
**Cause:** Code style violations
**Fix:**
```bash
ruff check weather_app/ tests/ --exclude tests/archive --fix
git add .
git commit -m "Fix: Resolve linting issues"
```

**Issue:** "mypy type checking failed"
**Cause:** Type annotation issues
**Fix:** Review mypy output and add/fix type hints. Common issues:
- Missing return type annotations
- Incorrect type specifications
- Missing imports for types

**Issue:** "pytest tests failed"
**Cause:** Test failures or errors
**Fix:**
```bash
# Run tests locally to see details
pytest tests/ -v -m "not requires_api_key"

# Run specific failing test
pytest tests/test_specific.py::test_function -v

# Run with print statements visible
pytest tests/ -v -s
```

#### Frontend Issues

**Issue:** "ESLint errors"
**Cause:** JavaScript/TypeScript linting violations
**Fix:**
```bash
cd web
npm run lint -- --fix  # Auto-fix some issues
npm run lint           # Review remaining issues
```

**Issue:** "TypeScript compilation failed"
**Cause:** Type errors in TypeScript code
**Fix:**
```bash
cd web
npx tsc -b --noEmit  # See all type errors
# Fix type errors in reported files
```

**Issue:** "Vite build failed"
**Cause:** Build errors, missing dependencies, or configuration issues
**Fix:**
```bash
cd web
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Security Issues

**Issue:** "Safety check found vulnerabilities"
**Cause:** Known vulnerabilities in Python dependencies
**Fix:**
1. Review Safety output for affected packages
2. Update vulnerable packages: `pip install --upgrade <package>`
3. If no fix available, assess risk and document in security review
4. Add to ignore list if false positive

**Issue:** "Bandit found security issues"
**Cause:** Potential security issues in Python code
**Fix:**
1. Review Bandit output
2. Fix legitimate issues (SQL injection, hardcoded secrets, etc.)
3. Add `# nosec` comment with justification for false positives

#### Documentation Issues

**Issue:** "Broken links in documentation"
**Cause:** Invalid internal or external links
**Fix:**
1. Review link-check job output
2. Fix broken links in markdown files
3. Update `.markdown-link-check.json` to ignore known external issues

**Issue:** "ADR sequence gap"
**Cause:** Missing ADR number in sequence
**Fix:**
- ADRs must be numbered sequentially (001, 002, 003, ...)
- If you deleted an ADR, don't reuse the number
- Add a note in the next ADR: "ADR-XXX was superseded and removed"

#### Workflow-Specific Issues

**Issue:** "workflow does not exist" error
**Solution:** Old workflow was removed. Update references to use `main-ci.yml` or `platform-builds.yml`

**Issue:** Path filtering not working
**Solution:** Ensure you're using `github.event_name == 'pull_request'` fallback in `if:` conditions

**Issue:** Platform builds not triggering
**Solution:** Check that your changes touch files in the path filter (weather_app/, installer/, web/, etc.)

**Issue:** Tests running even though I only changed docs
**Solution:** Check path filter syntax in `if:` conditions. Docs-only changes should only trigger `docs-ci.yml`

**Issue:** Job stuck "waiting for a runner"
**Solution:** GitHub Actions queue is full. Wait or cancel other running workflows to free up runners.

---

## Related Documentation

- **Workflows README**: [.github/workflows/README.md](../../.github/workflows/README.md)
- **Testing Guide**: [docs/testing/refactoring-test-plan.md](../testing/refactoring-test-plan.md)
- **Contributing**: [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- **Archived CI Docs**: [docs/archive/ci-cd/](../../archive/ci-cd/) - Historical workflow documentation (pre-consolidation)

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

**Last Updated:** January 7, 2026
**Architecture Version:** 2.2 (Simplified - Debug Builds for Both Platforms)
**Status:** ✅ Production Ready
