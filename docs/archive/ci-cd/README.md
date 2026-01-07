# Archived CI/CD Documentation

**Archive Date:** January 6, 2026
**Reason:** Workflow consolidation rendered these documents obsolete

---

## What Happened

On January 6, 2026, the Weather App's GitHub Actions workflows were consolidated from **7 workflows** down to **3 workflows**, achieving a 60-70% reduction in CI minutes and eliminating duplicate test runs.

### Old Architecture (Documented Here)
- `cross-platform-ci.yml` - Multi-platform matrix testing
- `backend-ci.yml` - Python/FastAPI testing
- `frontend-ci.yml` - React/TypeScript testing
- `windows-build.yml` - Windows installer builds
- `macos-build.yml` - macOS app preparation
- `dependabot-tests.yml` - Dependabot PR testing
- `docs-ci.yml` - Documentation validation

### New Architecture (Current)
- `main-ci.yml` - All standard CI (tests, lint, security)
- `platform-builds.yml` - Platform-specific builds only
- `docs-ci.yml` - Documentation validation (unchanged)

---

## Archived Documents

### [ci-cd-v1.md](ci-cd-v1.md)
**Original Purpose:** General CI/CD overview and developer guide
**Status:** Contains outdated workflow references, but has valuable content on:
- Quality gates
- Accessibility testing
- Local development commands
- Troubleshooting tips

**Note:** Unique valuable content has been migrated to [github-actions-overview.md](../../technical/github-actions-overview.md)

### [cross-platform-ci-v1.md](cross-platform-ci-v1.md)
**Original Purpose:** Detailed documentation for the cross-platform-ci.yml workflow
**Status:** Workflow no longer exists (replaced by main-ci.yml)
**Historical Value:** Shows the original matrix testing strategy and job organization

---

## Current Documentation

For up-to-date CI/CD documentation, see:

**📋 [GitHub Actions Overview](../../technical/github-actions-overview.md)** - Single comprehensive guide covering:
- Streamlined workflow architecture
- Main CI workflow details
- Platform builds workflow details
- Quality gates and PR requirements
- Local development and testing
- Comprehensive troubleshooting guide
- Migration guide from old to new workflows

---

## Why These Were Archived

1. **Outdated Workflow References** - All documented workflows have been deleted or consolidated
2. **Massive Duplication** - ~70% of content was duplicated across ci-cd.md, cross-platform-ci.md, and github-actions-overview.md
3. **Maintenance Burden** - Keeping 3 documents in sync was error-prone
4. **Confusion** - Multiple documents with conflicting information

---

## Historical Reference

These documents are preserved for:
- Understanding the evolution of the CI/CD pipeline
- Recovering any content that might have been missed during migration
- Historical context for future architectural decisions

**If you need CI/CD documentation, use [github-actions-overview.md](../../technical/github-actions-overview.md) - not these archived files.**

---

**Last Updated:** January 6, 2026
