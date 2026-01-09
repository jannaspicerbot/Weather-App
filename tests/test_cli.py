"""
Comprehensive tests for the CLI commands.

Tests cover:
- init_db command
- fetch command (with mocked API)
- backfill command (with mocked API)
- export command
- info command
- Error handling and validation
"""

import csv
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from weather_app.cli.cli import cli

# Get reference to the cli module (not the cli Click group)
cli_module = sys.modules["weather_app.cli.cli"]

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


@pytest.fixture
def temp_db_dir():
    """Create a temporary directory for database testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_api_credentials():
    """Mock environment variables for API credentials."""
    with patch.dict(
        "os.environ",
        {"AMBIENT_API_KEY": "test_api_key", "AMBIENT_APP_KEY": "test_app_key"},
    ):
        yield


@pytest.fixture
def mock_devices_response():
    """Mock response from get_devices."""
    return [
        {
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "info": {"name": "Test Weather Station"},
            "lastData": {"tempf": 72.5},
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
            "windspeedmph": 5.2,
        },
        {
            "dateutc": 1704114000000,
            "date": "2024-01-01T13:00:00",
            "tempf": 74.0,
            "humidity": 43,
            "windspeedmph": 6.1,
        },
    ]


# =============================================================================
# CLI GROUP TESTS
# =============================================================================


class TestCLIGroup:
    """Tests for the main CLI group."""

    @pytest.mark.unit
    def test_cli_shows_help(self, runner):
        """CLI should show help message."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Weather App" in result.output

    @pytest.mark.unit
    def test_cli_shows_version(self, runner):
        """CLI should show version."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    @pytest.mark.unit
    def test_cli_lists_commands(self, runner):
        """CLI help should list available commands."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "init-db" in result.output
        assert "fetch" in result.output
        assert "backfill" in result.output
        assert "export" in result.output
        assert "info" in result.output


# =============================================================================
# INIT_DB COMMAND TESTS
# =============================================================================


class TestInitDbCommand:
    """Tests for the init_db command."""

    @pytest.mark.unit
    def test_init_db_creates_database(self, runner, temp_db_dir):
        """init_db should create a new database."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["init-db"])

        assert result.exit_code == 0
        assert "initialized successfully" in result.output
        assert db_path.exists()

    @pytest.mark.unit
    def test_init_db_fails_if_exists(self, runner, temp_db_dir):
        """init_db should fail if database already exists."""
        db_path = temp_db_dir / "test.duckdb"
        db_path.touch()  # Create empty file

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["init-db"])

        assert result.exit_code == 1
        assert "already exists" in result.output

    @pytest.mark.unit
    def test_init_db_with_force(self, runner, temp_db_dir):
        """init_db --force should recreate database."""
        db_path = temp_db_dir / "test.duckdb"
        db_path.touch()  # Create empty file

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["init-db", "--force"])

        assert result.exit_code == 0
        assert "initialized successfully" in result.output


# =============================================================================
# FETCH COMMAND TESTS
# =============================================================================


class TestFetchCommand:
    """Tests for the fetch command."""

    @pytest.mark.unit
    def test_fetch_requires_credentials(self, runner, temp_db_dir):
        """fetch should fail without API credentials."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict("os.environ", {}, clear=True):
                result = runner.invoke(cli, ["fetch"])

        assert result.exit_code == 1
        assert "credentials not found" in result.output

    @pytest.mark.unit
    def test_fetch_requires_database(self, runner, temp_db_dir):
        """fetch should fail if database doesn't exist."""
        db_path = temp_db_dir / "nonexistent.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                result = runner.invoke(cli, ["fetch"])

        assert result.exit_code == 1
        assert "Database not found" in result.output

    @pytest.mark.unit
    def test_fetch_success(
        self, runner, temp_db_dir, mock_devices_response, mock_weather_data
    ):
        """fetch should successfully fetch and save data."""
        db_path = temp_db_dir / "test.duckdb"

        # Create database first
        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass

        # Mock API calls
        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = mock_weather_data
        mock_api.__enter__ = MagicMock(return_value=mock_api)
        mock_api.__exit__ = MagicMock(return_value=False)

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                with patch.object(
                    cli_module, "AmbientWeatherAPI", return_value=mock_api
                ):
                    with patch("time.sleep"):  # Skip delays
                        result = runner.invoke(cli, ["fetch", "--limit", "2"])

        assert result.exit_code == 0
        assert "Fetched" in result.output
        assert "Inserted" in result.output

    @pytest.mark.unit
    def test_fetch_no_devices(self, runner, temp_db_dir):
        """fetch should handle no devices found."""
        db_path = temp_db_dir / "test.duckdb"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass

        mock_api = MagicMock()
        mock_api.get_devices.return_value = []
        mock_api.__enter__ = MagicMock(return_value=mock_api)
        mock_api.__exit__ = MagicMock(return_value=False)

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                with patch.object(
                    cli_module, "AmbientWeatherAPI", return_value=mock_api
                ):
                    result = runner.invoke(cli, ["fetch"])

        assert result.exit_code == 1
        assert "No devices found" in result.output


# =============================================================================
# BACKFILL COMMAND TESTS
# =============================================================================


class TestBackfillCommand:
    """Tests for the backfill command."""

    @pytest.mark.unit
    def test_backfill_requires_dates(self, runner):
        """backfill should require start and end dates."""
        result = runner.invoke(cli, ["backfill"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    @pytest.mark.unit
    def test_backfill_validates_date_format(self, runner, temp_db_dir):
        """backfill should validate date format."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                result = runner.invoke(
                    cli, ["backfill", "--start", "invalid", "--end", "2024-01-31"]
                )

        assert result.exit_code == 1
        assert "Invalid date format" in result.output

    @pytest.mark.unit
    def test_backfill_validates_date_order(self, runner, temp_db_dir):
        """backfill should validate start date is before end date."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                result = runner.invoke(
                    cli, ["backfill", "--start", "2024-01-31", "--end", "2024-01-01"]
                )

        assert result.exit_code == 1
        assert "before end date" in result.output

    @pytest.mark.unit
    def test_backfill_requires_credentials(self, runner, temp_db_dir):
        """backfill should fail without API credentials."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict("os.environ", {}, clear=True):
                result = runner.invoke(
                    cli, ["backfill", "--start", "2024-01-01", "--end", "2024-01-31"]
                )

        assert result.exit_code == 1
        assert "credentials not found" in result.output


# =============================================================================
# EXPORT COMMAND TESTS
# =============================================================================


class TestExportCommand:
    """Tests for the export command."""

    @pytest.mark.unit
    def test_export_requires_output(self, runner):
        """export should require output path."""
        result = runner.invoke(cli, ["export"])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    @pytest.mark.unit
    def test_export_requires_database(self, runner, temp_db_dir):
        """export should fail if database doesn't exist."""
        db_path = temp_db_dir / "nonexistent.duckdb"
        output_path = temp_db_dir / "output.csv"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["export", "-o", str(output_path)])

        assert result.exit_code == 1
        assert "Database not found" in result.output

    @pytest.mark.unit
    def test_export_creates_csv(self, runner, temp_db_dir):
        """export should create CSV file with data."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

        # Create database with data
        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            db.insert_data(
                {
                    "dateutc": 1704110400000,
                    "date": "2024-01-01T12:00:00",
                    "tempf": 72.5,
                    "humidity": 45,
                }
            )

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["export", "-o", str(output_path)])

        assert result.exit_code == 0
        assert "Exported" in result.output
        assert output_path.exists()

        # Verify CSV content
        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["tempf"] == "72.5"

    @pytest.mark.unit
    def test_export_with_date_filter(self, runner, temp_db_dir):
        """export should filter by date range."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            db.insert_data(
                [
                    {
                        "dateutc": 1704110400000,
                        "date": "2024-01-01T12:00:00",
                        "tempf": 72.5,
                    },
                    {
                        "dateutc": 1704196800000,
                        "date": "2024-01-02T12:00:00",
                        "tempf": 75.0,
                    },
                ]
            )

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(
                cli,
                [
                    "export",
                    "-o",
                    str(output_path),
                    "--start",
                    "2024-01-02",
                    "--end",
                    "2024-01-03",
                ],
            )

        assert result.exit_code == 0
        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]["tempf"] == "75.0"

    @pytest.mark.unit
    def test_export_with_limit(self, runner, temp_db_dir):
        """export should respect limit parameter."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            db.insert_data(
                [
                    {
                        "dateutc": 1704110400000,
                        "date": "2024-01-01T12:00:00",
                        "tempf": 72.5,
                    },
                    {
                        "dateutc": 1704114000000,
                        "date": "2024-01-01T13:00:00",
                        "tempf": 74.0,
                    },
                    {
                        "dateutc": 1704117600000,
                        "date": "2024-01-01T14:00:00",
                        "tempf": 75.0,
                    },
                ]
            )

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(
                cli, ["export", "-o", str(output_path), "--limit", "2"]
            )

        assert result.exit_code == 0
        with open(output_path) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2

    @pytest.mark.unit
    def test_export_empty_database(self, runner, temp_db_dir):
        """export should handle empty database gracefully."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass  # Empty database

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["export", "-o", str(output_path)])

        assert result.exit_code == 0
        assert "No data found" in result.output


# =============================================================================
# INFO COMMAND TESTS
# =============================================================================


class TestInfoCommand:
    """Tests for the info command."""

    @pytest.mark.unit
    def test_info_shows_configuration(self, runner, temp_db_dir):
        """info should show configuration details."""
        db_path = temp_db_dir / "test.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "Configuration Info" in result.output
        assert "Database" in result.output

    @pytest.mark.unit
    def test_info_with_database(self, runner, temp_db_dir):
        """info should show database stats when database exists."""
        db_path = temp_db_dir / "test.duckdb"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            db.insert_data(
                {
                    "dateutc": 1704110400000,
                    "date": "2024-01-01T12:00:00",
                    "tempf": 72.5,
                }
            )

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "Total records:" in result.output
        assert "Date range:" in result.output

    @pytest.mark.unit
    def test_info_without_database(self, runner, temp_db_dir):
        """info should handle missing database gracefully."""
        db_path = temp_db_dir / "nonexistent.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "init-db" in result.output  # Should suggest running init-db
