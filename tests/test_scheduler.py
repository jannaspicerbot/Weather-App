"""
Comprehensive tests for the WeatherScheduler.

Tests cover:
- Scheduler initialization
- Job execution with mocked API
- Start/shutdown lifecycle
- Status reporting
- Error handling
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from weather_app.scheduler.scheduler import WeatherScheduler

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    temp_dir = tempfile.gettempdir()
    db_path = Path(temp_dir) / f"test_scheduler_{datetime.now().timestamp()}.duckdb"

    # Initialize database
    from weather_app.database.engine import WeatherDatabase

    with WeatherDatabase(str(db_path)) as db:
        pass

    yield str(db_path)

    # Cleanup
    db_path.unlink(missing_ok=True)
    wal_path = db_path.with_suffix(".duckdb.wal")
    wal_path.unlink(missing_ok=True)


@pytest.fixture
def mock_env_enabled():
    """Mock environment with scheduler enabled."""
    with patch.dict(
        "os.environ",
        {
            "AMBIENT_API_KEY": "test_api_key",
            "AMBIENT_APP_KEY": "test_app_key",
            "SCHEDULER_ENABLED": "true",
            "SCHEDULER_FETCH_INTERVAL_MINUTES": "5",
        },
    ):
        yield


@pytest.fixture
def mock_env_disabled():
    """Mock environment with scheduler disabled."""
    with patch.dict(
        "os.environ",
        {
            "SCHEDULER_ENABLED": "false",
        },
    ):
        yield


@pytest.fixture
def mock_devices_response():
    """Mock response from get_devices."""
    return [
        {
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "info": {"name": "Test Weather Station"},
        }
    ]


@pytest.fixture
def mock_weather_data():
    """Mock weather data response."""
    return [
        {
            "dateutc": 1704110400000,
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
        }
    ]


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestWeatherSchedulerInit:
    """Tests for WeatherScheduler initialization."""

    @pytest.mark.unit
    def test_init_loads_config(self, mock_env_enabled):
        """Scheduler should load configuration from environment."""
        scheduler = WeatherScheduler()

        assert scheduler.api_key == "test_api_key"
        assert scheduler.app_key == "test_app_key"
        assert scheduler.enabled is True
        assert scheduler.fetch_interval_minutes == 5

    @pytest.mark.unit
    def test_init_disabled(self, mock_env_disabled):
        """Scheduler should respect SCHEDULER_ENABLED=false."""
        scheduler = WeatherScheduler()

        assert scheduler.enabled is False

    @pytest.mark.unit
    def test_init_default_interval(self):
        """Scheduler should use default interval if not specified."""
        with patch.dict(
            "os.environ",
            {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            clear=True,
        ):
            # Need to reload to pick up env changes
            scheduler = WeatherScheduler()
            # Default is 5 minutes
            assert scheduler.fetch_interval_minutes == 5

    @pytest.mark.unit
    def test_init_creates_background_scheduler(self, mock_env_enabled):
        """Scheduler should create APScheduler BackgroundScheduler."""
        from apscheduler.schedulers.background import BackgroundScheduler

        scheduler = WeatherScheduler()

        assert isinstance(scheduler.scheduler, BackgroundScheduler)


# =============================================================================
# FETCH JOB TESTS
# =============================================================================


class TestFetchWeatherJob:
    """Tests for the fetch_weather_job method."""

    @pytest.mark.unit
    def test_fetch_job_missing_credentials(self, mock_env_disabled):
        """fetch_weather_job should handle missing credentials."""
        scheduler = WeatherScheduler()
        scheduler.api_key = None
        scheduler.app_key = None

        # Should not raise exception
        scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_success(
        self, mock_env_enabled, temp_db_path, mock_devices_response, mock_weather_data
    ):
        """fetch_weather_job should fetch and store data successfully."""
        scheduler = WeatherScheduler()

        # Mock API
        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = mock_weather_data

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ):
                scheduler.fetch_weather_job()

        # Verify data was stored
        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(temp_db_path) as db:
            result = db.conn.execute("SELECT COUNT(*) FROM weather_data").fetchone()
            assert result[0] == 1

    @pytest.mark.unit
    def test_fetch_job_no_devices(self, mock_env_enabled):
        """fetch_weather_job should handle no devices found."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = []

        with patch(
            "weather_app.scheduler.scheduler.AmbientWeatherAPI", return_value=mock_api
        ):
            # Should not raise exception
            scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_no_data(
        self, mock_env_enabled, temp_db_path, mock_devices_response
    ):
        """fetch_weather_job should handle no data returned."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = []

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ):
                # Should not raise exception
                scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_api_error(self, mock_env_enabled, mock_devices_response):
        """fetch_weather_job should handle API errors gracefully."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.side_effect = Exception("API Error")

        with patch(
            "weather_app.scheduler.scheduler.AmbientWeatherAPI", return_value=mock_api
        ):
            # Should not raise exception
            scheduler.fetch_weather_job()


# =============================================================================
# LIFECYCLE TESTS
# =============================================================================


class TestSchedulerLifecycle:
    """Tests for scheduler start/shutdown lifecycle."""

    @pytest.mark.unit
    def test_start_when_enabled(self, mock_env_enabled):
        """start() should add job and start scheduler when enabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "add_job") as mock_add_job:
            with patch.object(scheduler.scheduler, "start") as mock_start:
                with patch.object(scheduler.scheduler, "get_job") as mock_get_job:
                    # Mock the job to return next_run_time
                    mock_job = MagicMock()
                    mock_job.next_run_time = datetime.now()
                    mock_get_job.return_value = mock_job

                    scheduler.start()

                    mock_add_job.assert_called_once()
                    mock_start.assert_called_once()

    @pytest.mark.unit
    def test_start_when_disabled(self, mock_env_disabled):
        """start() should do nothing when scheduler is disabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "add_job") as mock_add_job:
            with patch.object(scheduler.scheduler, "start") as mock_start:
                scheduler.start()

                mock_add_job.assert_not_called()
                mock_start.assert_not_called()

    @pytest.mark.unit
    def test_shutdown_when_enabled(self, mock_env_enabled):
        """shutdown() should shutdown scheduler when enabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "shutdown") as mock_shutdown:
            scheduler.shutdown()

            mock_shutdown.assert_called_once_with(wait=True)

    @pytest.mark.unit
    def test_shutdown_when_disabled(self, mock_env_disabled):
        """shutdown() should do nothing when scheduler is disabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "shutdown") as mock_shutdown:
            scheduler.shutdown()

            mock_shutdown.assert_not_called()


# =============================================================================
# STATUS TESTS
# =============================================================================


class TestSchedulerStatus:
    """Tests for get_status method."""

    @pytest.mark.unit
    def test_status_when_disabled(self, mock_env_disabled):
        """get_status() should return disabled status."""
        scheduler = WeatherScheduler()

        status = scheduler.get_status()

        assert status["enabled"] is False
        assert status["running"] is False
        assert "disabled" in status["message"].lower()

    @pytest.mark.unit
    def test_status_when_enabled_not_running(self, mock_env_enabled):
        """get_status() should return status when enabled but not started."""
        scheduler = WeatherScheduler()

        # Don't start the scheduler, just check status
        with patch.object(scheduler.scheduler, "get_job", return_value=None):
            status = scheduler.get_status()

        assert status["enabled"] is True
        assert status["fetch_interval_minutes"] == 5
        assert status["next_run_time"] is None

    @pytest.mark.unit
    def test_status_when_running(self, mock_env_enabled):
        """get_status() should return full status when running."""
        scheduler = WeatherScheduler()

        # Mock a running job
        mock_job = MagicMock()
        mock_job.next_run_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_job.id = "fetch_weather"

        # Use PropertyMock for the 'running' property
        with patch.object(scheduler.scheduler, "get_job", return_value=mock_job):
            with patch.object(
                type(scheduler.scheduler),
                "running",
                new_callable=lambda: property(lambda self: True),
            ):
                status = scheduler.get_status()

        assert status["enabled"] is True
        assert status["running"] is True
        assert status["fetch_interval_minutes"] == 5
        assert status["job_id"] == "fetch_weather"
        assert status["next_run_time"] is not None


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestSchedulerIntegration:
    """Integration tests for scheduler with real APScheduler."""

    @pytest.mark.integration
    def test_full_lifecycle(self, mock_env_enabled, temp_db_path):
        """Test full scheduler lifecycle: init -> start -> shutdown."""
        scheduler = WeatherScheduler()

        # Verify initial state
        assert scheduler.enabled is True
        assert not scheduler.scheduler.running

        # Start scheduler
        scheduler.start()
        assert scheduler.scheduler.running

        # Check status
        status = scheduler.get_status()
        assert status["enabled"] is True
        assert status["running"] is True

        # Shutdown
        scheduler.shutdown()
        assert not scheduler.scheduler.running


# =============================================================================
# ADDITIONAL EDGE CASE TESTS
# =============================================================================


class TestSchedulerEdgeCases:
    """Tests for scheduler edge cases and error handling."""

    @pytest.mark.unit
    def test_fetch_job_missing_api_key(self, mock_env_disabled):
        """Job returns early if API key missing."""
        scheduler = WeatherScheduler()
        scheduler.api_key = None
        scheduler.app_key = "app_key"

        # Should not raise exception, should return early
        scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_missing_app_key(self, mock_env_enabled):
        """Job returns early if App key missing."""
        scheduler = WeatherScheduler()
        scheduler.app_key = None

        # Should not raise exception, should return early
        scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_device_not_found_fallback(
        self, mock_env_enabled, temp_db_path, mock_weather_data
    ):
        """Falls back to first device if configured device not found."""
        devices = [
            {"macAddress": "FIRST:DEVICE", "info": {"name": "First Device"}},
            {"macAddress": "SECOND:DEVICE", "info": {"name": "Second Device"}},
        ]

        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = devices
        mock_api.get_device_data.return_value = mock_weather_data

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ):
                with patch(
                    "weather_app.scheduler.scheduler.AMBIENT_DEVICE_MAC",
                    "NONEXISTENT:MAC",
                ):
                    scheduler.fetch_weather_job()

        # Should have called get_device_data with the first device
        mock_api.get_device_data.assert_called_once()
        call_args = mock_api.get_device_data.call_args
        assert call_args[0][0] == "FIRST:DEVICE"

    @pytest.mark.unit
    def test_fetch_job_no_data_from_device(
        self, mock_env_enabled, mock_devices_response
    ):
        """Handles empty data response gracefully."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = []  # Empty response

        with patch(
            "weather_app.scheduler.scheduler.AmbientWeatherAPI", return_value=mock_api
        ):
            # Should not raise exception
            scheduler.fetch_weather_job()

        # Should have called both methods
        mock_api.get_devices.assert_called_once()
        mock_api.get_device_data.assert_called_once()

    @pytest.mark.unit
    def test_fetch_job_exception_does_not_propagate(self, mock_env_enabled):
        """Exceptions are caught and don't propagate to scheduler."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.side_effect = Exception("Unexpected error")

        with patch(
            "weather_app.scheduler.scheduler.AmbientWeatherAPI", return_value=mock_api
        ):
            # Should NOT raise exception
            scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_db_error_does_not_propagate(
        self, mock_env_enabled, mock_devices_response, mock_weather_data
    ):
        """Database errors are caught and don't propagate."""
        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = mock_weather_data

        with patch(
            "weather_app.scheduler.scheduler.AmbientWeatherAPI", return_value=mock_api
        ):
            with patch(
                "weather_app.scheduler.scheduler.WeatherDatabase"
            ) as mock_db_class:
                mock_db_class.return_value.__enter__.side_effect = Exception("DB Error")

                # Should NOT raise exception
                scheduler.fetch_weather_job()

    @pytest.mark.unit
    def test_fetch_job_uses_configured_device(
        self, mock_env_enabled, temp_db_path, mock_weather_data
    ):
        """Uses configured device MAC when available."""
        devices = [
            {"macAddress": "WRONG:DEVICE", "info": {"name": "Wrong Device"}},
            {"macAddress": "CONFIGURED:MAC", "info": {"name": "Configured Device"}},
        ]

        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = devices
        mock_api.get_device_data.return_value = mock_weather_data

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ):
                with patch(
                    "weather_app.scheduler.scheduler.AMBIENT_DEVICE_MAC",
                    "CONFIGURED:MAC",
                ):
                    scheduler.fetch_weather_job()

        # Should have used the configured device
        mock_api.get_device_data.assert_called_once()
        call_args = mock_api.get_device_data.call_args
        assert call_args[0][0] == "CONFIGURED:MAC"

    @pytest.mark.unit
    def test_fetch_job_uses_first_device_when_no_config(
        self, mock_env_enabled, temp_db_path, mock_weather_data
    ):
        """Uses first device when no device configured."""
        devices = [
            {"macAddress": "FIRST:DEVICE", "info": {"name": "First Device"}},
            {"macAddress": "SECOND:DEVICE", "info": {"name": "Second Device"}},
        ]

        scheduler = WeatherScheduler()

        mock_api = MagicMock()
        mock_api.get_devices.return_value = devices
        mock_api.get_device_data.return_value = mock_weather_data

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ):
                with patch("weather_app.scheduler.scheduler.AMBIENT_DEVICE_MAC", None):
                    scheduler.fetch_weather_job()

        # Should have used the first device
        mock_api.get_device_data.assert_called_once()
        call_args = mock_api.get_device_data.call_args
        assert call_args[0][0] == "FIRST:DEVICE"

    @pytest.mark.unit
    def test_get_status_when_disabled(self, mock_env_disabled):
        """Status shows disabled state when scheduler disabled."""
        scheduler = WeatherScheduler()

        status = scheduler.get_status()

        assert status["enabled"] is False
        assert status["running"] is False
        assert "disabled" in status["message"].lower()

    @pytest.mark.unit
    def test_shutdown_when_disabled(self, mock_env_disabled):
        """Shutdown returns early if scheduler disabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "shutdown") as mock_shutdown:
            scheduler.shutdown()

        # Should not have called shutdown on the underlying scheduler
        mock_shutdown.assert_not_called()

    @pytest.mark.unit
    def test_start_when_disabled(self, mock_env_disabled):
        """Start returns early if scheduler disabled."""
        scheduler = WeatherScheduler()

        with patch.object(scheduler.scheduler, "add_job") as mock_add:
            with patch.object(scheduler.scheduler, "start") as mock_start:
                scheduler.start()

        mock_add.assert_not_called()
        mock_start.assert_not_called()

    @pytest.mark.unit
    def test_init_with_api_queue(self, mock_env_enabled):
        """Scheduler accepts and stores api_queue parameter."""
        mock_queue = MagicMock()

        scheduler = WeatherScheduler(api_queue=mock_queue)

        assert scheduler.api_queue is mock_queue

    @pytest.mark.unit
    def test_fetch_job_uses_api_queue(
        self, mock_env_enabled, temp_db_path, mock_devices_response, mock_weather_data
    ):
        """Fetch job passes api_queue to AmbientWeatherAPI."""
        mock_queue = MagicMock()
        scheduler = WeatherScheduler(api_queue=mock_queue)

        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = mock_weather_data

        with patch("weather_app.scheduler.scheduler.DB_PATH", temp_db_path):
            with patch(
                "weather_app.scheduler.scheduler.AmbientWeatherAPI",
                return_value=mock_api,
            ) as mock_api_class:
                scheduler.fetch_weather_job()

        # Verify AmbientWeatherAPI was called with the queue
        mock_api_class.assert_called_once()
        call_kwargs = mock_api_class.call_args
        assert call_kwargs[1]["request_queue"] is mock_queue
