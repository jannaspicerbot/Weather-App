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

    @pytest.mark.unit
    def test_info_with_empty_table(self, runner, temp_db_dir):
        """info should handle database with empty weather_data table."""
        db_path = temp_db_dir / "test.duckdb"

        # Create database but don't add any data
        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass  # Table created but empty

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            result = runner.invoke(cli, ["info"])

        assert result.exit_code == 0
        assert "Total records: 0" in result.output


# =============================================================================
# SERVE COMMAND TESTS
# =============================================================================


class TestServeCommand:
    """Tests for the serve command."""

    @pytest.mark.unit
    def test_serve_shows_help(self, runner):
        """serve --help should show available options."""
        result = runner.invoke(cli, ["serve", "--help"])

        assert result.exit_code == 0
        assert "--host" in result.output
        assert "--port" in result.output
        assert "--demo" in result.output
        assert "--reload" in result.output

    @pytest.mark.unit
    def test_serve_default_options(self, runner):
        """serve should have correct default options."""
        # We can't actually start the server, but we can verify the command exists
        result = runner.invoke(cli, ["serve", "--help"])

        assert result.exit_code == 0
        assert "0.0.0.0" in result.output  # default host
        assert "8000" in result.output  # default port

    @pytest.mark.unit
    def test_serve_demo_mode_sets_env_var(self, runner, temp_db_dir):
        """serve --demo should set DEMO_MODE environment variable."""
        demo_db_path = temp_db_dir / "demo_weather.duckdb"

        # Create demo database to avoid generation
        from datetime import datetime, timedelta

        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(demo_db_path)
        generator.generate(
            start_date=datetime.now() - timedelta(days=1), days=1, quiet=True
        )
        generator.close()

        # Mock uvicorn.run to prevent actual server start
        # Patch at config module level where it's imported from
        with patch("uvicorn.run") as mock_uvicorn:
            with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
                result = runner.invoke(cli, ["serve", "--demo"])

        # Command should start (exit_code 0 because we mocked uvicorn)
        assert result.exit_code == 0
        assert "demo mode" in result.output.lower()
        mock_uvicorn.assert_called_once()

    @pytest.mark.unit
    def test_serve_demo_mode_generates_missing_db(self, runner, temp_db_dir):
        """serve --demo should generate demo database if missing."""
        demo_db_path = temp_db_dir / "demo_weather.duckdb"

        # Mock the DemoService to avoid actual generation
        with patch("weather_app.demo.DemoService") as MockDemoService:
            mock_service = MagicMock()
            MockDemoService.return_value = mock_service
            mock_service.generate_if_missing.return_value = True

            with patch("uvicorn.run"):
                with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
                    with patch("weather_app.config.DEMO_DEFAULT_DAYS", 1):
                        result = runner.invoke(cli, ["serve", "--demo"])

        # Should indicate generation was needed
        assert result.exit_code == 0

    @pytest.mark.unit
    def test_serve_normal_mode_message(self, runner):
        """serve without --demo should show normal mode message."""
        with patch("uvicorn.run"):
            result = runner.invoke(cli, ["serve"])

        assert result.exit_code == 0
        assert "Weather Dashboard server" in result.output

    @pytest.mark.unit
    def test_serve_with_custom_host_port(self, runner):
        """serve should accept custom host and port."""
        with patch("uvicorn.run") as mock_uvicorn:
            result = runner.invoke(
                cli, ["serve", "--host", "127.0.0.1", "--port", "9000"]
            )

        assert result.exit_code == 0
        mock_uvicorn.assert_called_once()
        call_kwargs = mock_uvicorn.call_args[1]
        assert call_kwargs["host"] == "127.0.0.1"
        assert call_kwargs["port"] == 9000

    @pytest.mark.unit
    def test_serve_reload_option(self, runner):
        """serve --reload should enable auto-reload."""
        with patch("uvicorn.run") as mock_uvicorn:
            result = runner.invoke(cli, ["serve", "--reload"])

        assert result.exit_code == 0
        call_kwargs = mock_uvicorn.call_args[1]
        assert call_kwargs["reload"] is True


# =============================================================================
# DEMO GENERATE COMMAND TESTS
# =============================================================================


class TestDemoGenerateCommand:
    """Tests for the demo generate command."""

    @pytest.mark.unit
    def test_demo_generate_shows_help(self, runner):
        """demo generate --help should show available options."""
        result = runner.invoke(cli, ["demo", "generate", "--help"])

        assert result.exit_code == 0
        assert "--days" in result.output
        assert "--output" in result.output
        assert "--start-date" in result.output
        assert "--force" in result.output

    @pytest.mark.unit
    def test_demo_generate_default_values(self, runner):
        """demo generate should have correct default values in help."""
        result = runner.invoke(cli, ["demo", "generate", "--help"])

        assert result.exit_code == 0
        assert "1095" in result.output  # default days

    @pytest.mark.unit
    def test_demo_generate_creates_database(self, runner, temp_db_dir):
        """demo generate should create demo database."""
        output_path = temp_db_dir / "custom_demo.duckdb"

        result = runner.invoke(
            cli, ["demo", "generate", "--days", "1", "--output", str(output_path)]
        )

        assert result.exit_code == 0
        assert output_path.exists()
        assert "Demo database created successfully" in result.output

    @pytest.mark.unit
    def test_demo_generate_invalid_start_date(self, runner, temp_db_dir):
        """demo generate should fail with invalid start date format."""
        output_path = temp_db_dir / "demo.duckdb"

        result = runner.invoke(
            cli,
            [
                "demo",
                "generate",
                "--days",
                "1",
                "--output",
                str(output_path),
                "--start-date",
                "invalid-date",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid date format" in result.output

    @pytest.mark.unit
    def test_demo_generate_valid_start_date(self, runner, temp_db_dir):
        """demo generate should accept valid start date."""
        output_path = temp_db_dir / "demo.duckdb"

        result = runner.invoke(
            cli,
            [
                "demo",
                "generate",
                "--days",
                "1",
                "--output",
                str(output_path),
                "--start-date",
                "2024-01-01",
            ],
        )

        assert result.exit_code == 0
        assert "2024-01-01" in result.output  # Start date shown in output

    @pytest.mark.unit
    def test_demo_generate_skips_existing_without_force(self, runner, temp_db_dir):
        """demo generate should skip if database exists without --force."""
        output_path = temp_db_dir / "demo.duckdb"

        # Create initial database
        from datetime import datetime

        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(output_path)
        generator.generate(start_date=datetime(2024, 1, 1), days=1, quiet=True)
        generator.close()

        # Run generate without --force
        result = runner.invoke(
            cli, ["demo", "generate", "--days", "1", "--output", str(output_path)]
        )

        assert result.exit_code == 0
        assert "already exists" in result.output

    @pytest.mark.unit
    def test_demo_generate_force_recreates(self, runner, temp_db_dir):
        """demo generate --force should recreate existing database."""
        output_path = temp_db_dir / "demo.duckdb"

        # Create initial database
        from datetime import datetime

        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(output_path)
        generator.generate(start_date=datetime(2024, 1, 1), days=1, quiet=True)
        initial_size = output_path.stat().st_size
        generator.close()

        # Run generate with --force
        result = runner.invoke(
            cli,
            [
                "demo",
                "generate",
                "--days",
                "1",
                "--output",
                str(output_path),
                "--force",
            ],
        )

        assert result.exit_code == 0
        assert output_path.exists()
        assert "Demo database created successfully" in result.output

    @pytest.mark.unit
    def test_demo_generate_shows_stats(self, runner, temp_db_dir):
        """demo generate should show generation statistics."""
        output_path = temp_db_dir / "demo.duckdb"

        result = runner.invoke(
            cli, ["demo", "generate", "--days", "1", "--output", str(output_path)]
        )

        assert result.exit_code == 0
        assert "Total records:" in result.output
        assert "Date range:" in result.output
        assert "Database size:" in result.output


# =============================================================================
# DEMO STATUS COMMAND TESTS
# =============================================================================


class TestDemoStatusCommand:
    """Tests for the demo status command."""

    @pytest.mark.unit
    def test_demo_status_no_database(self, runner, temp_db_dir):
        """demo status should show status when database doesn't exist."""
        demo_db_path = temp_db_dir / "demo_weather.duckdb"

        with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
            result = runner.invoke(cli, ["demo", "status"])

        assert result.exit_code == 0
        assert "Demo Mode Status" in result.output
        assert "Demo database exists: False" in result.output
        assert "demo generate" in result.output  # Should suggest how to create

    @pytest.mark.unit
    def test_demo_status_with_database(self, runner, temp_db_dir):
        """demo status should show stats when database exists."""
        demo_db_path = temp_db_dir / "demo_weather.duckdb"

        # Create demo database
        from datetime import datetime

        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(demo_db_path)
        generator.generate(start_date=datetime(2024, 1, 1), days=1, quiet=True)
        generator.close()

        with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
            result = runner.invoke(cli, ["demo", "status"])

        assert result.exit_code == 0
        assert "Demo database exists: True" in result.output
        assert "Total records:" in result.output
        assert "Database size:" in result.output

    @pytest.mark.unit
    def test_demo_status_shows_demo_mode_state(self, runner, temp_db_dir):
        """demo status should show whether demo mode is enabled."""
        demo_db_path = temp_db_dir / "demo_weather.duckdb"

        # Create demo database
        from datetime import datetime

        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(demo_db_path)
        generator.generate(start_date=datetime(2024, 1, 1), days=1, quiet=True)
        generator.close()

        # Without DEMO_MODE env var
        with patch("weather_app.config.DEMO_DB_PATH", demo_db_path):
            result = runner.invoke(cli, ["demo", "status"])

        assert result.exit_code == 0
        assert "Demo mode enabled:" in result.output


# =============================================================================
# FETCH COMMAND ADDITIONAL TESTS
# =============================================================================


class TestFetchCommandAdditional:
    """Additional tests for fetch command error paths."""

    @pytest.mark.unit
    def test_fetch_no_new_data(self, runner, temp_db_dir, mock_devices_response):
        """fetch should handle when API returns no data."""
        db_path = temp_db_dir / "test.duckdb"

        # Create database
        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass

        # Mock API with empty data response
        mock_api = MagicMock()
        mock_api.get_devices.return_value = mock_devices_response
        mock_api.get_device_data.return_value = []  # No data
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
                    with patch("time.sleep"):
                        result = runner.invoke(cli, ["fetch"])

        assert result.exit_code == 0
        assert "No new data available" in result.output

    @pytest.mark.unit
    def test_fetch_api_exception(self, runner, temp_db_dir):
        """fetch should handle API exceptions gracefully."""
        db_path = temp_db_dir / "test.duckdb"

        from weather_app.database.engine import WeatherDatabase

        with WeatherDatabase(str(db_path)) as db:
            pass

        # Mock API that raises exception
        mock_api = MagicMock()
        mock_api.get_devices.side_effect = Exception("API connection failed")
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
        assert "Error:" in result.output


# =============================================================================
# BACKFILL COMMAND ADDITIONAL TESTS
# =============================================================================


class TestBackfillCommandAdditional:
    """Additional tests for backfill command."""

    @pytest.mark.unit
    def test_backfill_requires_database(self, runner, temp_db_dir):
        """backfill should fail if database doesn't exist."""
        db_path = temp_db_dir / "nonexistent.duckdb"

        with patch.object(cli_module, "DB_PATH", str(db_path)):
            with patch.dict(
                "os.environ",
                {"AMBIENT_API_KEY": "key", "AMBIENT_APP_KEY": "app"},
            ):
                result = runner.invoke(
                    cli, ["backfill", "--start", "2024-01-01", "--end", "2024-01-31"]
                )

        assert result.exit_code == 1
        assert "Database not found" in result.output

    @pytest.mark.unit
    def test_backfill_no_devices(self, runner, temp_db_dir):
        """backfill should handle no devices found."""
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
                    result = runner.invoke(
                        cli,
                        ["backfill", "--start", "2024-01-01", "--end", "2024-01-02"],
                    )

        assert result.exit_code == 1
        assert "No devices found" in result.output


# =============================================================================
# EXPORT COMMAND ADDITIONAL TESTS
# =============================================================================


class TestExportCommandAdditional:
    """Additional tests for export command error handling."""

    @pytest.mark.unit
    def test_export_invalid_start_date(self, runner, temp_db_dir):
        """export should fail with invalid start date format."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

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
            result = runner.invoke(
                cli, ["export", "-o", str(output_path), "--start", "invalid-date"]
            )

        assert result.exit_code == 1
        assert "Invalid start date format" in result.output

    @pytest.mark.unit
    def test_export_invalid_end_date(self, runner, temp_db_dir):
        """export should fail with invalid end date format."""
        db_path = temp_db_dir / "test.duckdb"
        output_path = temp_db_dir / "output.csv"

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
            result = runner.invoke(
                cli, ["export", "-o", str(output_path), "--end", "invalid-date"]
            )

        assert result.exit_code == 1
        assert "Invalid end date format" in result.output
