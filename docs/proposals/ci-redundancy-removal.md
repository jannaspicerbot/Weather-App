# Proposal: Remove Redundant CI Job by Merging OpenAPI Validation

**Author:** Claude Code
**Date:** 2026-01-19
**Status:** Proposed

---

## Summary

Remove the redundant `api-integration` job from `main-ci.yml` by merging its unique functionality (OpenAPI schema validation) into the existing `backend-tests` job.

---

## Problem

The current CI workflow has redundancy between two jobs:

| Job | Command | Platform | Depends On |
|-----|---------|----------|------------|
| `backend-tests` | `pytest tests/ -v -m "not requires_api_key"` | Ubuntu, Windows, macOS | `changes` |
| `api-integration` | `pytest tests/ -v -m "not requires_api_key"` | Ubuntu only | `changes`, `backend-tests` |

Both jobs run **identical pytest commands**. The `api-integration` job:
1. Waits for all 5 `backend-tests` matrix jobs to complete (~3-8 min)
2. Runs the same tests again (~1-2 min)
3. Validates OpenAPI schema (~10 sec) ← **only unique value**

**Impact:**
- Wasted CI minutes running duplicate tests
- Longer total CI time due to serial dependency
- Unnecessary complexity in workflow

---

## Proposed Solution

Merge the OpenAPI schema validation step into the `backend-tests` job, running only on Ubuntu with Python 3.11 (the primary configuration). Then remove the `api-integration` job entirely.

### Changes Required

**1. Add OpenAPI validation to `backend-tests` (Ubuntu/Python 3.11 only):**

```yaml
- name: Validate OpenAPI Schema
  if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'
  shell: bash
  run: |
    python -c "from weather_app.web.app import create_app; app = create_app(); import json; print(json.dumps(app.openapi(), indent=2))" > openapi.json
    echo "✅ OpenAPI schema generated successfully"
```

**2. Remove the entire `api-integration` job** (lines 222-266 in current workflow)

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Loss of test coverage | None - identical tests run in `backend-tests` |
| OpenAPI validation skipped | Conditional ensures it runs on Ubuntu/3.11 |
| Future API-specific tests have no home | Can add back a dedicated job if needed |

**Risk Level: Low**

The change removes duplicate execution while preserving all validation. No test coverage is lost.

---

## Expected Benefits

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Total jobs | 6 | 5 | -1 job |
| CI time (best case) | ~10 min | ~6 min | ~40% faster |
| Duplicate test runs | Yes | No | Eliminated |
| OpenAPI validation | ✅ | ✅ | Preserved |

---

## Implementation Plan

1. Create feature branch `chore/remove-ci-redundancy`
2. Edit `.github/workflows/main-ci.yml`:
   - Add OpenAPI validation step to `backend-tests`
   - Remove `api-integration` job
3. Test by pushing to branch and verifying CI passes
4. Create PR for review

---

## Alternatives Considered

### Alternative A: Keep separate job, remove duplicate tests

Keep `api-integration` but only run OpenAPI validation (no pytest).

**Rejected because:** Still incurs job startup overhead and dependency wait time for a 10-second task.

### Alternative B: Run jobs in parallel

Remove the `needs: backend-tests` dependency so both run simultaneously.

**Rejected because:** Wastes CI minutes on duplicate test execution.

---

## Decision

Proceed with merging OpenAPI validation into `backend-tests` and removing `api-integration` job.
