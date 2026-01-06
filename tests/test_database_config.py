#!/usr/bin/env python3
"""
Test Database Configuration
Verifies the test database is properly configured and accessible
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_app.config import get_db_info
from weather_app.database import WeatherRepository


def test_database_config():
    """Test database configuration and accessibility"""
    print("=" * 70)
    print("Database Configuration Test")
    print("=" * 70)
    print()

    # Show configuration
    db_info = get_db_info()
    print("Current Configuration:")
    print(f"  Mode: {db_info['mode']}")
    print(f"  Database Path: {db_info['database_path']}")
    print(f"  Database Engine: {db_info['database_engine']}")
    print(f"  Using Test DB: {db_info['using_test_db']}")
    print()

    # Test database access
    print("Testing Database Access...")
    print("-" * 70)

    try:
        # Get stats
        stats = WeatherRepository.get_stats()
        print("[OK] Database accessible")
        print(f"  Total records: {stats.get('total_records', 0):,}")
        print(
            f"  Date range: {stats.get('min_date', 'N/A')} to {stats.get('max_date', 'N/A')}"
        )

        if stats.get("total_records", 0) > 0:
            print(f"  Date range days: {stats.get('date_range_days', 'N/A')}")
        print()

        # Get latest reading
        print("Testing Latest Reading Query...")
        print("-" * 70)
        latest = WeatherRepository.get_latest_reading()

        if latest:
            print("[OK] Latest reading retrieved")
            print(f"  Date: {latest.get('date', 'N/A')}")
            print(f"  Temperature: {latest.get('tempf', 'N/A')}°F")
            print(f"  Humidity: {latest.get('humidity', 'N/A')}%")
            print(f"  Wind Speed: {latest.get('windspeedmph', 'N/A')} mph")
        else:
            print("[ERROR] No data found in database")
        print()

        # Test pagination
        print("Testing Pagination (10 records)...")
        print("-" * 70)
        records = WeatherRepository.get_all_readings(limit=10, order="desc")
        print(f"[OK] Retrieved {len(records)} records")
        if records:
            print(f"  First record date: {records[0].get('date', 'N/A')}")
            print(f"  Last record date: {records[-1].get('date', 'N/A')}")
        print()

        # Summary
        print("=" * 70)
        print("Database Test Summary")
        print("=" * 70)
        print("[OK] All database operations successful")
        print()

        if db_info["using_test_db"]:
            print("NOTE: Using TEST database - perfect for frontend development!")
            print("To switch to PRODUCTION database, set USE_TEST_DB=false in .env")
        else:
            print("NOTE: Using PRODUCTION database")
            print("To switch to TEST database, set USE_TEST_DB=true in .env")

        return True

    except Exception as e:
        print(f"[ERROR] Database error: {str(e)}")
        print()
        print("=" * 70)
        print("Troubleshooting")
        print("=" * 70)
        print("1. Make sure the database file exists:")
        print(f"   {db_info['database_path']}")
        print("2. If using test database, generate it first:")
        print("   python tests/generate_test_data.py --clear")
        print("3. Check .env file configuration")
        return False


if __name__ == "__main__":
    success = test_database_config()
    sys.exit(0 if success else 1)
