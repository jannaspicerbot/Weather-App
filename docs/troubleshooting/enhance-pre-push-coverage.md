# Enhance Pre-push Hook with Coverage Checking

**Status:** Complete
**Created:** 2026-01-14
**Completed:** 2026-01-14
**Purpose:** Add pytest-cov to pre-push hook to catch coverage regressions before push

---

## Problem

Previously, the pre-push hook ran pytest but did not check code coverage. This meant coverage regressions could slip through to CI, causing failed builds and delayed feedback.

## Solution Implemented

Enhanced the existing pre-push hook to run `pytest --cov` with a 60% minimum threshold.

### Changes Made

#### 1. Added `pytest-cov` to requirements.txt

```txt
pytest-cov>=4.1.0  # Coverage reporting for pytest
```

#### 2. Added coverage configuration to pyproject.toml

```toml
[tool.coverage.run]
source = ["weather_app"]
omit = ["*/tests/*", "*/scripts/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 60
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

#### 3. Updated pre-push hook in `.pre-commit-config.yaml`

```yaml
- id: pytest-check
  name: Run pytest with coverage before push
  entry: python -m pytest tests/ -x -q --tb=short -m "not requires_api_key" --cov=weather_app --cov-fail-under=60
  language: system
  pass_filenames: false
  stages: [pre-push]
  always_run: true
```

## Current Coverage

As of implementation, coverage is at **73%** (well above the 60% threshold).

## Behavior

- Pre-push hook runs tests with coverage measurement
- Push is **blocked** if coverage falls below 60%
- Developers see coverage report output before push completes
- Coverage regressions caught locally before reaching CI

## Notes

- The 60% threshold is a starting point; can be increased as test coverage improves
- Developers can bypass with `git push --no-verify` in emergencies (not recommended)
- Codecov.io integration already exists in CI for PR coverage diffs and historical tracking
