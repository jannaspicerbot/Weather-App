# Fixing Mypy and ESLint Errors

**Date:** 2026-01-14
**Branch:** feature/full-app-testing
**Status:** ✅ Complete

---

## Summary

This document tracks the effort to fix all mypy type-checking errors (69 total) and ESLint errors (10 total) in the codebase.

---

## Completed Fixes

### 1. ESLint Config ([web/eslint.config.js](../../web/eslint.config.js))

**Problem:** ESLint was linting auto-generated files in `dev-dist/` and `coverage/` directories.

**Fix:** Added `dev-dist` and `coverage` to the global ignores list:

```javascript
export default defineConfig([
  globalIgnores(['dist', 'dev-dist', 'coverage']),
  // ...
])
```

**Result:** ESLint now passes with 0 errors (only warnings remain).

---

### 2. logging_config.py ([weather_app/logging_config.py](../../weather_app/logging_config.py))

**Problems (22 errors):**
- Implicit `Optional` parameters (PEP 484 violation)
- Type mismatches in `log_data` dictionaries
- Structlog's dynamic API causing type inference issues

**Fixes:**
1. Added imports:
   ```python
   from typing import Any, Mapping, Optional
   from structlog.contextvars import BoundVarsToken
   ```

2. Changed function signatures to use explicit `Optional`:
   ```python
   def log_api_request(
       logger: structlog.stdlib.BoundLogger,
       method: str,
       endpoint: str,
       params: Optional[dict[str, Any]] = None,
       status_code: Optional[int] = None,
       duration_ms: Optional[float] = None,
   ) -> None:
   ```

3. Added type annotations to `log_data` variables:
   ```python
   log_data: dict[str, Any] = { ... }
   ```

4. Added `# type: ignore` comments for structlog's dynamic API:
   ```python
   logger.info(**log_data)  # type: ignore[arg-type]
   ```

---

### 3. database/engine.py ([weather_app/database/engine.py](../../weather_app/database/engine.py))

**Problems (22 errors):**
- `self.conn` typed as `None` initially, but used throughout without type narrowing
- Implicit `Optional` for `db_path` parameter

**Fixes:**
1. Added imports:
   ```python
   from typing import Optional
   from duckdb import DuckDBPyConnection
   ```

2. Changed `db_path` to explicit `Optional`:
   ```python
   def __init__(self, db_path: Optional[str] = None):
   ```

3. Added proper type annotation for `self.conn`:
   ```python
   self.conn: Optional[DuckDBPyConnection] = None
   ```

4. Added `_get_conn()` helper method for type narrowing:
   ```python
   def _get_conn(self) -> DuckDBPyConnection:
       """Get the database connection, raising an error if not connected."""
       if self.conn is None:
           raise RuntimeError("Database connection not established. Use as context manager.")
       return self.conn
   ```

5. Replaced all `self.conn` usages with `self._get_conn()` in methods that require an active connection.

---

### 4. launcher/resource_path.py ([weather_app/launcher/resource_path.py](../../weather_app/launcher/resource_path.py))

**Problems (4 errors):**
- PyInstaller's `sys._MEIPASS` attribute doesn't exist at type-check time

**Fixes:** ✅ COMPLETE
Added `# type: ignore[attr-defined]` comments to all 4 locations:
```python
base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
```

---

### 5. launcher/crash_logger.py ([weather_app/launcher/crash_logger.py](../../weather_app/launcher/crash_logger.py))

**Problem (1 error):**
- Line 132: `sys._MEIPASS` attribute doesn't exist at type-check time

**Fix:** ✅ COMPLETE
```python
base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
```

---

### 6. web/app.py ([weather_app/web/app.py](../../weather_app/web/app.py))

**Problem (1 error):**
- Line 71: `sys._MEIPASS` attribute doesn't exist at type-check time

**Fix:** ✅ COMPLETE
```python
static_dir = Path(sys._MEIPASS) / "web" / "dist"  # type: ignore[attr-defined]
```

---

### 7. launcher/setup_wizard.py ([weather_app/launcher/setup_wizard.py](../../weather_app/launcher/setup_wizard.py))

**Problem (1 error):**
- Line 202: `no-any-return` - wizard.run() returns Any

**Fix:** ✅ COMPLETE
```python
result: bool = wizard.run()
return result
```

---

### 8. logging_config.py - Additional Fixes ([weather_app/logging_config.py](../../weather_app/logging_config.py))

**Problems found in session 2:**
- `BoundVarsToken` import from `structlog.contextvars` doesn't exist
- Incorrect `type: ignore[return-value]` comment (should be `no-any-return`)

**Fixes:** ✅ COMPLETE
1. Removed invalid import:
   ```python
   # Removed: from structlog.contextvars import BoundVarsToken
   ```
2. Fixed type ignore comment:
   ```python
   return structlog.get_logger(name)  # type: ignore[no-any-return]
   ```

---

## Remaining Fixes

### Files Still Needing Fixes

| File | Errors | Fix Needed |
|------|--------|------------|
| `logging_config.py` | ~10 | Fix `LogContext.token` type annotation (remove `BoundVarsToken`) |
| `web/backfill_service.py` | ~8 | Add `Optional` to params, fix `_progress` dict access types |
| `web/routes.py` | ~4 | Add `Optional` to `device_mac`, `request` params |
| `api/client.py` | 2 | Add type annotation for `all_data`, fix `extend` on None |
| `services/ambient_api_queue.py` | 2 | Add type annotations for `future` and lambda |
| `database/repository.py` | ~10 | Fix `params` list types, use `_get_conn()` for db access |
| `cli/cli.py` | ~10 | Fix `reconfigure`, `Path` to `str`, use `_get_conn()` |

### Current Mypy Error Count: ~46 errors (down from 69)

**Session 2 Progress:**
- Fixed 4 `_MEIPASS` errors (resource_path.py, crash_logger.py, web/app.py)
- Fixed 1 `no-any-return` error (setup_wizard.py)
- Fixed 2 logging_config.py errors (removed bad import, fixed type ignore)
- Discovered additional errors in logging_config.py, repository.py, cli.py that need `_get_conn()` pattern

---

## Common Fix Patterns

### Pattern 1: Implicit Optional Parameters

**Before:**
```python
def func(param: str = None):
```

**After:**
```python
from typing import Optional

def func(param: Optional[str] = None):
```

### Pattern 2: PyInstaller _MEIPASS Attribute

**Before:**
```python
Path(sys._MEIPASS)
```

**After:**
```python
Path(sys._MEIPASS)  # type: ignore[attr-defined]
```

### Pattern 3: Optional Connection/Resource

**Before:**
```python
self.conn = None
# later...
self.conn.execute(...)  # Error: None has no attribute 'execute'
```

**After:**
```python
self.conn: Optional[Connection] = None

def _get_conn(self) -> Connection:
    if self.conn is None:
        raise RuntimeError("Not connected")
    return self.conn

# later...
self._get_conn().execute(...)  # Type-safe
```

### Pattern 4: Dynamic Dict Building

**Before:**
```python
log_data = {"key": "value"}
log_data["count"] = 5  # Error: incompatible types
```

**After:**
```python
log_data: dict[str, Any] = {"key": "value"}
log_data["count"] = 5  # OK
```

---

## Current Test Status

| Check | Status |
|-------|--------|
| Black (formatting) | ✅ Pass |
| Ruff (linting) | ✅ Pass |
| Mypy (type checking) | ✅ 0 errors |
| Pytest (Python tests) | ✅ 315 tests pass |
| ESLint (frontend) | ✅ 0 errors, 7 warnings |
| Vitest (frontend tests) | ✅ 42 tests pass |

---

## ✅ ALL FIXES COMPLETE

All mypy and ESLint errors have been resolved. The codebase now passes all type checks and linting.

---

## Session Log

### Session 1 (Initial)
- Fixed ESLint config
- Fixed logging_config.py (22 errors)
- Fixed database/engine.py (22 errors)
- Fixed resource_path.py (3 of 4 errors)

### Session 2 (2026-01-14)
- Fixed resource_path.py line 143 (`_MEIPASS`)
- Fixed crash_logger.py line 132 (`_MEIPASS`)
- Fixed web/app.py line 71 (`_MEIPASS`)
- Fixed setup_wizard.py line 202 (`no-any-return`)
- Fixed logging_config.py (removed invalid `BoundVarsToken` import, fixed type ignore comment)
- Ran mypy to discover actual error count: 46 errors remaining

### Session 3 (2026-01-14) - FINAL
- Fixed logging_config.py:
  - Changed `self.token: Mapping[str, BoundVarsToken]` to `self.token: Any`
  - Removed 8 unused `# type: ignore[arg-type]` comments
- Fixed ambient_api_queue.py:
  - Added type annotation `asyncio.Future[Any]` for future variable
  - Used `functools.partial` instead of lambda for thread executor (cleaner, type-safe)
- Fixed api/client.py:
  - Added `from typing import Any` import
  - Added type annotation `list[Any] | None` for `all_data`
  - Added None check before `.extend()` call
- Fixed database/repository.py:
  - Changed `params` type from `list[str]` to `list[Any]`
  - Used `db._get_conn()` instead of `db.conn` for type-safe connection access
  - Added None checks for query results (`count_result[0] if count_result else 0`)
- Fixed cli/cli.py:
  - Removed unused `# type: ignore[union-attr]` on reconfigure
  - Changed `WeatherDatabase(db_path)` to `WeatherDatabase(str(db_path))` (2 locations)
  - Used `db._get_conn()` for type-safe connection access
  - Added proper None handling for query results
- Fixed web/backfill_service.py:
  - Added `from typing import Optional` import
  - Changed implicit Optional parameters to explicit `str | None`
  - Renamed local vars to avoid shadowing (`effective_api_key`, `effective_app_key`)
  - Added isinstance checks for dict value arithmetic
- Fixed web/routes.py:
  - Added `from typing import Optional` import
  - Changed implicit Optional parameters to explicit `str | None`
- Added `types-requests>=2.31.0` to requirements.txt for proper type stubs
- Ran ruff --fix to convert `Optional[X]` to modern `X | None` syntax
- **All 49 mypy errors fixed - 0 errors remaining**
- Added mypy to `.pre-commit-config.yaml` to prevent regressions (in progress)

### Session 4 (2026-01-14) - VERIFICATION & PUSH
- Verified pre-commit mypy hook works: `pre-commit run mypy --all-files` passes
- Ran `pre-commit install` to update hooks
- Ran full pre-commit suite - all hooks pass:
  - check for added large files ✅
  - check yaml ✅
  - detect private key ✅
  - trim trailing whitespace ✅
  - fix end of files ✅
  - Block .env files ✅
  - ruff ✅
  - black ✅
  - isort ✅
  - mypy ✅
- Fixed pre-push pytest hook: changed `pytest` to `python -m pytest` (executable not in PATH)
- Updated `.pre-commit-config.yaml` header comment to include mypy
- Committed and pushed all changes to `feature/full-app-testing`
- Pre-push hook ran 315 tests successfully

**Commits pushed:**
1. `0b89904` Fix Python 3.10 compatibility for TimeoutError in test_api_queue
2. `c92d811` Add pre-push hook to run pytest before pushing
3. `f59adfd` Fix mypy and ESLint errors (partial)
4. `4904d71` Complete mypy type checking fixes (0 errors)

---

## ✅ PROJECT COMPLETE

All objectives achieved:
- **Mypy:** 0 errors (down from 69)
- **ESLint:** 0 errors (only 7 warnings remain)
- **Tests:** 315 passing
- **Pre-commit hooks:** All configured and passing (security, ruff, black, isort, mypy)
- **Pre-push hooks:** Pytest runs before every push
- **All changes pushed to remote**

---

## Recommendations for Future

1. **CI Integration** - Consider adding mypy to GitHub Actions workflow if not already present
2. **Strict Mode** - Once stable, consider enabling `--strict` mode in mypy for even stricter type checking
3. **Type Stub Updates** - Keep `types-requests` and other type stubs updated
