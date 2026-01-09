"""
Comprehensive tests for the database layer.

Tests cover:
- WeatherDatabase context manager and table creation
- WeatherRepository query methods
- Data insertion and retrieval
- Edge cases and error handling
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from weather_app.database.engine import WeatherDatabase


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def temp_db():
    """Create a temporary database path for testing.

    Note: We only generate a path, not an actual file, because DuckDB
    needs to create its own file format.
    """
    # Generate a unique path without creating the file
    temp_dir = tempfile.gettempdir()
    db_path = Path(temp_dir) / f"test_weather_{datetime.now().timestamp()}.duckdb"

    yield str(db_path)

    # Cleanup - remove database file and any associated files
    db_path.unlink(missing_ok=True)
    # DuckDB may create .wal files
    wal_path = db_path.with_suffix(".duckdb.wal")
    wal_path.unlink(missing_ok=True)


@pytest.fixture
def sample_record():
    """Single weather data record."""
    return {
        "dateutc": 1704110400000,  # 2024-01-01 12:00:00 UTC
        "date": "2024-01-01T12:00:00",
        "tempf": 72.5,
        "humidity": 45,
        "windspeedmph": 5.2,
        "winddir": 180,
        "baromrelin": 30.12,
        "baromabsin": 29.95,
    }


@pytest.fixture
def sample_records():
    """Multiple weather data records for testing."""
    return [
        {
            "dateutc": 1704106800000,  # 2024-01-01 11:00:00 UTC
            "date": "2024-01-01T11:00:00",
            "tempf": 70.0,
            "humidity": 50,
            "windspeedmph": 3.5,
            "baromrelin": 30.10,
        },
        {
            "dateutc": 1704110400000,  # 2024-01-01 12:00:00 UTC
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
            "windspeedmph": 5.2,
            "baromrelin": 30.12,
        },
        {
            "dateutc": 1704114000000,  # 2024-01-01 13:00:00 UTC
            "date": "2024-01-01T13:00:00",
            "tempf": 75.0,
            "humidity": 40,
            "windspeedmph": 4.8,
            "baromrelin": 30.15,
        },
    ]


# =============================================================================
# WeatherDatabase TESTS - Context Manager & Table Creation
# =============================================================================


class TestWeatherDatabaseContextManager:
    """Tests for WeatherDatabase context manager behavior."""

    @pytest.mark.unit
    def test_context_manager_creates_connection(self, temp_db):
        """Database connection should be established on context entry."""
        with WeatherDatabase(temp_db) as db:
            assert db.conn is not None

    @pytest.mark.unit
    def test_context_manager_closes_connection(self, temp_db):
        """Database connection should be closed on context exit."""
        db = WeatherDatabase(temp_db)
        with db:
            pass
        assert db.conn is None

    @pytest.mark.unit
    def test_context_manager_creates_tables(self, temp_db):
        """Tables should be created automatically on context entry."""
        with WeatherDatabase(temp_db) as db:
            # Check weather_data table exists
            result = db.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='weather_data'"
            ).fetchone()
            # DuckDB uses different metadata query
            tables = db.conn.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            assert "weather_data" in table_names
            assert "backfill_progress" in table_names

    @pytest.mark.unit
    def test_context_manager_creates_indexes(self, temp_db):
        """Indexes should be created for common queries."""
        with WeatherDatabase(temp_db) as db:
            # Check indexes exist (DuckDB specific query)
            indexes = db.conn.execute(
                "SELECT index_name FROM duckdb_indexes() WHERE table_name = 'weather_data'"
            ).fetchall()
            index_names = [idx[0] for idx in indexes]
            assert "idx_dateutc" in index_names
            assert "idx_date" in index_names

    @pytest.mark.unit
    def test_connection_closes_on_exception(self, temp_db):
        """Connection should close even if an exception occurs."""
        db = WeatherDatabase(temp_db)
        try:
            with db:
                raise ValueError("Test exception")
        except ValueError:
            pass
        assert db.conn is None


# =============================================================================
# WeatherDatabase TESTS - Data Insertion
# =============================================================================


class TestWeatherDatabaseInsert:
    """Tests for WeatherDatabase.insert_data method."""

    @pytest.mark.unit
    def test_insert_single_record(self, temp_db, sample_record):
        """Should insert a single record successfully."""
        with WeatherDatabase(temp_db) as db:
            inserted, skipped = db.insert_data(sample_record)
            assert inserted == 1
            assert skipped == 0

    @pytest.mark.unit
    def test_insert_multiple_records(self, temp_db, sample_records):
        """Should insert multiple records successfully."""
        with WeatherDatabase(temp_db) as db:
            inserted, skipped = db.insert_data(sample_records)
            assert inserted == 3
            assert skipped == 0

    @pytest.mark.unit
    def test_insert_empty_list(self, temp_db):
        """Should handle empty list gracefully."""
        with WeatherDatabase(temp_db) as db:
            inserted, skipped = db.insert_data([])
            assert inserted == 0
            assert skipped == 0

    @pytest.mark.unit
    def test_insert_duplicate_record_updates(self, temp_db, sample_record):
        """Should update existing record with same dateutc."""
        with WeatherDatabase(temp_db) as db:
            # Insert original
            db.insert_data(sample_record)

            # Insert duplicate with different temperature
            updated_record = sample_record.copy()
            updated_record["tempf"] = 80.0
            inserted, skipped = db.insert_data(updated_record)

            # Should count as inserted (update)
            assert inserted == 1
            assert skipped == 0

            # Verify updated value
            result = db.get_data(limit=1)
            assert result[0]["tempf"] == 80.0

    @pytest.mark.unit
    def test_insert_record_without_dateutc_skipped(self, temp_db):
        """Records without dateutc should be skipped."""
        with WeatherDatabase(temp_db) as db:
            record = {"tempf": 72.5, "humidity": 45}  # No dateutc
            inserted, skipped = db.insert_data(record)
            assert inserted == 0
            assert skipped == 1

    @pytest.mark.unit
    def test_insert_filters_unknown_columns(self, temp_db, sample_record):
        """Should filter out columns not in schema."""
        with WeatherDatabase(temp_db) as db:
            record_with_extra = sample_record.copy()
            record_with_extra["unknown_column"] = "ignored"
            record_with_extra["another_fake"] = 123

            inserted, skipped = db.insert_data(record_with_extra)
            assert inserted == 1
            assert skipped == 0

    @pytest.mark.unit
    def test_insert_invalid_type_raises(self, temp_db):
        """Should raise TypeError for invalid data types."""
        with WeatherDatabase(temp_db) as db:
            with pytest.raises(TypeError):
                db.insert_data("not a dict or list")


# =============================================================================
# WeatherDatabase TESTS - Data Retrieval
# =============================================================================


class TestWeatherDatabaseGetData:
    """Tests for WeatherDatabase.get_data method."""

    @pytest.mark.unit
    def test_get_data_returns_all_records(self, temp_db, sample_records):
        """Should return all records when no filters applied."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            result = db.get_data()
            assert len(result) == 3

    @pytest.mark.unit
    def test_get_data_with_limit(self, temp_db, sample_records):
        """Should respect limit parameter."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            result = db.get_data(limit=2)
            assert len(result) == 2

    @pytest.mark.unit
    def test_get_data_with_date_range(self, temp_db, sample_records):
        """Should filter by date range."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            result = db.get_data(
                start_date="2024-01-01T11:30:00", end_date="2024-01-01T12:30:00"
            )
            # Should only return the 12:00 record
            assert len(result) == 1
            assert result[0]["date"] == "2024-01-01T12:00:00"

    @pytest.mark.unit
    def test_get_data_empty_database(self, temp_db):
        """Should return empty list for empty database."""
        with WeatherDatabase(temp_db) as db:
            result = db.get_data()
            assert result == []

    @pytest.mark.unit
    def test_get_data_order_by_desc(self, temp_db, sample_records):
        """Should order by dateutc descending by default."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            result = db.get_data()
            # Most recent first
            assert result[0]["date"] == "2024-01-01T13:00:00"
            assert result[-1]["date"] == "2024-01-01T11:00:00"

    @pytest.mark.unit
    def test_get_data_order_by_asc(self, temp_db, sample_records):
        """Should respect custom order_by parameter."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            result = db.get_data(order_by="dateutc ASC")
            # Oldest first
            assert result[0]["date"] == "2024-01-01T11:00:00"
            assert result[-1]["date"] == "2024-01-01T13:00:00"


# =============================================================================
# WeatherDatabase TESTS - Statistics
# =============================================================================


class TestWeatherDatabaseStats:
    """Tests for WeatherDatabase.get_stats method."""

    @pytest.mark.unit
    def test_get_stats_with_data(self, temp_db, sample_records):
        """Should return correct statistics."""
        with WeatherDatabase(temp_db) as db:
            db.insert_data(sample_records)
            stats = db.get_stats()

            assert stats["total_records"] == 3
            assert stats["min_date"] == "2024-01-01T11:00:00"
            assert stats["max_date"] == "2024-01-01T13:00:00"
            # Temperature: 70, 72.5, 75 -> avg = 72.5
            assert stats["avg_temperature"] == pytest.approx(72.5, rel=0.01)
            assert stats["min_temperature"] == 70.0
            assert stats["max_temperature"] == 75.0

    @pytest.mark.unit
    def test_get_stats_empty_database(self, temp_db):
        """Should return None values for empty database."""
        with WeatherDatabase(temp_db) as db:
            stats = db.get_stats()

            assert stats["total_records"] == 0
            assert stats["min_date"] is None
            assert stats["max_date"] is None
            assert stats["avg_temperature"] is None


# =============================================================================
# WeatherDatabase TESTS - Backfill Progress
# =============================================================================


class TestWeatherDatabaseBackfill:
    """Tests for backfill progress tracking."""

    @pytest.mark.unit
    def test_init_backfill_progress(self, temp_db):
        """Should create a new backfill progress record."""
        with WeatherDatabase(temp_db) as db:
            progress_id = db.init_backfill_progress("2024-01-01", "2024-01-31")
            assert progress_id is not None
            assert progress_id > 0

    @pytest.mark.unit
    def test_get_backfill_progress(self, temp_db):
        """Should retrieve backfill progress record."""
        with WeatherDatabase(temp_db) as db:
            progress_id = db.init_backfill_progress("2024-01-01", "2024-01-31")
            progress = db.get_backfill_progress(progress_id)

            assert progress is not None
            assert progress["start_date"] == "2024-01-01"
            assert progress["end_date"] == "2024-01-31"
            assert progress["status"] == "in_progress"

    @pytest.mark.unit
    def test_update_backfill_progress(self, temp_db):
        """Should update backfill progress record."""
        with WeatherDatabase(temp_db) as db:
            progress_id = db.init_backfill_progress("2024-01-01", "2024-01-31")
            db.update_backfill_progress(
                progress_id,
                current_date="2024-01-15",
                total_records=1000,
                skipped_records=50,
                status="in_progress",
            )

            progress = db.get_backfill_progress(progress_id)
            assert progress["current_date"] == "2024-01-15"
            assert progress["total_records"] == 1000
            assert progress["skipped_records"] == 50

    @pytest.mark.unit
    def test_clear_backfill_progress(self, temp_db):
        """Should delete backfill progress record."""
        with WeatherDatabase(temp_db) as db:
            progress_id = db.init_backfill_progress("2024-01-01", "2024-01-31")
            db.clear_backfill_progress(progress_id)

            progress = db.get_backfill_progress(progress_id)
            assert progress is None

    @pytest.mark.unit
    def test_get_nonexistent_backfill_progress(self, temp_db):
        """Should return None for nonexistent progress ID."""
        with WeatherDatabase(temp_db) as db:
            progress = db.get_backfill_progress(99999)
            assert progress is None
