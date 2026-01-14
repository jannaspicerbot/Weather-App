#!/usr/bin/env python3
"""
Import Ambient Weather CSV files into DuckDB database

This script imports monthly CSV files downloaded from Ambient Weather's website
into the local DuckDB database.
"""

import csv
import glob
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from weather_app.config import DB_PATH
from weather_app.database.engine import WeatherDatabase


def parse_csv_row(row: dict) -> dict:
    """
    Convert CSV row to database format

    CSV columns from Ambient Weather:
    - Date (ISO format with timezone)
    - Outdoor Temperature (°F) → tempf
    - Feels Like (°F) → feelsLike
    - Dew Point (°F) → dewPoint
    - Wind Speed (mph) → windspeedmph
    - Wind Gust (mph) → windgustmph
    - Max Daily Gust (mph) → maxdailygust
    - Wind Direction (°) → winddir
    - Rain Rate (in/hr) → hourlyrainin
    - Event Rain (in) → eventrain
    - Daily Rain (in) → dailyrainin
    - Weekly Rain (in) → weeklyrainin
    - Monthly Rain (in) → monthlyrainin
    - Yearly Rain (in) → yearlyrainin
    - Relative Pressure (inHg) → baromrelin
    - Absolute Pressure (inHg) → baromabsin
    - Humidity (%) → humidity
    - Ultra-Violet Radiation Index → uv
    - Solar Radiation (W/m^2) → solarradiation
    """

    # Parse date field
    date_str = row.get("Date", "")
    if not date_str:
        return None

    try:
        # Parse ISO datetime with timezone
        dt = datetime.fromisoformat(date_str)
        # Convert to UTC timestamp in milliseconds
        dateutc = int(dt.timestamp() * 1000)
        # Format as ISO string without timezone for display
        date_display = dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        print(f"Warning: Could not parse date: {date_str}")
        return None

    def get_float(field_name: str) -> float | None:
        """Get float value from CSV, return None if empty or invalid"""
        value = row.get(field_name, "").strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None

    def get_int(field_name: str) -> int | None:
        """Get integer value from CSV, return None if empty or invalid"""
        value = row.get(field_name, "").strip()
        if not value:
            return None
        try:
            return int(float(value))  # Convert through float to handle decimals
        except ValueError:
            return None

    # Map CSV columns to database columns
    data = {
        "dateutc": dateutc,
        "date": date_display,
        "tempf": get_float("Outdoor Temperature (°F)"),
        "feelsLike": get_float("Feels Like (°F)"),
        "dewPoint": get_float("Dew Point (°F)"),
        "windspeedmph": get_float("Wind Speed (mph)"),
        "windgustmph": get_float("Wind Gust (mph)"),
        "maxdailygust": get_float("Max Daily Gust (mph)"),
        "winddir": get_int("Wind Direction (°)"),
        "hourlyrainin": get_float("Rain Rate (in/hr)"),
        "eventrain": get_float("Event Rain (in)"),
        "dailyrainin": get_float("Daily Rain (in)"),
        "weeklyrainin": get_float("Weekly Rain (in)"),
        "monthlyrainin": get_float("Monthly Rain (in)"),
        "yearlyrainin": get_float("Yearly Rain (in)"),
        "baromrelin": get_float("Relative Pressure (inHg)"),
        "baromabsin": get_float("Absolute Pressure (inHg)"),
        "humidity": get_int("Humidity (%)"),
        "uv": get_int("Ultra-Violet Radiation Index"),
        "solarradiation": get_float("Solar Radiation (W/m^2)"),
    }

    return data


def import_csv_file(csv_path: str, db: WeatherDatabase) -> tuple[int, int]:
    """
    Import a single CSV file into the database

    Returns:
        Tuple of (imported_count, skipped_count)
    """
    print(f"Importing {os.path.basename(csv_path)}...")

    imported = 0
    skipped = 0
    batch = []
    batch_size = 1000  # Insert in batches for performance

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            data = parse_csv_row(row)
            if data:
                batch.append(data)

                # Insert batch when it reaches batch_size
                if len(batch) >= batch_size:
                    inserted, skip = db.insert_data(batch)
                    imported += inserted
                    skipped += skip
                    batch = []

        # Insert remaining records
        if batch:
            inserted, skip = db.insert_data(batch)
            imported += inserted
            skipped += skip

    print(f"  Imported: {imported}, Skipped: {skipped}")
    return imported, skipped


def main():
    """Import all CSV files from data/downloads/ directory"""

    # Find all CSV files
    csv_dir = Path(__file__).parent.parent / "data" / "downloads"
    csv_files = sorted(glob.glob(str(csv_dir / "*.csv")))

    if not csv_files:
        print(f"No CSV files found in {csv_dir}")
        print("Expected files like: ambient-weather-YYYYMMDD-YYYYMMDD.csv")
        return 1

    print(f"Found {len(csv_files)} CSV files")
    print(f"Database: {DB_PATH}")
    print()

    total_imported = 0
    total_skipped = 0

    with WeatherDatabase(DB_PATH) as db:
        for csv_file in csv_files:
            imported, skipped = import_csv_file(csv_file, db)
            total_imported += imported
            total_skipped += skipped

    print()
    print("=" * 60)
    print("Import complete!")
    print(f"Total imported: {total_imported}")
    print(f"Total skipped: {total_skipped} (duplicates)")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
