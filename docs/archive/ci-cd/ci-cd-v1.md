# CI/CD Automation

**Version:** 2.0
**Date:** 2026-01-06
**Status:** Active

---

## Overview

The Weather App uses GitHub Actions for continuous integration and continuous deployment. All code changes are automatically tested for quality, security, accessibility, and documentation standards before merging.

**NEW:** The project now uses a **three-tiered CI/CD strategy** with dedicated workflows for cross-platform testing, macOS builds, and Windows installers. See [GitHub Actions Overview](github-actions-overview.md) for complete details.

---

## Quick Links

- **📋 [GitHub Actions Overview](github-actions-overview.md)** - Complete workflow architecture and strategy
- **🔄 [Cross-Platform CI Details](cross-platform-ci.md)** - Matrix testing documentation
- **🪟 Windows Build:** `.github/workflows/windows-build.yml`
- **🍎 macOS Build:** `.github/workflows/macos-build.yml`
- **🌐 Cross-Platform:** `.github/workflows/cross-platform-ci.yml`

---

## Table of Contents

- [Workflows](#workflows)
- [Quality Gates](#quality-gates)
- [Accessibility Testing](#accessibility-testing)
- [Local Development](#local-development)
- [Troubleshooting](#troubleshooting)

---

## Workflows

### Primary Workflows (Active)

#### 1. Cross-Platform CI (`cross-platform-ci.yml`) ⭐ NEW

**Purpose:** Fast, efficient multi-platform matrix testing

**Triggers:** Push/PR to `main` or `develop`

**Jobs:**
- **multi-platform-test**: Tests on Ubuntu, Windows, macOS with Python 3.10, 3.11, 3.12
- **lint-and-quality**: Python (Ruff, Black, isort, mypy) + Frontend (ESLint, TSC)
- **security-scan**: Safety + Bandit
- **api-integration**: FastAPI endpoint tests
- **build-artifacts**: Production builds for all platforms

**See:** [cross-platform-ci.md](cross-platform-ci.md) for detailed documentation

---

#### 2. macOS Build (`macos-build.yml`) ⭐ NEW

**Purpose:** Native macOS validation and builds

**Triggers:** Push/PR to `main` or `develop`

**Jobs:**
- **build-macos**: Complete macOS build, test, and validation
  - Backend tests with DuckDB/FastAPI validation
  - Frontend Vite build
  - macOS system integration tests
  - Artifact uploads (frontend dist, test results)

**Future:** macOS .app bundle creation

---

#### 3. Windows Build (`windows-build.yml`) ⭐ NEW

**Purpose:** Windows-specific testing and installer builds

**Triggers:** Push/PR to `main` or `develop`

**Jobs:**
- **build-windows**: Complete Windows build, test, and package
  - Backend tests with Windows-specific validations
  - Frontend Vite build
  - Console encoding tests (emoji support)
  - System tray icon compatibility
  - **PyInstaller .exe build** (on main branch)
  - Installer verification tests

**Artifacts:** Windows installer (.exe) retained for 30 days

---

### Legacy Workflows (Retained for Compatibility)

#### 1. Backend CI (`backend-ci.yml`)

**Triggers:** Push/PR to `main` or `develop` affecting Python code

**Jobs:**

#### Lint
- **Ruff**: Fast Python linter (Flake8 replacement)
- **Black**: Code formatting enforcement
- **isort**: Import sorting validation
- **mypy**: Static type checking

#### Test
- **Matrix**: Python 3.10, 3.11, 3.12 on Ubuntu, Windows, macOS
- **Coverage**: pytest with coverage reporting
- **Upload**: Codecov integration for coverage tracking

#### Security
- **Safety**: Check for known vulnerabilities in dependencies
- **Bandit**: Security linter for Python code

#### API Tests
- **Integration**: FastAPI endpoint testing
- **Schema validation**: OpenAPI schema generation test

**Required checks:**
- ✅ Black formatting must pass
- ✅ isort import sorting must pass
- ✅ Tests must pass on all platforms

---

### 2. Frontend CI & Accessibility (`frontend-ci.yml`)

**Triggers:** Push/PR to `main` or `develop` affecting frontend code

**Jobs:**

#### Lint
- **ESLint**: JavaScript/TypeScript linting
- **ESLint jsx-a11y**: Accessibility linting (WCAG 2.2 AA)
- **TypeScript**: Type checking
- **Prettier**: Code formatting enforcement

#### Test
- **Jest**: Unit and integration tests
- **Coverage**: Code coverage reporting
- **Upload**: Codecov integration

#### Accessibility
- **axe-core**: Automated WCAG 2.2 Level AA testing
- **pa11y**: Additional accessibility validation
- **Reports**: Uploaded as artifacts for review

#### Lighthouse CI
- **Performance**: Lighthouse performance audits
- **Accessibility**: Lighthouse accessibility score (must be ≥95)
- **Best Practices**: PWA and security checks
- **SEO**: Search engine optimization validation

#### Build
- **Matrix**: Ubuntu, Windows, macOS
- **Bundle analysis**: Check for bundle size regressions

**Required checks:**
- ✅ ESLint must pass (including jsx-a11y rules)
- ✅ TypeScript compilation must succeed
- ✅ Tests must pass
- ✅ Accessibility tests must pass (0 violations)
- ✅ Lighthouse accessibility score ≥95

---

### 3. Documentation CI (`docs-ci.yml`)

**Triggers:** Push/PR to `main` or `develop` affecting documentation

**Jobs:**

#### Markdown Lint
- **markdownlint**: Enforce consistent markdown style

#### Link Check
- **Broken links**: Validate all internal and external links

#### ADR Validation
- **Naming convention**: ADRs must follow `NNN-name.md` format
- **Required sections**: Status, Date, Context, Decision, Consequences
- **Sequence check**: ADR numbers must be sequential

#### Spell Check
- **pyspelling**: Spell check all markdown files
- **Wordlist**: Custom dictionary for technical terms

#### Doc Structure
- **Required files**: Ensure all documentation sections exist
- **Completeness**: Verify inclusive design docs cover WCAG 2.2 topics

**Required checks:**
- ✅ All markdown files must be valid
- ✅ No broken links (internal)
- ✅ ADRs must follow template
- ✅ Required documentation files must exist

---

## Quality Gates

### Pull Request Requirements

Before a PR can be merged to `main`, it must:

1. **Pass all CI workflows** ✅
   - Backend CI (all jobs)
   - Frontend CI (all jobs)
   - Documentation CI (all jobs)

2. **Accessibility standards** ✅
   - 0 axe-core violations
   - Lighthouse accessibility score ≥95
   - ESLint jsx-a11y warnings reviewed

3. **Code coverage** (recommended)
   - Backend: ≥80% coverage
   - Frontend: ≥80% coverage

4. **Code review** (manual)
   - At least one approval from code owner
   - All conversations resolved

---

## Accessibility Testing

### Automated Testing

The Weather App enforces **WCAG 2.2 Level AA** compliance through automated testing:

#### axe-core Integration
```typescript
// Example: Component test with axe-core
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('Dashboard has no accessibility violations', async () => {
  const { container } = render(<Dashboard />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

#### ESLint jsx-a11y Rules
```json
{
  "extends": [
    "plugin:jsx-a11y/recommended"
  ],
  "rules": {
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-role": "error",
    "jsx-a11y/click-events-have-key-events": "error",
    "jsx-a11y/label-has-associated-control": "error"
  }
}
```

#### Lighthouse CI Configuration
```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'npm run preview',
      url: ['http://localhost:4173']
    },
    assert: {
      preset: 'lighthouse:recommended',
      assertions: {
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'categories:performance': ['warn', { minScore: 0.8 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }]
      }
    }
  }
};
```

### Manual Testing Checklist

While automated tests catch 30-40% of accessibility issues, **manual testing is required** before release:

- [ ] Keyboard-only navigation (Tab, Shift+Tab, Enter, Escape, Arrow keys)
- [ ] Screen reader testing (NVDA on Windows, VoiceOver on macOS/iOS)
- [ ] Color contrast validation (WCAG Contrast Checker)
- [ ] Zoom to 200% (no horizontal scrolling, all content accessible)
- [ ] Touch target verification on iPad (44×44px minimum)

See [docs/design/inclusive-design.md](../design/inclusive-design.md) for complete testing checklist.

---

## Local Development

### Running Tests Locally

#### Backend Tests
```bash
# Install dev dependencies
pip install pytest pytest-cov pytest-asyncio ruff black isort mypy

# Run tests with coverage
pytest tests/ -v --cov=weather_app

# Run linting
ruff check weather_app/ tests/
black --check weather_app/ tests/
isort --check-only weather_app/ tests/
mypy weather_app/

# Auto-fix formatting
black weather_app/ tests/
isort weather_app/ tests/
```

#### Frontend Tests
```bash
cd frontend

# Install dev dependencies
npm install

# Run tests with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y

# Run linting
npm run lint
npm run lint:a11y

# Type check
npm run type-check

# Auto-fix formatting
npm run format
```

#### Documentation Checks
```bash
# Install markdownlint-cli
npm install -g markdownlint-cli

# Lint markdown files
markdownlint '**/*.md' --ignore node_modules

# Check links (requires markdown-link-check)
npm install -g markdown-link-check
find docs -name "*.md" -exec markdown-link-check {} \;
```

---

## Troubleshooting

### Common CI Failures

#### "Black formatting failed"
**Cause:** Code not formatted with Black
**Fix:**
```bash
black weather_app/ tests/
git add .
git commit --amend --no-edit
```

#### "ESLint jsx-a11y errors"
**Cause:** Accessibility violations in React components
**Fix:** Review [docs/design/inclusive-design.md](../design/inclusive-design.md) and fix violations:
```bash
cd frontend
npm run lint:a11y -- --fix  # Auto-fix some issues
npm run lint:a11y           # Review remaining issues
```

#### "axe-core violations found"
**Cause:** WCAG 2.2 AA accessibility violations
**Fix:**
1. Run tests locally: `npm run test:a11y`
2. Review violation details in test output
3. Fix accessibility issues (see [Inclusive Design Standards](../design/inclusive-design.md))
4. Re-run tests to verify

#### "Lighthouse accessibility score <95"
**Cause:** Accessibility score below threshold
**Fix:**
1. Download Lighthouse report artifact from GitHub Actions
2. Review failing audits
3. Common issues:
   - Missing alt text on images
   - Low color contrast
   - Missing ARIA labels
   - Touch targets too small (<44×44px)
4. Fix issues and re-test locally:
```bash
cd frontend
npm run build
npx lhci autorun
```

#### "Broken links in documentation"
**Cause:** Invalid internal or external links
**Fix:**
1. Review link-check job output
2. Fix broken links in markdown files
3. Update `.markdown-link-check.json` to ignore known issues

#### "ADR sequence gap"
**Cause:** Missing ADR number in sequence
**Fix:**
- ADRs must be numbered sequentially (001, 002, 003, ...)
- If you deleted an ADR, don't reuse the number
- Add a note in the next ADR: "ADR-XXX was superseded and removed"

---

## CI/CD Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Pull Request                            │
└─────────────────┬───────────────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐ ┌──────────────────┐
│  Backend CI     │ │  Frontend CI     │
│  • Lint         │ │  • Lint          │
│  • Test         │ │  • Test          │
│  • Security     │ │  • Accessibility │
│  • API Tests    │ │  • Lighthouse    │
└─────────────────┘ └──────────────────┘
         │                 │
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Documentation  │
         │  CI             │
         │  • Markdown     │
         │  • Links        │
         │  • ADR Valid    │
         │  • Spell Check  │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  All Checks     │
         │  Passed? ✅      │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Code Review    │
         │  (Manual)       │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Merge to Main  │
         └─────────────────┘
```

---

## Badges

Add these badges to `README.md` to show CI status:

```markdown
![Backend CI](https://github.com/jannaspicerbot/Weather-App/workflows/Backend%20CI/badge.svg)
![Frontend CI](https://github.com/jannaspicerbot/Weather-App/workflows/Frontend%20CI%20%26%20Accessibility/badge.svg)
![Documentation CI](https://github.com/jannaspicerbot/Weather-App/workflows/Documentation%20CI/badge.svg)
[![codecov](https://codecov.io/gh/jannaspicerbot/Weather-App/branch/main/graph/badge.svg)](https://codecov.io/gh/jannaspicerbot/Weather-App)
```

---

## Future Enhancements

### Planned Improvements
- [ ] E2E testing with Playwright (Phase 3)
- [ ] Visual regression testing with Percy (Phase 3)
- [ ] Automated dependency updates with Dependabot
- [ ] Automated release notes generation
- [ ] Performance budget enforcement
- [ ] Docker image scanning with Trivy

### Phase 3 Additions
- [ ] Deploy previews for PRs (Vercel/Netlify)
- [ ] Staging environment deployment
- [ ] Production deployment automation
- [ ] Database migration testing

---

## Related Documents

- [ADR-006: React Aria Components](../architecture/decisions/006-react-aria-components.md) - Accessibility testing requirements
- [ADR-007: Victory Charts](../architecture/decisions/007-victory-charts.md) - Chart accessibility validation
- [Inclusive Design Standards](../design/inclusive-design.md) - Manual accessibility testing checklist
- [Deployment Guide](deployment-guide.md) - Production deployment process

---

## Document Changelog

- **2026-01-03:** Initial CI/CD documentation created
  - Documented Backend CI, Frontend CI, and Documentation CI workflows
  - Added accessibility testing requirements (WCAG 2.2 Level AA)
  - Included troubleshooting guide and local development instructions
