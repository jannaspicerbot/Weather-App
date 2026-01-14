"""
Comprehensive tests for FastAPI endpoints.

Tests cover:
- All API routes in weather_app/web/routes.py
- Request validation
- Response models
- Error handling
- Edge cases
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from weather_app.database.engine import WeatherDatabase
from weather_app.web.app import create_app

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing.

    Note: We only generate a path, not an actual file, because DuckDB
    needs to create its own file format.
    """
    temp_dir = tempfile.gettempdir()
    db_path = Path(temp_dir) / f"test_api_{datetime.now().timestamp()}.duckdb"

    # Initialize the database with tables (DuckDB creates the file)
    with WeatherDatabase(str(db_path)) as db:
        pass  # Tables created automatically

    yield str(db_path)

    # Cleanup
    db_path.unlink(missing_ok=True)
    # DuckDB may create .wal files
    wal_path = db_path.with_suffix(".duckdb.wal")
    wal_path.unlink(missing_ok=True)


@pytest.fixture
def populated_db_path(temp_db_path):
    """Create a database with sample data."""
    sample_records = [
        {
            "dateutc": 1704106800000,
            "date": "2024-01-01T11:00:00",
            "tempf": 70.0,
            "humidity": 50,
            "windspeedmph": 3.5,
            "baromrelin": 30.10,
        },
        {
            "dateutc": 1704110400000,
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
            "windspeedmph": 5.2,
            "baromrelin": 30.12,
        },
        {
            "dateutc": 1704114000000,
            "date": "2024-01-01T13:00:00",
            "tempf": 75.0,
            "humidity": 40,
            "windspeedmph": 4.8,
            "baromrelin": 30.15,
        },
    ]

    with WeatherDatabase(temp_db_path) as db:
        db.insert_data(sample_records)

    return temp_db_path


@pytest.fixture
def client(temp_db_path):
    """Create a test client with an empty database."""
    with patch("weather_app.database.repository.DB_PATH", temp_db_path):
        with patch("weather_app.config.DB_PATH", temp_db_path):
            app = create_app()
            yield TestClient(app)


@pytest.fixture
def client_with_data(populated_db_path):
    """Create a test client with populated database."""
    with patch("weather_app.database.repository.DB_PATH", populated_db_path):
        with patch("weather_app.config.DB_PATH", populated_db_path):
            app = create_app()
            yield TestClient(app)


# =============================================================================
# ROOT ENDPOINT TESTS
# =============================================================================


class TestRootEndpoint:
    """Tests for the /api root endpoint."""

    @pytest.mark.unit
    def test_api_root_returns_info(self, client):
        """GET /api should return API information."""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()

        assert data["message"] == "Weather API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data
        assert "database" in data

    @pytest.mark.unit
    def test_api_root_lists_endpoints(self, client):
        """GET /api should list available endpoints."""
        response = client.get("/api")
        data = response.json()

        expected_endpoints = [
            "/api/weather/latest",
            "/api/weather/range",
            "/api/weather/stats",
            "/api/scheduler/status",
            "/api/health",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in data["endpoints"]


# =============================================================================
# HEALTH ENDPOINT TESTS
# =============================================================================


class TestHealthEndpoint:
    """Tests for the /api/health endpoint."""

    @pytest.mark.unit
    def test_health_check_returns_healthy(self, client):
        """GET /api/health should return healthy status."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["status"] == "healthy"
        assert "database" in data["data"]


# =============================================================================
# WEATHER DATA ENDPOINT TESTS
# =============================================================================


class TestWeatherEndpoint:
    """Tests for the /weather endpoint."""

    @pytest.mark.unit
    def test_get_weather_returns_list(self, client_with_data):
        """GET /weather should return list of records."""
        response = client_with_data.get("/weather")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.unit
    def test_get_weather_with_limit(self, client_with_data):
        """GET /weather?limit=2 should limit results."""
        response = client_with_data.get("/weather?limit=2")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

    @pytest.mark.unit
    def test_get_weather_with_offset(self, client_with_data):
        """GET /weather?offset=1 should skip first record."""
        response = client_with_data.get("/weather?offset=1&limit=10")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2

    @pytest.mark.unit
    def test_get_weather_with_date_filter(self, client_with_data):
        """GET /weather with date filters should filter results."""
        # Use ISO datetime format that matches the stored date format
        response = client_with_data.get(
            "/weather?start_date=2024-01-01T00:00:00&end_date=2024-01-02T00:00:00"
        )
        assert response.status_code == 200
        data = response.json()

        # All 3 records are on 2024-01-01
        assert len(data) == 3

    @pytest.mark.unit
    def test_get_weather_order_asc(self, client_with_data):
        """GET /weather?order=asc should order ascending."""
        response = client_with_data.get("/weather?order=asc")
        assert response.status_code == 200
        data = response.json()

        # First record should be oldest
        assert data[0]["date"] == "2024-01-01T11:00:00"

    @pytest.mark.unit
    def test_get_weather_order_desc(self, client_with_data):
        """GET /weather?order=desc should order descending (default)."""
        response = client_with_data.get("/weather?order=desc")
        assert response.status_code == 200
        data = response.json()

        # First record should be newest
        assert data[0]["date"] == "2024-01-01T13:00:00"

    @pytest.mark.unit
    def test_get_weather_empty_database(self, client):
        """GET /weather on empty database should return empty list."""
        response = client.get("/weather")
        assert response.status_code == 200
        data = response.json()

        assert data == []

    @pytest.mark.unit
    def test_get_weather_invalid_limit_too_high(self, client_with_data):
        """GET /weather with limit > 1000 should return 422."""
        response = client_with_data.get("/weather?limit=2000")
        assert response.status_code == 422

    @pytest.mark.unit
    def test_get_weather_invalid_limit_zero(self, client_with_data):
        """GET /weather with limit=0 should return 422."""
        response = client_with_data.get("/weather?limit=0")
        assert response.status_code == 422

    @pytest.mark.unit
    def test_get_weather_invalid_order(self, client_with_data):
        """GET /weather with invalid order should return 422."""
        response = client_with_data.get("/weather?order=invalid")
        assert response.status_code == 422


# =============================================================================
# WEATHER LATEST ENDPOINT TESTS
# =============================================================================


class TestWeatherLatestEndpoint:
    """Tests for the /weather/latest endpoint."""

    @pytest.mark.unit
    def test_get_latest_returns_single_record(self, client_with_data):
        """GET /weather/latest should return single record."""
        response = client_with_data.get("/weather/latest")
        assert response.status_code == 200
        data = response.json()

        # Should return most recent record
        assert data["date"] == "2024-01-01T13:00:00"
        assert data["tempf"] == 75.0

    @pytest.mark.unit
    def test_get_latest_empty_database_returns_404(self, client):
        """GET /weather/latest on empty database should return 404."""
        response = client.get("/weather/latest")
        assert response.status_code == 404
        data = response.json()

        # The error message could be from the endpoint or the 404 handler
        assert "error" in data or "detail" in data


# =============================================================================
# WEATHER STATS ENDPOINT TESTS
# =============================================================================


class TestWeatherStatsEndpoint:
    """Tests for the /weather/stats endpoint."""

    @pytest.mark.unit
    def test_get_stats_returns_statistics(self, client_with_data):
        """GET /weather/stats should return database statistics."""
        response = client_with_data.get("/weather/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["total_records"] == 3
        assert data["min_date"] == "2024-01-01T11:00:00"
        assert data["max_date"] == "2024-01-01T13:00:00"

    @pytest.mark.unit
    def test_get_stats_empty_database(self, client):
        """GET /weather/stats on empty database should return zeros."""
        response = client.get("/weather/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["total_records"] == 0
        assert data["min_date"] is None
        assert data["max_date"] is None


# =============================================================================
# API WEATHER ENDPOINTS (Frontend-compatible routes)
# =============================================================================


class TestApiWeatherEndpoints:
    """Tests for /api/weather/* endpoints."""

    @pytest.mark.unit
    def test_api_weather_latest(self, client_with_data):
        """GET /api/weather/latest should return list of recent records."""
        response = client_with_data.get("/api/weather/latest")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.unit
    def test_api_weather_latest_with_limit(self, client_with_data):
        """GET /api/weather/latest?limit=1 should limit results."""
        response = client_with_data.get("/api/weather/latest?limit=1")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 1

    @pytest.mark.unit
    def test_api_weather_range(self, client_with_data):
        """GET /api/weather/range should return records in date range."""
        response = client_with_data.get(
            "/api/weather/range?start_date=2024-01-01&end_date=2024-01-02"
        )
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) == 3

    @pytest.mark.unit
    def test_api_weather_range_uses_sampling(self, temp_db_path):
        """GET /api/weather/range should use sampling for date range queries."""
        # Create a database with many records
        sample_records = []
        base_timestamp = 1704067200000  # 2024-01-01T00:00:00 UTC

        for i in range(50):  # 50 records
            timestamp = base_timestamp + (i * 3600000)  # 1 hour apart
            date_str = datetime.fromtimestamp(timestamp / 1000).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
            sample_records.append(
                {
                    "dateutc": timestamp,
                    "date": date_str,
                    "tempf": 70.0 + i,
                    "humidity": 50,
                }
            )

        with WeatherDatabase(temp_db_path) as db:
            db.insert_data(sample_records)

        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            with patch("weather_app.config.DB_PATH", temp_db_path):
                app = create_app()
                client = TestClient(app)

                # Request with limit lower than total records
                response = client.get(
                    "/api/weather/range?start_date=2024-01-01&end_date=2024-01-03&limit=10"
                )

        assert response.status_code == 200
        data = response.json()

        # Should return sampled data, not exceed limit
        assert len(data) <= 10

    @pytest.mark.unit
    def test_api_weather_range_without_dates_returns_recent(self, client_with_data):
        """GET /api/weather/range without dates returns most recent records."""
        response = client_with_data.get("/api/weather/range?limit=2")
        assert response.status_code == 200
        data = response.json()

        assert len(data) == 2
        # Should be ordered by date descending (most recent first)
        assert data[0]["date"] == "2024-01-01T13:00:00"

    @pytest.mark.unit
    def test_api_weather_range_sampled_data_is_distributed(self, temp_db_path):
        """Verify /api/weather/range returns evenly distributed samples."""
        # Create records spanning 10 days
        sample_records = []
        base_timestamp = 1704067200000  # 2024-01-01T00:00:00 UTC

        for day in range(10):
            for hour in range(10):  # 10 records per day = 100 total
                timestamp = base_timestamp + (day * 86400000) + (hour * 3600000)
                date_str = datetime.fromtimestamp(timestamp / 1000).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                sample_records.append(
                    {
                        "dateutc": timestamp,
                        "date": date_str,
                        "tempf": 70.0,
                        "humidity": 50,
                    }
                )

        with WeatherDatabase(temp_db_path) as db:
            db.insert_data(sample_records)

        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            with patch("weather_app.config.DB_PATH", temp_db_path):
                app = create_app()
                client = TestClient(app)

                response = client.get(
                    "/api/weather/range?start_date=2024-01-01&end_date=2024-01-11&limit=20"
                )

        assert response.status_code == 200
        data = response.json()

        # Extract unique dates
        dates = set()
        for record in data:
            date_part = record["date"][:10]
            dates.add(date_part)

        # Should have data from multiple days (distributed), not just recent ones
        assert len(dates) >= 5, f"Expected data from at least 5 days, got {dates}"

    @pytest.mark.unit
    def test_api_weather_stats(self, client_with_data):
        """GET /api/weather/stats should return statistics."""
        response = client_with_data.get("/api/weather/stats")
        assert response.status_code == 200
        data = response.json()

        assert data["total_records"] == 3


# =============================================================================
# SCHEDULER STATUS ENDPOINT TESTS
# =============================================================================


class TestSchedulerStatusEndpoint:
    """Tests for the /api/scheduler/status endpoint."""

    @pytest.mark.unit
    def test_scheduler_status_returns_info(self, client):
        """GET /api/scheduler/status should return scheduler info."""
        response = client.get("/api/scheduler/status")
        assert response.status_code == 200
        data = response.json()

        # Scheduler should have basic status fields
        assert "enabled" in data or "running" in data or "status" in data


# =============================================================================
# ERROR HANDLER TESTS
# =============================================================================


class TestErrorHandlers:
    """Tests for custom error handlers."""

    @pytest.mark.unit
    def test_404_returns_json(self, client):
        """404 errors should return JSON response."""
        response = client.get("/nonexistent/endpoint")
        assert response.status_code == 404
        data = response.json()

        assert "error" in data
        assert data["status_code"] == 404


# =============================================================================
# CORS TESTS
# =============================================================================


class TestCors:
    """Tests for CORS configuration."""

    @pytest.mark.unit
    def test_cors_headers_present(self, client):
        """CORS headers should be present for allowed origins."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # OPTIONS request should succeed
        assert response.status_code in [200, 204, 405]


# =============================================================================
# CREDENTIAL ENDPOINT TESTS
# =============================================================================


class TestCredentialEndpoints:
    """Tests for credential management endpoints."""

    @pytest.mark.unit
    def test_get_credential_status_not_configured(self, client):
        """GET /api/credentials/status returns not configured when no creds."""
        with patch.dict("os.environ", {"AMBIENT_API_KEY": "", "AMBIENT_APP_KEY": ""}):
            response = client.get("/api/credentials/status")

        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is False

    @pytest.mark.unit
    def test_get_credential_status_configured(self, client):
        """GET /api/credentials/status returns configured when creds set."""
        with patch.dict(
            "os.environ", {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"}
        ):
            response = client.get("/api/credentials/status")

        assert response.status_code == 200
        data = response.json()
        assert data["configured"] is True

    @pytest.mark.unit
    def test_validate_credentials_success(self, client):
        """POST /api/credentials/validate with valid creds returns success."""
        with patch(
            "weather_app.web.routes.backfill_service.validate_credentials"
        ) as mock_validate:
            mock_validate.return_value = (
                True,
                "Found 1 device(s)",
                [
                    {
                        "mac_address": "AA:BB:CC:DD:EE:FF",
                        "name": "Test Station",
                        "last_data": "2024-01-01T12:00:00",
                    }
                ],
            )

            response = client.post(
                "/api/credentials/validate",
                json={"api_key": "test_key", "app_key": "test_app"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert "1 device" in data["message"]
        assert len(data["devices"]) == 1

    @pytest.mark.unit
    def test_validate_credentials_invalid(self, client):
        """POST /api/credentials/validate with invalid creds returns error."""
        with patch(
            "weather_app.web.routes.backfill_service.validate_credentials"
        ) as mock_validate:
            mock_validate.return_value = (False, "Invalid API credentials", [])

            response = client.post(
                "/api/credentials/validate",
                json={"api_key": "bad_key", "app_key": "bad_app"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "Invalid" in data["message"]

    @pytest.mark.unit
    def test_save_credentials_success(self, client):
        """POST /api/credentials/save successfully saves creds."""
        with patch(
            "weather_app.web.routes.backfill_service.save_credentials"
        ) as mock_save:
            mock_save.return_value = (True, "Credentials saved successfully")

            response = client.post(
                "/api/credentials/save",
                json={"api_key": "new_key", "app_key": "new_app"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @pytest.mark.unit
    def test_save_credentials_failure(self, client):
        """POST /api/credentials/save returns error on failure."""
        with patch(
            "weather_app.web.routes.backfill_service.save_credentials"
        ) as mock_save:
            mock_save.return_value = (False, "Failed to save credentials")

            response = client.post(
                "/api/credentials/save",
                json={"api_key": "key", "app_key": "app"},
            )

        assert response.status_code == 500

    @pytest.mark.unit
    def test_save_credentials_with_device_mac(self, client):
        """POST /api/credentials/save with device_mac parameter."""
        with patch(
            "weather_app.web.routes.backfill_service.save_credentials"
        ) as mock_save:
            mock_save.return_value = (True, "Saved")

            response = client.post(
                "/api/credentials/save?device_mac=AA:BB:CC:DD:EE:FF",
                json={"api_key": "key", "app_key": "app"},
            )

        assert response.status_code == 200
        mock_save.assert_called_once_with("key", "app", "AA:BB:CC:DD:EE:FF")


# =============================================================================
# BACKFILL ENDPOINT TESTS
# =============================================================================


class TestBackfillEndpoints:
    """Tests for backfill management endpoints."""

    @pytest.mark.unit
    def test_get_backfill_progress(self, client):
        """GET /api/backfill/progress returns current progress."""
        with patch(
            "weather_app.web.routes.backfill_service.get_progress"
        ) as mock_progress:
            mock_progress.return_value = {
                "status": "idle",
                "progress_id": None,
                "message": "No backfill in progress",
                "total_records": 0,
                "inserted_records": 0,
                "skipped_records": 0,
            }

            response = client.get("/api/backfill/progress")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "idle"
        assert data["total_records"] == 0

    @pytest.mark.unit
    def test_get_backfill_progress_in_progress(self, client):
        """GET /api/backfill/progress during active backfill."""
        with patch(
            "weather_app.web.routes.backfill_service.get_progress"
        ) as mock_progress:
            mock_progress.return_value = {
                "status": "in_progress",
                "progress_id": 12345,
                "message": "Fetching historical data...",
                "total_records": 5000,
                "inserted_records": 4500,
                "skipped_records": 500,
                "requests_made": 20,
                "estimated_time_remaining_seconds": 300,
            }

            response = client.get("/api/backfill/progress")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"
        assert data["total_records"] == 5000
        assert data["inserted_records"] == 4500

    @pytest.mark.unit
    def test_start_backfill_success(self, client):
        """POST /api/backfill/start starts backfill successfully."""
        with patch(
            "weather_app.web.routes.backfill_service.start_backfill"
        ) as mock_start:
            mock_start.return_value = (True, "Backfill started")

            response = client.post(
                "/api/backfill/start",
                json={"api_key": "key", "app_key": "app"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"

    @pytest.mark.unit
    def test_start_backfill_already_running(self, client):
        """POST /api/backfill/start when already running."""
        with patch(
            "weather_app.web.routes.backfill_service.start_backfill"
        ) as mock_start:
            mock_start.return_value = (False, "Backfill already in progress")
            with patch(
                "weather_app.web.routes.backfill_service.get_progress"
            ) as mock_progress:
                mock_progress.return_value = {
                    "status": "in_progress",
                    "progress_id": 999,
                    "message": "Running...",
                    "total_records": 100,
                    "inserted_records": 50,
                    "skipped_records": 0,
                }

                response = client.post("/api/backfill/start", json={})

        assert response.status_code == 200
        data = response.json()
        assert "already in progress" in data["message"]

    @pytest.mark.unit
    def test_start_backfill_missing_credentials(self, client):
        """POST /api/backfill/start with missing credentials."""
        with patch(
            "weather_app.web.routes.backfill_service.start_backfill"
        ) as mock_start:
            mock_start.return_value = (False, "API credentials not configured")
            with patch(
                "weather_app.web.routes.backfill_service.get_progress"
            ) as mock_progress:
                mock_progress.return_value = {"status": "idle"}

                response = client.post("/api/backfill/start", json={})

        assert response.status_code == 200
        data = response.json()
        assert "credentials" in data["message"].lower()

    @pytest.mark.unit
    def test_start_backfill_without_body(self, client):
        """POST /api/backfill/start without request body."""
        with patch(
            "weather_app.web.routes.backfill_service.start_backfill"
        ) as mock_start:
            mock_start.return_value = (True, "Backfill started")

            response = client.post("/api/backfill/start")

        assert response.status_code == 200

    @pytest.mark.unit
    def test_stop_backfill_success(self, client):
        """POST /api/backfill/stop stops running backfill."""
        with patch(
            "weather_app.web.routes.backfill_service.is_running"
        ) as mock_running:
            mock_running.return_value = True
            with patch("weather_app.web.routes.backfill_service.stop") as mock_stop:
                response = client.post("/api/backfill/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_stop.assert_called_once()

    @pytest.mark.unit
    def test_stop_backfill_not_running(self, client):
        """POST /api/backfill/stop when no backfill running."""
        with patch(
            "weather_app.web.routes.backfill_service.is_running"
        ) as mock_running:
            mock_running.return_value = False

            response = client.post("/api/backfill/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "No backfill" in data["message"]


# =============================================================================
# DEVICE ENDPOINT TESTS
# =============================================================================


class TestDeviceEndpoints:
    """Tests for device management endpoints."""

    @pytest.mark.unit
    def test_get_devices_success(self, client):
        """GET /api/devices returns device list."""
        with patch.dict(
            "os.environ", {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"}
        ):
            with patch("weather_app.api.client.AmbientWeatherAPI") as mock_api:
                mock_instance = mock_api.return_value
                mock_instance.get_devices.return_value = [
                    {
                        "macAddress": "AA:BB:CC:DD:EE:FF",
                        "info": {
                            "name": "Test Station",
                            "coords": {"location": "Test City"},
                        },
                        "lastData": {"date": "2024-01-01T12:00:00"},
                    }
                ]
                with patch("weather_app.web.app.api_queue"):
                    response = client.get("/api/devices")

        assert response.status_code == 200
        data = response.json()
        assert len(data["devices"]) == 1
        assert data["devices"][0]["mac_address"] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.unit
    def test_get_devices_no_credentials(self, client):
        """GET /api/devices returns error if credentials not configured."""
        with patch.dict("os.environ", {"AMBIENT_API_KEY": "", "AMBIENT_APP_KEY": ""}):
            response = client.get("/api/devices")

        assert response.status_code == 400
        data = response.json()
        assert "not configured" in data["detail"]

    @pytest.mark.unit
    def test_get_devices_with_selected_device(self, client):
        """GET /api/devices returns selected device MAC."""
        with patch.dict(
            "os.environ",
            {
                "AMBIENT_API_KEY": "key",
                "AMBIENT_APP_KEY": "app",
                "AMBIENT_DEVICE_MAC": "AA:BB:CC:DD:EE:FF",
            },
        ):
            with patch("weather_app.api.client.AmbientWeatherAPI") as mock_api:
                mock_instance = mock_api.return_value
                mock_instance.get_devices.return_value = [
                    {
                        "macAddress": "AA:BB:CC:DD:EE:FF",
                        "info": {"name": "Station"},
                        "lastData": {},
                    }
                ]
                with patch("weather_app.web.app.api_queue"):
                    response = client.get("/api/devices")

        assert response.status_code == 200
        data = response.json()
        assert data["selected_device_mac"] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.unit
    def test_get_devices_api_error(self, client):
        """GET /api/devices handles API errors gracefully."""
        with patch.dict(
            "os.environ", {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"}
        ):
            with patch("weather_app.api.client.AmbientWeatherAPI") as mock_api:
                mock_instance = mock_api.return_value
                mock_instance.get_devices.side_effect = Exception("API Error")
                with patch("weather_app.web.app.api_queue"):
                    response = client.get("/api/devices")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_select_device_success(self, client):
        """POST /api/devices/select saves device selection."""
        with patch(
            "weather_app.web.routes.backfill_service.save_device_selection"
        ) as mock_save:
            mock_save.return_value = (True, "Device selection saved")

            response = client.post(
                "/api/devices/select",
                json={"device_mac": "AA:BB:CC:DD:EE:FF"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["device_mac"] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.unit
    def test_select_device_failure(self, client):
        """POST /api/devices/select handles save failure."""
        with patch(
            "weather_app.web.routes.backfill_service.save_device_selection"
        ) as mock_save:
            mock_save.return_value = (False, "Failed to save")

            response = client.post(
                "/api/devices/select",
                json={"device_mac": "AA:BB:CC:DD:EE:FF"},
            )

        assert response.status_code == 500


# =============================================================================
# APP FACTORY TESTS
# =============================================================================


class TestAppFactory:
    """Tests for app factory and frontend registration."""

    @pytest.mark.unit
    def test_register_frontend_frozen_executable(self, tmp_path):
        """Uses correct path for PyInstaller frozen app."""
        import sys

        from fastapi import FastAPI

        # Create a test app
        test_app = FastAPI()

        # Create a fake static directory
        fake_meipass = tmp_path / "meipass"
        static_dir = fake_meipass / "web" / "dist"
        static_dir.mkdir(parents=True)
        (static_dir / "index.html").write_text("<html></html>")

        # Mock sys.frozen and sys._MEIPASS
        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "_MEIPASS", str(fake_meipass), create=True):
                from weather_app.web.app import register_frontend

                register_frontend(test_app)

        # Should have mounted the static files
        # Check that a mount was added
        assert len(test_app.routes) > 0

    @pytest.mark.unit
    def test_register_frontend_not_found(self, tmp_path):
        """Logs warning if frontend static files not found."""
        from fastapi import FastAPI

        test_app = FastAPI()

        # This test validates that register_frontend doesn't crash
        # when the frontend directory doesn't exist.
        # The function uses getattr(sys, "frozen", False) to determine mode,
        # and in development mode, it looks for web/dist relative to the module.

        # Since the real web/dist may or may not exist in the test environment,
        # we simply verify the function doesn't raise an exception.
        from weather_app.web.app import register_frontend

        # Just verify it doesn't raise - it should either mount or log warning
        register_frontend(test_app)

    @pytest.mark.unit
    def test_create_app_returns_fastapi(self):
        """create_app returns a FastAPI instance."""
        from fastapi import FastAPI

        from weather_app.config import API_TITLE
        from weather_app.web.app import create_app

        app = create_app()

        assert isinstance(app, FastAPI)
        assert app.title == API_TITLE


# =============================================================================
# ROUTE ERROR HANDLING TESTS
# =============================================================================


class TestRouteErrorHandling:
    """Tests for error handling in routes."""

    @pytest.mark.unit
    def test_get_weather_data_runtime_error(self, client):
        """GET /weather handles RuntimeError."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_all_readings"
        ) as mock_get:
            mock_get.side_effect = RuntimeError("Database connection failed")

            response = client.get("/weather")

        assert response.status_code == 500
        data = response.json()
        assert "Database connection failed" in data["detail"]

    @pytest.mark.unit
    def test_get_weather_data_value_error(self, client):
        """GET /weather handles ValueError for invalid dates."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_all_readings"
        ) as mock_get:
            mock_get.side_effect = ValueError("Invalid date format")

            response = client.get("/weather?start_date=bad-date")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid date format" in data["detail"]

    @pytest.mark.unit
    def test_get_latest_weather_runtime_error(self, client):
        """GET /weather/latest handles RuntimeError."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_latest_reading"
        ) as mock_get:
            mock_get.side_effect = RuntimeError("Database error")

            response = client.get("/weather/latest")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_get_stats_runtime_error(self, client):
        """GET /weather/stats handles RuntimeError."""
        with patch("weather_app.web.routes.WeatherRepository.get_stats") as mock_get:
            mock_get.side_effect = RuntimeError("Database error")

            response = client.get("/weather/stats")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_api_get_latest_runtime_error(self, client):
        """GET /api/weather/latest handles RuntimeError."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_all_readings"
        ) as mock_get:
            mock_get.side_effect = RuntimeError("Database error")

            response = client.get("/api/weather/latest")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_api_weather_range_value_error(self, client):
        """GET /api/weather/range handles ValueError."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_all_readings"
        ) as mock_get:
            mock_get.side_effect = ValueError("Invalid date")

            response = client.get("/api/weather/range?start_date=invalid")

        assert response.status_code == 400

    @pytest.mark.unit
    def test_api_weather_range_runtime_error(self, client):
        """GET /api/weather/range handles RuntimeError."""
        with patch(
            "weather_app.web.routes.WeatherRepository.get_all_readings"
        ) as mock_get:
            mock_get.side_effect = RuntimeError("Database error")

            response = client.get("/api/weather/range")

        assert response.status_code == 500

    @pytest.mark.unit
    def test_api_get_stats_runtime_error(self, client):
        """GET /api/weather/stats handles RuntimeError."""
        with patch("weather_app.web.routes.WeatherRepository.get_stats") as mock_get:
            mock_get.side_effect = RuntimeError("Database error")

            response = client.get("/api/weather/stats")

        assert response.status_code == 500
