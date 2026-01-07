# Cross-Platform CI/CD Workflow

**Status:** ✅ Active
**Last Updated:** January 6, 2026
**Workflow File:** [`.github/workflows/cross-platform-ci.yml`](../../.github/workflows/cross-platform-ci.yml)

---

## Overview

The **Cross-Platform Build & Test** workflow is a comprehensive CI/CD pipeline that ensures the Weather App's Phase 2 stack (FastAPI + DuckDB + React/Vite) remains stable across all target platforms:

- **Linux** (Ubuntu) - iPad proxy/server environment
- **Windows** - Desktop PC environment
- **macOS** - Mac desktop environment

This unified workflow consolidates and replaces individual platform-specific checks, providing:
- **Consistent testing** across all platforms
- **Efficient resource usage** through strategic job organization
- **Comprehensive validation** of backend, frontend, and integrations
- **Platform-specific checks** where needed (e.g., DuckDB compatibility)

---

## Architecture

### Job Structure

The workflow consists of **5 main jobs** organized for optimal efficiency:

```
┌─────────────────────────────────────────────────────────────┐
│  1. multi-platform-test (Matrix: 3 OS × 3 Python versions)  │
│     - Backend tests (FastAPI + DuckDB)                       │
│     - Frontend build (React + Vite)                          │
│     - Platform-specific validations                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ├─────────────────────────┐
                              ▼                         ▼
┌───────────────────────────────────┐   ┌───────────────────────────────┐
│  2. lint-and-quality (Ubuntu)     │   │  3. security-scan (Ubuntu)    │
│     - Python: Ruff, Black, mypy   │   │     - Safety (dependencies)   │
│     - Frontend: ESLint, TSC       │   │     - Bandit (code security)  │
└───────────────────────────────────┘   └───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  4. api-integration (Ubuntu)                                 │
│     - FastAPI endpoint tests                                 │
│     - OpenAPI schema validation                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  5. build-artifacts (Matrix: 3 OS)                           │
│     - Production builds for all platforms                    │
│     - Artifact size validation                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Job Details

### 1. Multi-Platform Test (Matrix Build)

**Purpose:** Ensure core functionality works across all target platforms and Python versions.

**Matrix Configuration:**
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
  python-version: ['3.11']  # Primary version
  include:
    - os: ubuntu-latest
      python-version: '3.10'
    - os: ubuntu-latest
      python-version: '3.12'
```

**Total Runs:** 5 combinations
- Ubuntu + Python 3.10
- Ubuntu + Python 3.11
- Ubuntu + Python 3.12
- Windows + Python 3.11
- macOS + Python 3.11

**Steps:**
1. **Backend Testing**
   - Install Python dependencies
   - Run pytest suite (excludes `requires_api_key` tests)
   - Generate coverage reports

2. **Frontend Building**
   - Install Node.js 20
   - Run `npm ci` for reproducible builds
   - Execute Vite build process
   - Validate TypeScript compilation

3. **Platform Validations**
   - Verify DuckDB initialization
   - Validate FastAPI app creation
   - Ensure OS-specific compatibility

4. **Coverage Upload** (Ubuntu 3.11 only)
   - Upload to Codecov for tracking

---

### 2. Lint & Code Quality (Ubuntu Only)

**Purpose:** Enforce code standards and catch style/type issues early.

**Why Ubuntu Only?**
Linting results are platform-independent. Running on one platform saves CI minutes while maintaining quality.

**Python Checks:**
- **Ruff** - Fast linter (replaces flake8, isort in check mode)
- **Black** - Code formatting validation (88 char line length)
- **isort** - Import sorting check (Black-compatible profile)
- **mypy** - Static type checking

**Frontend Checks:**
- **ESLint** - JavaScript/TypeScript linting
  - Includes touch event compatibility checks (iPad)
  - CSS standards validation
- **TypeScript Compiler** - Type checking (`tsc --noEmit`)

**Configuration Files:**
- Python: [`pyproject.toml`](../../pyproject.toml)
- Frontend: [`web/eslint.config.js`](../../web/eslint.config.js)

---

### 3. Security Scan (Ubuntu Only)

**Purpose:** Identify security vulnerabilities in dependencies and code.

**Tools:**
- **Safety** - Checks Python dependencies against known vulnerability databases
- **Bandit** - Scans Python code for security issues (SQL injection, hardcoded secrets, etc.)

**Why Ubuntu Only?**
Security scans analyze code and dependencies, not runtime behavior, so results are platform-independent.

**Continue on Error:**
Both security checks use `continue-on-error: true` to report issues without blocking PRs. Review warnings in CI logs.

---

### 4. API Integration Tests (Ubuntu Only)

**Purpose:** Validate FastAPI endpoints and OpenAPI schema.

**Test Environment:**
- Creates `.env` file with test credentials
- Uses `USE_TEST_DB=true` for isolated testing
- Excludes tests requiring real Ambient Weather API keys

**Validations:**
1. FastAPI endpoint functionality
2. HTTP request/response handling
3. OpenAPI schema generation
4. JSON schema compliance

**Output:**
- Generates `openapi.json` for inspection
- Validates schema structure

---

### 5. Build Artifacts (Multi-Platform)

**Purpose:** Ensure production builds succeed on all target platforms.

**Dependencies:**
Requires successful completion of:
- `multi-platform-test`
- `lint-and-quality`

**Steps:**
1. Build frontend with Vite
2. Check bundle sizes
3. Validate artifact creation

**Platform-Specific Notes:**
- **Windows:** Uses `dir` for directory listing
- **Linux/Mac:** Uses `du -sh` for size checking

---

## Triggers

### Push Events
```yaml
on:
  push:
    branches: [ main, develop ]
```

Runs on every push to `main` or `develop` branches.

### Pull Request Events
```yaml
on:
  pull_request:
    branches: [ main, develop ]
```

Runs on PRs targeting `main` or `develop` branches.

---

## Performance Optimizations

### 1. Dependency Caching

**Python (pip):**
```yaml
uses: actions/setup-python@v5
with:
  cache: 'pip'
```

**Node.js (npm):**
```yaml
uses: actions/setup-node@v4
with:
  cache: 'npm'
  cache-dependency-path: web/package-lock.json
```

**Impact:** Reduces dependency installation time by ~60-80%.

### 2. Strategic Job Distribution

- **Run once on Ubuntu:** Linting, security, API tests (platform-independent)
- **Run on all platforms:** Core functionality tests, builds (platform-dependent)

**Savings:** ~40% reduction in total CI minutes compared to running everything on all platforms.

### 3. Fail-Fast Strategy

```yaml
strategy:
  fail-fast: false
```

**Disabled** to allow all platform combinations to complete, providing comprehensive results even if one platform fails.

### 4. Parallel Execution

Jobs run in parallel where possible:
- `multi-platform-test` runs independently
- `lint-and-quality`, `security-scan`, `api-integration` run in parallel after tests
- `build-artifacts` waits for quality gates

---

## Platform-Specific Considerations

### Ubuntu (Linux)

**Purpose:**
- Primary CI platform (fastest, most cost-effective)
- iPad server environment proxy
- Runs all quality checks

**Unique Tests:**
- Python 3.10, 3.11, 3.12 compatibility
- iPad UI linting (touch events, responsive CSS)

### Windows

**Purpose:**
- Desktop PC environment
- Windows-specific path handling
- Console encoding (UTF-8 for emojis)

**Known Issues:**
- Uses `\` path separators (handled by `shell: bash`)
- Directory listing uses `dir` instead of `du`

**Validations:**
- DuckDB Windows compatibility
- PyInstaller frozen app support
- Windows tray icon functionality

### macOS

**Purpose:**
- Mac desktop environment
- Unix-like path handling
- Native macOS app compatibility

**Validations:**
- DuckDB macOS compatibility
- macOS-specific UI behaviors
- Potential future macOS app bundle builds

---

## Monitoring & Debugging

### Viewing Results

**GitHub Actions UI:**
1. Go to repository → Actions tab
2. Select "Cross-Platform Build & Test" workflow
3. Click on a specific run
4. View matrix results by OS/Python version

**Job Summaries:**
- ✅ Green checkmark: All tests passed
- ❌ Red X: Tests failed (click for details)
- 🟡 Yellow: Some checks failed but allowed to continue

### Common Failure Scenarios

| Issue | Likely Cause | Where to Check |
|-------|--------------|----------------|
| Backend tests fail on Windows only | Path separator issues, encoding | `multi-platform-test` → Windows logs |
| Frontend build fails on all platforms | TypeScript errors, missing deps | `multi-platform-test` → Build Frontend step |
| Linting fails | Code style violations | `lint-and-quality` → Ruff/ESLint logs |
| Security scan warnings | Outdated dependencies | `security-scan` → Safety output |
| API tests fail | Schema changes, breaking changes | `api-integration` → pytest logs |

### Debugging Tips

**Local Reproduction:**
```bash
# Reproduce backend tests locally
pytest tests/ -v -m "not requires_api_key" --cov=weather_app

# Reproduce linting locally
ruff check weather_app/ tests/
black --check weather_app/
isort --check-only weather_app/

# Reproduce frontend build locally
cd web
npm ci
npm run build
npm run lint
npx tsc -b --noEmit
```

**Check Platform-Specific Issues:**
```bash
# Windows-specific encoding test
python -c "import sys; print(sys.stdout.encoding)"

# DuckDB compatibility test
python -c "import duckdb; print(duckdb.__version__)"
```

---

## Migration Notes

### Replaced Workflows

This workflow consolidates functionality from:
- [`backend-ci.yml`](../../.github/workflows/backend-ci.yml) - Backend testing
- [`frontend-ci.yml`](../../.github/workflows/frontend-ci.yml) - Frontend testing

### What Changed

**Before (Separate Workflows):**
- Backend CI: 3 jobs (lint, test matrix, security, api-tests)
- Frontend CI: 3 jobs (lint, type-check, build)
- **Total:** 6 jobs across 2 workflows

**After (Unified Workflow):**
- Cross-Platform CI: 5 jobs with smart distribution
- **Benefit:** Unified status checks, better resource usage

### Keeping Old Workflows

**Decision:** Keep `backend-ci.yml` and `frontend-ci.yml` temporarily for:
1. Gradual migration validation
2. Fallback if issues arise
3. Path-specific triggers (only run when backend/frontend changes)

**Future:** Once `cross-platform-ci.yml` is proven stable, consider:
- Disabling old workflows
- Adding path filters to new workflow
- Archiving old workflows with documentation

---

## Future Enhancements

### Planned Improvements

1. **Docker Integration**
   - Add Docker build tests
   - Validate `docker-compose.yml`
   - Test containerized deployments

2. **End-to-End Tests**
   - Playwright for browser automation
   - Full stack integration tests
   - iPad Safari compatibility tests

3. **Performance Benchmarks**
   - API response time tracking
   - Frontend bundle size limits
   - Database query performance

4. **Deployment Preview**
   - Automatic preview deployments on PR
   - Vercel/Netlify integration for frontend
   - Railway/Fly.io for backend

5. **Artifact Publishing**
   - Upload build artifacts as GitHub releases
   - Publish to PyPI (backend)
   - Publish to npm (frontend components)

### Path-Based Triggers

Consider adding path filters to optimize CI runs:

```yaml
on:
  push:
    branches: [ main, develop ]
    paths:
      - 'weather_app/**'
      - 'web/**'
      - 'tests/**'
      - 'requirements.txt'
      - 'web/package.json'
      - '.github/workflows/cross-platform-ci.yml'
```

This prevents CI runs on documentation-only changes.

---

## Related Documentation

- **General CI/CD:** [docs/technical/ci-cd.md](ci-cd.md)
- **Testing Guide:** [docs/testing/refactoring-test-plan.md](../testing/refactoring-test-plan.md)
- **Backend Testing:** [pytest.ini](../../pytest.ini)
- **Frontend Linting:** [web/eslint.config.js](../../web/eslint.config.js)
- **Project Guidelines:** [.claude/CLAUDE.md](../../.claude/CLAUDE.md)

---

## Quick Reference

### Workflow Status Badge

Add to README.md:
```markdown
[![Cross-Platform CI](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/cross-platform-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/cross-platform-ci.yml)
```

### Manual Trigger

To manually run the workflow:
1. Go to Actions tab
2. Select "Cross-Platform Build & Test"
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button

### CI Minute Usage Estimate

**Per Workflow Run:**
- Multi-platform test (5 jobs): ~15 minutes
- Lint & quality: ~3 minutes
- Security scan: ~2 minutes
- API integration: ~2 minutes
- Build artifacts (3 jobs): ~6 minutes

**Total:** ~28 minutes per push (actual time ~8-10 minutes with parallelization)

---

**Questions?** See [docs/CONTRIBUTING.md](../CONTRIBUTING.md) or open an issue.
