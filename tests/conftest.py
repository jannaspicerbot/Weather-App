"""Shared test fixtures for pytest.

This module provides common fixtures used across multiple test files.
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from dotenv import load_dotenv
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    pass


@pytest.fixture
def test_db():
    """Create a temporary test database.

    Creates a DuckDB database in a temporary file, initializes it,
    and automatically cleans up after the test.

    Yields:
        WeatherDatabase: Initialized database instance

    Example:
        def test_insert_data(test_db):
            result = test_db.insert_weather_data(data)
            assert result.success
    """
    # Lazy import to avoid import errors when fixture isn't used
    from weather_app.database import WeatherDatabase

    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name

    db = WeatherDatabase(db_path)
    db.initialize()
    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sample_weather_data():
    """Provide sample weather data for tests.

    Returns:
        dict: Weather data with typical fields

    Example:
        def test_process_data(sample_weather_data):
            result = process(sample_weather_data)
            assert result["tempf"] == 72.5
    """
    return {
        "tempf": 72.5,
        "humidity": 45,
        "windspeedmph": 5.2,
        "winddir": 180,
        "baromrelin": 30.12,
        "baromabsin": 29.95,
        "dailyrainin": 0.0,
        "hourlyrainin": 0.0,
        "dewPoint": 50.3,
        "feelsLike": 71.8,
        "date": "2024-01-01T12:00:00",
    }


@pytest.fixture
def sample_weather_data_list():
    """Provide a list of sample weather data for bulk tests.

    Returns:
        list[dict]: List of weather data records

    Example:
        def test_bulk_insert(test_db, sample_weather_data_list):
            result = test_db.bulk_insert(sample_weather_data_list)
            assert result.inserted_count == len(sample_weather_data_list)
    """
    return [
        {
            "tempf": 70.0,
            "humidity": 50,
            "windspeedmph": 3.5,
            "baromrelin": 30.10,
            "date": "2024-01-01T10:00:00",
        },
        {
            "tempf": 72.5,
            "humidity": 45,
            "windspeedmph": 5.2,
            "baromrelin": 30.12,
            "date": "2024-01-01T11:00:00",
        },
        {
            "tempf": 75.0,
            "humidity": 40,
            "windspeedmph": 4.8,
            "baromrelin": 30.15,
            "date": "2024-01-01T12:00:00",
        },
    ]


@pytest.fixture
def api_credentials():
    """Load API credentials from environment.

    Both API key and App key are required for Ambient Weather API.
    These are used together for account and device verification.

    Returns:
        dict: Dictionary with 'api_key' and 'app_key'

    Raises:
        pytest.skip: If credentials are not available

    Example:
        @pytest.mark.requires_api_key
        def test_api_call(api_credentials):
            api = AmbientWeatherAPI(**api_credentials)
            result = api.get_devices()
            assert result is not None
    """
    load_dotenv()

    api_key = os.getenv("AMBIENT_API_KEY")
    app_key = os.getenv("AMBIENT_APP_KEY")

    if not api_key or not app_key:
        pytest.skip(
            "API credentials not available (AMBIENT_API_KEY and AMBIENT_APP_KEY required)"
        )

    return {"api_key": api_key, "app_key": app_key}


@pytest.fixture
def mock_api_response():
    """Provide a mock API response for testing without hitting real API.

    Returns:
        list[dict]: Simulated API response

    Example:
        def test_parse_response(mock_api_response):
            result = parse_api_data(mock_api_response)
            assert len(result) == 2
    """
    return [
        {
            "dateutc": 1704110400000,  # 2024-01-01 12:00:00 UTC
            "tempf": 72.5,
            "humidity": 45,
            "windspeedmph": 5.2,
            "winddir": 180,
            "baromrelin": 30.12,
        },
        {
            "dateutc": 1704114000000,  # 2024-01-01 13:00:00 UTC
            "tempf": 74.0,
            "humidity": 43,
            "windspeedmph": 6.1,
            "winddir": 185,
            "baromrelin": 30.10,
        },
    ]


# =============================================================================
# CLI TEST FIXTURES
# =============================================================================


@pytest.fixture
def cli_runner():
    """Click CLI test runner for command testing."""
    return CliRunner()


@pytest.fixture
def temp_db_dir(tmp_path):
    """Create a temporary directory for database testing."""
    return tmp_path


# =============================================================================
# DEMO MODE FIXTURES
# =============================================================================


@pytest.fixture
def demo_db_path(tmp_path):
    """Create a temporary demo database with sample data.

    Creates a minimal demo database with 1 day of weather data
    for fast test execution.
    """
    from weather_app.demo.data_generator import SeattleWeatherGenerator

    db_path = tmp_path / "demo.duckdb"
    generator = SeattleWeatherGenerator(db_path)

    # Generate 1 day of data starting from yesterday
    start_date = datetime.now() - timedelta(days=1)
    generator.generate(start_date=start_date, days=1, quiet=True)
    generator.close()

    return db_path


@pytest.fixture
def demo_client(tmp_path, demo_db_path):
    """Create a FastAPI test client configured for demo mode.

    Patches both the database path and enables demo mode.
    """
    from weather_app.web.app import create_app

    # Patch the necessary paths for demo mode
    with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
        with patch("weather_app.web.app.DEMO_DB_PATH", demo_db_path):
            # Set demo mode environment variable
            with patch.dict(os.environ, {"DEMO_MODE": "true"}):
                app = create_app()
                yield TestClient(app)


@pytest.fixture
def app_client_isolated(tmp_path):
    """Create a FastAPI test client with isolated config paths.

    Both main DB and demo DB paths point to temp directory.
    Demo mode is disabled by default.
    """
    from weather_app.web.app import create_app

    db_path = tmp_path / "app.duckdb"
    demo_db_path = tmp_path / "demo.duckdb"

    with patch("weather_app.database.repository.DB_PATH", str(db_path)):
        with patch("weather_app.config.DB_PATH", str(db_path)):
            with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
                with patch("weather_app.web.app.DEMO_DB_PATH", demo_db_path):
                    with patch("weather_app.web.routes.DEMO_DB_PATH", demo_db_path):
                        app = create_app()
                        yield TestClient(app)


@pytest.fixture
def mock_demo_service(tmp_path):
    """Create a mock DemoService for testing without actual database.

    Returns a configured mock that simulates DemoService behavior.
    """
    from unittest.mock import MagicMock

    mock_service = MagicMock()
    mock_service.is_available = True
    mock_service.get_latest_reading.return_value = {
        "dateutc": 1704110400000,
        "date": "2024-01-01T12:00:00",
        "tempf": 72.5,
        "humidity": 45,
        "windspeedmph": 5.2,
        "baromrelin": 30.12,
    }
    mock_service.get_all_readings.return_value = [
        {
            "dateutc": 1704110400000,
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
        }
    ]
    mock_service.get_stats.return_value = {
        "total_records": 288,
        "min_date": "2024-01-01T00:00:00",
        "max_date": "2024-01-01T23:55:00",
        "date_range_days": 1,
    }
    mock_service.get_devices.return_value = [
        {
            "mac_address": "DEMO:SEATTLE:01",
            "name": "Seattle Demo Station",
            "location": "Seattle, WA",
        }
    ]
    mock_service.get_sampled_readings.return_value = []

    return mock_service
