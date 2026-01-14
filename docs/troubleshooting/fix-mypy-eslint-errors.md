# Fixing Mypy and ESLint Errors

**Date:** 2026-01-14
**Branch:** feature/full-app-testing
**Status:** In Progress

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

**Fixes (3 of 4 complete):**
Added `# type: ignore[attr-defined]` comments:
```python
base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
```

**Remaining:** Line 143 in `get_meipass()` function needs the same fix.

---

## Remaining Fixes

### Files Still Needing Fixes

| File | Errors | Fix Needed |
|------|--------|------------|
| `launcher/resource_path.py:143` | 1 | Add `# type: ignore[attr-defined]` to `get_meipass()` |
| `web/backfill_service.py` | 5 | Add `Optional` to `device_mac`, `api_key`, `app_key` params |
| `web/routes.py` | 4 | Add `Optional` to `device_mac`, `request` params |
| `api/client.py` | 3 | Add type annotation for `all_data`, fix `extend` on None |
| `services/ambient_api_queue.py` | 2 | Add type annotations for `future` and lambda |
| `database/repository.py:70` | 2 | Fix list item types (int vs str) |
| `cli/cli.py` | 3 | Fix `reconfigure` and `Path` to `str` conversion |
| `launcher/crash_logger.py:132` | 1 | Add `# type: ignore[attr-defined]` for `_MEIPASS` |
| `web/app.py:71` | 1 | Add `# type: ignore[attr-defined]` for `_MEIPASS` |
| `launcher/setup_wizard.py:202` | 1 | Fix `no-any-return` |

### Estimated Remaining Errors: ~25 (down from 69)

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
| Mypy (type checking) | ❌ ~25 errors remaining |
| Pytest (Python tests) | ✅ 316 tests pass |
| ESLint (frontend) | ✅ 0 errors, 7 warnings |
| Vitest (frontend tests) | ✅ 42 tests pass |

---

## Next Steps

1. Complete remaining `_MEIPASS` fixes (3 files)
2. Fix `Optional` parameters in `backfill_service.py` and `routes.py`
3. Fix type annotations in `api/client.py` and `ambient_api_queue.py`
4. Fix remaining miscellaneous errors
5. Run full pre-commit check to verify all fixes
6. Commit changes
