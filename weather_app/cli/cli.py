"""
Command-line interface for Weather App
"""

import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import click
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from weather_app.api import AmbientWeatherAPI
from weather_app.config import DB_PATH, get_db_info
from weather_app.database import WeatherDatabase
from weather_app.logging_config import get_logger, log_cli_command

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = get_logger(__name__)


@click.group()
@click.version_option(version="1.0.0", prog_name="weather-app")
def cli():
    """Weather App - Ambient Weather data collection and visualization"""
    pass


@cli.command()
@click.option("--force", is_flag=True, help="Drop existing tables and recreate")
def init_db(force):
    """Initialize the weather database"""
    start_time = time.time()
    db_path = Path(DB_PATH)

    logger.info("init_db_started", db_path=str(db_path), force=force)
    click.echo(f"Initializing DuckDB database at: {db_path}")

    # Check if database already exists
    if db_path.exists() and not force:
        logger.warning("init_db_failed", reason="database_exists", db_path=str(db_path))
        click.echo(f"❌ Database already exists at {db_path}")
        click.echo("Use --force to drop and recreate the database")
        sys.exit(1)

    # Create database directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # If force, delete existing database
    if force and db_path.exists():
        logger.info("dropping_existing_database", db_path=str(db_path))
        click.echo("Dropping existing database...")
        db_path.unlink()

    # Create database and tables using WeatherDatabase context manager
    click.echo("Creating weather_data and backfill_progress tables...")
    with WeatherDatabase(str(db_path)):
        # Tables are created automatically in __enter__
        pass

    duration_ms = (time.time() - start_time) * 1000
    log_cli_command(
        logger,
        "init_db",
        {"force": force, "db_path": str(db_path)},
        success=True,
        duration_ms=duration_ms,
    )

    click.echo(f"✅ Database initialized successfully at {db_path}")
    click.echo(f"📊 Database engine: {get_db_info()['database_engine']}")
    click.echo(f"📊 Database mode: {get_db_info()['mode']}")


@cli.command()
@click.option(
    "--limit",
    default=1,
    type=int,
    help="Number of latest records to fetch (default: 1)",
)
def fetch(limit):
    """Fetch latest weather data from Ambient Weather API"""
    start_time = time.time()

    # Get API credentials from environment
    api_key = os.getenv("AMBIENT_API_KEY")
    app_key = os.getenv("AMBIENT_APP_KEY")

    if not api_key or not app_key:
        logger.error("fetch_failed", reason="missing_credentials")
        click.echo("❌ Error: API credentials not found!")
        click.echo("Please set environment variables:")
        click.echo("  AMBIENT_API_KEY - Your API key")
        click.echo("  AMBIENT_APP_KEY - Your Application key")
        click.echo("\nOr create a .env file with these variables.")
        sys.exit(1)

    db_path = Path(DB_PATH)
    if not db_path.exists():
        logger.error("fetch_failed", reason="database_not_found", db_path=str(db_path))
        click.echo(f"❌ Database not found at {db_path}")
        click.echo("Run 'weather-app init-db' first")
        sys.exit(1)

    try:
        logger.info("fetch_started", limit=limit)

        # Initialize API client with context manager for proper cleanup
        click.echo(f"Fetching {limit} latest weather record(s)...")
        with AmbientWeatherAPI(api_key, app_key) as api:
            # Get devices
            devices = api.get_devices()
            if not devices:
                logger.warning("fetch_failed", reason="no_devices")
                click.echo("❌ No devices found in your account")
                sys.exit(1)

            device = devices[0]
            mac = device["macAddress"]
            device_name = device["info"]["name"]

            logger.info("device_found", mac=mac, device_name=device_name)
            click.echo(f"📡 Fetching from device: {device_name}")

            # Add delay to respect rate limits (1 request per second)
            time.sleep(1.1)

            # Fetch data
            data = api.get_device_data(mac, limit=limit)

        if not data:
            logger.info("fetch_completed", records=0, reason="no_new_data")
            click.echo("⚠️  No new data available")
            return

        # Save to database
        with WeatherDatabase(str(db_path)) as db:
            inserted, skipped = db.insert_data(data)

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "fetch_completed",
            records=len(data),
            inserted=inserted,
            skipped=skipped,
            duration_ms=round(duration_ms, 2),
        )

        click.echo(f"✅ Fetched {len(data)} record(s)")
        click.echo(f"   Inserted: {inserted}")
        click.echo(f"   Skipped (duplicates): {skipped}")

        # Show latest record
        if data:
            latest = data[0]
            click.echo("\n📊 Latest reading:")
            click.echo(f"   Date: {latest.get('date', 'N/A')}")
            click.echo(f"   Temp: {latest.get('tempf', 'N/A')}°F")
            click.echo(f"   Humidity: {latest.get('humidity', 'N/A')}%")
            click.echo(f"   Wind: {latest.get('windspeedmph', 'N/A')} mph")

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error("fetch_failed", error=str(e), duration_ms=round(duration_ms, 2))
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--start", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--end", required=True, help="End date (YYYY-MM-DD)")
@click.option(
    "--batch-size", default=288, type=int, help="Records per API call (default: 288)"
)
@click.option(
    "--delay",
    default=1.0,
    type=float,
    help="Delay between API calls in seconds (default: 1.0)",
)
def backfill(start, end, batch_size, delay):
    """Backfill historical weather data for a date range"""
    start_time = time.time()

    # Validate dates
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
    except ValueError as e:
        logger.error("backfill_failed", reason="invalid_date_format", error=str(e))
        click.echo(f"❌ Invalid date format: {e}")
        click.echo("Use YYYY-MM-DD format (e.g., 2024-01-01)")
        sys.exit(1)

    if start_date > end_date:
        logger.error(
            "backfill_failed", reason="invalid_date_range", start=start, end=end
        )
        click.echo("❌ Start date must be before end date")
        sys.exit(1)

    # Get API credentials
    api_key = os.getenv("AMBIENT_API_KEY")
    app_key = os.getenv("AMBIENT_APP_KEY")

    if not api_key or not app_key:
        logger.error("backfill_failed", reason="missing_credentials")
        click.echo("❌ Error: API credentials not found!")
        click.echo("Please set environment variables:")
        click.echo("  AMBIENT_API_KEY - Your API key")
        click.echo("  AMBIENT_APP_KEY - Your Application key")
        sys.exit(1)

    db_path = Path(DB_PATH)
    if not db_path.exists():
        logger.error(
            "backfill_failed", reason="database_not_found", db_path=str(db_path)
        )
        click.echo(f"❌ Database not found at {db_path}")
        click.echo("Run 'weather-app init-db' first")
        sys.exit(1)

    logger.info(
        "backfill_started",
        start_date=start,
        end_date=end,
        batch_size=batch_size,
        delay=delay,
    )

    click.echo(f"Backfilling data from {start} to {end}")
    click.echo(f"Batch size: {batch_size} records per API call")
    click.echo(f"Delay: {delay} seconds between calls")
    click.echo("")

    try:
        # Initialize API client with context manager for proper cleanup
        with AmbientWeatherAPI(api_key, app_key) as api:
            # Get devices
            devices = api.get_devices()
            if not devices:
                logger.warning("backfill_failed", reason="no_devices")
                click.echo("❌ No devices found in your account")
                sys.exit(1)

            device = devices[0]
            mac = device["macAddress"]
            device_name = device["info"]["name"]

            logger.info("device_found", mac=mac, device_name=device_name)
            click.echo(f"📡 Fetching from device: {device_name}\n")

            # Fetch and save data incrementally
            with WeatherDatabase(str(db_path)) as db:
                # Initialize backfill progress
                progress_id = db.init_backfill_progress(start, end)

                # Progress callback - shows fetch progress
                def progress_callback(records_fetched, requests_made):
                    logger.info(
                        "backfill_progress",
                        records_fetched=records_fetched,
                        requests_made=requests_made,
                    )
                    click.echo(
                        f"Progress: {records_fetched} records fetched, "
                        f"{requests_made} API requests made"
                    )

                # Batch callback - saves each batch immediately to database
                def batch_callback(batch_data):
                    inserted, skipped = db.insert_data(batch_data)
                    logger.debug(
                        "batch_saved",
                        batch_size=len(batch_data),
                        inserted=inserted,
                        skipped=skipped,
                    )
                    return inserted, skipped

                # Fetch data with incremental saving
                result = api.fetch_all_historical_data(
                    mac,
                    start_date=start_date,
                    end_date=end_date,
                    batch_size=batch_size,
                    delay=delay,
                    progress_callback=progress_callback,
                    batch_callback=batch_callback,
                )

                total_fetched, total_inserted, total_skipped = result

                if total_fetched == 0:
                    logger.info("backfill_completed", records=0, reason="no_data_found")
                    click.echo("\n⚠️  No data found for the specified date range")
                    db.clear_backfill_progress(progress_id)
                    return

                # Update progress as completed
                db.update_backfill_progress(
                    progress_id=progress_id,
                    current_date=end,
                    total_records=total_fetched,
                    skipped_records=total_skipped,
                    status="completed",
                )

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "backfill_completed",
            total_records=total_fetched,
            inserted=total_inserted,
            skipped=total_skipped,
            duration_ms=round(duration_ms, 2),
        )

        click.echo("\n✅ Backfill completed!")
        click.echo(f"   Total records: {total_fetched}")
        click.echo(f"   Inserted: {total_inserted}")
        click.echo(f"   Skipped (duplicates): {total_skipped}")

    except KeyboardInterrupt:
        duration_ms = (time.time() - start_time) * 1000
        logger.warning("backfill_interrupted", duration_ms=round(duration_ms, 2))
        click.echo("\n\n⚠️  Backfill interrupted by user")
        click.echo("Progress has been saved. Run the command again to resume.")
        sys.exit(1)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error("backfill_failed", error=str(e), duration_ms=round(duration_ms, 2))
        click.echo(f"\n❌ Error: {e}")
        # Note: progress_id may not be defined if error occurred before init
        # The backfill_progress table will retain any partial progress for debugging
        sys.exit(1)


@cli.command()
@click.option(
    "--output", "-o", required=True, type=click.Path(), help="Output CSV file path"
)
@click.option("--start", help="Start date (YYYY-MM-DD) - optional")
@click.option("--end", help="End date (YYYY-MM-DD) - optional")
@click.option("--limit", type=int, help="Maximum number of records to export")
def export(output, start, end, limit):
    """Export weather data to CSV"""
    db_path = Path(DB_PATH)

    if not db_path.exists():
        click.echo(f"❌ Database not found at {db_path}")
        click.echo("Run 'weather-app init-db' first")
        sys.exit(1)

    # Build query
    query = "SELECT * FROM weather_data"
    conditions = []
    params = []

    if start:
        try:
            datetime.strptime(start, "%Y-%m-%d")
            conditions.append("date >= ?")
            params.append(start)
        except ValueError:
            click.echo(f"❌ Invalid start date format: {start}")
            sys.exit(1)

    if end:
        try:
            datetime.strptime(end, "%Y-%m-%d")
            conditions.append("date <= ?")
            params.append(end)
        except ValueError:
            click.echo(f"❌ Invalid end date format: {end}")
            sys.exit(1)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY dateutc DESC"

    if limit:
        query += f" LIMIT {limit}"

    # Execute query and export using DuckDB
    with WeatherDatabase(str(db_path)) as db:
        conn = db._get_conn()
        result = conn.execute(query, params).fetchall()

        if not result:
            click.echo("⚠️  No data found matching criteria")
            return

        # Convert to list of dictionaries
        columns = [desc[0] for desc in conn.description]
        rows = [dict(zip(columns, row)) for row in result]

    # Write to CSV
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    logger.info("export_completed", output_path=str(output_path), records=len(rows))
    click.echo(f"✅ Exported {len(rows)} records to {output_path}")


@cli.command()
def info():
    """Show database and configuration information"""
    db_info = get_db_info()
    db_path = Path(DB_PATH)

    logger.info("info_command_started")

    click.echo("=" * 60)
    click.echo("Weather App - Configuration Info")
    click.echo("=" * 60)
    click.echo(f"Database mode: {db_info['mode']}")
    click.echo(f"Database path: {db_info['database_path']}")
    click.echo(f"Database exists: {db_path.exists()}")

    if db_path.exists():
        try:
            # Use WeatherDatabase to get record count
            with WeatherDatabase(str(db_path)) as db:
                conn = db._get_conn()
                result = conn.execute("SELECT COUNT(*) FROM weather_data").fetchone()
                count = result[0] if result else 0
                click.echo(f"Total records: {count:,}")

                if count > 0:
                    date_result = conn.execute(
                        "SELECT MIN(date), MAX(date) FROM weather_data"
                    ).fetchone()
                    if date_result:
                        min_date, max_date = date_result
                        click.echo(f"Date range: {min_date} to {max_date}")

            logger.info("info_command_completed", total_records=count)
        except Exception as e:
            logger.error("info_command_failed", error=str(e))
            click.echo("⚠️  Database exists but weather_data table not found")
            click.echo("Run 'weather-app init-db' to create the schema")
    else:
        click.echo("⚠️  Run 'weather-app init-db' to create the database")

    click.echo("=" * 60)


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
@click.option("--port", default=8000, type=int, help="Port to bind to (default: 8000)")
@click.option("--demo", is_flag=True, help="Start in demo mode with sample Seattle data")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def serve(host, port, demo, reload):
    """Start the Weather Dashboard web server"""
    import uvicorn

    logger.info(
        "serve_started",
        host=host,
        port=port,
        demo_mode=demo,
        reload=reload,
    )

    if demo:
        # Set demo mode environment variable
        os.environ["DEMO_MODE"] = "true"
        click.echo("Starting in demo mode...")

        # Check if demo database exists, auto-generate if missing
        from weather_app.config import DEMO_DB_PATH, DEMO_DEFAULT_DAYS
        from weather_app.demo import DemoService

        if not DEMO_DB_PATH.exists():
            click.echo(f"Demo database not found at {DEMO_DB_PATH}")
            click.echo("Generating demo data (this will take a few minutes)...")
            click.echo()

            service = DemoService(DEMO_DB_PATH)

            # Use click's progress bar for CLI feedback
            with click.progressbar(
                length=DEMO_DEFAULT_DAYS,
                label="Generating Seattle weather data",
                show_percent=True,
                show_pos=True,
            ) as bar:
                last_pos = 0

                def progress_callback(current_day: int, total_days: int) -> None:
                    nonlocal last_pos
                    bar.update(current_day - last_pos)
                    last_pos = current_day

                service.generate_if_missing(
                    days=DEMO_DEFAULT_DAYS,
                    progress_callback=progress_callback,
                )

            click.echo()
            click.echo("✅ Demo database generated successfully!")
            click.echo()

        click.echo(f"Using demo database: {DEMO_DB_PATH}")
    else:
        click.echo("Starting Weather Dashboard server...")

    click.echo(f"Server: http://{host}:{port}")
    click.echo("Press Ctrl+C to stop\n")

    # Use factory pattern to ensure config is loaded fresh with current env vars
    uvicorn.run(
        "weather_app.web.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@cli.group()
def demo():
    """Demo mode commands"""
    pass


@demo.command("generate")
@click.option(
    "--days",
    default=1095,
    type=int,
    help="Days of data to generate (default: 1095 = 3 years)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output database path (default: user data directory)",
)
@click.option(
    "--start-date",
    type=str,
    default=None,
    help="Start date YYYY-MM-DD (default: N days ago from today)",
)
@click.option(
    "--force",
    is_flag=True,
    help="Regenerate database even if it already exists",
)
def demo_generate(days, output, start_date, force):
    """Generate Seattle weather data for demo mode"""
    from datetime import timedelta

    from weather_app.config import DEMO_DB_PATH
    from weather_app.demo.data_generator import SeattleWeatherGenerator

    # Determine output path
    if output:
        db_path = Path(output)
    else:
        db_path = DEMO_DB_PATH

    # Determine start date
    if start_date:
        try:
            start = datetime.fromisoformat(start_date)
        except ValueError:
            click.echo(f"❌ Invalid date format: {start_date}")
            click.echo("Use YYYY-MM-DD format")
            sys.exit(1)
    else:
        # Default: start from N days ago so data ends "today"
        start = datetime.now() - timedelta(days=days)

    click.echo("=" * 60)
    click.echo("Seattle Demo Weather Data Generator")
    click.echo("=" * 60)
    click.echo(f"Database: {db_path}")
    click.echo(f"Start date: {start.strftime('%Y-%m-%d')}")
    click.echo(f"End date: {(start + timedelta(days=days)).strftime('%Y-%m-%d')}")
    click.echo(f"Days: {days}")
    click.echo(f"Estimated records: {days * 288:,}")
    click.echo()

    # Check if database exists
    if db_path.exists():
        if not force:
            click.echo(f"Demo database already exists at {db_path}")
            click.echo("Use --force to regenerate")
            sys.exit(0)
        click.echo("Removing existing demo database...")
        db_path.unlink()

    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate data with progress bar
    logger.info(
        "demo_generate_started",
        db_path=str(db_path),
        days=days,
        start_date=start.isoformat(),
    )

    generator = SeattleWeatherGenerator(db_path)

    # Use click's progress bar for CLI feedback
    with click.progressbar(
        length=days,
        label="Generating weather data",
        show_percent=True,
        show_pos=True,
    ) as bar:
        last_pos = 0

        def progress_callback(current_day: int, total_days: int) -> None:
            nonlocal last_pos
            bar.update(current_day - last_pos)
            last_pos = current_day

        records = generator.generate(
            start_date=start,
            days=days,
            progress_callback=progress_callback,
            quiet=True,
        )

    stats = generator.get_stats()
    generator.close()

    logger.info(
        "demo_generate_completed",
        records=records,
        db_size_mb=db_path.stat().st_size / 1024 / 1024,
    )

    click.echo()
    click.echo("=" * 60)
    click.echo("Generation Complete!")
    click.echo("=" * 60)
    click.echo(f"Total records: {stats['count']:,}")
    click.echo(f"Date range: {stats['min_date']} to {stats['max_date']}")
    click.echo(f"Database size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    click.echo()
    click.echo("✅ Demo database created successfully!")
    click.echo()
    click.echo("To start in demo mode:")
    click.echo("  weather-app serve --demo")


@demo.command("status")
def demo_status():
    """Check demo mode status and database"""
    from weather_app.config import DEMO_DB_PATH, get_demo_info

    info = get_demo_info()

    click.echo("=" * 60)
    click.echo("Demo Mode Status")
    click.echo("=" * 60)
    click.echo(f"Demo mode enabled: {info['demo_mode']}")
    click.echo(f"Demo database path: {info['demo_db_path']}")
    click.echo(f"Demo database exists: {info['demo_db_exists']}")

    if info["demo_db_exists"]:
        # Get database stats
        from weather_app.demo import DemoService

        service = DemoService(DEMO_DB_PATH)
        if service.is_available:
            stats = service.get_stats()
            click.echo(f"Total records: {stats['total_records']:,}")
            if stats["date_range_days"]:
                click.echo(f"Date range: {stats['date_range_days']} days")
            click.echo(
                f"Database size: {DEMO_DB_PATH.stat().st_size / 1024 / 1024:.1f} MB"
            )
            service.close()
        else:
            click.echo("⚠️  Demo database exists but could not be read")
    else:
        click.echo()
        click.echo("To create demo database:")
        click.echo("  weather-app demo generate")

    click.echo("=" * 60)


if __name__ == "__main__":
    cli()
