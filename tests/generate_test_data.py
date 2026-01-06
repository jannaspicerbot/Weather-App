#!/usr/bin/env python3
"""
Generate Test Weather Data
Creates realistic synthetic weather data for testing the API and frontend
"""

import json
import math
import random
from datetime import datetime, timedelta

import duckdb


class WeatherDataGenerator:
    def __init__(self, db_path="ambient_weather_test.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create the weather_data table (same schema as production DuckDB)"""
        # DuckDB schema - id column will be auto-generated as a sequence
        self.conn.execute(
            """
            CREATE SEQUENCE IF NOT EXISTS weather_data_id_seq START 1
        """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY DEFAULT nextval('weather_data_id_seq'),
                dateutc BIGINT UNIQUE NOT NULL,
                date VARCHAR,
                tempf DOUBLE,
                humidity INTEGER,
                baromabsin DOUBLE,
                baromrelin DOUBLE,
                windspeedmph DOUBLE,
                winddir INTEGER,
                windgustmph DOUBLE,
                maxdailygust DOUBLE,
                hourlyrainin DOUBLE,
                eventrain DOUBLE,
                dailyrainin DOUBLE,
                weeklyrainin DOUBLE,
                monthlyrainin DOUBLE,
                yearlyrainin DOUBLE,
                totalrainin DOUBLE,
                solarradiation DOUBLE,
                uv INTEGER,
                feelsLike DOUBLE,
                dewPoint DOUBLE,
                feelsLikein DOUBLE,
                dewPointin DOUBLE,
                lastRain VARCHAR,
                tz VARCHAR,
                raw_json VARCHAR
            )
        """
        )

        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)"
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON weather_data(date)")

    def clear_data(self):
        """Clear all existing data"""
        self.conn.execute("DELETE FROM weather_data")
        print("Cleared existing data")

    def generate_realistic_weather(self, start_date, days=365, interval_minutes=5):
        """
        Generate realistic weather data with seasonal patterns and weather events

        Args:
            start_date: datetime object for when to start
            days: number of days to generate (default: 365 for 1 year)
            interval_minutes: minutes between readings (default: 5)
        """
        print(f"Generating {days} days of weather data...")
        print(f"Start date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Interval: {interval_minutes} minutes")
        print()

        current_date = start_date
        end_date = start_date + timedelta(days=days)

        # Base weather conditions (will vary throughout the day/season)
        base_temp = 50.0  # Base temperature in Fahrenheit (adjusted for more variation)
        base_humidity = 60
        base_pressure = 30.0  # inches of mercury

        # Accumulating rain totals
        total_rain = 0.0
        yearly_rain = 0.0
        weekly_rain = 0.0
        monthly_rain = 0.0
        event_rain = 0.0
        last_rain_date = None

        # Track day for reset logic
        last_day = current_date.day
        last_week = current_date.isocalendar()[1]
        last_month = current_date.month
        last_year = current_date.year

        records_generated = 0

        while current_date < end_date:
            # Calculate day of year for seasonal variations
            day_of_year = current_date.timetuple().tm_yday
            hour_of_day = current_date.hour + current_date.minute / 60.0

            # Seasonal temperature variation (warmer in summer, cooler in winter)
            # Range: 20°F in winter to 80°F in summer
            seasonal_temp = 30 * math.sin((day_of_year - 80) * 2 * math.pi / 365)

            # Daily temperature variation (warmer in afternoon, cooler at night)
            daily_temp_variation = 15 * math.sin((hour_of_day - 6) * math.pi / 12)

            # Random noise for realism
            temp_noise = random.uniform(-5, 5)

            # Calculate temperature
            tempf = base_temp + seasonal_temp + daily_temp_variation + temp_noise

            # Humidity (inversely related to temperature, higher at night)
            humidity = int(
                base_humidity - (tempf - base_temp) * 0.5 + random.uniform(-10, 10)
            )
            humidity = max(30, min(100, humidity))  # Clamp between 30-100%

            # Calculate dew point (simplified formula)
            dewPoint = tempf - ((100 - humidity) / 5)

            # Calculate feels like temperature (simplified heat index/wind chill)
            feelsLike = tempf + (humidity - 50) * 0.15 + random.uniform(-3, 3)

            # Barometric pressure (slight variations, lower pressure = more likely rain)
            pressure_variation = 0.5 * math.sin(
                day_of_year * 2 * math.pi / 30
            )  # Monthly cycle
            baromrelin = base_pressure + pressure_variation + random.uniform(-0.2, 0.2)
            baromabsin = baromrelin - 0.2  # Absolute slightly lower

            # Wind (more wind during the day, varies with pressure)
            is_daytime = 6 <= hour_of_day <= 20
            base_wind = 7 if is_daytime else 3
            windspeedmph = max(0, base_wind + random.uniform(-4, 10))
            windgustmph = windspeedmph + random.uniform(3, 12)
            winddir = random.randint(0, 359)

            # Max daily gust (track highest gust of the day)
            if current_date.day != last_day:
                maxdailygust = windgustmph
            else:
                maxdailygust = max(windgustmph, random.uniform(18, 30))

            # Rain (occasional rain events, influenced by pressure)
            hourlyrainin = 0.0
            dailyrainin = 0.0

            # Higher chance of rain with lower pressure
            rain_probability = 0.15 if baromrelin < 29.8 else 0.08

            # Create occasional multi-hour rain events
            if random.random() < rain_probability:
                hourlyrainin = random.uniform(0.01, 0.8)

                # If it's raining, continue the rain event
                if event_rain > 0:
                    event_rain += hourlyrainin
                else:
                    event_rain = hourlyrainin

                total_rain += hourlyrainin
                yearly_rain += hourlyrainin
                weekly_rain += hourlyrainin
                monthly_rain += hourlyrainin
                last_rain_date = current_date.isoformat()
            else:
                # Rain event ended
                event_rain = 0.0

            # Calculate daily rain (approximate based on current hour)
            if hour_of_day < 1:
                dailyrainin = 0.0
            else:
                dailyrainin = (
                    monthly_rain * random.uniform(0.8, 1.2) if monthly_rain > 0 else 0.0
                )

            # Reset counters at appropriate intervals
            if current_date.isocalendar()[1] != last_week:
                weekly_rain = 0.0
                last_week = current_date.isocalendar()[1]

            if current_date.month != last_month:
                monthly_rain = 0.0
                last_month = current_date.month

            if current_date.year != last_year:
                yearly_rain = 0.0
                last_year = current_date.year

            last_day = current_date.day

            # Solar radiation (based on time of day and season)
            if 6 <= hour_of_day <= 20:  # Daytime
                # Peak at solar noon (12:00)
                solar_factor = math.sin((hour_of_day - 6) * math.pi / 14)
                seasonal_solar = 1.0 + 0.4 * math.sin(
                    (day_of_year - 80) * 2 * math.pi / 365
                )
                solarradiation = 900 * solar_factor * seasonal_solar + random.uniform(
                    -80, 80
                )
                solarradiation = max(0, solarradiation)

                # UV index (0-11+)
                uv = int(solarradiation / 100) + random.randint(-1, 1)
                uv = max(0, min(11, uv))
            else:  # Nighttime
                solarradiation = 0.0
                uv = 0

            # Create data point
            dateutc = int(current_date.timestamp() * 1000)
            date_iso = current_date.isoformat()

            data_point = {
                "dateutc": dateutc,
                "date": date_iso,
                "tempf": round(tempf, 1),
                "feelsLike": round(feelsLike, 1),
                "dewPoint": round(dewPoint, 1),
                "humidity": humidity,
                "baromrelin": round(baromrelin, 2),
                "baromabsin": round(baromabsin, 2),
                "windspeedmph": round(windspeedmph, 1),
                "windgustmph": round(windgustmph, 1),
                "winddir": winddir,
                "maxdailygust": round(maxdailygust, 1),
                "hourlyrainin": round(hourlyrainin, 2),
                "eventrain": round(event_rain, 2),
                "dailyrainin": round(dailyrainin, 2),
                "weeklyrainin": round(weekly_rain, 2),
                "monthlyrainin": round(monthly_rain, 2),
                "yearlyrainin": round(yearly_rain, 2),
                "totalrainin": round(total_rain, 2),
                "solarradiation": round(solarradiation, 1),
                "uv": uv,
                "lastRain": last_rain_date,
                "tz": "America/New_York",
            }

            # Insert into database
            self.insert_data(data_point)

            records_generated += 1
            if records_generated % 5000 == 0:
                print(f"  Generated {records_generated:,} records...")

            # Move to next interval
            current_date += timedelta(minutes=interval_minutes)

        print(f"\nCompleted! Generated {records_generated:,} total records")
        return records_generated

    def insert_data(self, data_point):
        """Insert a data point into the database"""
        try:
            # Check if record already exists
            dateutc = data_point.get("dateutc")
            existing = self.conn.execute(
                "SELECT id FROM weather_data WHERE dateutc = ?", [dateutc]
            ).fetchone()

            # Add raw_json
            data_point["raw_json"] = json.dumps(data_point)

            if existing:
                # Update existing record
                columns = [k for k in data_point.keys() if k != "id"]
                set_clause = ", ".join([f"{k} = ?" for k in columns])
                values = [data_point.get(k) for k in columns] + [dateutc]
                query = f"UPDATE weather_data SET {set_clause} WHERE dateutc = ?"
                self.conn.execute(query, values)
            else:
                # Insert new record
                columns = [k for k in data_point.keys()]
                placeholders = ", ".join(["?" for _ in columns])
                values = [data_point.get(k) for k in columns]
                query = f"INSERT INTO weather_data ({', '.join(columns)}) VALUES ({placeholders})"
                self.conn.execute(query, values)

            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    def get_stats(self):
        """Get database statistics"""
        result = self.conn.execute("SELECT COUNT(*) FROM weather_data").fetchone()
        count = result[0]

        if count > 0:
            result = self.conn.execute(
                "SELECT MIN(date), MAX(date) FROM weather_data"
            ).fetchone()
            min_date, max_date = result
            return {"count": count, "min_date": min_date, "max_date": max_date}
        return {"count": 0}

    def close(self):
        self.conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic weather data for testing the frontend and API"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days of data to generate (default: 365 for 1 year)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Minutes between readings (default: 5 = 288 records/day)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date (YYYY-MM-DD format, default: 365 days ago)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before generating new data",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="ambient_weather_test.duckdb",
        help="Database filename (default: ambient_weather_test.duckdb)",
    )

    args = parser.parse_args()

    # Determine start date
    if args.start_date:
        try:
            start_date = datetime.fromisoformat(args.start_date)
        except ValueError:
            print(f"Invalid date format: {args.start_date}")
            print("Use YYYY-MM-DD format")
            return
    else:
        # Default: start from N days ago to present
        start_date = datetime.now() - timedelta(days=args.days)

    print("=" * 70)
    print("Weather Test Data Generator - DuckDB Edition")
    print("=" * 70)
    print(f"Database: {args.db}")
    print(
        f"Generating {args.days} days = ~{args.days * (1440 // args.interval):,} records"
    )
    print()

    # Initialize generator
    generator = WeatherDataGenerator(args.db)

    # Clear data if requested
    if args.clear:
        generator.clear_data()

    # Generate data
    generator.generate_realistic_weather(
        start_date=start_date, days=args.days, interval_minutes=args.interval
    )

    # Show statistics
    stats = generator.get_stats()
    print("\n" + "=" * 70)
    print("Database Statistics")
    print("=" * 70)
    print(f"Total records: {stats['count']:,}")
    if stats["count"] > 0:
        print(f"Date range: {stats['min_date']} to {stats['max_date']}")
    print()
    print(f"[OK] Database saved to: {args.db}")
    print("\nTo use this database with the API:")
    print("  1. Copy to project root or data directory")
    print("  2. Update .env file:")
    print(f'     DB_PATH="{args.db}"')
    print("  3. Restart the API server")

    generator.close()


if __name__ == "__main__":
    main()
