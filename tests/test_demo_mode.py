"""
Tests for Demo Mode functionality

Tests the DemoService, data generator, and API endpoints for demo mode.
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from weather_app.demo.data_generator import SeattleWeatherGenerator
from weather_app.demo.demo_service import DemoService


class TestDemoConfig:
    """Tests for demo mode configuration."""

    def test_demo_db_path_uses_base_dir(self) -> None:
        """Test that DEMO_DB_PATH uses the user data directory (BASE_DIR)."""
        from weather_app.config import BASE_DIR, DEMO_DB_FILENAME, DEMO_DB_PATH

        # DEMO_DB_PATH should be BASE_DIR / DEMO_DB_FILENAME
        expected_path = BASE_DIR / DEMO_DB_FILENAME
        assert DEMO_DB_PATH == expected_path

    def test_demo_db_filename_is_correct(self) -> None:
        """Test that the demo database filename is correct."""
        from weather_app.config import DEMO_DB_FILENAME

        assert DEMO_DB_FILENAME == "demo_weather.duckdb"

    def test_demo_default_days_is_set(self) -> None:
        """Test that DEMO_DEFAULT_DAYS is set to 3 years."""
        from weather_app.config import DEMO_DEFAULT_DAYS

        assert DEMO_DEFAULT_DAYS == 1095  # 3 years


class TestSeattleWeatherGenerator:
    """Tests for the Seattle weather data generator."""

    def test_generates_records(self, tmp_path: Path) -> None:
        """Test that generator creates weather records."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        start_date = datetime(2024, 1, 1)
        records = generator.generate(start_date=start_date, days=1)

        assert records > 0
        # 1 day with 5-minute intervals = 288 records
        assert records == 288

        stats = generator.get_stats()
        assert stats["count"] == 288
        generator.close()

    def test_generates_realistic_temperatures(self, tmp_path: Path) -> None:
        """Test that generated temperatures are within realistic Seattle ranges."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        # Generate January data (should be cold)
        start_date = datetime(2024, 1, 15)
        generator.generate(start_date=start_date, days=1)

        # Query the generated data
        result = generator.conn.execute(
            "SELECT AVG(tempf), MIN(tempf), MAX(tempf) FROM weather_data"
        ).fetchone()
        avg_temp, min_temp, max_temp = result

        # Seattle January temps typically 35-50°F
        assert 25 < avg_temp < 60, f"Average temp {avg_temp}°F outside expected range"
        assert min_temp > 10, f"Min temp {min_temp}°F too cold for Seattle"
        assert max_temp < 80, f"Max temp {max_temp}°F too warm for January"

        generator.close()

    def test_generates_humidity(self, tmp_path: Path) -> None:
        """Test that humidity values are within valid range."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        start_date = datetime(2024, 6, 1)
        generator.generate(start_date=start_date, days=1)

        result = generator.conn.execute(
            "SELECT MIN(humidity), MAX(humidity) FROM weather_data"
        ).fetchone()
        min_humidity, max_humidity = result

        assert min_humidity >= 30, "Humidity too low"
        assert max_humidity <= 100, "Humidity exceeds 100%"

        generator.close()

    def test_generates_rain_data(self, tmp_path: Path) -> None:
        """Test that rain data is generated properly."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        # Generate winter data (more likely to have rain)
        start_date = datetime(2024, 11, 1)
        generator.generate(start_date=start_date, days=7)

        result = generator.conn.execute(
            "SELECT SUM(hourlyrainin) FROM weather_data"
        ).fetchone()
        total_rain = result[0]

        # November in Seattle should have some rain
        assert total_rain >= 0, "Rain should be non-negative"

        generator.close()

    def test_progress_callback_called(self, tmp_path: Path) -> None:
        """Test that progress callback is called during generation."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        progress_calls: list[tuple[int, int]] = []

        def progress_callback(current_day: int, total_days: int) -> None:
            progress_calls.append((current_day, total_days))

        start_date = datetime(2024, 1, 1)
        generator.generate(
            start_date=start_date,
            days=30,  # 30 days, should get callbacks every 10 days
            progress_callback=progress_callback,
            quiet=True,
        )

        # Should have at least 3 progress calls (day 0, 10, 20) + final 100%
        assert len(progress_calls) >= 3
        # Last call should be final 100%
        assert progress_calls[-1] == (30, 30)

        generator.close()

    def test_quiet_mode_suppresses_output(self, tmp_path: Path, capsys) -> None:
        """Test that quiet mode suppresses print output."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        start_date = datetime(2024, 1, 1)
        generator.generate(start_date=start_date, days=1, quiet=True)

        captured = capsys.readouterr()
        assert captured.out == "", "No output should be printed in quiet mode"

        generator.close()


class TestDemoService:
    """Tests for the DemoService class."""

    @pytest.fixture
    def demo_db(self, tmp_path: Path) -> Path:
        """Create a temporary demo database."""
        db_path = tmp_path / "demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        # Generate 3 days of data
        start_date = datetime.now() - timedelta(days=3)
        generator.generate(start_date=start_date, days=3)
        generator.close()

        return db_path

    def test_service_initializes(self, demo_db: Path) -> None:
        """Test that DemoService initializes properly."""
        service = DemoService(demo_db)

        assert service.is_available
        service.close()

    def test_service_handles_missing_db(self, tmp_path: Path) -> None:
        """Test that DemoService handles missing database gracefully."""
        missing_path = tmp_path / "nonexistent.duckdb"
        service = DemoService(missing_path)

        assert not service.is_available

    def test_generate_if_missing_creates_database(self, tmp_path: Path) -> None:
        """Test that generate_if_missing creates database when it doesn't exist."""
        db_path = tmp_path / "new_demo.duckdb"
        service = DemoService(db_path)

        # Initially not available
        assert not service.is_available
        assert not db_path.exists()

        # Generate database
        was_generated = service.generate_if_missing(days=1)

        # Should have been generated
        assert was_generated
        assert db_path.exists()
        assert service.is_available

        # Should have records
        stats = service.get_stats()
        assert stats["total_records"] == 288  # 1 day = 288 records

        service.close()

    def test_generate_if_missing_skips_existing(self, demo_db: Path) -> None:
        """Test that generate_if_missing doesn't regenerate if DB exists."""
        service = DemoService(demo_db)

        # Get initial stats
        initial_stats = service.get_stats()
        initial_count = initial_stats["total_records"]

        # Try to generate again
        was_generated = service.generate_if_missing(days=1)

        # Should NOT have been regenerated
        assert not was_generated

        # Count should be unchanged
        stats = service.get_stats()
        assert stats["total_records"] == initial_count

        service.close()

    def test_generate_if_missing_with_progress_callback(self, tmp_path: Path) -> None:
        """Test that generate_if_missing calls progress callback."""
        db_path = tmp_path / "new_demo.duckdb"
        service = DemoService(db_path)

        progress_calls: list[tuple[int, int]] = []

        def progress_callback(current_day: int, total_days: int) -> None:
            progress_calls.append((current_day, total_days))

        was_generated = service.generate_if_missing(
            days=20,  # Short for faster test
            progress_callback=progress_callback,
        )

        assert was_generated
        assert len(progress_calls) > 0
        # Last call should be final 100%
        assert progress_calls[-1] == (20, 20)

        service.close()

    def test_get_latest_reading(self, demo_db: Path) -> None:
        """Test fetching the latest reading."""
        service = DemoService(demo_db)

        latest = service.get_latest_reading()

        assert latest is not None
        assert "tempf" in latest
        assert "dateutc" in latest
        assert "humidity" in latest

        service.close()

    def test_time_shifting(self, demo_db: Path) -> None:
        """Test that timestamps are shifted to appear current."""
        service = DemoService(demo_db)

        latest = service.get_latest_reading()
        now = datetime.now()

        # Parse the date from the reading
        reading_date = datetime.fromisoformat(latest["date"].replace("Z", "+00:00"))

        # The shifted date should be close to now (within a day)
        time_diff = abs((now - reading_date.replace(tzinfo=None)).total_seconds())
        assert time_diff < 86400, "Latest reading should be within 24 hours of now"

        service.close()

    def test_get_all_readings_with_limit(self, demo_db: Path) -> None:
        """Test fetching readings with a limit."""
        service = DemoService(demo_db)

        readings = service.get_all_readings(limit=10)

        assert len(readings) == 10
        for reading in readings:
            assert "tempf" in reading
            assert "dateutc" in reading

        service.close()

    def test_get_stats(self, demo_db: Path) -> None:
        """Test getting database statistics."""
        service = DemoService(demo_db)

        stats = service.get_stats()

        assert "total_records" in stats
        assert stats["total_records"] > 0
        assert "min_date" in stats
        assert "max_date" in stats
        assert "date_range_days" in stats

        service.close()

    def test_get_demo_device(self, demo_db: Path) -> None:
        """Test getting demo device info."""
        service = DemoService(demo_db)

        device = service.get_demo_device()

        assert device["mac_address"] == "DEMO:SEATTLE:01"
        assert device["name"] == "Seattle Demo Station"
        assert device["location"] == "Seattle, WA"

        service.close()

    def test_get_devices(self, demo_db: Path) -> None:
        """Test getting list of devices (should return demo device)."""
        service = DemoService(demo_db)

        devices = service.get_devices()

        assert len(devices) == 1
        assert devices[0]["mac_address"] == "DEMO:SEATTLE:01"

        service.close()

    def test_get_sampled_readings(self, demo_db: Path) -> None:
        """Test getting evenly sampled readings."""
        service = DemoService(demo_db)

        stats = service.get_stats()
        start_date = stats["min_date"]
        end_date = stats["max_date"]

        readings = service.get_sampled_readings(
            start_date=start_date,
            end_date=end_date,
            target_count=100,
        )

        # Should return up to 100 evenly distributed readings
        assert len(readings) <= 100
        assert len(readings) > 0

        service.close()


class TestDemoModeIntegration:
    """Integration tests for demo mode with the web app."""

    @pytest.fixture
    def demo_db(self, tmp_path: Path) -> Path:
        """Create a temporary demo database."""
        db_path = tmp_path / "demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        start_date = datetime.now() - timedelta(days=7)
        generator.generate(start_date=start_date, days=7)
        generator.close()

        return db_path

    def test_demo_service_works_with_app_functions(
        self, demo_db: Path, monkeypatch
    ) -> None:
        """Test that demo service integrates with app module functions."""
        # Patch the DEMO_DB_PATH to use our test database
        monkeypatch.setattr("weather_app.config.DEMO_DB_PATH", demo_db)

        from weather_app.web.app import (
            disable_demo_mode,
            enable_demo_mode,
            get_demo_service,
            is_demo_mode,
        )

        # Initially not in demo mode
        assert not is_demo_mode()

        # Enable demo mode
        success, message = enable_demo_mode()
        assert success, f"Failed to enable: {message}"
        assert is_demo_mode()

        # Get demo service
        service = get_demo_service()
        assert service is not None
        assert service.is_available

        # Disable demo mode
        success, message = disable_demo_mode()
        assert success
        assert not is_demo_mode()
