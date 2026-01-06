"""Shared test fixtures for pytest.

This module provides common fixtures used across multiple test files.
"""

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from dotenv import load_dotenv

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
