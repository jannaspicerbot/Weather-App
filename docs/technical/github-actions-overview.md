# GitHub Actions CI/CD Overview

**Status:** ✅ Active
**Last Updated:** January 6, 2026
**Phase:** Phase 2 - Multi-Platform Testing

---

## Overview

The Weather App uses a **three-tiered GitHub Actions strategy** to ensure comprehensive testing and build validation across all target platforms:

1. **Cross-Platform CI** - Quick, efficient multi-platform matrix testing
2. **macOS Build** - Dedicated macOS-specific validations and builds
3. **Windows Build** - Windows-specific testing with installer builds

---

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PUSH/PULL REQUEST                        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
        ┌───────────────┐ ┌──────────┐ ┌──────────────┐
        │ Cross-Platform│ │  macOS   │ │   Windows    │
        │      CI       │ │  Build   │ │    Build     │
        └───────────────┘ └──────────┘ └──────────────┘
                │              │              │
                │              │              │
        ┌───────┴──────────────┴──────────────┴────────┐
        │          ALL WORKFLOWS MUST PASS              │
        │     (Required for merge to main/develop)      │
        └───────────────────────────────────────────────┘
```

---

## Workflow Comparison

| Feature | Cross-Platform CI | macOS Build | Windows Build |
|---------|-------------------|-------------|---------------|
| **Primary Purpose** | Fast matrix testing | Native Mac validation | Native Windows + Installer |
| **Platforms Tested** | Linux, Windows, Mac | macOS only | Windows only |
| **Python Versions** | 3.10, 3.11, 3.12 | 3.11 | 3.11 |
| **Backend Tests** | ✅ Full suite | ✅ Full suite | ✅ Full suite |
| **Frontend Build** | ✅ Vite + TypeScript | ✅ Vite + TypeScript | ✅ Vite + TypeScript |
| **Linting** | ✅ Python + TypeScript | ❌ (covered by cross-platform) | ❌ (covered by cross-platform) |
| **Security Scan** | ✅ Safety + Bandit | ❌ (covered by cross-platform) | ❌ (covered by cross-platform) |
| **Platform-Specific** | DuckDB + FastAPI checks | macOS system info, file paths | Console encoding, tray icon, paths |
| **Installer Build** | ❌ | ❌ (future: .app bundle) | ✅ PyInstaller .exe |
| **Artifacts Uploaded** | Coverage only | Frontend dist + test results | Frontend dist + .exe + test results |
| **Typical Runtime** | ~8-10 min (parallel) | ~5-7 min | ~8-12 min (with installer) |
| **Runs On** | Every push/PR | Every push/PR | Every push/PR |

---

## When Each Workflow Runs

### Cross-Platform CI (`.github/workflows/cross-platform-ci.yml`)

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Purpose:**
- Primary quality gate for all code changes
- Ensures compatibility across all platforms
- Runs comprehensive test suite
- Validates code quality and security

**Jobs:**
1. `multi-platform-test` - Tests on Ubuntu, Windows, macOS (matrix)
2. `lint-and-quality` - Code style and type checking
3. `security-scan` - Dependency and code security
4. `api-integration` - FastAPI endpoint tests
5. `build-artifacts` - Production build validation

**When to Check:**
- ✅ Before merging any PR
- ✅ After pushing to main/develop
- ✅ For multi-platform compatibility issues

---

### macOS Build (`.github/workflows/macos-build.yml`)

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Purpose:**
- Dedicated macOS environment validation
- Native Mac system testing
- Preparation for future macOS app bundle

**Jobs:**
1. `build-macos` - Complete macOS build and test

**Unique Features:**
- macOS system information (`sw_vers`)
- Native file system testing
- macOS-specific path handling
- Future: `.app` bundle creation

**When to Check:**
- ✅ For macOS-specific issues
- ✅ Before releasing Mac-compatible versions
- ✅ Testing macOS system integration

---

### Windows Build (`.github/workflows/windows-build.yml`)

**Triggers:**
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
```

**Purpose:**
- Windows-specific validation and builds
- PyInstaller executable creation
- Windows desktop compatibility testing

**Jobs:**
1. `build-windows` - Complete Windows build, test, and package

**Unique Features:**
- Windows console encoding tests (emoji support)
- System tray icon validation
- **PyInstaller .exe build** (on main branch pushes)
- PowerShell-based validations
- Windows path handling tests

**Installer Build:**
- Only builds on `push` to `main` branch
- Uses `installer/windows/weather_app_debug.spec`
- Runs verification tests from `tests/test_installer_build.py`
- Uploads `.exe` artifact with 30-day retention

**When to Check:**
- ✅ For Windows-specific issues
- ✅ Before releasing Windows installers
- ✅ Testing desktop tray functionality
- ✅ Validating PyInstaller builds

---

## Workflow Relationships

### Redundancy vs. Specialization

**Question:** Why run tests on multiple workflows?

**Answer:** Strategic redundancy with specialization:

1. **Cross-Platform CI** = Fast, broad coverage
   - Tests all platforms in matrix
   - Quick feedback (~10 min total)
   - Covers 80% of platform issues

2. **macOS/Windows Build** = Deep, platform-specific
   - Native environment testing
   - Platform-specific features
   - Build artifacts (installers)
   - Catches edge cases missed by matrix

### Optimization Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│  CROSS-PLATFORM CI (Runs on all platforms - FAST)               │
│  - Quick matrix testing                                          │
│  - Linting (once on Ubuntu)                                      │
│  - Security (once on Ubuntu)                                     │
│  - Basic platform compatibility                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ If all pass ✅
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  PLATFORM-SPECIFIC BUILDS (Parallel execution)                  │
│  ┌──────────────────────┐  ┌─────────────────────────────────┐ │
│  │   macOS Build        │  │   Windows Build                 │ │
│  │  - macOS validation  │  │  - Windows validation           │ │
│  │  - System integration│  │  - Installer build              │ │
│  │  - Future: .app      │  │  - Tray icon test               │ │
│  └──────────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Cost Efficiency:**
- Linting runs once (Ubuntu) instead of 3x (all platforms)
- Security scans run once (Ubuntu) instead of 3x
- Platform-specific tests only run on relevant platforms
- **Total CI Minutes:** ~25-30 min per push (vs. ~60 min if everything ran on all platforms)

---

## Artifact Management

### What Gets Uploaded

| Workflow | Artifact Name | Contents | Retention |
|----------|---------------|----------|-----------|
| **Cross-Platform CI** | ❌ None | Coverage uploaded to Codecov | N/A |
| **macOS Build** | `macos-weather-app-dist` | `web/dist/` (frontend bundle) | 7 days |
| **macOS Build** | `macos-test-results` | `.coverage`, `htmlcov/` | 7 days |
| **Windows Build** | `windows-weather-app-dist` | `web/dist/` (frontend bundle) | 7 days |
| **Windows Build** | `windows-installer-exe` | `WeatherApp.exe` | 30 days |
| **Windows Build** | `windows-test-results` | `.coverage`, `htmlcov/` | 7 days |

### Downloading Artifacts

**From GitHub UI:**
1. Go to Actions tab
2. Click on a completed workflow run
3. Scroll to "Artifacts" section
4. Download desired artifact

**From CLI (gh):**
```bash
# List artifacts from latest run
gh run list --workflow=windows-build.yml --limit 1

# Download specific artifact
gh run download <run-id> -n windows-installer-exe
```

---

## Branch Protection Rules

### Recommended Settings

Configure in **Settings → Branches → Branch Protection Rules** for `main`:

```yaml
Require status checks to pass before merging: ✅
  - Cross-Platform Build & Test / multi-platform-test (ubuntu-latest, 3.11)
  - Cross-Platform Build & Test / lint-and-quality
  - macOS Build & Test / build-macos
  - Windows Build & Test / build-windows

Require branches to be up to date before merging: ✅
Require pull request reviews before merging: ✅ (1 reviewer)
```

**Effect:** PRs must pass ALL workflows before merging.

---

## Debugging Failed Workflows

### Step-by-Step Debugging

1. **Identify Which Workflow Failed**
   - Check GitHub Actions tab
   - Look for ❌ red X next to workflow name

2. **Open Failed Workflow**
   - Click on failed run
   - Expand failed job
   - Identify failed step

3. **Common Failure Patterns**

| Symptom | Likely Cause | Where to Look |
|---------|--------------|---------------|
| Backend tests fail on Windows only | Path separators, encoding | `windows-build.yml` → Backend tests |
| Frontend build fails on all platforms | TypeScript error, dependency issue | Any workflow → Build Frontend |
| macOS-specific failure | File permissions, system paths | `macos-build.yml` → Platform checks |
| Installer build fails | PyInstaller config, missing files | `windows-build.yml` → Build Windows Installer |
| Linting fails | Code style violation | `cross-platform-ci.yml` → lint-and-quality |

4. **Reproduce Locally**

```bash
# Reproduce cross-platform tests
pytest tests/ -v -m "not requires_api_key"

# Reproduce frontend build
cd web && npm ci && npm run build

# Reproduce linting
ruff check weather_app/
black --check weather_app/
cd web && npm run lint

# Reproduce Windows installer build (Windows only)
cd installer/windows
pyinstaller weather_app_debug.spec
```

---

## Performance Monitoring

### CI Minute Usage Tracking

**Monthly Budget Considerations:**
- Free tier: 2,000 minutes/month
- Windows minutes: 2x multiplier
- macOS minutes: 10x multiplier

**Per Push Estimate:**
| Workflow | Ubuntu | Windows | macOS | Total Minutes |
|----------|--------|---------|-------|---------------|
| Cross-Platform CI | 8 min | 4 min (×2=8) | 4 min (×10=40) | ~56 min |
| macOS Build | - | - | 6 min (×10=60) | ~60 min |
| Windows Build | - | 10 min (×2=20) | - | ~20 min |
| **Total per push** | | | | **~136 min** |

**Actual cost:** Lower due to parallel execution (~30-40 min wall time)

### Optimization Tips

1. **Use Path Filters** (future enhancement)
   ```yaml
   on:
     push:
       paths:
         - 'weather_app/**'
         - 'web/**'
         - 'tests/**'
   ```
   Skips CI on doc-only changes.

2. **Conditional Jobs**
   ```yaml
   if: github.event_name == 'push' && github.ref == 'refs/heads/main'
   ```
   Only build installers on main branch.

3. **Cache Dependencies**
   Already implemented:
   - `cache: 'pip'` for Python
   - `cache: 'npm'` for Node.js

---

## Future Enhancements

### Planned Improvements

1. **Docker Integration**
   - Add Docker build workflow
   - Test containerized deployment
   - Push to Docker Hub/GitHub Container Registry

2. **End-to-End Testing**
   - Add Playwright workflow
   - Browser automation tests
   - iPad Safari compatibility

3. **Deployment Workflows**
   - Auto-deploy to staging (on PR)
   - Auto-deploy to production (on main merge)
   - Vercel/Netlify for frontend
   - Railway/Fly.io for backend

4. **Release Automation**
   - Semantic versioning
   - Auto-generate release notes
   - Publish artifacts to GitHub Releases
   - Update version numbers automatically

5. **Performance Benchmarks**
   - API response time tracking
   - Frontend bundle size limits
   - Database query performance

### Experimental Features

- **Scheduled Runs:** Daily integration tests
- **Dependency Updates:** Automated Dependabot PR testing
- **Coverage Reports:** Automatic PR comments with coverage diffs
- **Deploy Previews:** Temporary environments for PR testing

---

## Related Documentation

- **Cross-Platform CI Details:** [docs/technical/cross-platform-ci.md](cross-platform-ci.md)
- **General CI/CD:** [docs/technical/ci-cd.md](ci-cd.md)
- **Testing Guide:** [docs/testing/refactoring-test-plan.md](../testing/refactoring-test-plan.md)
- **Windows Installer:** [installer/windows/TESTING.md](../../installer/windows/TESTING.md)
- **Contributing:** [docs/CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Quick Reference

### Workflow Status Badges

Add to `README.md`:

```markdown
[![Cross-Platform CI](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/cross-platform-ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/cross-platform-ci.yml)
[![macOS Build](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/macos-build.yml/badge.svg)](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/macos-build.yml)
[![Windows Build](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/windows-build.yml/badge.svg)](https://github.com/YOUR_USERNAME/Weather-App/actions/workflows/windows-build.yml)
```

### Manual Workflow Runs

Trigger workflows manually via GitHub UI:
1. Actions tab → Select workflow
2. "Run workflow" dropdown
3. Select branch → "Run workflow"

### Checking Workflow Syntax

```bash
# Install actionlint
brew install actionlint  # macOS
# or
scoop install actionlint  # Windows

# Validate workflow files
actionlint .github/workflows/*.yml
```

---

## Troubleshooting

### Common Issues

**Issue:** "PyInstaller not found" in Windows workflow
**Solution:** Ensure `pyinstaller` is in `requirements.txt` or installed in workflow

**Issue:** macOS workflow fails on file permissions
**Solution:** Check file permissions in spec files, ensure `chmod +x` if needed

**Issue:** Frontend build fails with "ENOENT: package-lock.json"
**Solution:** Verify `cache-dependency-path: web/package-lock.json` is correct

**Issue:** Tests fail with "Module not found"
**Solution:** Ensure `pip install -e .` runs before tests

**Issue:** Workflow doesn't trigger
**Solution:** Check branch names match trigger configuration (`main`, not `master`)

---

## Support

**Questions?**
- Review [docs/CONTRIBUTING.md](../CONTRIBUTING.md)
- Check existing [GitHub Issues](https://github.com/YOUR_USERNAME/Weather-App/issues)
- Open new issue with `ci-cd` label

**Last Updated:** January 6, 2026
