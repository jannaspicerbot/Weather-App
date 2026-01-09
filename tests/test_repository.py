"""
Comprehensive tests for the WeatherRepository static methods.

Tests cover:
- get_all_readings with various filters
- get_latest_reading
- get_stats
- Error handling and edge cases
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from weather_app.database.engine import WeatherDatabase
from weather_app.database.repository import WeatherRepository

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_db_path():
    """Create a temporary database path for testing."""
    temp_dir = tempfile.gettempdir()
    db_path = Path(temp_dir) / f"test_repo_{datetime.now().timestamp()}.duckdb"

    # Initialize database
    with WeatherDatabase(str(db_path)) as db:
        pass

    yield str(db_path)

    # Cleanup
    db_path.unlink(missing_ok=True)
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
        },
        {
            "dateutc": 1704110400000,
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
        },
        {
            "dateutc": 1704114000000,
            "date": "2024-01-01T13:00:00",
            "tempf": 75.0,
            "humidity": 40,
        },
        {
            "dateutc": 1704200400000,
            "date": "2024-01-02T13:00:00",
            "tempf": 68.0,
            "humidity": 55,
        },
        {
            "dateutc": 1704286800000,
            "date": "2024-01-03T13:00:00",
            "tempf": 65.0,
            "humidity": 60,
        },
    ]

    with WeatherDatabase(temp_db_path) as db:
        db.insert_data(sample_records)

    return temp_db_path


# =============================================================================
# GET_ALL_READINGS TESTS
# =============================================================================


class TestGetAllReadings:
    """Tests for WeatherRepository.get_all_readings()."""

    @pytest.mark.unit
    def test_get_all_readings_default(self, populated_db_path):
        """Should return all records with default parameters."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings()

        assert len(results) == 5
        # Default order is desc (newest first)
        assert results[0]["date"] == "2024-01-03T13:00:00"

    @pytest.mark.unit
    def test_get_all_readings_with_limit(self, populated_db_path):
        """Should respect limit parameter."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(limit=2)

        assert len(results) == 2

    @pytest.mark.unit
    def test_get_all_readings_with_offset(self, populated_db_path):
        """Should respect offset parameter for pagination."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(limit=2, offset=2)

        assert len(results) == 2
        # After skipping 2, should get the 3rd and 4th records (by date desc)

    @pytest.mark.unit
    def test_get_all_readings_order_asc(self, populated_db_path):
        """Should order by date ascending."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(order="asc")

        assert len(results) == 5
        assert results[0]["date"] == "2024-01-01T11:00:00"
        assert results[-1]["date"] == "2024-01-03T13:00:00"

    @pytest.mark.unit
    def test_get_all_readings_order_desc(self, populated_db_path):
        """Should order by date descending."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(order="desc")

        assert len(results) == 5
        assert results[0]["date"] == "2024-01-03T13:00:00"
        assert results[-1]["date"] == "2024-01-01T11:00:00"

    @pytest.mark.unit
    def test_get_all_readings_with_start_date(self, populated_db_path):
        """Should filter by start date."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(
                start_date="2024-01-02T00:00:00"
            )

        assert len(results) == 2
        # Should only include Jan 2 and Jan 3 records

    @pytest.mark.unit
    def test_get_all_readings_with_end_date(self, populated_db_path):
        """Should filter by end date."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(end_date="2024-01-01T23:59:59")

        assert len(results) == 3
        # Should only include Jan 1 records

    @pytest.mark.unit
    def test_get_all_readings_with_date_range(self, populated_db_path):
        """Should filter by date range."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(
                start_date="2024-01-01T12:00:00", end_date="2024-01-02T13:00:00"
            )

        # Should include: 12:00, 13:00 on Jan 1, and 13:00 on Jan 2
        assert len(results) == 3

    @pytest.mark.unit
    def test_get_all_readings_invalid_start_date(self, populated_db_path):
        """Should raise ValueError for invalid start date format."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            with pytest.raises(RuntimeError) as exc_info:
                WeatherRepository.get_all_readings(start_date="invalid-date")

        assert "Invalid start_date format" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_all_readings_invalid_end_date(self, populated_db_path):
        """Should raise ValueError for invalid end date format."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            with pytest.raises(RuntimeError) as exc_info:
                WeatherRepository.get_all_readings(end_date="01/02/2024")

        assert "Invalid end_date format" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_all_readings_empty_database(self, temp_db_path):
        """Should return empty list for empty database."""
        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            results = WeatherRepository.get_all_readings()

        assert results == []

    @pytest.mark.unit
    def test_get_all_readings_returns_dictionaries(self, populated_db_path):
        """Results should be dictionaries with correct keys."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            results = WeatherRepository.get_all_readings(limit=1)

        assert len(results) == 1
        record = results[0]
        assert isinstance(record, dict)
        assert "date" in record
        assert "tempf" in record
        assert "humidity" in record


# =============================================================================
# GET_LATEST_READING TESTS
# =============================================================================


class TestGetLatestReading:
    """Tests for WeatherRepository.get_latest_reading()."""

    @pytest.mark.unit
    def test_get_latest_reading_returns_most_recent(self, populated_db_path):
        """Should return the most recent record."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            result = WeatherRepository.get_latest_reading()

        assert result is not None
        assert result["date"] == "2024-01-03T13:00:00"
        assert result["tempf"] == 65.0

    @pytest.mark.unit
    def test_get_latest_reading_empty_database(self, temp_db_path):
        """Should return None for empty database."""
        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            result = WeatherRepository.get_latest_reading()

        assert result is None

    @pytest.mark.unit
    def test_get_latest_reading_returns_dictionary(self, populated_db_path):
        """Result should be a dictionary with correct keys."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            result = WeatherRepository.get_latest_reading()

        assert isinstance(result, dict)
        assert "date" in result
        assert "dateutc" in result
        assert "tempf" in result


# =============================================================================
# GET_STATS TESTS
# =============================================================================


class TestGetStats:
    """Tests for WeatherRepository.get_stats()."""

    @pytest.mark.unit
    def test_get_stats_with_data(self, populated_db_path):
        """Should return correct statistics."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            stats = WeatherRepository.get_stats()

        assert stats["total_records"] == 5
        assert stats["min_date"] == "2024-01-01T11:00:00"
        assert stats["max_date"] == "2024-01-03T13:00:00"
        assert stats["date_range_days"] == 2

    @pytest.mark.unit
    def test_get_stats_empty_database(self, temp_db_path):
        """Should return zeros/nulls for empty database."""
        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            stats = WeatherRepository.get_stats()

        assert stats["total_records"] == 0
        assert stats["min_date"] is None
        assert stats["max_date"] is None
        assert stats["date_range_days"] is None

    @pytest.mark.unit
    def test_get_stats_single_record(self, temp_db_path):
        """Should handle single record (date range = 0)."""
        with WeatherDatabase(temp_db_path) as db:
            db.insert_data(
                {
                    "dateutc": 1704110400000,
                    "date": "2024-01-01T12:00:00",
                    "tempf": 72.5,
                }
            )

        with patch("weather_app.database.repository.DB_PATH", temp_db_path):
            stats = WeatherRepository.get_stats()

        assert stats["total_records"] == 1
        assert stats["min_date"] == "2024-01-01T12:00:00"
        assert stats["max_date"] == "2024-01-01T12:00:00"
        assert stats["date_range_days"] == 0

    @pytest.mark.unit
    def test_get_stats_returns_all_keys(self, populated_db_path):
        """Stats should contain all expected keys."""
        with patch("weather_app.database.repository.DB_PATH", populated_db_path):
            stats = WeatherRepository.get_stats()

        expected_keys = ["total_records", "min_date", "max_date", "date_range_days"]
        for key in expected_keys:
            assert key in stats


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


class TestRepositoryErrorHandling:
    """Tests for error handling in repository methods."""

    @pytest.mark.unit
    def test_get_all_readings_database_error(self):
        """Should raise RuntimeError on database error."""
        with patch(
            "weather_app.database.repository.DB_PATH", "/nonexistent/path/db.duckdb"
        ):
            with pytest.raises(RuntimeError) as exc_info:
                WeatherRepository.get_all_readings()

        assert "Database error" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_latest_reading_database_error(self):
        """Should raise RuntimeError on database error."""
        with patch(
            "weather_app.database.repository.DB_PATH", "/nonexistent/path/db.duckdb"
        ):
            with pytest.raises(RuntimeError) as exc_info:
                WeatherRepository.get_latest_reading()

        assert "Database error" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_stats_database_error(self):
        """Should raise RuntimeError on database error."""
        with patch(
            "weather_app.database.repository.DB_PATH", "/nonexistent/path/db.duckdb"
        ):
            with pytest.raises(RuntimeError) as exc_info:
                WeatherRepository.get_stats()

        assert "Database error" in str(exc_info.value)
