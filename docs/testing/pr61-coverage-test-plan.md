# PR 61 Code Coverage Test Plan

**Date:** January 13, 2026
**Target:** Improve patch coverage from 58.36% to 90%+
**Missing Lines:** 112 lines across 6 files

---

## Coverage Summary

| File | Current | Missing Lines | Priority | Effort |
|------|---------|---------------|----------|--------|
| `weather_app/web/backfill_service.py` | 5.35% | 53 | **HIGHEST** | High |
| `weather_app/web/routes.py` | 17.85% | 23 | **HIGH** | Medium |
| `weather_app/api/client.py` | 47.82% | 12 | Medium | Low |
| `weather_app/scheduler/scheduler.py` | 47.61% | 11 | Medium | Low |
| `weather_app/services/ambient_api_queue.py` | 91.47% | 11 | Low | Minimal |
| `weather_app/web/app.py` | 60.00% | 2 | Low | Minimal |

---

## Phase 1: BackfillService (53 lines - HIGHEST PRIORITY)

**File:** `weather_app/web/backfill_service.py`
**Test File:** `tests/test_backfill_service.py` (NEW)

### Functions to Test

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

### Test Cases for `validate_credentials()`

```python
@pytest.mark.unit
class TestValidateCredentials:

    def test_validate_credentials_success(self, mock_api):
        """Valid credentials return success with device list."""

    def test_validate_credentials_401_unauthorized(self, mock_api):
        """Invalid API key returns appropriate error."""

    def test_validate_credentials_403_forbidden(self, mock_api):
        """Forbidden access returns appropriate error."""

    def test_validate_credentials_429_rate_limit(self, mock_api):
        """Rate limit returns retry message."""

    def test_validate_credentials_generic_exception(self, mock_api):
        """Generic exception is handled gracefully."""

    def test_validate_credentials_empty_devices(self, mock_api):
        """Empty device list returns appropriate message."""

    def test_validate_credentials_uses_cache(self, mock_api):
        """Cached devices are returned without API call."""
```

### Test Cases for `save_credentials()`

```python
@pytest.mark.unit
class TestSaveCredentials:

    def test_save_credentials_new_file(self, temp_env):
        """Creates .env file if it doesn't exist."""

    def test_save_credentials_update_existing(self, temp_env):
        """Updates existing credentials in .env file."""

    def test_save_credentials_with_device_mac(self, temp_env):
        """Saves device MAC along with credentials."""

    def test_save_credentials_without_device_mac(self, temp_env):
        """Saves credentials without device MAC."""

    def test_save_credentials_file_error(self, temp_env):
        """Handles file I/O errors gracefully."""
```

### Test Cases for `_run_backfill()`

```python
@pytest.mark.unit
class TestRunBackfill:

    def test_backfill_success(self, mock_api, mock_db):
        """Successful backfill inserts data and updates progress."""

    def test_backfill_no_devices(self, mock_api):
        """Handles no devices found scenario."""

    def test_backfill_device_not_found_fallback(self, mock_api):
        """Falls back to first device if configured device not found."""

    def test_backfill_stop_requested(self, mock_api):
        """Stops when stop() is called."""

    def test_backfill_rate_limit_handling(self, mock_api):
        """Handles 429 rate limit with appropriate delay."""

    def test_backfill_batch_callback(self, mock_api, mock_db):
        """Batch callback processes accumulated data."""

    def test_backfill_progress_updates(self, mock_api):
        """Progress is updated throughout backfill."""

    def test_backfill_exception_handling(self, mock_api):
        """Exceptions are caught and reported in progress."""
```

### Mocking Strategy

```python
import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path

@pytest.fixture
def mock_api():
    """Mock AmbientWeatherAPI client."""
    with patch('weather_app.web.backfill_service.AmbientWeatherAPI') as mock:
        yield mock

@pytest.fixture
def mock_db():
    """Mock WeatherDatabase."""
    with patch('weather_app.web.backfill_service.WeatherDatabase') as mock:
        yield mock

@pytest.fixture
def mock_api_queue():
    """Mock the global api_queue."""
    with patch('weather_app.web.backfill_service.api_queue') as mock:
        yield mock

@pytest.fixture
def temp_env(tmp_path):
    """Temporary .env file for testing."""
    env_file = tmp_path / '.env'
    with patch('weather_app.web.backfill_service.ENV_FILE', env_file):
        yield env_file
```

---

## Phase 2: Routes (23 lines - HIGH PRIORITY)

**File:** `weather_app/web/routes.py`
**Test File:** `tests/test_api_endpoints.py` (UPDATE)

### Missing Endpoint Tests

| Endpoint | Method | Test Status |
|----------|--------|-------------|
| `/api/credentials/status` | GET | **MISSING** |
| `/api/credentials/validate` | POST | **MISSING** |
| `/api/credentials/save` | POST | **MISSING** |
| `/api/backfill/progress` | GET | **MISSING** |
| `/api/backfill/start` | POST | **MISSING** |
| `/api/backfill/stop` | POST | **MISSING** |
| `/api/devices` | GET | **MISSING** |
| `/api/devices/select` | POST | **MISSING** |
| `/api/scheduler/status` | GET | **MISSING** |

### Test Cases for Credential Endpoints

```python
@pytest.mark.unit
class TestCredentialEndpoints:

    def test_get_credential_status(self, client):
        """Returns credential configuration status."""

    def test_validate_credentials_success(self, client, mock_backfill):
        """Valid credentials return success with devices."""

    def test_validate_credentials_invalid(self, client, mock_backfill):
        """Invalid credentials return error message."""

    def test_save_credentials_success(self, client, mock_backfill):
        """Saves credentials successfully."""

    def test_save_credentials_failure(self, client, mock_backfill):
        """Handles save failure gracefully."""
```

### Test Cases for Backfill Endpoints

```python
@pytest.mark.unit
class TestBackfillEndpoints:

    def test_get_backfill_progress(self, client, mock_backfill):
        """Returns current backfill progress."""

    def test_start_backfill_success(self, client, mock_backfill):
        """Starts backfill successfully."""

    def test_start_backfill_already_running(self, client, mock_backfill):
        """Returns error if backfill already running."""

    def test_start_backfill_missing_credentials(self, client, mock_backfill):
        """Returns error if credentials missing."""

    def test_stop_backfill_success(self, client, mock_backfill):
        """Stops running backfill."""

    def test_stop_backfill_not_running(self, client, mock_backfill):
        """Returns message if no backfill running."""
```

### Test Cases for Device Endpoints

```python
@pytest.mark.unit
class TestDeviceEndpoints:

    def test_get_devices_success(self, client, mock_backfill):
        """Returns cached device list."""

    def test_get_devices_no_credentials(self, client, mock_backfill):
        """Returns error if credentials not configured."""

    def test_select_device_success(self, client, mock_backfill):
        """Selects device successfully."""

    def test_select_device_failure(self, client, mock_backfill):
        """Handles device selection failure."""
```

### Test Cases for Error Handling

```python
@pytest.mark.unit
class TestRouteErrorHandling:

    def test_get_weather_data_runtime_error(self, client, mock_db):
        """Handles RuntimeError in weather data endpoint."""

    def test_get_weather_data_value_error(self, client, mock_db):
        """Handles ValueError for invalid dates."""

    def test_get_latest_weather_runtime_error(self, client, mock_db):
        """Handles RuntimeError in latest weather endpoint."""

    def test_get_stats_runtime_error(self, client, mock_db):
        """Handles RuntimeError in stats endpoint."""
```

### Mocking Strategy

```python
@pytest.fixture
def mock_backfill():
    """Mock the backfill_service singleton."""
    with patch('weather_app.web.routes.backfill_service') as mock:
        mock.get_progress.return_value = {
            'status': 'idle',
            'progress': 0,
            'message': ''
        }
        mock.is_running.return_value = False
        yield mock

@pytest.fixture
def mock_scheduler():
    """Mock the scheduler instance."""
    with patch('weather_app.web.routes.scheduler') as mock:
        mock.get_status.return_value = {
            'enabled': True,
            'running': True
        }
        yield mock
```

---

## Phase 3: API Client (12 lines)

**File:** `weather_app/api/client.py`
**Test File:** `tests/test_api_client.py` (UPDATE)

### Test Cases to Add

```python
@pytest.mark.unit
class TestAPIClientEdgeCases:

    def test_get_devices_no_event_loop(self, mock_session):
        """Creates new event loop when none exists."""

    def test_get_devices_with_request_queue(self, mock_queue):
        """Uses request queue when provided."""

    def test_get_device_data_no_event_loop(self, mock_session):
        """Creates new event loop for device data."""

    def test_get_device_data_with_request_queue(self, mock_queue):
        """Uses request queue for device data."""

@pytest.mark.unit
class TestHistoricalDataFetching:

    def test_fetch_historical_with_start_date_filter(self, mock_api):
        """Filters data by start_date parameter."""

    def test_fetch_historical_rate_limit_handling(self, mock_api):
        """Handles 429 rate limit with 60s sleep."""

    def test_fetch_historical_pagination(self, mock_api):
        """Correctly paginates through historical data."""

    def test_fetch_historical_batch_callback(self, mock_api):
        """Executes batch callback with accumulated data."""

    def test_fetch_historical_progress_callback(self, mock_api):
        """Executes progress callback during fetch."""
```

### Mocking Strategy

```python
@pytest.fixture
def mock_no_event_loop():
    """Simulate no existing event loop."""
    with patch('asyncio.get_event_loop', side_effect=RuntimeError):
        with patch('asyncio.new_event_loop') as mock_loop:
            yield mock_loop

@pytest.fixture
def mock_rate_limit_response():
    """Mock 429 rate limit response."""
    response = MagicMock()
    response.status_code = 429
    response.raise_for_status.side_effect = requests.HTTPError(response=response)
    return response
```

---

## Phase 4: Scheduler (11 lines)

**File:** `weather_app/scheduler/scheduler.py`
**Test File:** `tests/test_scheduler.py` (UPDATE)

### Test Cases to Add

```python
@pytest.mark.unit
class TestSchedulerEdgeCases:

    def test_fetch_job_missing_credentials(self, scheduler):
        """Job returns early if credentials missing."""

    def test_fetch_job_no_devices(self, scheduler, mock_api):
        """Job returns early if no devices found."""

    def test_fetch_job_device_not_found_fallback(self, scheduler, mock_api):
        """Falls back to first device if configured not found."""

    def test_fetch_job_no_data_from_device(self, scheduler, mock_api):
        """Handles empty data response gracefully."""

    def test_fetch_job_exception_handling(self, scheduler, mock_api):
        """Exceptions don't propagate, are logged."""

    def test_start_when_disabled(self, disabled_scheduler):
        """Start returns early if scheduler disabled."""

    def test_get_status_when_disabled(self, disabled_scheduler):
        """Status shows disabled state."""

    def test_shutdown_when_disabled(self, disabled_scheduler):
        """Shutdown returns early if disabled."""
```

### Mocking Strategy

```python
@pytest.fixture
def scheduler_with_mock_apscheduler():
    """Scheduler with mocked APScheduler."""
    with patch('weather_app.scheduler.scheduler.BackgroundScheduler') as mock:
        yield mock

@pytest.fixture
def disabled_scheduler():
    """Scheduler with SCHEDULER_ENABLED=false."""
    with patch.dict(os.environ, {'SCHEDULER_ENABLED': 'false'}):
        from weather_app.scheduler.scheduler import WeatherScheduler
        yield WeatherScheduler(None)
```

---

## Phase 5: Queue & App (13 lines - Minimal)

### AmbientAPIQueue (`ambient_api_queue.py`)

**Test File:** `tests/test_api_queue.py` (UPDATE)

```python
@pytest.mark.unit
class TestQueueEdgeCases:

    def test_start_when_already_running(self, running_queue):
        """Start is no-op when queue already running."""

    def test_shutdown_when_not_running(self, stopped_queue):
        """Shutdown is no-op when queue not running."""

    def test_enqueue_when_not_running(self, stopped_queue):
        """Enqueue raises RuntimeError when queue stopped."""

    def test_shutdown_timeout_scenario(self, running_queue):
        """Handles timeout during graceful shutdown."""
```

### App Factory (`web/app.py`)

**Test File:** `tests/test_app.py` (NEW or add to `test_api_endpoints.py`)

```python
@pytest.mark.unit
class TestAppFactory:

    def test_register_frontend_frozen_executable(self):
        """Uses correct path for PyInstaller frozen app."""
        with patch('sys.frozen', True, create=True):
            # Test frozen executable path

    def test_register_frontend_not_found(self, tmp_path):
        """Logs warning if frontend static files not found."""
        with patch('weather_app.web.app.static_dir', tmp_path / 'nonexistent'):
            # Test warning is logged
```

---

## Required Fixtures Summary

Add these to `tests/conftest.py`:

```python
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

# BackfillService fixtures
@pytest.fixture
def mock_ambient_api():
    """Mock AmbientWeatherAPI for backfill tests."""
    with patch('weather_app.web.backfill_service.AmbientWeatherAPI') as mock:
        mock_instance = MagicMock()
        mock_instance.get_devices.return_value = [
            {'macAddress': 'AA:BB:CC:DD:EE:FF', 'info': {'name': 'Test Station'}}
        ]
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_weather_db():
    """Mock WeatherDatabase for backfill tests."""
    with patch('weather_app.web.backfill_service.WeatherDatabase') as mock:
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock.return_value = mock_instance
        yield mock

@pytest.fixture
def temp_env_file(tmp_path):
    """Temporary .env file for credential tests."""
    env_file = tmp_path / '.env'
    env_file.write_text('')
    with patch('weather_app.web.backfill_service.ENV_FILE', env_file):
        yield env_file

# Route testing fixtures
@pytest.fixture
def mock_backfill_service():
    """Mock backfill_service for route tests."""
    with patch('weather_app.web.routes.backfill_service') as mock:
        mock.get_progress.return_value = {'status': 'idle', 'progress': 0}
        mock.is_running.return_value = False
        mock.cached_devices = []
        yield mock

@pytest.fixture
def mock_scheduler_instance():
    """Mock scheduler for route tests."""
    with patch('weather_app.web.routes.scheduler') as mock:
        mock.get_status.return_value = {'enabled': True, 'running': True}
        yield mock
```

---

## Execution Order

1. **Create `tests/test_backfill_service.py`** - Highest impact (53 lines)
2. **Update `tests/test_api_endpoints.py`** - Add missing endpoint tests (23 lines)
3. **Update `tests/test_api_client.py`** - Add edge case tests (12 lines)
4. **Update `tests/test_scheduler.py`** - Add missing scenarios (11 lines)
5. **Update `tests/test_api_queue.py`** - Minor edge cases (9 lines)
6. **Add app factory tests** - Minimal work (2 lines)

---

## Expected Results

| File | Before | After | Lines Covered |
|------|--------|-------|---------------|
| backfill_service.py | 5% | 85%+ | +45 |
| routes.py | 18% | 90%+ | +20 |
| api/client.py | 48% | 90%+ | +10 |
| scheduler.py | 48% | 90%+ | +9 |
| ambient_api_queue.py | 91% | 98%+ | +2 |
| web/app.py | 60% | 98%+ | +2 |
| **Total Patch Coverage** | **58%** | **90%+** | **+88 lines** |

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=weather_app --cov-report=html

# Run specific test file
pytest tests/test_backfill_service.py -v

# Run only unit tests (fast)
pytest -m unit

# Run with verbose output
pytest -v -s
```
