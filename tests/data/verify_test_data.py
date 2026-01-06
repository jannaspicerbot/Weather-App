#!/usr/bin/env python3
"""
Verify Test Data Quality
Checks the generated synthetic weather data for realistic patterns
"""

import duckdb


def verify_data(db_path="ambient_weather_test.duckdb"):
    """Verify the generated test data"""
    print("=" * 70)
    print("Test Data Quality Verification")
    print("=" * 70)
    print(f"Database: {db_path}\n")

    conn = duckdb.connect(db_path)

    # Basic stats
    print("1. Basic Statistics")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            COUNT(*) as total_records,
            MIN(date) as min_date,
            MAX(date) as max_date
        FROM weather_data
    """
    ).fetchone()
    print(f"   Total records: {result[0]:,}")
    print(f"   Date range: {result[1]} to {result[2]}")

    # Temperature stats
    print("\n2. Temperature Statistics")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            ROUND(AVG(tempf), 1) as avg_temp,
            ROUND(MIN(tempf), 1) as min_temp,
            ROUND(MAX(tempf), 1) as max_temp,
            ROUND(STDDEV(tempf), 1) as std_dev
        FROM weather_data
        WHERE tempf IS NOT NULL
    """
    ).fetchone()
    print(f"   Average: {result[0]}°F")
    print(f"   Min: {result[1]}°F")
    print(f"   Max: {result[2]}°F")
    print(f"   Std Dev: {result[3]}°F")

    # Check for seasonal variation (compare winter vs summer)
    print("\n3. Seasonal Variation (Temperature)")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            CASE
                WHEN MONTH(date::DATE) IN (12, 1, 2) THEN 'Winter'
                WHEN MONTH(date::DATE) IN (3, 4, 5) THEN 'Spring'
                WHEN MONTH(date::DATE) IN (6, 7, 8) THEN 'Summer'
                ELSE 'Fall'
            END as season,
            ROUND(AVG(tempf), 1) as avg_temp,
            ROUND(MIN(tempf), 1) as min_temp,
            ROUND(MAX(tempf), 1) as max_temp
        FROM weather_data
        WHERE tempf IS NOT NULL
        GROUP BY season
        ORDER BY
            CASE season
                WHEN 'Winter' THEN 1
                WHEN 'Spring' THEN 2
                WHEN 'Summer' THEN 3
                WHEN 'Fall' THEN 4
            END
    """
    ).fetchall()

    for row in result:
        print(
            f"   {row[0]:8} - Avg: {row[1]:5}°F  Min: {row[2]:5}°F  Max: {row[3]:5}°F"
        )

    # Humidity stats
    print("\n4. Humidity Statistics")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            ROUND(AVG(humidity), 1) as avg_humidity,
            MIN(humidity) as min_humidity,
            MAX(humidity) as max_humidity
        FROM weather_data
        WHERE humidity IS NOT NULL
    """
    ).fetchone()
    print(f"   Average: {result[0]}%")
    print(f"   Min: {result[1]}%")
    print(f"   Max: {result[2]}%")

    # Wind stats
    print("\n5. Wind Statistics")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            ROUND(AVG(windspeedmph), 1) as avg_wind,
            ROUND(MIN(windspeedmph), 1) as min_wind,
            ROUND(MAX(windspeedmph), 1) as max_wind,
            ROUND(AVG(windgustmph), 1) as avg_gust,
            ROUND(MAX(windgustmph), 1) as max_gust
        FROM weather_data
        WHERE windspeedmph IS NOT NULL
    """
    ).fetchone()
    print(f"   Average Speed: {result[0]} mph")
    print(f"   Min Speed: {result[1]} mph")
    print(f"   Max Speed: {result[2]} mph")
    print(f"   Average Gust: {result[3]} mph")
    print(f"   Max Gust: {result[4]} mph")

    # Rain stats
    print("\n6. Rain Statistics")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            COUNT(*) as total_records,
            SUM(CASE WHEN hourlyrainin > 0 THEN 1 ELSE 0 END) as rainy_records,
            ROUND(SUM(hourlyrainin), 2) as total_rain,
            ROUND(MAX(hourlyrainin), 2) as max_hourly_rain
        FROM weather_data
    """
    ).fetchone()
    rainy_percentage = (result[1] / result[0] * 100) if result[0] > 0 else 0
    print(f"   Total records: {result[0]:,}")
    print(f"   Rainy records: {result[1]:,} ({rainy_percentage:.1f}%)")
    print(f"   Total rain: {result[2]} inches")
    print(f"   Max hourly rain: {result[3]} inches")

    # Solar radiation check (should be 0 at night)
    print("\n7. Solar Radiation Verification")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            COUNT(*) as night_records,
            SUM(CASE WHEN solarradiation > 0 THEN 1 ELSE 0 END) as night_solar_errors
        FROM weather_data
        WHERE HOUR(date::TIMESTAMP) < 6 OR HOUR(date::TIMESTAMP) > 20
    """
    ).fetchone()
    print(f"   Night records (6pm-6am): {result[0]:,}")
    print(f"   Night records with solar > 0: {result[1]:,}")
    if result[1] == 0:
        print("   [OK] Solar radiation correctly 0 at night")
    else:
        print("   [ERROR] Solar radiation should be 0 at night")

    # Daily temperature variation
    print("\n8. Daily Temperature Variation")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT
            DATE(date::TIMESTAMP) as day,
            ROUND(MAX(tempf) - MIN(tempf), 1) as temp_range
        FROM weather_data
        WHERE tempf IS NOT NULL
        GROUP BY day
        ORDER BY day
        LIMIT 5
    """
    ).fetchall()
    print("   Sample days (first 5):")
    for row in result:
        print(f"   {row[0]}: {row[1]}°F daily range")

    # Check for data continuity (5-minute intervals)
    print("\n9. Data Continuity Check")
    print("-" * 70)
    result = conn.execute(
        """
        SELECT COUNT(*) as gaps
        FROM (
            SELECT
                dateutc,
                LAG(dateutc) OVER (ORDER BY dateutc) as prev_dateutc,
                (dateutc - LAG(dateutc) OVER (ORDER BY dateutc)) / 1000 / 60 as minutes_gap
            FROM weather_data
        ) gaps
        WHERE minutes_gap > 6
    """
    ).fetchone()
    print(f"   Data gaps > 6 minutes: {result[0]}")
    if result[0] == 0:
        print("   [OK] No gaps in data - continuous 5-minute intervals")
    else:
        print(f"   [WARNING] Found {result[0]} gaps larger than 6 minutes")

    print("\n" + "=" * 70)
    print("Verification Complete!")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    verify_data()
