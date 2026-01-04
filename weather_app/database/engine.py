"""
DuckDB database engine for Ambient Weather data
Provides context manager-based database access with high-performance analytics
DuckDB is 10-100x faster than SQLite for analytical queries
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import duckdb

from weather_app.config import DB_PATH


class WeatherDatabase:
    """Context manager for DuckDB operations on Ambient Weather data"""

    def __init__(self, db_path: str = None):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the DuckDB database file (defaults to config DB_PATH)
        """
        if db_path is None:
            db_path = DB_PATH

        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        """
        Enter context manager - establish database connection.

        Returns:
            self: The WeatherDatabase instance
        """
        self.conn = duckdb.connect(self.db_path)
        self._create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context manager - close database connection.

        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        if self.conn:
            self.conn.close()
        self.conn = None
        return False

    def _create_tables(self):
        """Create weather_data and backfill_progress tables if they don't exist."""
        # Create weather_data table
        # DuckDB uses BIGINT for large integers, DOUBLE for floats, INTEGER for smaller ints
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY,
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

        # Create indexes for common queries
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)"
        )
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON weather_data(date)")

        # Create backfill_progress table to track backfill operations
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS backfill_progress (
                id INTEGER PRIMARY KEY,
                start_date VARCHAR NOT NULL,
                end_date VARCHAR NOT NULL,
                current_date VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'in_progress',
                total_records INTEGER DEFAULT 0,
                skipped_records INTEGER DEFAULT 0,
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL
            )
        """
        )

    def insert_data(self, data: Union[Dict, List[Dict]]) -> Tuple[int, int]:
        """
        Insert weather data into the database with idempotent INSERT OR REPLACE.

        Handles both single dictionaries and lists of dictionaries.
        Returns the count of inserted and skipped records.

        Args:
            data: Single dictionary or list of dictionaries containing weather data

        Returns:
            Tuple of (inserted_count, skipped_count)
        """
        if isinstance(data, dict):
            data = [data]

        if not isinstance(data, list):
            raise TypeError("Data must be a dictionary or list of dictionaries")

        if not data:
            return 0, 0

        inserted_count = 0
        skipped_count = 0

        # Define all possible columns in weather_data table
        all_columns = [
            "dateutc",
            "date",
            "tempf",
            "humidity",
            "baromabsin",
            "baromrelin",
            "windspeedmph",
            "winddir",
            "windgustmph",
            "maxdailygust",
            "hourlyrainin",
            "eventrain",
            "dailyrainin",
            "weeklyrainin",
            "monthlyrainin",
            "yearlyrainin",
            "totalrainin",
            "solarradiation",
            "uv",
            "feelsLike",
            "dewPoint",
            "feelsLikein",
            "dewPointin",
            "lastRain",
            "tz",
            "raw_json",
        ]

        for record in data:
            try:
                # Filter record to only include columns that exist in table
                filtered_record = {k: v for k, v in record.items() if k in all_columns}

                if not filtered_record:
                    skipped_count += 1
                    continue

                # Check if record already exists
                dateutc = filtered_record.get("dateutc")
                if dateutc:
                    existing = self.conn.execute(
                        "SELECT id FROM weather_data WHERE dateutc = ?", [dateutc]
                    ).fetchone()

                    if existing:
                        # Update existing record
                        set_clause = ", ".join(
                            [f"{k} = ?" for k in filtered_record.keys()]
                        )
                        values = list(filtered_record.values()) + [dateutc]
                        query = (
                            f"UPDATE weather_data SET {set_clause} WHERE dateutc = ?"
                        )
                        self.conn.execute(query, values)
                    else:
                        # Insert new record
                        columns = ", ".join(filtered_record.keys())
                        placeholders = ", ".join(["?" for _ in filtered_record])
                        values = list(filtered_record.values())
                        query = f"INSERT INTO weather_data ({columns}) VALUES ({placeholders})"
                        self.conn.execute(query, values)

                    inserted_count += 1
                else:
                    skipped_count += 1

            except Exception as e:
                skipped_count += 1
                continue

        return inserted_count, skipped_count

    def get_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        order_by: str = "dateutc DESC",
    ) -> List[Dict]:
        """
        Retrieve weather data from the database.

        Args:
            start_date: Start date in YYYY-MM-DD format (optional)
            end_date: End date in YYYY-MM-DD format (optional)
            limit: Maximum number of records to return (optional)
            order_by: ORDER BY clause (default: 'dateutc DESC')

        Returns:
            List of dictionaries containing weather data
        """
        query = "SELECT * FROM weather_data"
        params = []

        conditions = []
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        result = self.conn.execute(query, params).fetchall()

        # Convert to list of dictionaries
        if result:
            columns = [desc[0] for desc in self.conn.description]
            return [dict(zip(columns, row)) for row in result]
        return []

    def get_stats(self) -> Dict:
        """
        Get statistics about the weather data in the database.

        Returns:
            Dictionary containing count, min_date, max_date
        """
        stats = {}

        # Get total record count
        result = self.conn.execute("SELECT COUNT(*) FROM weather_data").fetchone()
        stats["total_records"] = result[0]

        if stats["total_records"] > 0:
            # Get date range
            result = self.conn.execute(
                "SELECT MIN(date), MAX(date) FROM weather_data"
            ).fetchone()
            stats["min_date"] = result[0]
            stats["max_date"] = result[1]

            # Get temperature statistics
            result = self.conn.execute(
                "SELECT AVG(tempf), MIN(tempf), MAX(tempf) FROM weather_data WHERE tempf IS NOT NULL"
            ).fetchone()
            stats["avg_temperature"] = result[0]
            stats["min_temperature"] = result[1]
            stats["max_temperature"] = result[2]

            # Get humidity statistics
            result = self.conn.execute(
                "SELECT AVG(humidity), MIN(humidity), MAX(humidity) FROM weather_data WHERE humidity IS NOT NULL"
            ).fetchone()
            stats["avg_humidity"] = result[0]
            stats["min_humidity"] = result[1]
            stats["max_humidity"] = result[2]
        else:
            stats["min_date"] = None
            stats["max_date"] = None
            stats["avg_temperature"] = None
            stats["min_temperature"] = None
            stats["max_temperature"] = None
            stats["avg_humidity"] = None
            stats["min_humidity"] = None
            stats["max_humidity"] = None

        return stats

    def init_backfill_progress(self, start_date: str, end_date: str) -> int:
        """
        Initialize a new backfill progress record.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            The ID of the created backfill_progress record
        """
        now = datetime.utcnow().isoformat()

        self.conn.execute(
            """
            INSERT INTO backfill_progress (start_date, end_date, current_date, status, created_at, updated_at)
            VALUES (?, ?, ?, 'in_progress', ?, ?)
        """,
            [start_date, end_date, start_date, now, now],
        )

        # Get the last inserted row id
        result = self.conn.execute("SELECT MAX(id) FROM backfill_progress").fetchone()
        return result[0]

    def get_backfill_progress(self, progress_id: int) -> Optional[Dict]:
        """
        Get the backfill progress for a specific progress record.

        Args:
            progress_id: The ID of the backfill_progress record

        Returns:
            Dictionary containing backfill progress data, or None if not found
        """
        result = self.conn.execute(
            "SELECT * FROM backfill_progress WHERE id = ?", [progress_id]
        ).fetchone()

        if result:
            columns = [desc[0] for desc in self.conn.description]
            return dict(zip(columns, result))
        return None

    def update_backfill_progress(
        self,
        progress_id: int,
        current_date: str,
        total_records: int = 0,
        skipped_records: int = 0,
        status: str = "in_progress",
    ):
        """
        Update the backfill progress record.

        Args:
            progress_id: The ID of the backfill_progress record
            current_date: Current date being processed (YYYY-MM-DD format)
            total_records: Total records processed so far
            skipped_records: Total records skipped so far
            status: Status of the backfill ('in_progress', 'completed', 'failed')
        """
        now = datetime.utcnow().isoformat()

        self.conn.execute(
            """
            UPDATE backfill_progress
            SET current_date = ?, total_records = ?, skipped_records = ?, status = ?, updated_at = ?
            WHERE id = ?
        """,
            [current_date, total_records, skipped_records, status, now, progress_id],
        )

    def clear_backfill_progress(self, progress_id: int):
        """
        Clear/delete a backfill progress record.

        Args:
            progress_id: The ID of the backfill_progress record to delete
        """
        self.conn.execute("DELETE FROM backfill_progress WHERE id = ?", [progress_id])
