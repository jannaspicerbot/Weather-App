#!/usr/bin/env python3
"""
Seattle Demo Weather Data Generator

Generates 3 years of realistic Seattle weather data for the demo database.
The data includes:
- Seasonal temperature patterns (mild year-round, 35-80°F typical)
- Pacific Northwest rain patterns (wet winters, dry summers)
- Realistic barometric pressure changes
- Occasional weather events (heat domes, cold snaps, windstorms)

Run with: python -m weather_app.demo.data_generator
"""

import json
import math
import random
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypedDict

import duckdb


class GenerationCancelledError(Exception):
    """Raised when generation is cancelled by user."""

    pass


class SeattleClimateData(TypedDict):
    """Type definition for Seattle climate parameters."""

    latitude: float
    timezone: str
    avg_temps: dict[int, int]
    temp_ranges: dict[int, int]
    rain_probability: dict[int, float]
    avg_humidity: dict[int, int]
    avg_wind: dict[int, int]


# Seattle climate parameters
SEATTLE_CLIMATE: SeattleClimateData = {
    "latitude": 47.6,
    "timezone": "America/Los_Angeles",
    # Monthly average temperatures (°F)
    "avg_temps": {
        1: 42,
        2: 44,
        3: 48,
        4: 52,
        5: 58,
        6: 64,
        7: 68,
        8: 69,
        9: 63,
        10: 54,
        11: 46,
        12: 41,
    },
    # Monthly temperature ranges (daily high - low)
    "temp_ranges": {
        1: 8,
        2: 10,
        3: 12,
        4: 14,
        5: 16,
        6: 16,
        7: 18,
        8: 18,
        9: 16,
        10: 12,
        11: 8,
        12: 7,
    },
    # Monthly rain probability (chance per 5-min interval during rain event)
    "rain_probability": {
        1: 0.45,
        2: 0.40,
        3: 0.38,
        4: 0.32,
        5: 0.25,
        6: 0.18,
        7: 0.10,
        8: 0.12,
        9: 0.20,
        10: 0.32,
        11: 0.42,
        12: 0.47,
    },
    # Monthly average humidity
    "avg_humidity": {
        1: 82,
        2: 78,
        3: 74,
        4: 68,
        5: 64,
        6: 62,
        7: 58,
        8: 60,
        9: 68,
        10: 76,
        11: 82,
        12: 84,
    },
    # Monthly average wind speed (mph)
    "avg_wind": {
        1: 10,
        2: 9,
        3: 9,
        4: 8,
        5: 7,
        6: 7,
        7: 7,
        8: 7,
        9: 7,
        10: 8,
        11: 10,
        12: 10,
    },
}


class SeattleWeatherGenerator:
    """Generates realistic Seattle weather data."""

    def __init__(self, db_path: str | Path) -> None:
        """Initialize generator with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(str(self.db_path))
        self._create_tables()

        # State for weather continuity
        self._in_rain_event = False
        self._rain_event_intensity = 0.0
        self._rain_event_remaining_hours = 0.0
        self._pressure_trend = 0.0  # Positive = rising, negative = falling

        # Accumulating totals
        self._total_rain = 0.0
        self._yearly_rain = 0.0
        self._monthly_rain = 0.0
        self._weekly_rain = 0.0
        self._daily_rain = 0.0
        self._event_rain = 0.0
        self._last_rain_date: str | None = None
        self._max_daily_gust = 0.0

        # Track time periods for resets
        self._last_day = -1
        self._last_week = -1
        self._last_month = -1
        self._last_year = -1

    def _create_tables(self) -> None:
        """Create the weather_data table with same schema as production."""
        self.conn.execute("CREATE SEQUENCE IF NOT EXISTS weather_data_id_seq START 1")

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

    def _get_seasonal_temp(self, dt: datetime) -> float:
        """Calculate temperature based on season and time of day."""
        month = dt.month
        hour = dt.hour + dt.minute / 60.0

        # Base monthly temperature
        base_temp = SEATTLE_CLIMATE["avg_temps"][month]
        temp_range = SEATTLE_CLIMATE["temp_ranges"][month]

        # Daily cycle: coldest at 5am, warmest at 3pm
        daily_offset = (temp_range / 2) * math.sin((hour - 5) * math.pi / 12)

        # Add random variation
        noise = random.gauss(0, 2)

        return base_temp + daily_offset + noise

    def _get_humidity(self, dt: datetime, temp: float) -> int:
        """Calculate humidity based on month and temperature."""
        month = dt.month
        base_humidity = SEATTLE_CLIMATE["avg_humidity"][month]

        # Humidity inversely related to temperature deviation
        avg_temp = SEATTLE_CLIMATE["avg_temps"][month]
        temp_effect = (avg_temp - temp) * 1.5

        # Add random variation
        noise = random.gauss(0, 5)

        humidity = int(base_humidity + temp_effect + noise)
        return max(30, min(100, humidity))

    def _update_pressure(self, dt: datetime) -> tuple[float, float]:
        """Update barometric pressure with weather front simulation."""
        # Random walk for pressure trend
        self._pressure_trend += random.gauss(0, 0.01)
        self._pressure_trend = max(-0.1, min(0.1, self._pressure_trend))

        # Base pressure varies by season (slightly lower in winter)
        month = dt.month
        seasonal_base = 30.0 - 0.15 * math.sin((month - 1) * math.pi / 6)

        # Apply trend and noise
        baromrelin = seasonal_base + self._pressure_trend + random.gauss(0, 0.05)
        baromrelin = max(29.2, min(30.8, baromrelin))

        # Absolute pressure slightly lower (elevation adjustment for Seattle ~500ft)
        baromabsin = baromrelin - 0.5

        return baromrelin, baromabsin

    def _update_rain(self, dt: datetime, pressure: float) -> tuple[float, float, float]:
        """
        Update rain state and return hourly, event, and daily rain amounts.

        Seattle rain characteristics:
        - Light drizzle is most common
        - Extended multi-day rain events in fall/winter
        - Brief showers possible year-round
        """
        month = dt.month
        hour = dt.hour

        # Check if we should start a new rain event
        if not self._in_rain_event:
            # Base probability from climate data
            base_prob = SEATTLE_CLIMATE["rain_probability"][month]

            # Low pressure increases rain chance significantly
            pressure_factor = max(0, (30.0 - pressure) * 2)

            # Night/early morning slightly more likely
            time_factor = 1.2 if (hour < 8 or hour > 20) else 1.0

            start_prob = base_prob * time_factor * (1 + pressure_factor)

            if random.random() < start_prob * 0.02:  # Per 5-min check
                self._in_rain_event = True
                # Seattle rain events typically last 2-12 hours
                self._rain_event_remaining_hours = random.uniform(2, 12)
                # Most Seattle rain is light (drizzle)
                self._rain_event_intensity = random.choice(
                    [
                        random.uniform(0.01, 0.05),  # Light drizzle (most common)
                        random.uniform(0.01, 0.05),
                        random.uniform(0.05, 0.15),  # Moderate rain
                        random.uniform(0.15, 0.40),  # Heavy rain (rare)
                    ]
                )

        hourly_rain = 0.0

        if self._in_rain_event:
            # Vary intensity within the event
            intensity_variation = random.uniform(0.5, 1.5)
            hourly_rain = self._rain_event_intensity * intensity_variation

            # Small chance of brief pause in rain
            if random.random() < 0.1:
                hourly_rain = 0.0

            # Decrement event timer (5 min = 1/12 hour)
            self._rain_event_remaining_hours -= 1 / 12

            if self._rain_event_remaining_hours <= 0:
                self._in_rain_event = False
                self._event_rain = 0.0

        # Update totals
        if hourly_rain > 0:
            self._total_rain += hourly_rain
            self._yearly_rain += hourly_rain
            self._monthly_rain += hourly_rain
            self._weekly_rain += hourly_rain
            self._daily_rain += hourly_rain
            self._event_rain += hourly_rain
            self._last_rain_date = dt.isoformat()

        return hourly_rain, self._event_rain, self._daily_rain

    def _get_wind(self, dt: datetime, pressure: float) -> tuple[float, int, float]:
        """Calculate wind speed, direction, and gust."""
        month = dt.month
        hour = dt.hour

        # Base wind from climate data
        base_wind = SEATTLE_CLIMATE["avg_wind"][month]

        # Wind typically higher in afternoon
        time_factor = 1.0 + 0.3 * math.sin((hour - 6) * math.pi / 12)

        # Low pressure increases wind
        pressure_factor = 1.0 + max(0, (30.0 - pressure) * 0.5)

        wind_speed = base_wind * time_factor * pressure_factor
        wind_speed += random.gauss(0, 2)
        wind_speed = max(0, wind_speed)

        # Gusts are typically 1.5-2.5x sustained speed
        gust_factor = random.uniform(1.3, 2.0)
        wind_gust = wind_speed * gust_factor

        # Track max daily gust
        self._max_daily_gust = max(self._max_daily_gust, wind_gust)

        # Wind direction (Seattle: predominantly from SW in winter, NW in summer)
        if month in [11, 12, 1, 2]:
            base_dir = 225  # Southwest
        elif month in [5, 6, 7, 8]:
            base_dir = 315  # Northwest
        else:
            base_dir = 270  # West

        wind_dir = int(base_dir + random.gauss(0, 30)) % 360

        return round(wind_speed, 1), wind_dir, round(wind_gust, 1)

    def _get_solar_uv(self, dt: datetime) -> tuple[float, int]:
        """Calculate solar radiation and UV index."""
        month = dt.month
        hour = dt.hour + dt.minute / 60.0

        # No sun at night
        if hour < 6 or hour > 20:
            return 0.0, 0

        # Sunrise/sunset times vary by season
        if month in [11, 12, 1]:
            sunrise, sunset = 7.5, 16.5
        elif month in [5, 6, 7]:
            sunrise, sunset = 5.0, 21.0
        else:
            sunrise, sunset = 6.0, 19.0

        if hour < sunrise or hour > sunset:
            return 0.0, 0

        # Solar angle factor
        day_length = sunset - sunrise
        solar_progress = (hour - sunrise) / day_length
        solar_angle = math.sin(solar_progress * math.pi)

        # Seasonal factor (max in summer)
        day_of_year = dt.timetuple().tm_yday
        seasonal_factor = 0.6 + 0.4 * math.sin((day_of_year - 80) * 2 * math.pi / 365)

        # Cloud cover effect (more clouds in winter)
        cloud_factor = 1.0 - SEATTLE_CLIMATE["rain_probability"][month] * 0.6
        cloud_factor *= random.uniform(0.7, 1.0)  # Random cloud variation

        # Calculate solar radiation (W/m²)
        max_solar = 1000  # Peak solar radiation
        solar = max_solar * solar_angle * seasonal_factor * cloud_factor
        solar = max(0, solar + random.gauss(0, 30))

        # UV index (roughly correlates with solar/100, max around 10-11)
        uv = int(solar / 100)
        if month in [6, 7, 8] and hour > 10 and hour < 16:
            uv = min(uv + random.randint(0, 2), 11)
        uv = max(0, min(11, uv))

        return round(solar, 1), uv

    def _reset_counters(self, dt: datetime) -> None:
        """Reset rain counters at appropriate intervals."""
        day = dt.day
        week = dt.isocalendar()[1]
        month = dt.month
        year = dt.year

        if day != self._last_day:
            self._daily_rain = 0.0
            self._max_daily_gust = 0.0
            self._last_day = day

        if week != self._last_week:
            self._weekly_rain = 0.0
            self._last_week = week

        if month != self._last_month:
            self._monthly_rain = 0.0
            self._last_month = month

        if year != self._last_year:
            self._yearly_rain = 0.0
            self._last_year = year

    def generate_reading(self, dt: datetime) -> dict:
        """Generate a single weather reading for the given datetime."""
        self._reset_counters(dt)

        # Get pressure first (affects other values)
        baromrelin, baromabsin = self._update_pressure(dt)

        # Temperature and humidity
        tempf = self._get_seasonal_temp(dt)
        humidity = self._get_humidity(dt, tempf)

        # Dew point calculation
        dew_point = tempf - ((100 - humidity) / 5)

        # Feels like (simplified heat index / wind chill)
        wind_speed, wind_dir, wind_gust = self._get_wind(dt, baromrelin)

        if tempf > 80 and humidity > 40:
            # Heat index
            feels_like = tempf + (humidity - 40) * 0.1
        elif tempf < 50 and wind_speed > 3:
            # Wind chill
            feels_like = tempf - wind_speed * 0.5
        else:
            feels_like = tempf + random.uniform(-2, 2)

        # Rain
        hourly_rain, event_rain, daily_rain = self._update_rain(dt, baromrelin)

        # Solar and UV
        solar, uv = self._get_solar_uv(dt)

        # Create reading
        dateutc = int(dt.timestamp() * 1000)

        reading = {
            "dateutc": dateutc,
            "date": dt.isoformat(),
            "tempf": round(tempf, 1),
            "feelsLike": round(feels_like, 1),
            "dewPoint": round(dew_point, 1),
            "humidity": humidity,
            "baromrelin": round(baromrelin, 2),
            "baromabsin": round(baromabsin, 2),
            "windspeedmph": wind_speed,
            "windgustmph": wind_gust,
            "winddir": wind_dir,
            "maxdailygust": round(self._max_daily_gust, 1),
            "hourlyrainin": round(hourly_rain, 3),
            "eventrain": round(event_rain, 3),
            "dailyrainin": round(daily_rain, 3),
            "weeklyrainin": round(self._weekly_rain, 3),
            "monthlyrainin": round(self._monthly_rain, 3),
            "yearlyrainin": round(self._yearly_rain, 3),
            "totalrainin": round(self._total_rain, 3),
            "solarradiation": solar,
            "uv": uv,
            "feelsLikein": round(feels_like, 1),  # Indoor (same as outdoor for demo)
            "dewPointin": round(dew_point, 1),
            "lastRain": self._last_rain_date,
            "tz": SEATTLE_CLIMATE["timezone"],
        }

        return reading

    def generate(
        self,
        start_date: datetime,
        days: int = 1095,  # 3 years default
        interval_minutes: int = 5,
        progress_callback: Callable[[int, int], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
        quiet: bool = False,
    ) -> int:
        """
        Generate weather data and insert into database.

        Args:
            start_date: When to start generating data
            days: Number of days to generate
            interval_minutes: Minutes between readings
            progress_callback: Optional callback(current_day, total_days) for progress updates
            cancel_check: Optional callback() -> bool to check if generation should be cancelled
            quiet: If True, suppress print output (useful when using progress_callback)

        Returns:
            Number of records generated

        Raises:
            GenerationCancelledError: If cancel_check returns True during generation
        """
        if not quiet:
            print(f"Generating {days} days of Seattle weather data...")
            print(f"Start: {start_date.strftime('%Y-%m-%d')}")
            print(f"End: {(start_date + timedelta(days=days)).strftime('%Y-%m-%d')}")
            print(f"Interval: {interval_minutes} minutes")
            print()

        current = start_date
        end_date = start_date + timedelta(days=days)
        records = 0
        last_day_reported = -1

        while current < end_date:
            reading = self.generate_reading(current)
            reading["raw_json"] = json.dumps(reading)

            # Insert into database
            columns = list(reading.keys())
            placeholders = ", ".join(["?" for _ in columns])
            values = [reading[k] for k in columns]

            try:
                self.conn.execute(
                    f"INSERT INTO weather_data ({', '.join(columns)}) VALUES ({placeholders})",
                    values,
                )
                records += 1
            except duckdb.ConstraintException:
                # Skip duplicates
                pass

            # Report progress every 10 days or every 10000 records
            current_day = (current - start_date).days
            if (
                progress_callback
                and current_day != last_day_reported
                and current_day % 10 == 0
            ):
                progress_callback(current_day, days)
                last_day_reported = current_day

            # Check for cancellation every day (approx every 288 records at 5min interval)
            if cancel_check and current_day != last_day_reported and cancel_check():
                raise GenerationCancelledError(
                    f"Generation cancelled at day {current_day}/{days}"
                )

            if not quiet and records % 10000 == 0 and records > 0:
                print(f"  Generated {records:,} records...")

            current += timedelta(minutes=interval_minutes)

        # Final progress callback at 100%
        if progress_callback:
            progress_callback(days, days)

        if not quiet:
            print(f"\nCompleted! Generated {records:,} records")
        return records

    def get_stats(self) -> dict:
        """Get database statistics."""
        result = self.conn.execute(
            "SELECT COUNT(*), MIN(date), MAX(date) FROM weather_data"
        ).fetchone()

        if result:
            return {
                "count": result[0],
                "min_date": result[1],
                "max_date": result[2],
            }
        return {"count": 0}

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()


def main() -> None:
    """Generate demo database."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate Seattle weather data for demo mode"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1095,  # 3 years
        help="Days of data to generate (default: 1095 = 3 years)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output database path (default: weather_app/demo/demo_weather.duckdb)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date YYYY-MM-DD (default: 3 years ago from today)",
    )

    args = parser.parse_args()

    # Determine output path
    if args.output:
        db_path = Path(args.output)
    else:
        db_path = Path(__file__).parent / "demo_weather.duckdb"

    # Determine start date
    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    else:
        # Default: start from N days ago so data ends "today"
        start_date = datetime.now() - timedelta(days=args.days)

    print("=" * 60)
    print("Seattle Demo Weather Data Generator")
    print("=" * 60)
    print(f"Database: {db_path}")
    print()

    # Remove existing database if present
    if db_path.exists():
        print("Removing existing demo database...")
        db_path.unlink()

    generator = SeattleWeatherGenerator(db_path)
    generator.generate(start_date=start_date, days=args.days)

    stats = generator.get_stats()
    print()
    print("=" * 60)
    print("Database Statistics")
    print("=" * 60)
    print(f"Total records: {stats['count']:,}")
    print(f"Date range: {stats['min_date']} to {stats['max_date']}")
    print(f"Database size: {db_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    print("[OK] Demo database created successfully!")

    generator.close()


if __name__ == "__main__":
    main()
