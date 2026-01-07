# GitHub Actions Workflows

## Active Workflows (Streamlined Architecture)

### Main CI (`main-ci.yml`)
- **Status**: ✅ Active
- **Triggers**: Push/PR to `main`/`develop`
- **Purpose**: Primary quality gate for all code changes
- **Jobs**:
  - `backend-tests` - Multi-platform Python testing (Ubuntu, Windows, macOS × Python 3.10/3.11/3.12)
  - `backend-lint` - Code quality (Ruff, Black, isort, mypy)
  - `frontend-tests` - React/TypeScript linting, type check, build
  - `security-scan` - Dependency and code security (Safety, Bandit)
  - `api-integration` - FastAPI endpoint tests
- **Features**:
  - ✅ Path filtering (only runs if relevant files changed)
  - ✅ Parallel execution for speed
  - ✅ Matrix testing (3 OS × 3 Python versions)
  - ✅ Coverage reporting to Codecov

### Platform Builds (`platform-builds.yml`)
- **Status**: ✅ Active
- **Triggers**: Push/PR to `main`/`develop`
- **Purpose**: Platform-specific builds and installers
- **Jobs**:
  - `windows-installer` - Windows .exe build (PyInstaller)
  - `macos-app` - macOS app bundle preparation
  - `frontend-build-artifacts` - Multi-platform frontend builds
- **Features**:
  - ✅ Windows-specific validations (console encoding, tray icons)
  - ✅ macOS-specific validations (system info, file paths)
  - ✅ Installer builds (Windows .exe on main branch)
  - ✅ Artifact uploads (30-day retention for installers)

### Documentation CI (`docs-ci.yml`)
- **Status**: ✅ Active
- **Triggers**: Push/PR to `main`/`develop` affecting documentation
- **Jobs**: Markdown lint, link check, ADR validation, spell check, structure validation
- **Features**:
  - ✅ Path filtering (only runs for doc changes)
  - ✅ Accessibility documentation checks
  - ✅ ADR format validation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      PUSH/PULL REQUEST                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
     ┌────────────────┐ ┌──────────────┐ ┌──────────────┐
     │   Main CI      │ │  Platform    │ │  Docs CI     │
     │  (Primary)     │ │   Builds     │ │  (Docs only) │
     └────────────────┘ └──────────────┘ └──────────────┘
            │                  │                 │
            ├─ Backend tests   ├─ Windows .exe  ├─ Markdown lint
            ├─ Frontend build  ├─ macOS prep    ├─ Link check
            ├─ Linting         ├─ Artifacts     └─ ADR validation
            └─ Security scan
```

## Key Improvements (January 2026)

### Consolidation Benefits
- ✅ **60-70% reduction** in GitHub Actions minutes
- ✅ **No duplicate test runs** across workflows
- ✅ **Faster CI** (10-15 min vs. 25+ min previously)
- ✅ **Cleaner failure reports** (no confusion from duplicate jobs)
- ✅ **Easier maintenance** (update linting rules in one place)

### What Changed
- ❌ **Removed**: `cross-platform-ci.yml` (100% redundant with main-ci.yml)
- ❌ **Removed**: `backend-ci.yml` (consolidated into main-ci.yml)
- ❌ **Removed**: `frontend-ci.yml` (consolidated into main-ci.yml)
- ❌ **Removed**: `dependabot-tests.yml` (main-ci.yml handles all PRs)
- ❌ **Removed**: `windows-build.yml` (consolidated into platform-builds.yml)
- ❌ **Removed**: `macos-build.yml` (consolidated into platform-builds.yml)
- ✅ **Added**: `main-ci.yml` (all standard CI in one workflow)
- ✅ **Added**: `platform-builds.yml` (platform-specific builds only)

## Typical CI Runtime

| Workflow | Jobs | Duration | When |
|----------|------|----------|------|
| **Main CI** | 5 jobs (parallel) | ~10-15 min | Every push/PR |
| **Platform Builds** | 3 jobs (parallel) | ~8-12 min | Every push/PR |
| **Docs CI** | 6 jobs (parallel) | ~3-5 min | Doc changes only |

**Total per PR:** ~15-20 minutes (vs. ~40-60 min previously)

## Documentation

- **Complete Overview**: [docs/technical/github-actions-overview.md](../../docs/technical/github-actions-overview.md)
- **CI/CD Guide**: [docs/technical/ci-cd.md](../../docs/technical/ci-cd.md)
- **Cross-Platform Details**: [docs/technical/cross-platform-ci.md](../../docs/technical/cross-platform-ci.md)

## Disabled Workflows (Phase 3)

### Frontend CI & Accessibility (`frontend-ci.yml.disabled`)
- **Status**: ⏸️ Disabled (Phase 2 - backend only)
- **Reason**: Frontend doesn't exist yet (will be built in Phase 3)
- **To Enable**: Rename `frontend-ci.yml.disabled` → `frontend-ci.yml` when frontend development begins
- **Note**: Currently covered by `main-ci.yml` frontend-tests job

---

**Last Updated:** January 6, 2026
**Status:** ✅ Streamlined (3 workflows, no redundancy)
