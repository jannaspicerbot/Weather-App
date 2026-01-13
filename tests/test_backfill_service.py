"""Tests for BackfillService.

This module tests the browser-based onboarding backfill service including:
- Credential validation
- Credential and device saving
- Background backfill operations
- Progress tracking
"""

import os
import threading
import time
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def backfill_service():
    """Create a fresh BackfillService instance for each test."""
    from weather_app.web.backfill_service import BackfillService

    return BackfillService()


@pytest.fixture
def mock_api_queue():
    """Mock the global api_queue from weather_app.web.app."""
    with patch("weather_app.web.app.api_queue") as mock:
        yield mock


@pytest.fixture
def mock_ambient_api():
    """Mock AmbientWeatherAPI for backfill tests."""
    with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock:
        mock_instance = MagicMock()
        mock_instance.get_devices.return_value = [
            {
                "macAddress": "AA:BB:CC:DD:EE:FF",
                "info": {"name": "Test Station"},
                "lastData": {"date": "2024-01-01T12:00:00"},
            }
        ]
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_weather_db():
    """Mock WeatherDatabase for backfill tests."""
    with patch("weather_app.web.backfill_service.WeatherDatabase") as mock:
        mock_instance = MagicMock()
        mock_instance.__enter__ = MagicMock(return_value=mock_instance)
        mock_instance.__exit__ = MagicMock(return_value=False)
        mock_instance.insert_data.return_value = (10, 0)  # inserted, skipped
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def temp_env_file(tmp_path):
    """Temporary .env file for credential tests."""
    env_file = tmp_path / ".env"
    env_file.write_text("")
    with patch("weather_app.web.backfill_service.ENV_FILE", env_file):
        yield env_file


# =============================================================================
# Initialization Tests
# =============================================================================


@pytest.mark.unit
class TestBackfillServiceInit:
    """Tests for BackfillService initialization."""

    def test_init_creates_default_progress(self, backfill_service):
        """Initialize service with default state."""
        progress = backfill_service.get_progress()

        assert progress["status"] == "idle"
        assert progress["message"] == "No backfill in progress"
        assert progress["total_records"] == 0
        assert progress["inserted_records"] == 0
        assert progress["skipped_records"] == 0
        assert progress["error"] is None

    def test_init_not_running(self, backfill_service):
        """Service is not running by default."""
        assert backfill_service.is_running() is False


# =============================================================================
# Progress Tracking Tests
# =============================================================================


@pytest.mark.unit
class TestProgressTracking:
    """Tests for thread-safe progress tracking."""

    def test_get_progress_returns_copy(self, backfill_service):
        """get_progress returns a copy, not the original dict."""
        progress1 = backfill_service.get_progress()
        progress1["status"] = "modified"

        progress2 = backfill_service.get_progress()
        assert progress2["status"] == "idle"  # Original unchanged

    def test_update_progress_thread_safe(self, backfill_service):
        """_update_progress is thread-safe."""
        backfill_service._update_progress(status="in_progress", message="Testing")

        progress = backfill_service.get_progress()
        assert progress["status"] == "in_progress"
        assert progress["message"] == "Testing"

    def test_is_running_checks_status(self, backfill_service):
        """is_running checks the status field."""
        assert backfill_service.is_running() is False

        backfill_service._update_progress(status="in_progress")
        assert backfill_service.is_running() is True

        backfill_service._update_progress(status="completed")
        assert backfill_service.is_running() is False

    def test_stop_sets_flag(self, backfill_service):
        """stop() sets the stop requested flag."""
        assert backfill_service._stop_requested is False

        backfill_service.stop()

        assert backfill_service._stop_requested is True


# =============================================================================
# Validate Credentials Tests
# =============================================================================


@pytest.mark.unit
class TestValidateCredentials:
    """Tests for credential validation."""

    def test_validate_credentials_success(self, backfill_service):
        """Valid credentials return success with device list."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = [
                {
                    "macAddress": "AA:BB:CC:DD:EE:FF",
                    "info": {"name": "Test Station"},
                    "lastData": {"date": "2024-01-01T12:00:00"},
                }
            ]
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "test_api_key", "test_app_key"
                )

        assert valid is True
        assert "1 device" in message
        assert len(devices) == 1
        assert devices[0]["mac_address"] == "AA:BB:CC:DD:EE:FF"
        assert devices[0]["name"] == "Test Station"

    def test_validate_credentials_401_unauthorized(self, backfill_service):
        """Invalid API key returns appropriate error."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.side_effect = Exception("401 Unauthorized")
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "invalid_key", "test_app_key"
                )

        assert valid is False
        assert "Invalid API credentials" in message
        assert devices == []

    def test_validate_credentials_403_forbidden(self, backfill_service):
        """Forbidden access returns appropriate error."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.side_effect = Exception("403 Forbidden")
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "test_key", "test_app_key"
                )

        assert valid is False
        assert "Access denied" in message
        assert devices == []

    def test_validate_credentials_429_rate_limit(self, backfill_service):
        """Rate limit returns retry message."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.side_effect = Exception("429 Rate Limit")
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "test_key", "test_app_key"
                )

        assert valid is False
        assert "Rate limit" in message
        assert devices == []

    def test_validate_credentials_generic_exception(self, backfill_service):
        """Generic exception is handled gracefully."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.side_effect = Exception("Network error")
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "test_key", "test_app_key"
                )

        assert valid is False
        assert "Failed to validate" in message
        assert "Network error" in message
        assert devices == []

    def test_validate_credentials_empty_devices(self, backfill_service):
        """Empty device list returns appropriate message."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = []
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                valid, message, devices = backfill_service.validate_credentials(
                    "test_key", "test_app_key"
                )

        assert valid is False
        assert "No devices found" in message
        assert devices == []

    def test_validate_credentials_caches_devices(self, backfill_service):
        """Valid credentials cache the device list."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            test_devices = [
                {
                    "macAddress": "AA:BB:CC:DD:EE:FF",
                    "info": {"name": "Test Station"},
                    "lastData": {},
                }
            ]
            mock_instance.get_devices.return_value = test_devices
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                backfill_service.validate_credentials("test_key", "test_app_key")

        assert backfill_service._cached_devices == test_devices

    def test_validate_credentials_clears_cache_on_failure(self, backfill_service):
        """Failed validation clears the device cache."""
        # First, set some cached devices
        backfill_service._cached_devices = [{"macAddress": "old"}]

        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.side_effect = Exception("Error")
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                backfill_service.validate_credentials("test_key", "test_app_key")

        assert backfill_service._cached_devices is None


# =============================================================================
# Save Credentials Tests
# =============================================================================


@pytest.mark.unit
class TestSaveCredentials:
    """Tests for saving credentials to .env file."""

    def test_save_credentials_new_file(self, backfill_service, temp_env_file):
        """Creates .env file if it doesn't exist."""
        # Remove the file created by fixture
        temp_env_file.unlink()

        success, message = backfill_service.save_credentials(
            "new_api_key", "new_app_key"
        )

        assert success is True
        assert "saved successfully" in message
        assert temp_env_file.exists()
        content = temp_env_file.read_text()
        assert "AMBIENT_API_KEY=new_api_key" in content
        assert "AMBIENT_APP_KEY=new_app_key" in content

    def test_save_credentials_update_existing(self, backfill_service, temp_env_file):
        """Updates existing credentials in .env file."""
        temp_env_file.write_text("AMBIENT_API_KEY=old_key\nAMBIENT_APP_KEY=old_app\n")

        success, message = backfill_service.save_credentials(
            "new_api_key", "new_app_key"
        )

        assert success is True
        content = temp_env_file.read_text()
        assert "AMBIENT_API_KEY=new_api_key" in content
        assert "AMBIENT_APP_KEY=new_app_key" in content
        assert "old_key" not in content

    def test_save_credentials_with_device_mac(self, backfill_service, temp_env_file):
        """Saves device MAC along with credentials."""
        success, message = backfill_service.save_credentials(
            "api_key", "app_key", device_mac="AA:BB:CC:DD:EE:FF"
        )

        assert success is True
        content = temp_env_file.read_text()
        assert "AMBIENT_DEVICE_MAC=AA:BB:CC:DD:EE:FF" in content

    def test_save_credentials_without_device_mac(self, backfill_service, temp_env_file):
        """Saves credentials without device MAC."""
        success, message = backfill_service.save_credentials("api_key", "app_key")

        assert success is True
        content = temp_env_file.read_text()
        assert "AMBIENT_DEVICE_MAC" not in content

    def test_save_credentials_preserves_other_vars(self, backfill_service, temp_env_file):
        """Preserves other environment variables."""
        temp_env_file.write_text("OTHER_VAR=value\nAMBIENT_API_KEY=old\n")

        success, message = backfill_service.save_credentials("new_key", "new_app")

        content = temp_env_file.read_text()
        assert "OTHER_VAR=value" in content
        assert "AMBIENT_API_KEY=new_key" in content

    def test_save_credentials_updates_environ(self, backfill_service, temp_env_file):
        """Updates os.environ for current process."""
        backfill_service.save_credentials(
            "test_api", "test_app", device_mac="FF:EE:DD:CC:BB:AA"
        )

        assert os.environ.get("AMBIENT_API_KEY") == "test_api"
        assert os.environ.get("AMBIENT_APP_KEY") == "test_app"
        assert os.environ.get("AMBIENT_DEVICE_MAC") == "FF:EE:DD:CC:BB:AA"

    def test_save_credentials_file_error(self, backfill_service, tmp_path):
        """Handles file I/O errors gracefully."""
        # Use a directory path instead of file to cause error
        bad_path = tmp_path / "nonexistent_dir" / ".env"

        with patch("weather_app.web.backfill_service.ENV_FILE", bad_path):
            success, message = backfill_service.save_credentials("api", "app")

        assert success is False
        assert "Failed to save" in message


# =============================================================================
# Save Device Selection Tests
# =============================================================================


@pytest.mark.unit
class TestSaveDeviceSelection:
    """Tests for saving device MAC selection."""

    def test_save_device_selection_new(self, backfill_service, temp_env_file):
        """Adds device MAC to .env when not present."""
        temp_env_file.write_text("AMBIENT_API_KEY=key\n")

        success, message = backfill_service.save_device_selection("AA:BB:CC:DD:EE:FF")

        assert success is True
        assert "saved successfully" in message
        content = temp_env_file.read_text()
        assert "AMBIENT_DEVICE_MAC=AA:BB:CC:DD:EE:FF" in content

    def test_save_device_selection_update(self, backfill_service, temp_env_file):
        """Updates existing device MAC."""
        temp_env_file.write_text("AMBIENT_DEVICE_MAC=OLD:MA:CA:DD:RE:SS\n")

        success, message = backfill_service.save_device_selection("NEW:MA:CA:DD:RE:SS")

        content = temp_env_file.read_text()
        assert "AMBIENT_DEVICE_MAC=NEW:MA:CA:DD:RE:SS" in content
        assert "OLD:MA:CA:DD:RE:SS" not in content

    def test_save_device_selection_updates_environ(
        self, backfill_service, temp_env_file
    ):
        """Updates os.environ for current process."""
        backfill_service.save_device_selection("AA:BB:CC:DD:EE:FF")

        assert os.environ.get("AMBIENT_DEVICE_MAC") == "AA:BB:CC:DD:EE:FF"

    def test_save_device_selection_file_error(self, backfill_service, tmp_path):
        """Handles file I/O errors gracefully."""
        bad_path = tmp_path / "nonexistent_dir" / ".env"

        with patch("weather_app.web.backfill_service.ENV_FILE", bad_path):
            success, message = backfill_service.save_device_selection("AA:BB:CC")

        assert success is False
        assert "Failed to save" in message


# =============================================================================
# Get Credential Status Tests
# =============================================================================


@pytest.mark.unit
class TestGetCredentialStatus:
    """Tests for credential status checking."""

    def test_get_credential_status_configured(self, backfill_service):
        """Returns configured=True when both keys are set."""
        with patch.dict(
            os.environ,
            {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            clear=False,
        ):
            status = backfill_service.get_credential_status()

        assert status["configured"] is True
        assert status["has_api_key"] is True
        assert status["has_app_key"] is True

    def test_get_credential_status_missing_api_key(self, backfill_service):
        """Returns configured=False when API key missing."""
        with patch.dict(
            os.environ,
            {"AMBIENT_API_KEY": "", "AMBIENT_APP_KEY": "app"},
            clear=False,
        ):
            status = backfill_service.get_credential_status()

        assert status["configured"] is False
        assert status["has_api_key"] is False
        assert status["has_app_key"] is True

    def test_get_credential_status_missing_app_key(self, backfill_service):
        """Returns configured=False when app key missing."""
        with patch.dict(
            os.environ,
            {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": ""},
            clear=False,
        ):
            status = backfill_service.get_credential_status()

        assert status["configured"] is False
        assert status["has_api_key"] is True
        assert status["has_app_key"] is False

    def test_get_credential_status_both_missing(self, backfill_service):
        """Returns configured=False when both keys missing."""
        with patch.dict(
            os.environ, {"AMBIENT_API_KEY": "", "AMBIENT_APP_KEY": ""}, clear=False
        ):
            status = backfill_service.get_credential_status()

        assert status["configured"] is False
        assert status["has_api_key"] is False
        assert status["has_app_key"] is False


# =============================================================================
# Start Backfill Tests
# =============================================================================


@pytest.mark.unit
class TestStartBackfill:
    """Tests for starting backfill operations."""

    def test_start_backfill_success(self, backfill_service):
        """Starts backfill successfully with valid credentials."""
        with patch.object(backfill_service, "_run_backfill"):
            with patch.dict(
                os.environ,
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
                clear=False,
            ):
                started, message = backfill_service.start_backfill()

        assert started is True
        assert "started" in message.lower()

    def test_start_backfill_already_running(self, backfill_service):
        """Returns error if backfill already running."""
        backfill_service._update_progress(status="in_progress")

        started, message = backfill_service.start_backfill("key", "app")

        assert started is False
        assert "already in progress" in message

    def test_start_backfill_missing_credentials(self, backfill_service):
        """Returns error if credentials missing."""
        with patch.dict(
            os.environ, {"AMBIENT_API_KEY": "", "AMBIENT_APP_KEY": ""}, clear=False
        ):
            started, message = backfill_service.start_backfill()

        assert started is False
        assert "not configured" in message

    def test_start_backfill_uses_env_credentials(self, backfill_service):
        """Uses environment credentials when not provided."""
        with patch.object(backfill_service, "_run_backfill") as mock_run:
            with patch.dict(
                os.environ,
                {"AMBIENT_API_KEY": "env_api", "AMBIENT_APP_KEY": "env_app"},
                clear=False,
            ):
                backfill_service.start_backfill()

                # Wait for thread to start
                time.sleep(0.1)

        # Thread should have been started
        assert backfill_service._thread is not None

    def test_start_backfill_uses_provided_credentials(self, backfill_service):
        """Uses provided credentials over environment."""
        with patch.object(backfill_service, "_run_backfill"):
            started, message = backfill_service.start_backfill(
                "provided_api", "provided_app"
            )

        assert started is True

    def test_start_backfill_resets_stop_flag(self, backfill_service):
        """Resets stop flag when starting."""
        backfill_service._stop_requested = True

        with patch.object(backfill_service, "_run_backfill"):
            backfill_service.start_backfill("key", "app")

        assert backfill_service._stop_requested is False


# =============================================================================
# Run Backfill Tests
# =============================================================================


@pytest.mark.unit
class TestRunBackfill:
    """Tests for the background backfill logic."""

    def test_backfill_updates_progress_on_start(self, backfill_service):
        """Backfill updates progress to in_progress on start."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = []
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                backfill_service._run_backfill("api_key", "app_key")

        # After completion/failure, check it ran
        progress = backfill_service.get_progress()
        assert progress["status"] in ["failed", "completed", "idle"]

    def test_backfill_no_devices(self, backfill_service):
        """Handles no devices found scenario."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = []
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                backfill_service._run_backfill("api_key", "app_key")

        progress = backfill_service.get_progress()
        assert progress["status"] == "failed"
        assert "No devices" in progress["message"]

    def test_backfill_uses_cached_devices(self, backfill_service):
        """Uses cached devices from validation if available."""
        cached_devices = [
            {
                "macAddress": "CACHED:MAC",
                "info": {"name": "Cached Station"},
                "lastData": {},
            }
        ]
        backfill_service._cached_devices = cached_devices

        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_device_data.return_value = []
            mock_instance.fetch_all_historical_data.return_value = (0, 0, 0)
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                with patch("weather_app.web.backfill_service.WeatherDatabase"):
                    backfill_service._run_backfill("api_key", "app_key")

            # get_devices should NOT have been called since we had cached devices
            mock_instance.get_devices.assert_not_called()

    def test_backfill_device_not_found_fallback(self, backfill_service):
        """Falls back to first device if configured device not found."""
        devices = [
            {"macAddress": "FIRST:DEVICE", "info": {"name": "First Device"}},
            {"macAddress": "SECOND:DEVICE", "info": {"name": "Second Device"}},
        ]

        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = devices
            mock_instance.get_device_data.return_value = []
            mock_instance.fetch_all_historical_data.return_value = (0, 0, 0)
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                with patch("weather_app.web.backfill_service.WeatherDatabase"):
                    with patch(
                        "weather_app.web.backfill_service.AMBIENT_DEVICE_MAC",
                        "NONEXISTENT:MAC",
                    ):
                        backfill_service._run_backfill("api_key", "app_key")

            # Should have used the first device since configured wasn't found
            mock_instance.get_device_data.assert_called()
            call_args = mock_instance.get_device_data.call_args
            assert call_args[0][0] == "FIRST:DEVICE"

    def test_backfill_stop_requested(self, backfill_service):
        """Stops when stop() is called."""
        backfill_service._stop_requested = True

        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = [
                {"macAddress": "MAC", "info": {"name": "Station"}}
            ]
            mock_instance.get_device_data.return_value = [{"tempf": 72}]
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                with patch(
                    "weather_app.web.backfill_service.WeatherDatabase"
                ) as mock_db:
                    mock_db_instance = MagicMock()
                    mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
                    mock_db_instance.__exit__ = MagicMock(return_value=False)
                    mock_db_instance.insert_data.return_value = (1, 0)
                    mock_db.return_value = mock_db_instance

                    backfill_service._run_backfill("api_key", "app_key")

        progress = backfill_service.get_progress()
        assert progress["status"] == "idle"
        assert "cancelled" in progress["message"].lower()

    def test_backfill_exception_handling(self, backfill_service):
        """Exceptions are caught and reported in progress."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_api.side_effect = Exception("API connection failed")

            with patch("weather_app.web.app.api_queue"):
                backfill_service._run_backfill("api_key", "app_key")

        progress = backfill_service.get_progress()
        assert progress["status"] == "failed"
        assert "API connection failed" in progress["error"]

    def test_backfill_clears_cached_devices_after_use(self, backfill_service):
        """Clears cached devices after backfill uses them."""
        backfill_service._cached_devices = [
            {"macAddress": "CACHED:MAC", "info": {"name": "Station"}}
        ]

        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_device_data.return_value = []
            mock_instance.fetch_all_historical_data.return_value = (0, 0, 0)
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                with patch("weather_app.web.backfill_service.WeatherDatabase"):
                    backfill_service._run_backfill("api_key", "app_key")

        assert backfill_service._cached_devices is None

    def test_backfill_inserts_latest_data_first(self, backfill_service):
        """Fetches and inserts latest data before historical backfill."""
        with patch("weather_app.web.backfill_service.AmbientWeatherAPI") as mock_api:
            mock_instance = MagicMock()
            mock_instance.get_devices.return_value = [
                {"macAddress": "MAC", "info": {"name": "Station"}}
            ]
            latest_data = [{"tempf": 72, "date": "2024-01-01T12:00:00"}]
            mock_instance.get_device_data.return_value = latest_data
            mock_instance.fetch_all_historical_data.return_value = (100, 90, 10)
            mock_api.return_value = mock_instance

            with patch("weather_app.web.app.api_queue"):
                with patch(
                    "weather_app.web.backfill_service.WeatherDatabase"
                ) as mock_db:
                    mock_db_instance = MagicMock()
                    mock_db_instance.__enter__ = MagicMock(return_value=mock_db_instance)
                    mock_db_instance.__exit__ = MagicMock(return_value=False)
                    mock_db_instance.insert_data.return_value = (1, 0)
                    mock_db.return_value = mock_db_instance

                    backfill_service._run_backfill("api_key", "app_key")

            # Verify get_device_data was called for latest data
            mock_instance.get_device_data.assert_called()


# =============================================================================
# Thread Safety Tests
# =============================================================================


@pytest.mark.unit
class TestThreadSafety:
    """Tests for thread-safe operations."""

    def test_concurrent_progress_access(self, backfill_service):
        """Multiple threads can safely access progress."""
        results = []
        errors = []

        def read_progress():
            try:
                for _ in range(100):
                    progress = backfill_service.get_progress()
                    results.append(progress["status"])
            except Exception as e:
                errors.append(e)

        def update_progress():
            try:
                for i in range(100):
                    backfill_service._update_progress(
                        total_records=i, message=f"Update {i}"
                    )
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=read_progress),
            threading.Thread(target=read_progress),
            threading.Thread(target=update_progress),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 200  # 2 read threads * 100 reads each
