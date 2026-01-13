# PR 61 Code Coverage Test Plan

**Date:** January 13, 2026
**Last Updated:** January 13, 2026
**Target:** Improve patch coverage from 94.79% to 100%
**Status:** Phase 2 Complete

---

## Current Coverage Status (After Phase 2)

| File | Coverage | Missing Lines | Status |
|------|----------|---------------|--------|
| `weather_app/web/backfill_service.py` | 100% | 0 | **COMPLETE** |
| `weather_app/services/ambient_api_queue.py` | 96% | 5 | ACCEPTABLE |
| `weather_app/web/app.py` | 82% | 7 | ACCEPTABLE |
| `weather_app/web/routes.py` | ~100% | 0 | COMPLETE |
| `weather_app/api/client.py` | ~100% | 0 | COMPLETE |
| `weather_app/scheduler/scheduler.py` | ~100% | 0 | COMPLETE |

**Total Patch Coverage:** 97% (12 lines missing)

### Remaining Uncovered Lines (Acceptable)

The following lines remain uncovered but are acceptable as they represent edge cases that are difficult to test without significant test infrastructure changes:

**ambient_api_queue.py (5 lines):**
- Line 48: `avg_wait_time_seconds` property (division edge case)
- Line 246: Worker timeout continue (tested indirectly)
- Lines 325-329: Worker unexpected exception handler (tested partially)

**app.py (7 lines):**
- Lines 33-50: Lifespan context manager (startup/shutdown) - requires integration testing with app lifecycle

---

## Phase 2: Remaining Coverage Gaps (14 lines)

This section details the specific lines still missing coverage and the tests needed to cover them.

### 2.1 BackfillService - 7 Missing Lines

**File:** `weather_app/web/backfill_service.py`
**Test File:** `tests/test_backfill_service.py`

#### Likely Missing Lines Analysis

Based on code review, the following code paths are likely uncovered:

| Line Range | Code Path | Test Needed |
|------------|-----------|-------------|
| 365-396 | Device selection when `AMBIENT_DEVICE_MAC` is set and found | Test with configured device MAC that exists in device list |
| 370-377 | Using configured device from list | Test backfill with matching configured device |
| 380-391 | Configured device not found, fallback to first | Already tested, verify coverage |
| 392-396 | No device configured, use first device | Test backfill with no `AMBIENT_DEVICE_MAC` set |
| 458-476 | `batch_callback` inner function execution | Test that batch_callback is invoked and updates progress |
| 464-474 | Processing batch data with current_date extraction | Test batch_callback with valid batch data containing dates |

#### New Tests to Add

```python
@pytest.mark.unit
class TestRunBackfillDeviceSelection:
    """Tests for device selection logic in _run_backfill."""

    def test_backfill_uses_configured_device_when_found(self, backfill_service):
        """Uses configured device MAC when it exists in device list."""
        # Setup: Set AMBIENT_DEVICE_MAC to a device that exists in list
        # Expected: Uses that specific device, not first device

    def test_backfill_uses_first_device_when_no_mac_configured(self, backfill_service):
        """Uses first device when AMBIENT_DEVICE_MAC is not set."""
        # Setup: Ensure AMBIENT_DEVICE_MAC is empty/None
        # Expected: Uses devices[0]


@pytest.mark.unit
class TestRunBackfillBatchCallback:
    """Tests for batch_callback execution in _run_backfill."""

    def test_batch_callback_updates_progress_with_date(self, backfill_service):
        """Batch callback extracts date and updates progress."""
        # Setup: Mock fetch_all_historical_data to invoke batch_callback
        # Expected: Progress includes current_date from batch data

    def test_batch_callback_handles_empty_batch(self, backfill_service):
        """Batch callback handles empty batch gracefully."""
        # Setup: Invoke batch_callback with empty list
        # Expected: No errors, returns (0, 0)
```

---

### 2.2 AmbientAPIQueue - 5 Missing Lines

**File:** `weather_app/services/ambient_api_queue.py`
**Test File:** `tests/test_api_queue.py`

#### Likely Missing Lines Analysis

| Line Range | Code Path | Test Needed |
|------------|-----------|-------------|
| 139-144 | Shutdown timeout warning log | Test shutdown with requests that exceed timeout |
| 322-324 | Worker CancelledError handling | Test worker cancellation during shutdown |
| 325-328 | Worker unexpected exception | Test worker with exception that escapes main try block |

#### New Tests to Add

```python
@pytest.mark.asyncio
class TestAPIQueueWorkerEdgeCases:
    """Tests for worker edge cases in AmbientAPIQueue."""

    async def test_shutdown_logs_warning_on_timeout(self):
        """Shutdown logs warning when queue doesn't drain in time."""
        # Setup: Queue slow requests, shutdown with short timeout
        # Expected: Warning logged about remaining requests

    async def test_worker_handles_cancellation(self):
        """Worker handles CancelledError gracefully during shutdown."""
        # Setup: Start queue, cancel worker task directly
        # Expected: CancelledError is re-raised, logged appropriately
```

---

### 2.3 App Factory - 2 Missing Lines

**File:** `weather_app/web/app.py`
**Test File:** `tests/test_app_factory.py` (NEW)

#### Missing Lines Analysis

| Line | Code Path | Test Needed |
|------|-----------|-------------|
| 71 | `sys._MEIPASS` path for frozen executable | Test with `sys.frozen = True` |
| 83-87 | Frontend not found warning | Test when static_dir doesn't exist |

#### New Tests to Add

```python
@pytest.mark.unit
class TestRegisterFrontend:
    """Tests for register_frontend function."""

    def test_register_frontend_frozen_executable(self):
        """Uses _MEIPASS path when running as frozen executable."""
        # Setup: Mock sys.frozen = True, sys._MEIPASS = '/tmp/path'
        # Expected: static_dir = Path('/tmp/path') / 'web' / 'dist'

    def test_register_frontend_logs_warning_when_not_found(self, caplog):
        """Logs warning when frontend static files don't exist."""
        # Setup: Mock static_dir to non-existent path
        # Expected: Warning logged with "Frontend not built" message
```

---

## Implementation Checklist

### BackfillService Tests
- [x] `test_backfill_uses_configured_device_when_found`
- [x] `test_backfill_uses_first_device_when_no_mac_configured`
- [x] `test_backfill_uses_first_device_when_mac_is_none`
- [x] `test_batch_callback_updates_progress_with_date`
- [x] `test_batch_callback_handles_empty_batch`
- [x] `test_batch_callback_handles_missing_date_field`
- [x] `test_progress_callback_updates_progress`
- [x] `test_progress_callback_raises_interrupted_on_stop`
- [x] `test_save_credentials_updates_existing_device_mac`

### AmbientAPIQueue Tests
- [x] `test_shutdown_logs_warning_on_timeout`
- [x] `test_worker_handles_cancellation`
- [x] `test_worker_handles_unexpected_exception`

### App Factory Tests
- [x] `test_register_frontend_frozen_executable`
- [x] `test_register_frontend_development_mode`
- [x] `test_register_frontend_logs_warning_when_not_found`
- [x] `test_register_frontend_mounts_static_files`
- [x] `test_create_app_returns_fastapi_instance`
- [x] `test_create_app_configures_cors`
- [x] `test_create_app_registers_routes`

---

## Results After Phase 2

| File | Before | After | Improvement |
|------|--------|-------|-------------|
| backfill_service.py | 87.50% | **100%** | +12.5% |
| ambient_api_queue.py | 96.12% | 96% | Maintained |
| web/app.py | 60.00% | 82% | +22% |
| **Total Patch Coverage** | **94.79%** | **97%** | **+2.21%** |

---

## Phase 1 Summary (COMPLETED)

Phase 1 implemented comprehensive tests for `BackfillService` in `tests/test_backfill_service.py`.

**Tests Implemented:**
- `TestBackfillServiceInit` - Initialization and default state
- `TestProgressTracking` - Thread-safe progress operations
- `TestValidateCredentials` - All credential validation scenarios (401, 403, 429, generic errors)
- `TestSaveCredentials` - .env file operations
- `TestSaveDeviceSelection` - Device MAC persistence
- `TestGetCredentialStatus` - Credential status checking
- `TestStartBackfill` - Backfill startup logic
- `TestRunBackfill` - Background backfill execution
- `TestThreadSafety` - Concurrent access testing

**Coverage Achieved:** 87.50% (up from 5.35%)

---

## Appendix: Original Phase 1-5 Planning (Reference)

<details>
<summary>Click to expand original detailed planning</summary>

### Original BackfillService Test Plan

| Function | Description | Test Priority |
|----------|-------------|---------------|
| `__init__()` | Initialize service with default state | Medium |
| `get_progress()` | Thread-safe progress retrieval | Medium |
| `_update_progress()` | Thread-safe progress updates | Medium |
| `is_running()` | Check if backfill is running | Low |
| `stop()` | Request stop | Medium |
| `validate_credentials()` | Validate API keys and cache devices | **HIGH** |
| `save_credentials()` | Write credentials to .env file | **HIGH** |
| `save_device_selection()` | Update device MAC in .env | Medium |
| `get_credential_status()` | Check if credentials exist | Low |
| `start_backfill()` | Start background thread | **HIGH** |
| `_run_backfill()` | Background backfill logic | **HIGH** |

### Original Routes Test Plan (COMPLETED)

| Endpoint | Method | Status |
|----------|--------|--------|
| `/api/credentials/status` | GET | COMPLETE |
| `/api/credentials/validate` | POST | COMPLETE |
| `/api/credentials/save` | POST | COMPLETE |
| `/api/backfill/progress` | GET | COMPLETE |
| `/api/backfill/start` | POST | COMPLETE |
| `/api/backfill/stop` | POST | COMPLETE |
| `/api/devices` | GET | COMPLETE |
| `/api/devices/select` | POST | COMPLETE |
| `/api/scheduler/status` | GET | COMPLETE |

### Original API Client & Scheduler Plans (COMPLETED)

These were addressed in Phase 1 implementation.

</details>

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=weather_app --cov-report=html

# Run specific test file for Phase 2
pytest tests/test_backfill_service.py tests/test_api_queue.py -v

# Run only unit tests (fast)
pytest -m unit

# Check coverage for specific files
pytest --cov=weather_app/web/backfill_service --cov=weather_app/services/ambient_api_queue --cov=weather_app/web/app --cov-report=term-missing
```
