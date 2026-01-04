"""
Command-line interface for Weather App
"""

import click
from pathlib import Path
from datetime import datetime
import csv
import sys
import os
import time
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from weather_app.config import DB_PATH, get_db_info
from weather_app.api import AmbientWeatherAPI
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
    with WeatherDatabase(str(db_path)) as db:
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

        # Initialize API client
        click.echo(f"Fetching {limit} latest weather record(s)...")
        api = AmbientWeatherAPI(api_key, app_key)

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

        # Fetch data
        data = api.get_device_data(mac, limit=limit)

        if not data:
            logger.info("fetch_completed", records=0, reason="no_new_data")
            click.echo("⚠️  No new data available")
            return

        # Save to database
        with WeatherDatabase(db_path) as db:
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
            click.echo(f"\n📊 Latest reading:")
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
        # Initialize API client
        api = AmbientWeatherAPI(api_key, app_key)

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

        # Progress callback
        total_inserted = 0
        total_skipped = 0

        def progress_callback(records_fetched, requests_made):
            nonlocal total_inserted, total_skipped
            logger.info(
                "backfill_progress",
                records_fetched=records_fetched,
                requests_made=requests_made,
            )
            click.echo(
                f"Progress: {records_fetched} records fetched, {requests_made} API requests made"
            )

        # Fetch all historical data
        with WeatherDatabase(db_path) as db:
            # Initialize backfill progress
            db.init_backfill_progress(start, end)

            # Fetch data using the API client's built-in pagination
            all_data = api.fetch_all_historical_data(
                mac,
                start_date=start_date,
                end_date=end_date,
                batch_size=batch_size,
                delay=delay,
                progress_callback=progress_callback,
            )

            if not all_data:
                logger.info("backfill_completed", records=0, reason="no_data_found")
                click.echo("\n⚠️  No data found for the specified date range")
                db.clear_backfill_progress()
                return

            # Insert data in batches
            click.echo(f"\n💾 Saving {len(all_data)} records to database...")
            inserted, skipped = db.insert_data(all_data)

            total_inserted = inserted
            total_skipped = skipped

            # Update progress as completed
            db.update_backfill_progress(
                current_position=int(start_date.timestamp() * 1000),
                records_fetched=len(all_data),
                requests_made=0,  # Tracked in progress_callback
                status="completed",
            )

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "backfill_completed",
            total_records=len(all_data),
            inserted=total_inserted,
            skipped=total_skipped,
            duration_ms=round(duration_ms, 2),
        )

        click.echo(f"\n✅ Backfill completed!")
        click.echo(f"   Total records: {len(all_data)}")
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
        with WeatherDatabase(db_path) as db:
            db.update_backfill_progress(
                current_position=0,
                records_fetched=0,
                requests_made=0,
                status="failed",
                error=str(e),
            )
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
        result = db.conn.execute(query, params).fetchall()

        if not result:
            click.echo("⚠️  No data found matching criteria")
            return

        # Convert to list of dictionaries
        columns = [desc[0] for desc in db.conn.description]
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
                result = db.conn.execute("SELECT COUNT(*) FROM weather_data").fetchone()
                count = result[0]
                click.echo(f"Total records: {count:,}")

                if count > 0:
                    result = db.conn.execute(
                        "SELECT MIN(date), MAX(date) FROM weather_data"
                    ).fetchone()
                    min_date, max_date = result
                    click.echo(f"Date range: {min_date} to {max_date}")

            logger.info("info_command_completed", total_records=count)
        except Exception as e:
            logger.error("info_command_failed", error=str(e))
            click.echo("⚠️  Database exists but weather_data table not found")
            click.echo("Run 'weather-app init-db' to create the schema")
    else:
        click.echo("⚠️  Run 'weather-app init-db' to create the database")

    click.echo("=" * 60)


if __name__ == "__main__":
    cli()
