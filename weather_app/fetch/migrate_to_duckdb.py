"""
Migration script to convert SQLite database to DuckDB
Transfers all weather_data and backfill_progress records from SQLite to DuckDB
"""
import click
from pathlib import Path
from weather_app.fetch.database import AmbientWeatherDB
from weather_app.fetch.database_duckdb import AmbientWeatherDuckDB
from weather_app.config import DB_PATH


def migrate_sqlite_to_duckdb(sqlite_path: str, duckdb_path: str = None, batch_size: int = 1000):
    """
    Migrate data from SQLite database to DuckDB database.

    Args:
        sqlite_path: Path to the SQLite database file
        duckdb_path: Path to the DuckDB database file (optional)
        batch_size: Number of records to process at a time

    Returns:
        Tuple of (total_records_migrated, total_skipped)
    """
    if duckdb_path is None:
        duckdb_path = sqlite_path.replace('.db', '.duckdb')

    click.echo(f"📊 Migrating from SQLite to DuckDB")
    click.echo(f"   Source: {sqlite_path}")
    click.echo(f"   Target: {duckdb_path}")
    click.echo()

    # Check if source database exists
    if not Path(sqlite_path).exists():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    total_migrated = 0
    total_skipped = 0

    # Open both databases
    with AmbientWeatherDB(sqlite_path) as sqlite_db:
        with AmbientWeatherDuckDB(duckdb_path) as duckdb_db:
            # Get total record count from SQLite
            stats = sqlite_db.get_stats()
            total_records = stats['total_records']

            if total_records == 0:
                click.echo("⚠️  No records found in SQLite database")
                return 0, 0

            click.echo(f"📦 Found {total_records} records to migrate")
            click.echo()

            # Migrate weather_data in batches
            offset = 0
            with click.progressbar(length=total_records, label='Migrating weather data') as bar:
                while offset < total_records:
                    # Fetch batch from SQLite
                    batch_data = sqlite_db.get_data(
                        limit=batch_size,
                        order_by=f'dateutc ASC LIMIT {batch_size} OFFSET {offset}'
                    )

                    if not batch_data:
                        break

                    # Insert batch into DuckDB
                    inserted, skipped = duckdb_db.insert_data(batch_data)
                    total_migrated += inserted
                    total_skipped += skipped

                    bar.update(len(batch_data))
                    offset += batch_size

            # Migrate backfill_progress records
            click.echo()
            click.echo("📋 Migrating backfill progress records...")

            # Get all backfill progress records from SQLite
            sqlite_db.cursor.execute('SELECT * FROM backfill_progress')
            progress_records = sqlite_db.cursor.fetchall()

            if progress_records:
                for record in progress_records:
                    # Insert into DuckDB
                    record_dict = dict(record)
                    duckdb_db.conn.execute('''
                        INSERT INTO backfill_progress
                        (id, start_date, end_date, current_date, status, total_records, skipped_records, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', [
                        record_dict['id'],
                        record_dict['start_date'],
                        record_dict['end_date'],
                        record_dict['current_date'],
                        record_dict['status'],
                        record_dict['total_records'],
                        record_dict['skipped_records'],
                        record_dict['created_at'],
                        record_dict['updated_at']
                    ])

                click.echo(f"   Migrated {len(progress_records)} backfill progress record(s)")

    click.echo()
    click.echo("✅ Migration complete!")
    click.echo(f"   Records migrated: {total_migrated}")
    click.echo(f"   Records skipped: {total_skipped}")
    click.echo()

    # Verify migration
    with AmbientWeatherDuckDB(duckdb_path) as duckdb_db:
        duckdb_stats = duckdb_db.get_stats()
        click.echo("📊 DuckDB Database Statistics:")
        click.echo(f"   Total records: {duckdb_stats['total_records']}")
        if duckdb_stats['min_date']:
            click.echo(f"   Date range: {duckdb_stats['min_date']} to {duckdb_stats['max_date']}")
            click.echo(f"   Temperature: {duckdb_stats['min_temperature']:.1f}°F to {duckdb_stats['max_temperature']:.1f}°F (avg: {duckdb_stats['avg_temperature']:.1f}°F)")
            click.echo(f"   Humidity: {duckdb_stats['min_humidity']}% to {duckdb_stats['max_humidity']}% (avg: {duckdb_stats['avg_humidity']:.1f}%)")

    return total_migrated, total_skipped


@click.command()
@click.option(
    '--sqlite-path',
    default=DB_PATH,
    help='Path to SQLite database file (default: ambient_weather.db)'
)
@click.option(
    '--duckdb-path',
    default=None,
    help='Path to DuckDB database file (default: replaces .db with .duckdb)'
)
@click.option(
    '--batch-size',
    default=1000,
    type=int,
    help='Number of records to process at a time (default: 1000)'
)
@click.option(
    '--backup-sqlite',
    is_flag=True,
    help='Create a backup of the SQLite database before migration'
)
def migrate(sqlite_path, duckdb_path, batch_size, backup_sqlite):
    """
    Migrate weather data from SQLite to DuckDB database.

    This command transfers all weather_data and backfill_progress records
    from the SQLite database to a new DuckDB database for improved
    analytical performance (10-100x faster for aggregations).
    """
    try:
        if backup_sqlite:
            import shutil
            backup_path = f"{sqlite_path}.backup"
            click.echo(f"💾 Creating backup: {backup_path}")
            shutil.copy2(sqlite_path, backup_path)
            click.echo()

        migrate_sqlite_to_duckdb(sqlite_path, duckdb_path, batch_size)

    except FileNotFoundError as e:
        click.echo(f"❌ Error: {e}")
        click.echo()
        click.echo("Make sure the SQLite database exists before running migration.")
        exit(1)

    except Exception as e:
        click.echo(f"❌ Migration failed: {e}")
        exit(1)


if __name__ == '__main__':
    migrate()
