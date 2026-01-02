"""
Database management for Ambient Weather data
Provides context manager-based database access with proper schema handling
"""
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional
from datetime import datetime

from weather_app.config import DB_PATH


class AmbientWeatherDB:
    """Context manager for database operations on Ambient Weather data"""

    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """
        Enter context manager - establish database connection.

        Returns:
            self: The AmbientWeatherDB instance
        """
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
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
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.commit()
            self.conn.close()
        self.cursor = None
        self.conn = None
        return False

    def _create_tables(self):
        """Create weather_data and backfill_progress tables if they don't exist."""
        # Create weather_data table with exact schema from cli.py
        self.cursor.execute('''
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
                eventrain REAL,
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
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_dateutc ON weather_data(dateutc)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON weather_data(date)')

        # Create backfill_progress table to track backfill operations
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS backfill_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                current_date TEXT NOT NULL,
                status TEXT DEFAULT 'in_progress',
                total_records INTEGER DEFAULT 0,
                skipped_records INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')

        self.conn.commit()

    def insert_data(
        self,
        data: Union[Dict, List[Dict]]
    ) -> Tuple[int, int]:
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
            'dateutc', 'date', 'tempf', 'humidity', 'baromabsin', 'baromrelin',
            'windspeedmph', 'winddir', 'windgustmph', 'maxdailygust', 'hourlyrainin',
            'eventrain', 'dailyrainin', 'weeklyrainin', 'monthlyrainin',
            'yearlyrainin', 'totalrainin', 'solarradiation', 'uv',
            'feelsLike', 'dewPoint', 'feelsLikein', 'dewPointin',
            'lastRain', 'tz', 'raw_json'
        ]

        for record in data:
            try:
                # Filter record to only include columns that exist in table
                filtered_record = {k: v for k, v in record.items() if k in all_columns}

                if not filtered_record:
                    skipped_count += 1
                    continue

                # Build INSERT OR REPLACE query
                columns = ', '.join(filtered_record.keys())
                placeholders = ', '.join(['?' for _ in filtered_record])
                values = tuple(filtered_record.values())

                query = f'INSERT OR REPLACE INTO weather_data ({columns}) VALUES ({placeholders})'
                self.cursor.execute(query, values)
                inserted_count += 1

            except (sqlite3.IntegrityError, sqlite3.OperationalError):
                skipped_count += 1
                continue

        self.conn.commit()
        return inserted_count, skipped_count

    def get_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: Optional[int] = None,
        order_by: str = 'dateutc DESC'
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

        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        """
        Get statistics about the weather data in the database.

        Returns:
            Dictionary containing count, min_date, max_date
        """
        stats = {}

        # Get total record count
        self.cursor.execute("SELECT COUNT(*) FROM weather_data")
        stats['total_records'] = self.cursor.fetchone()[0]

        if stats['total_records'] > 0:
            # Get date range
            self.cursor.execute("SELECT MIN(date), MAX(date) FROM weather_data")
            min_date, max_date = self.cursor.fetchone()
            stats['min_date'] = min_date
            stats['max_date'] = max_date

            # Get temperature statistics
            self.cursor.execute("SELECT AVG(tempf), MIN(tempf), MAX(tempf) FROM weather_data WHERE tempf IS NOT NULL")
            avg_temp, min_temp, max_temp = self.cursor.fetchone()
            stats['avg_temperature'] = avg_temp
            stats['min_temperature'] = min_temp
            stats['max_temperature'] = max_temp

            # Get humidity statistics
            self.cursor.execute("SELECT AVG(humidity), MIN(humidity), MAX(humidity) FROM weather_data WHERE humidity IS NOT NULL")
            avg_humidity, min_humidity, max_humidity = self.cursor.fetchone()
            stats['avg_humidity'] = avg_humidity
            stats['min_humidity'] = min_humidity
            stats['max_humidity'] = max_humidity
        else:
            stats['min_date'] = None
            stats['max_date'] = None
            stats['avg_temperature'] = None
            stats['min_temperature'] = None
            stats['max_temperature'] = None
            stats['avg_humidity'] = None
            stats['min_humidity'] = None
            stats['max_humidity'] = None

        return stats

    def init_backfill_progress(
        self,
        start_date: str,
        end_date: str
    ) -> int:
        """
        Initialize a new backfill progress record.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            The ID of the created backfill_progress record
        """
        now = datetime.utcnow().isoformat()

        self.cursor.execute('''
            INSERT INTO backfill_progress (start_date, end_date, current_date, status, created_at, updated_at)
            VALUES (?, ?, ?, 'in_progress', ?, ?)
        ''', (start_date, end_date, start_date, now, now))

        self.conn.commit()
        return self.cursor.lastrowid

    def get_backfill_progress(self, progress_id: int) -> Optional[Dict]:
        """
        Get the backfill progress for a specific progress record.

        Args:
            progress_id: The ID of the backfill_progress record

        Returns:
            Dictionary containing backfill progress data, or None if not found
        """
        self.cursor.execute('SELECT * FROM backfill_progress WHERE id = ?', (progress_id,))
        row = self.cursor.fetchone()

        return dict(row) if row else None

    def update_backfill_progress(
        self,
        progress_id: int,
        current_date: str,
        total_records: int = 0,
        skipped_records: int = 0,
        status: str = 'in_progress'
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

        self.cursor.execute('''
            UPDATE backfill_progress
            SET current_date = ?, total_records = ?, skipped_records = ?, status = ?, updated_at = ?
            WHERE id = ?
        ''', (current_date, total_records, skipped_records, status, now, progress_id))

        self.conn.commit()

    def clear_backfill_progress(self, progress_id: int):
        """
        Clear/delete a backfill progress record.

        Args:
            progress_id: The ID of the backfill_progress record to delete
        """
        self.cursor.execute('DELETE FROM backfill_progress WHERE id = ?', (progress_id,))
        self.conn.commit()
