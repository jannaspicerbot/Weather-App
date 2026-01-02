"""
Command-line interface for Weather App
"""
import click
import sqlite3
from pathlib import Path
from datetime import datetime
import csv
import sys
import os
from dotenv import load_dotenv

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from weather_app.config import DB_PATH, get_db_info
from weather_app.fetch import AmbientWeatherAPI, AmbientWeatherDB

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version='1.0.0', prog_name='weather-app')
def cli():
    """Weather App - Ambient Weather data collection and visualization"""
    pass


@cli.command()
@click.option('--force', is_flag=True, help='Drop existing tables and recreate')
def init_db(force):
    """Initialize the weather database"""
    db_path = Path(DB_PATH)

    click.echo(f"Initializing database at: {db_path}")

    # Check if database already exists
    if db_path.exists() and not force:
        click.echo(f"❌ Database already exists at {db_path}")
        click.echo("Use --force to drop and recreate the database")
        sys.exit(1)

    # Create database directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Connect and create schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    if force:
        click.echo("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS weather_data")

    click.echo("Creating weather_data table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dateutc INTEGER UNIQUE NOT NULL,
            date TEXT,
            tempf REAL,
            humidity INTEGER,
            baromabsin REAL,
            baromrelin REAL,
            windspeedmph REAL,
            winddir INTEGER,
            windgustmph REAL,
            maxdailygust REAL,
            hourlyrainin REAL,
            eventrain IN REAL,
            dailyrainin REAL,
            weeklyrainin REAL,
            monthlyrainin REAL,
            yearlyrainin REAL,
            totalrainin REAL,
            solarradiation REAL,
            uv INTEGER,
            feelsLike REAL,
            dewPoint REAL,
            feelsLikein REAL,
            dewPointin REAL,
            lastRain TEXT,
            tz TEXT,
            raw_json TEXT
        )
    ''')

    # Create indexes for common queries
    click.echo("Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON weather_data(date)')

    conn.commit()
    conn.close()

    click.echo(f"✅ Database initialized successfully at {db_path}")
    click.echo(f"📊 Database info: {get_db_info()['mode']} mode")


@cli.command()
@click.option('--limit', default=1, type=int, help='Number of latest records to fetch (default: 1)')
def fetch(limit):
    """Fetch latest weather data from Ambient Weather API"""
    # Get API credentials from environment
    api_key = os.getenv('AMBIENT_API_KEY')
    app_key = os.getenv('AMBIENT_APP_KEY')

    if not api_key or not app_key:
        click.echo("❌ Error: API credentials not found!")
        click.echo("Please set environment variables:")
        click.echo("  AMBIENT_API_KEY - Your API key")
        click.echo("  AMBIENT_APP_KEY - Your Application key")
        click.echo("\nOr create a .env file with these variables.")
        sys.exit(1)

    db_path = Path(DB_PATH)
    if not db_path.exists():
        click.echo(f"❌ Database not found at {db_path}")
        click.echo("Run 'weather-app init-db' first")
        sys.exit(1)

    try:
        # Initialize API client
        click.echo(f"Fetching {limit} latest weather record(s)...")
        api = AmbientWeatherAPI(api_key, app_key)

        # Get devices
        devices = api.get_devices()
        if not devices:
            click.echo("❌ No devices found in your account")
            sys.exit(1)

        device = devices[0]
        mac = device['macAddress']
        device_name = device['info']['name']

        click.echo(f"📡 Fetching from device: {device_name}")

        # Fetch data
        data = api.get_device_data(mac, limit=limit)

        if not data:
            click.echo("⚠️  No new data available")
            return

        # Save to database
        with AmbientWeatherDB(db_path) as db:
            inserted, skipped = db.insert_data(data)

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
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--start', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end', required=True, help='End date (YYYY-MM-DD)')
@click.option('--batch-size', default=288, type=int, help='Records per API call (default: 288)')
@click.option('--delay', default=1.0, type=float, help='Delay between API calls in seconds (default: 1.0)')
def backfill(start, end, batch_size, delay):
    """Backfill historical weather data for a date range"""
    # Validate dates
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError as e:
        click.echo(f"❌ Invalid date format: {e}")
        click.echo("Use YYYY-MM-DD format (e.g., 2024-01-01)")
        sys.exit(1)

    if start_date > end_date:
        click.echo("❌ Start date must be before end date")
        sys.exit(1)

    # Get API credentials
    api_key = os.getenv('AMBIENT_API_KEY')
    app_key = os.getenv('AMBIENT_APP_KEY')

    if not api_key or not app_key:
        click.echo("❌ Error: API credentials not found!")
        click.echo("Please set environment variables:")
        click.echo("  AMBIENT_API_KEY - Your API key")
        click.echo("  AMBIENT_APP_KEY - Your Application key")
        sys.exit(1)

    db_path = Path(DB_PATH)
    if not db_path.exists():
        click.echo(f"❌ Database not found at {db_path}")
        click.echo("Run 'weather-app init-db' first")
        sys.exit(1)

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
            click.echo("❌ No devices found in your account")
            sys.exit(1)

        device = devices[0]
        mac = device['macAddress']
        device_name = device['info']['name']

        click.echo(f"📡 Fetching from device: {device_name}\n")

        # Progress callback
        total_inserted = 0
        total_skipped = 0

        def progress_callback(records_fetched, requests_made):
            nonlocal total_inserted, total_skipped
            click.echo(f"Progress: {records_fetched} records fetched, {requests_made} API requests made")

        # Fetch all historical data
        with AmbientWeatherDB(db_path) as db:
            # Initialize backfill progress
            db.init_backfill_progress(start, end)

            # Fetch data using the API client's built-in pagination
            all_data = api.fetch_all_historical_data(
                mac,
                start_date=start_date,
                end_date=end_date,
                batch_size=batch_size,
                delay=delay,
                progress_callback=progress_callback
            )

            if not all_data:
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
                status='completed'
            )

        click.echo(f"\n✅ Backfill completed!")
        click.echo(f"   Total records: {len(all_data)}")
        click.echo(f"   Inserted: {total_inserted}")
        click.echo(f"   Skipped (duplicates): {total_skipped}")

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Backfill interrupted by user")
        click.echo("Progress has been saved. Run the command again to resume.")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        with AmbientWeatherDB(db_path) as db:
            db.update_backfill_progress(
                current_position=0,
                records_fetched=0,
                requests_made=0,
                status='failed',
                error=str(e)
            )
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', required=True, type=click.Path(), help='Output CSV file path')
@click.option('--start', help='Start date (YYYY-MM-DD) - optional')
@click.option('--end', help='End date (YYYY-MM-DD) - optional')
@click.option('--limit', type=int, help='Maximum number of records to export')
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
            datetime.strptime(start, '%Y-%m-%d')
            conditions.append("date >= ?")
            params.append(start)
        except ValueError:
            click.echo(f"❌ Invalid start date format: {start}")
            sys.exit(1)

    if end:
        try:
            datetime.strptime(end, '%Y-%m-%d')
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

    # Execute query and export
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(query, params)
    rows = cursor.fetchall()

    if not rows:
        click.echo("⚠️  No data found matching criteria")
        conn.close()
        return

    # Write to CSV
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(row))

    conn.close()

    click.echo(f"✅ Exported {len(rows)} records to {output_path}")


@cli.command()
def info():
    """Show database and configuration information"""
    db_info = get_db_info()
    db_path = Path(DB_PATH)

    click.echo("=" * 60)
    click.echo("Weather App - Configuration Info")
    click.echo("=" * 60)
    click.echo(f"Database mode: {db_info['mode']}")
    click.echo(f"Database path: {db_info['database_path']}")
    click.echo(f"Database exists: {db_path.exists()}")

    if db_path.exists():
        # Get record count
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            count = cursor.fetchone()[0]
            click.echo(f"Total records: {count:,}")

            if count > 0:
                cursor.execute("SELECT MIN(date), MAX(date) FROM weather_data")
                min_date, max_date = cursor.fetchone()
                click.echo(f"Date range: {min_date} to {max_date}")
        except sqlite3.OperationalError:
            click.echo("⚠️  Database exists but weather_data table not found")
            click.echo("Run 'weather-app init-db' to create the schema")
        finally:
            conn.close()
    else:
        click.echo("⚠️  Run 'weather-app init-db' to create the database")

    click.echo("=" * 60)


if __name__ == '__main__':
    cli()
