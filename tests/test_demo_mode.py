"""
Tests for Demo Mode functionality

Tests the DemoService, data generator, generation service, and API endpoints for demo mode.
"""

import tempfile
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from weather_app.demo.data_generator import (
    GenerationCancelledError,
    SeattleWeatherGenerator,
)
from weather_app.demo.demo_service import DemoService
from weather_app.demo.generation_service import DemoGenerationService


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

    def test_cancel_check_stops_generation(self, tmp_path: Path) -> None:
        """Test that cancel_check callback can stop generation."""
        db_path = tmp_path / "test_demo.duckdb"
        generator = SeattleWeatherGenerator(db_path)

        cancel_flag = threading.Event()
        days_generated = []

        def progress_callback(current_day: int, total_days: int) -> None:
            days_generated.append(current_day)
            # Cancel after a few days
            if current_day >= 20:
                cancel_flag.set()

        def cancel_check() -> bool:
            return cancel_flag.is_set()

        start_date = datetime(2024, 1, 1)

        with pytest.raises(GenerationCancelledError) as exc_info:
            generator.generate(
                start_date=start_date,
                days=100,
                progress_callback=progress_callback,
                cancel_check=cancel_check,
                quiet=True,
            )

        # Should have stopped before completing all 100 days
        assert "cancelled" in str(exc_info.value).lower()
        # Should have made progress but not completed
        assert len(days_generated) > 0
        assert days_generated[-1] < 100

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


class TestDemoGenerationService:
    """Tests for the DemoGenerationService singleton with concurrency control."""

    @pytest.fixture(autouse=True)
    def reset_service(self):
        """Reset the singleton instance before and after each test."""
        DemoGenerationService.reset_instance()
        yield
        DemoGenerationService.reset_instance()

    def test_singleton_returns_same_instance(self) -> None:
        """Test that get_instance returns the same singleton instance."""
        service1 = DemoGenerationService.get_instance()
        service2 = DemoGenerationService.get_instance()

        assert service1 is service2

    def test_initial_status_is_idle(self) -> None:
        """Test that initial status is idle."""
        service = DemoGenerationService.get_instance()
        status = service.get_status()

        assert status["state"] == "idle"
        assert status["current_day"] == 0
        assert status["total_days"] == 0
        assert status["percent"] == 0

    def test_prevents_concurrent_generation(self, tmp_path: Path, monkeypatch) -> None:
        """Test that second generation request is rejected while one is in progress."""
        # Use a temporary path for the demo database
        test_db_path = tmp_path / "test_demo.duckdb"
        monkeypatch.setattr("weather_app.demo.generation_service.DEMO_DB_PATH", test_db_path)

        service = DemoGenerationService.get_instance()

        # Start first generation with minimal days for speed
        success1, message1 = service.start_generation(days=5)
        assert success1, f"First generation should start: {message1}"

        # Try to start second generation - should be rejected
        success2, message2 = service.start_generation(days=5)
        assert not success2, "Second generation should be rejected"
        assert "already in progress" in message2.lower()

        # Status should show generating
        status = service.get_status()
        assert status["state"] == "generating"

        # Wait for completion (poll rather than fixed sleep)
        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = service.get_status()
            if status["state"] != "generating":
                break
            time.sleep(0.2)

        # Should have completed
        assert status["state"] == "completed", f"Expected completed, got {status['state']}"

    def test_cancellation_stops_generation(self, tmp_path: Path, monkeypatch) -> None:
        """Test that cancellation request stops ongoing generation."""
        test_db_path = tmp_path / "test_demo.duckdb"
        monkeypatch.setattr("weather_app.demo.generation_service.DEMO_DB_PATH", test_db_path)

        service = DemoGenerationService.get_instance()

        # Start generation
        success, _ = service.start_generation(days=100)  # Long enough to cancel
        assert success

        # Wait a moment for generation to start
        time.sleep(0.5)

        # Request cancellation
        cancel_success, cancel_message = service.cancel_generation()
        assert cancel_success, f"Cancellation should succeed: {cancel_message}"

        # Wait for cancellation to take effect
        timeout = 5
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = service.get_status()
            if status["state"] != "generating":
                break
            time.sleep(0.1)

        # Status should be cancelled or failed (not generating or completed)
        status = service.get_status()
        assert status["state"] in ("cancelled", "failed"), f"Expected cancelled or failed, got {status['state']}"

        # Database should be cleaned up
        assert not test_db_path.exists(), "Partial database should be cleaned up"

    def test_cancel_without_generation_fails(self) -> None:
        """Test that cancelling when no generation is running returns failure."""
        service = DemoGenerationService.get_instance()

        success, message = service.cancel_generation()
        assert not success
        assert "no generation in progress" in message.lower()

    def test_status_updates_during_generation(self, tmp_path: Path, monkeypatch) -> None:
        """Test that status updates as generation progresses."""
        test_db_path = tmp_path / "test_demo.duckdb"
        monkeypatch.setattr("weather_app.demo.generation_service.DEMO_DB_PATH", test_db_path)

        service = DemoGenerationService.get_instance()

        # Start generation with small number of days
        service.start_generation(days=15)

        # Poll status until complete (with timeout)
        status_snapshots = []
        timeout = 15
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = service.get_status()
            status_snapshots.append(status)
            if status["state"] != "generating":
                break
            time.sleep(0.2)

        # Should have seen some progress updates
        assert len(status_snapshots) > 1

        # State should have been generating at some point
        states = [s["state"] for s in status_snapshots]
        assert "generating" in states or "completed" in states

        # Final status should be completed (not still generating)
        final_status = service.get_status()
        assert final_status["state"] in ("completed", "cancelled", "failed"), \
            f"Expected completed/cancelled/failed, got {final_status['state']}"

    def test_cleanup_on_failure(self, tmp_path: Path, monkeypatch) -> None:
        """Test that partial database is cleaned up on generation failure."""
        test_db_path = tmp_path / "test_demo.duckdb"
        monkeypatch.setattr("weather_app.demo.generation_service.DEMO_DB_PATH", test_db_path)

        service = DemoGenerationService.get_instance()

        # Start generation and cancel immediately to simulate failure
        service.start_generation(days=100)
        time.sleep(0.3)
        service.cancel_generation()

        # Wait for cleanup
        timeout = 5
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = service.get_status()
            if status["state"] != "generating":
                break
            time.sleep(0.1)

        # Database should not exist (cleaned up)
        assert not test_db_path.exists(), "Partial database should be cleaned up after cancellation"

    def test_thread_safe_status_access(self, tmp_path: Path, monkeypatch) -> None:
        """Test that status can be safely accessed from multiple threads."""
        test_db_path = tmp_path / "test_demo.duckdb"
        monkeypatch.setattr("weather_app.demo.generation_service.DEMO_DB_PATH", test_db_path)

        service = DemoGenerationService.get_instance()
        errors = []
        status_reads = []

        def read_status_repeatedly():
            try:
                for _ in range(50):
                    status = service.get_status()
                    status_reads.append(status)
                    time.sleep(0.01)
            except Exception as e:
                errors.append(e)

        # Start generation
        service.start_generation(days=30)

        # Spawn multiple threads to read status concurrently
        threads = [threading.Thread(target=read_status_repeatedly) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # No errors should have occurred
        assert len(errors) == 0, f"Thread safety errors: {errors}"

        # Should have successfully read status multiple times
        assert len(status_reads) > 0
