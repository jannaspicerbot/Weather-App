#!/usr/bin/env python3
"""
Generate Test Weather Data
Creates realistic synthetic weather data for testing the API and frontend
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random
import math


class WeatherDataGenerator:
    def __init__(self, db_path="ambient_weather_test.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """Create the weather_data table (same schema as production)"""
        cursor = self.conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dateutc INTEGER UNIQUE,
                date TEXT,

                -- Temperature
                tempf REAL,
                feelsLike REAL,
                dewPoint REAL,
                tempinf REAL,

                -- Humidity
                humidity INTEGER,
                humidityin INTEGER,

                -- Pressure
                baromrelin REAL,
                baromabsin REAL,

                -- Wind
                windspeedmph REAL,
                windgustmph REAL,
                winddir INTEGER,
                maxdailygust REAL,

                -- Rain
                hourlyrainin REAL,
                dailyrainin REAL,
                weeklyrainin REAL,
                monthlyrainin REAL,
                totalrainin REAL,

                -- Solar
                solarradiation REAL,
                uv INTEGER,

                -- Additional fields
                battout INTEGER,
                battin INTEGER,

                -- Raw JSON for any additional fields
                raw_json TEXT
            )
        """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)
        """
        )

        self.conn.commit()

    def clear_data(self):
        """Clear all existing data"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM weather_data")
        self.conn.commit()
        print("Cleared existing data")

    def generate_realistic_weather(self, start_date, days=30, interval_minutes=5):
        """
        Generate realistic weather data

        Args:
            start_date: datetime object for when to start
            days: number of days to generate
            interval_minutes: minutes between readings (default: 5)
        """
        print(f"Generating {days} days of weather data...")
        print(f"Start date: {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Interval: {interval_minutes} minutes")
        print()

        current_date = start_date
        end_date = start_date + timedelta(days=days)

        # Base weather conditions (will vary throughout the day/season)
        base_temp = 65.0  # Base temperature in Fahrenheit
        base_humidity = 60
        base_pressure = 30.0  # inches of mercury

        # Accumulating rain totals
        total_rain = 0.0
        weekly_rain = 0.0
        monthly_rain = 0.0

        records_generated = 0

        while current_date < end_date:
            # Calculate day of year for seasonal variations
            day_of_year = current_date.timetuple().tm_yday
            hour_of_day = current_date.hour + current_date.minute / 60.0

            # Seasonal temperature variation (warmer in summer, cooler in winter)
            seasonal_temp = 20 * math.sin((day_of_year - 80) * 2 * math.pi / 365)

            # Daily temperature variation (warmer in afternoon, cooler at night)
            daily_temp_variation = 10 * math.sin((hour_of_day - 6) * math.pi / 12)

            # Random noise
            temp_noise = random.uniform(-3, 3)

            # Calculate temperature
            tempf = base_temp + seasonal_temp + daily_temp_variation + temp_noise

            # Indoor temperature (more stable, slightly warmer)
            tempinf = base_temp + 2 + random.uniform(-1, 1)

            # Humidity (inversely related to temperature, higher at night)
            humidity = int(
                base_humidity - (tempf - base_temp) * 0.5 + random.uniform(-5, 5)
            )
            humidity = max(20, min(95, humidity))  # Clamp between 20-95%

            humidityin = int(45 + random.uniform(-5, 5))  # Indoor humidity more stable

            # Calculate dew point (simplified formula)
            dewPoint = tempf - ((100 - humidity) / 5)

            # Calculate feels like temperature (simplified)
            feelsLike = tempf + (humidity - 50) * 0.1 + random.uniform(-2, 2)

            # Barometric pressure (slight variations)
            pressure_variation = 0.3 * math.sin(
                day_of_year * 2 * math.pi / 30
            )  # Monthly cycle
            baromrelin = base_pressure + pressure_variation + random.uniform(-0.1, 0.1)
            baromabsin = baromrelin - 0.2  # Absolute slightly lower

            # Wind (more wind during the day, varies with pressure)
            is_daytime = 6 <= hour_of_day <= 20
            base_wind = 5 if is_daytime else 2
            windspeedmph = max(0, base_wind + random.uniform(-3, 8))
            windgustmph = windspeedmph + random.uniform(2, 10)
            winddir = random.randint(0, 359)

            # Max daily gust (reset at midnight, track highest gust)
            if hour_of_day < 0.1:  # Near midnight
                maxdailygust = windgustmph
            else:
                maxdailygust = max(windgustmph, random.uniform(15, 25))

            # Rain (occasional rain events)
            hourlyrainin = 0.0
            dailyrainin = 0.0

            # 10% chance of rain
            if random.random() < 0.10:
                hourlyrainin = random.uniform(0.01, 0.5)
                dailyrainin = hourlyrainin * random.uniform(1, 4)
                total_rain += hourlyrainin
                weekly_rain += hourlyrainin
                monthly_rain += hourlyrainin

            # Reset weekly rain (every 7 days)
            if day_of_year % 7 == 0 and hour_of_day < 0.1:
                weekly_rain = 0.0

            # Reset monthly rain (first of month)
            if current_date.day == 1 and hour_of_day < 0.1:
                monthly_rain = 0.0

            # Solar radiation (based on time of day and season)
            if 6 <= hour_of_day <= 20:  # Daytime
                # Peak at solar noon (12:00)
                solar_factor = math.sin((hour_of_day - 6) * math.pi / 14)
                seasonal_solar = 1.0 + 0.3 * math.sin(
                    (day_of_year - 80) * 2 * math.pi / 365
                )
                solarradiation = 800 * solar_factor * seasonal_solar + random.uniform(
                    -50, 50
                )
                solarradiation = max(0, solarradiation)

                # UV index (0-11+)
                uv = int(solarradiation / 100) + random.randint(-1, 1)
                uv = max(0, min(11, uv))
            else:  # Nighttime
                solarradiation = 0.0
                uv = 0

            # Battery levels (1 = ok, simulation shows mostly ok with occasional low)
            battout = 1 if random.random() > 0.05 else 0
            battin = 1

            # Create data point
            dateutc = int(current_date.timestamp() * 1000)
            date_iso = current_date.isoformat()

            data_point = {
                "dateutc": dateutc,
                "date": date_iso,
                "tempf": round(tempf, 1),
                "feelsLike": round(feelsLike, 1),
                "dewPoint": round(dewPoint, 1),
                "tempinf": round(tempinf, 1),
                "humidity": humidity,
                "humidityin": humidityin,
                "baromrelin": round(baromrelin, 2),
                "baromabsin": round(baromabsin, 2),
                "windspeedmph": round(windspeedmph, 1),
                "windgustmph": round(windgustmph, 1),
                "winddir": winddir,
                "maxdailygust": round(maxdailygust, 1),
                "hourlyrainin": round(hourlyrainin, 2),
                "dailyrainin": round(dailyrainin, 2),
                "weeklyrainin": round(weekly_rain, 2),
                "monthlyrainin": round(monthly_rain, 2),
                "totalrainin": round(total_rain, 2),
                "solarradiation": round(solarradiation, 1),
                "uv": uv,
                "battout": battout,
                "battin": battin,
            }

            # Insert into database
            self.insert_data(data_point)

            records_generated += 1
            if records_generated % 1000 == 0:
                print(f"  Generated {records_generated} records...")

            # Move to next interval
            current_date += timedelta(minutes=interval_minutes)

        print(f"\nCompleted! Generated {records_generated} total records")
        return records_generated

    def insert_data(self, data_point):
        """Insert a data point into the database"""
        cursor = self.conn.cursor()

        try:
            cursor.execute(
                """
                INSERT OR REPLACE INTO weather_data (
                    dateutc, date, tempf, feelsLike, dewPoint, tempinf,
                    humidity, humidityin, baromrelin, baromabsin,
                    windspeedmph, windgustmph, winddir, maxdailygust,
                    hourlyrainin, dailyrainin, weeklyrainin, monthlyrainin, totalrainin,
                    solarradiation, uv, battout, battin, raw_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    data_point.get("dateutc"),
                    data_point.get("date"),
                    data_point.get("tempf"),
                    data_point.get("feelsLike"),
                    data_point.get("dewPoint"),
                    data_point.get("tempinf"),
                    data_point.get("humidity"),
                    data_point.get("humidityin"),
                    data_point.get("baromrelin"),
                    data_point.get("baromabsin"),
                    data_point.get("windspeedmph"),
                    data_point.get("windgustmph"),
                    data_point.get("winddir"),
                    data_point.get("maxdailygust"),
                    data_point.get("hourlyrainin"),
                    data_point.get("dailyrainin"),
                    data_point.get("weeklyrainin"),
                    data_point.get("monthlyrainin"),
                    data_point.get("totalrainin"),
                    data_point.get("solarradiation"),
                    data_point.get("uv"),
                    data_point.get("battout"),
                    data_point.get("battin"),
                    json.dumps(data_point),
                ),
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            return False

    def get_stats(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        count = cursor.fetchone()[0]

        if count > 0:
            cursor.execute("SELECT MIN(date), MAX(date) FROM weather_data")
            min_date, max_date = cursor.fetchone()
            return {"count": count, "min_date": min_date, "max_date": max_date}
        return {"count": 0}

    def close(self):
        self.conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate synthetic weather data for testing"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of data to generate (default: 30)",
    )
    parser.add_argument(
        "--interval", type=int, default=5, help="Minutes between readings (default: 5)"
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date (YYYY-MM-DD format, default: 30 days ago)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before generating new data",
    )
    parser.add_argument(
        "--db",
        type=str,
        default="ambient_weather_test.db",
        help="Database filename (default: ambient_weather_test.db)",
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
        # Default: start from N days ago
        start_date = datetime.now() - timedelta(days=args.days)

    print("=" * 60)
    print("Weather Test Data Generator")
    print("=" * 60)
    print(f"Database: {args.db}")
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
    print("\n" + "=" * 60)
    print("Database Statistics")
    print("=" * 60)
    print(f"Total records: {stats['count']}")
    if stats["count"] > 0:
        print(f"Date range: {stats['min_date']} to {stats['max_date']}")
    print()
    print(f"Database saved to: {args.db}")
    print("\nTo use this database with the API, update main.py:")
    print(f"  DB_PATH = '{args.db}'")

    generator.close()


if __name__ == "__main__":
    main()
