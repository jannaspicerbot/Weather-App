"""
Demo Service

Provides weather data from a pre-populated demo database with time-shifting
to make historical data appear current. Enables users to evaluate the
Weather Dashboard UI without real hardware.
"""

from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb

from weather_app.logging_config import get_logger

logger = get_logger(__name__)


class DemoService:
    """
    Serves weather data from pre-populated demo database.

    Time-shifts historical data so the most recent demo reading
    appears as "now", preserving realistic seasonal patterns.
    """

    # Demo device info shown in device selection
    DEMO_DEVICE = {
        "mac_address": "DEMO:SEATTLE:01",
        "name": "Seattle Demo Station",
        "location": "Seattle, WA",
        "last_data": None,  # Will be set dynamically
    }

    def __init__(self, demo_db_path: Path | str) -> None:
        """
        Initialize demo service with database path.

        Args:
            demo_db_path: Path to the demo DuckDB database file
        """
        self.db_path = Path(demo_db_path)
        self._conn: duckdb.DuckDBPyConnection | None = None
        self._time_offset: timedelta | None = None
        self._initialized = False

        if self.db_path.exists():
            self._initialize()
        else:
            logger.warning(
                "demo_db_not_found",
                path=str(self.db_path),
                message="Demo database not found. Run 'weather-app demo generate' to create it.",
            )

    def _initialize(self) -> None:
        """Initialize database connection and calculate time offset."""
        try:
            self._conn = duckdb.connect(str(self.db_path), read_only=True)
            self._time_offset = self._calculate_time_offset()
            self._initialized = True
            logger.info(
                "demo_service_initialized",
                db_path=str(self.db_path),
                time_offset_days=self._time_offset.days if self._time_offset else 0,
            )
        except Exception as e:
            logger.error("demo_service_init_failed", error=str(e))
            self._initialized = False

    def _calculate_time_offset(self) -> timedelta:
        """
        Calculate offset to shift demo data timestamps to present.

        Returns:
            Timedelta to add to demo timestamps to make latest = now
        """
        if not self._conn:
            return timedelta(0)

        result = self._conn.execute(
            "SELECT MAX(dateutc) FROM weather_data"
        ).fetchone()

        if result and result[0]:
            latest_demo_ms = result[0]
            latest_demo = datetime.fromtimestamp(latest_demo_ms / 1000)
            offset = datetime.now() - latest_demo
            return offset

        return timedelta(0)

    def _shift_timestamp(self, timestamp_ms: int) -> int:
        """Shift a timestamp by the time offset."""
        if not self._time_offset:
            return timestamp_ms

        original = datetime.fromtimestamp(timestamp_ms / 1000)
        shifted = original + self._time_offset
        return int(shifted.timestamp() * 1000)

    def _shift_date_string(self, date_str: str | None) -> str | None:
        """Shift an ISO date string by the time offset."""
        if not date_str or not self._time_offset:
            return date_str

        try:
            original = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            shifted = original + self._time_offset
            return shifted.isoformat()
        except (ValueError, TypeError):
            return date_str

    def _shift_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        """Apply time shift to a weather reading."""
        shifted = reading.copy()

        if "dateutc" in shifted and shifted["dateutc"]:
            shifted["dateutc"] = self._shift_timestamp(shifted["dateutc"])

        if "date" in shifted and shifted["date"]:
            shifted["date"] = self._shift_date_string(shifted["date"])

        if "lastRain" in shifted and shifted["lastRain"]:
            shifted["lastRain"] = self._shift_date_string(shifted["lastRain"])

        return shifted

    @property
    def is_available(self) -> bool:
        """Check if demo service is properly initialized."""
        return self._initialized and self._conn is not None

    def generate_if_missing(
        self,
        days: int = 1095,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> bool:
        """
        Generate demo database if it doesn't exist.

        Args:
            days: Number of days of data to generate (default: 3 years)
            progress_callback: Optional callback(current_day, total_days) for progress updates

        Returns:
            True if database was generated, False if it already existed
        """
        if self.db_path.exists():
            logger.info("demo_db_already_exists", path=str(self.db_path))
            return False

        logger.info("demo_db_generating", path=str(self.db_path), days=days)

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Calculate start date so data ends "today"
        start_date = datetime.now() - timedelta(days=days)

        # Generate database
        from weather_app.demo.data_generator import SeattleWeatherGenerator

        generator = SeattleWeatherGenerator(self.db_path)
        records = generator.generate(
            start_date=start_date,
            days=days,
            progress_callback=progress_callback,
            quiet=True,  # Suppress print output when using callback
        )
        generator.close()

        logger.info(
            "demo_db_generated",
            path=str(self.db_path),
            records=records,
            size_mb=self.db_path.stat().st_size / 1024 / 1024,
        )

        # Re-initialize now that DB exists
        self._initialize()
        return True

    def get_latest_reading(self) -> dict[str, Any] | None:
        """
        Get the most recent weather reading (time-shifted to now).

        Returns:
            Latest weather reading with timestamps shifted to present
        """
        if not self._conn:
            return None

        result = self._conn.execute(
            """
            SELECT * FROM weather_data
            ORDER BY dateutc DESC
            LIMIT 1
            """
        ).fetchone()

        if result:
            columns = [desc[0] for desc in self._conn.description]
            reading = dict(zip(columns, result))
            return self._shift_reading(reading)

        return None

    def get_all_readings(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: str | None = None,
        end_date: str | None = None,
        order: str = "desc",
    ) -> list[dict[str, Any]]:
        """
        Get weather readings with optional filtering.

        Args:
            limit: Maximum records to return
            offset: Records to skip
            start_date: Filter start (ISO format, in shifted time)
            end_date: Filter end (ISO format, in shifted time)
            order: Sort order ('asc' or 'desc')

        Returns:
            List of weather readings with time-shifted timestamps
        """
        if not self._conn:
            return []

        # Convert shifted dates back to demo database time for query
        query_start = self._unshift_date(start_date) if start_date else None
        query_end = self._unshift_date(end_date) if end_date else None

        conditions = []
        params = []

        if query_start:
            conditions.append("date >= ?")
            params.append(query_start)

        if query_end:
            conditions.append("date <= ?")
            params.append(query_end)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        order_clause = "DESC" if order.lower() == "desc" else "ASC"

        query = f"""
            SELECT * FROM weather_data
            {where_clause}
            ORDER BY dateutc {order_clause}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        results = self._conn.execute(query, params).fetchall()
        columns = [desc[0] for desc in self._conn.description]

        return [self._shift_reading(dict(zip(columns, row))) for row in results]

    def get_sampled_readings(
        self,
        start_date: str,
        end_date: str,
        target_count: int = 1000,
    ) -> list[dict[str, Any]]:
        """
        Get evenly sampled readings across a date range.

        Args:
            start_date: Start date (ISO format, in shifted time)
            end_date: End date (ISO format, in shifted time)
            target_count: Target number of samples

        Returns:
            Evenly distributed readings with time-shifted timestamps
        """
        if not self._conn:
            return []

        # Convert shifted dates back to demo database time
        query_start = self._unshift_date(start_date)
        query_end = self._unshift_date(end_date)

        # Get total count in range
        count_result = self._conn.execute(
            """
            SELECT COUNT(*) FROM weather_data
            WHERE date >= ? AND date <= ?
            """,
            [query_start, query_end],
        ).fetchone()

        total_count = count_result[0] if count_result else 0

        if total_count <= target_count:
            # Return all records if fewer than target
            return self.get_all_readings(
                limit=total_count,
                start_date=start_date,
                end_date=end_date,
                order="asc",
            )

        # Sample evenly using row numbers
        sample_interval = total_count // target_count

        query = f"""
            WITH numbered AS (
                SELECT *, ROW_NUMBER() OVER (ORDER BY dateutc ASC) as rn
                FROM weather_data
                WHERE date >= ? AND date <= ?
            )
            SELECT * FROM numbered
            WHERE (rn - 1) % ? = 0
            ORDER BY dateutc ASC
            LIMIT ?
        """

        results = self._conn.execute(
            query, [query_start, query_end, sample_interval, target_count]
        ).fetchall()

        # Get column names (excluding the rn column we added)
        columns = [desc[0] for desc in self._conn.description if desc[0] != "rn"]

        readings = []
        for row in results:
            # Create dict excluding the rn column
            reading = {}
            for i, col in enumerate(self._conn.description):
                if col[0] != "rn":
                    reading[col[0]] = row[i]
            readings.append(self._shift_reading(reading))

        return readings

    def _unshift_date(self, date_str: str | None) -> str | None:
        """Convert a shifted date back to demo database time."""
        if not date_str or not self._time_offset:
            return date_str

        try:
            shifted = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            original = shifted - self._time_offset
            return original.isoformat()
        except (ValueError, TypeError):
            return date_str

    def get_stats(self) -> dict[str, Any]:
        """
        Get database statistics (with time-shifted dates).

        Returns:
            Stats including total records and date range
        """
        if not self._conn:
            return {
                "total_records": 0,
                "min_date": None,
                "max_date": None,
                "date_range_days": None,
            }

        result = self._conn.execute(
            """
            SELECT
                COUNT(*) as total_records,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM weather_data
            """
        ).fetchone()

        if result:
            total_records, min_date, max_date = result

            # Shift dates to present
            shifted_min = self._shift_date_string(min_date)
            shifted_max = self._shift_date_string(max_date)

            # Calculate date range
            date_range_days = None
            if shifted_min and shifted_max:
                try:
                    min_dt = datetime.fromisoformat(
                        shifted_min.replace("Z", "+00:00")
                    )
                    max_dt = datetime.fromisoformat(
                        shifted_max.replace("Z", "+00:00")
                    )
                    date_range_days = (max_dt - min_dt).days
                except (ValueError, TypeError):
                    pass

            return {
                "total_records": total_records,
                "min_date": shifted_min,
                "max_date": shifted_max,
                "date_range_days": date_range_days,
            }

        return {
            "total_records": 0,
            "min_date": None,
            "max_date": None,
            "date_range_days": None,
        }

    def get_demo_device(self) -> dict[str, Any]:
        """Get demo device info with current timestamp."""
        device = self.DEMO_DEVICE.copy()
        device["last_data"] = datetime.now().isoformat()
        return device

    def get_devices(self) -> list[dict[str, Any]]:
        """Get list of demo devices (single Seattle station)."""
        return [self.get_demo_device()]

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
            self._initialized = False
