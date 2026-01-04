"""
Repository pattern for database operations
Provides clean interface for querying weather data using DuckDB
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from weather_app.config import DB_PATH
from weather_app.database.engine import WeatherDatabase
from weather_app.logging_config import get_logger, log_database_operation

logger = get_logger(__name__)


class WeatherRepository:
    """Repository for weather data operations"""

    @staticmethod
    def get_all_readings(
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Query weather data from the database

        Args:
            limit: Maximum number of records to return (1-10000)
            offset: Number of records to skip (for pagination)
            start_date: Filter by start date (ISO format: YYYY-MM-DD)
            end_date: Filter by end date (ISO format: YYYY-MM-DD)
            order: Sort order by date ('asc' or 'desc')

        Returns:
            List of weather data records as dictionaries
        """
        start_time = time.time()
        try:
            with WeatherDatabase(DB_PATH) as db:
                # Build query
                query = "SELECT * FROM weather_data WHERE 1=1"
                params = []

                # Add date filters if provided
                if start_date:
                    try:
                        datetime.fromisoformat(start_date)  # Validate format
                        query += " AND date >= ?"
                        params.append(start_date)
                    except ValueError:
                        raise ValueError("Invalid start_date format. Use YYYY-MM-DD")

                if end_date:
                    try:
                        datetime.fromisoformat(end_date)  # Validate format
                        query += " AND date <= ?"
                        params.append(end_date)
                    except ValueError:
                        raise ValueError("Invalid end_date format. Use YYYY-MM-DD")

                # Add sorting
                query += f" ORDER BY dateutc {order.upper()}"

                # Add limit and offset
                query += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                result = db.conn.execute(query, params).fetchall()

                # Convert to list of dictionaries
                records = []
                if result:
                    columns = [desc[0] for desc in db.conn.description]
                    records = [dict(zip(columns, row)) for row in result]

                duration_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    logger,
                    "SELECT",
                    "weather_data",
                    records=len(records),
                    duration_ms=duration_ms,
                )

                return records

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_database_operation(
                logger, "SELECT", "weather_data", duration_ms=duration_ms, error=str(e)
            )
            raise RuntimeError(f"Database error: {str(e)}")

    @staticmethod
    def get_latest_reading() -> Optional[Dict[str, Any]]:
        """
        Get the most recent weather data reading

        Returns:
            Latest weather data record as dictionary, or None if no data exists
        """
        start_time = time.time()
        try:
            with WeatherDatabase(DB_PATH) as db:
                result = db.conn.execute(
                    """
                    SELECT * FROM weather_data
                    ORDER BY dateutc DESC
                    LIMIT 1
                """
                ).fetchone()

                record = None
                if result:
                    columns = [desc[0] for desc in db.conn.description]
                    record = dict(zip(columns, result))

                duration_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    logger,
                    "SELECT",
                    "weather_data",
                    records=1 if record else 0,
                    duration_ms=duration_ms,
                )

                return record

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_database_operation(
                logger, "SELECT", "weather_data", duration_ms=duration_ms, error=str(e)
            )
            raise RuntimeError(f"Database error: {str(e)}")

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get statistics about the weather database

        Returns:
            Dictionary with total_records, min_date, max_date, and date_range_days
        """
        start_time = time.time()
        try:
            with WeatherDatabase(DB_PATH) as db:
                # Get total count
                count_result = db.conn.execute(
                    "SELECT COUNT(*) as count FROM weather_data"
                ).fetchone()
                total_records = count_result[0]

                if total_records == 0:
                    duration_ms = (time.time() - start_time) * 1000
                    log_database_operation(
                        logger,
                        "SELECT",
                        "weather_data",
                        records=0,
                        duration_ms=duration_ms,
                    )
                    return {
                        "total_records": 0,
                        "min_date": None,
                        "max_date": None,
                        "date_range_days": None,
                    }

                # Get date range
                date_result = db.conn.execute(
                    "SELECT MIN(date) as min_date, MAX(date) as max_date FROM weather_data"
                ).fetchone()

                min_date = date_result[0]
                max_date = date_result[1]

                # Calculate date range in days
                date_range_days = None
                if min_date and max_date:
                    try:
                        min_dt = datetime.fromisoformat(min_date)
                        max_dt = datetime.fromisoformat(max_date)
                        date_range_days = (max_dt - min_dt).days
                    except Exception:
                        pass

                duration_ms = (time.time() - start_time) * 1000
                log_database_operation(
                    logger,
                    "SELECT",
                    "weather_data",
                    records=total_records,
                    duration_ms=duration_ms,
                )

                return {
                    "total_records": total_records,
                    "min_date": min_date,
                    "max_date": max_date,
                    "date_range_days": date_range_days,
                }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_database_operation(
                logger, "SELECT", "weather_data", duration_ms=duration_ms, error=str(e)
            )
            raise RuntimeError(f"Database error: {str(e)}")
