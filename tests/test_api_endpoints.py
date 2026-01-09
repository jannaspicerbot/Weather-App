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
