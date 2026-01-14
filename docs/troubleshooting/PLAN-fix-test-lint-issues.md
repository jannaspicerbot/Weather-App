# Fix Plan for Test and Lint Issues

**Created:** January 2026
**Branch:** feature/full-app-testing

---

## Summary of Issues

| Category | Count | Severity | Priority |
|----------|-------|----------|----------|
| Backend Test Failures | 4 | Medium | P1 |
| Mypy Type Errors | 69 | Low | P2 |
| ESLint Errors | 10 | Low | P3 |
| ESLint Warnings | 14 | Low | P4 |

---

## P1: Backend Test Failures (4 tests)

### Location
`tests/test_api_client.py::TestRequestQueueIntegration`

### Failed Tests
1. `test_get_devices_no_event_loop_creates_one`
2. `test_get_devices_with_request_queue`
3. `test_get_device_data_no_event_loop_creates_one`
4. `test_get_device_data_with_request_queue`

### Root Cause
Async/event loop handling issues in Python 3.13. The tests attempt to create and manage event loops manually, which conflicts with how pytest-asyncio handles event loops in newer Python versions.

Key error: `RuntimeError: no running event loop`

### Fix Steps
1. Review `tests/test_api_client.py` lines 460-540 (TestRequestQueueIntegration class)
2. Replace manual event loop creation with pytest-asyncio fixtures
3. Use `@pytest.mark.asyncio` decorator properly
4. Replace `asyncio.Future()` with proper async test patterns
5. Consider using `asyncio.get_event_loop()` alternatives for Python 3.10+

### Example Fix Pattern
```python
# Before (broken in Python 3.13)
def test_with_event_loop(self):
    mock_future = asyncio.Future()  # No running loop!
    mock_future.set_result(...)

# After (compatible)
@pytest.mark.asyncio
async def test_with_event_loop(self):
    result = await some_async_function()
    assert result == expected
```

---

## P2: Mypy Type Errors (69 errors)

### Categories

#### 2a. Implicit Optional (22 errors)
**Files:** `backfill_service.py`, `routes.py`

**Issue:** Parameters with `= None` default but typed as `str` instead of `Optional[str]`

**Fix:**
```python
# Before
def start_backfill(self, device_mac: str = None):

# After
def start_backfill(self, device_mac: Optional[str] = None):
# Or in Python 3.10+:
def start_backfill(self, device_mac: str | None = None):
```

**Affected locations:**
- `weather_app/web/backfill_service.py:144` - `device_mac`
- `weather_app/web/backfill_service.py:281` - `api_key`, `app_key`
- `weather_app/web/routes.py:305` - `device_mac`
- `weather_app/web/routes.py:356` - `request`

#### 2b. None Attribute Access (6 errors)
**File:** `weather_app/database/engine.py`

**Issue:** Accessing `.execute()` on potentially `None` connection

**Fix:** Add None checks or assert connection exists
```python
# Before
self.conn.execute(query)

# After
if self.conn is None:
    raise RuntimeError("Database connection not initialized")
self.conn.execute(query)
```

**Affected lines:** 339, 340, 352, 357, 381, 397

#### 2c. Type Mismatches (12 errors)
**Files:** `repository.py`, `cli.py`

**Issues:**
- `repository.py:70` - List items typed as `int` but expected `str`
- `cli.py:17` - `TextIO` doesn't have `reconfigure` attribute
- `cli.py:147, 264` - `Path` passed where `str` expected

**Fixes:**
- Cast or convert types appropriately
- Use `str(path)` for Path to str conversion
- Add type guard for TextIO check

#### 2d. PyInstaller Attribute (1 error)
**File:** `weather_app/web/app.py:71`

**Issue:** `sys._MEIPASS` doesn't exist in type stubs

**Fix:** Add type ignore comment or use `getattr()`
```python
# Option 1: Type ignore
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS  # type: ignore[attr-defined]

# Option 2: getattr
base_path = getattr(sys, '_MEIPASS', None)
```

#### 2e. Deprecated datetime.utcnow() (4 warnings)
**File:** `weather_app/database/engine.py:328, 379`

**Fix:**
```python
# Before
now = datetime.utcnow().isoformat()

# After
from datetime import datetime, UTC
now = datetime.now(UTC).isoformat()
```

---

## P3: ESLint Errors (10 errors)

### 3a. Generated File Errors (9 errors)
**File:** `web/dev-dist/workbox-6d565866.js`

**Issue:** ESLint rules referenced that don't exist in current config (e.g., `@typescript-eslint/ban-types`)

**Fix Options:**
1. Add `dev-dist/` to `.eslintignore`
2. Or exclude in `eslint.config.js`:
```javascript
{
  ignores: ['dev-dist/**', 'coverage/**']
}
```

### 3b. Auto-generated API Client Warnings (6 warnings)
**Files:** `web/src/api/**/*.ts`

**Issue:** Unused eslint-disable directives in generated OpenAPI client

**Fix:** These are auto-generated - add to `.eslintignore` or regenerate client

---

## P4: ESLint Warnings (14 warnings)

### 4a. Coverage Report Files (3 warnings)
**Files:** `web/coverage/*.js`

**Fix:** Add `coverage/` to `.eslintignore`

### 4b. React Hook Dependency (1 warning)
**File:** `web/src/components/Dashboard.tsx:84`

**Issue:** Missing `fetchHistoricalData` in useCallback dependency array

**Fix:**
```typescript
// Review the callback and either:
// 1. Add the missing dependency
// 2. Use useCallback for fetchHistoricalData first
// 3. Add eslint-disable with justification if intentional
```

---

## Implementation Order

### Phase 1: Quick Wins (30 min)
1. Add `dev-dist/` and `coverage/` to `.eslintignore`
2. Fix the Dashboard.tsx useCallback dependency

### Phase 2: Type Safety (1-2 hours)
1. Fix Implicit Optional types in `backfill_service.py` and `routes.py`
2. Add None checks in `engine.py`
3. Fix type mismatches in `repository.py` and `cli.py`
4. Update deprecated `datetime.utcnow()` calls

### Phase 3: Test Infrastructure (1-2 hours)
1. Refactor `TestRequestQueueIntegration` tests
2. Use proper async test patterns
3. Ensure compatibility with Python 3.13

---

## Verification Commands

After fixes, run:

```bash
# Python tests
python -m pytest tests/ -v

# Type checking
python -m mypy weather_app/ --ignore-missing-imports

# Linting
python -m ruff check weather_app/
cd web && npm run lint

# Full pre-push check
python -m black weather_app/ && \
python -m ruff check --fix weather_app/ && \
python -m mypy weather_app/ && \
python -m pytest tests/ -v && \
cd web && npm run lint:fix && npm test
```

---

## Notes

- The 4 failing tests are **test infrastructure issues**, not application bugs
- The mypy errors are **type annotation issues**, not runtime bugs
- The ESLint errors are mostly in **generated files**
- The app itself is **functional** and can be tested manually
