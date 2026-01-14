"""
Repository pattern for database operations
Provides clean interface for querying weather data using DuckDB
"""

import time
from datetime import datetime
from typing import Any

from weather_app.config import DB_PATH
from weather_app.database.engine import WeatherDatabase
from weather_app.logging_config import get_logger, log_database_operation

logger = get_logger(__name__)


class WeatherRepository:
    """Repository for weather data operations"""

    @staticmethod
    def get_sampled_readings(
        start_date: str,
        end_date: str,
        target_count: int = 10000,
    ) -> list[dict[str, Any]]:
        """
        Get evenly sampled weather readings across a date range.

        Uses window functions to select every Nth record to achieve
        approximately target_count records distributed across the range.

        Args:
            start_date: Start date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            end_date: End date (ISO format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            target_count: Target number of records to return (default 10000)

        Returns:
            List of weather data records as dictionaries, evenly distributed
            across the date range
        """
        start_time = time.time()
        try:
            # Validate date formats
            try:
                datetime.fromisoformat(start_date)
            except ValueError:
                raise ValueError("Invalid start_date format. Use YYYY-MM-DD")

            try:
                datetime.fromisoformat(end_date)
            except ValueError:
                raise ValueError("Invalid end_date format. Use YYYY-MM-DD")

            with WeatherDatabase(DB_PATH) as db:
                conn = db._get_conn()

                # First, get total count for the range
                count_query = """
                    SELECT COUNT(*) FROM weather_data
                    WHERE date >= ? AND date <= ?
                """
                count_result = conn.execute(
                    count_query, [start_date, end_date]
                ).fetchone()
                total = count_result[0] if count_result else 0

                if total == 0:
                    duration_ms = (time.time() - start_time) * 1000
                    log_database_operation(
                        logger,
                        "SELECT",
                        "weather_data",
                        records=0,
                        duration_ms=duration_ms,
                    )
                    return []

                if total <= target_count:
                    # No sampling needed - return all records
                    query = """
                        SELECT * FROM weather_data
                        WHERE date >= ? AND date <= ?
                        ORDER BY dateutc ASC
                    """
                    result = conn.execute(query, [start_date, end_date]).fetchall()
                else:
                    # Sample every Nth record using ROW_NUMBER window function
                    # Use ceiling division to ensure we cover the full date range
                    # This prevents the bug where LIMIT truncated data before
                    # reaching the end of the dataset
                    sample_interval = max(1, (total + target_count - 1) // target_count)
                    query = """
                        SELECT * EXCLUDE (rn) FROM (
                            SELECT *, ROW_NUMBER() OVER (ORDER BY dateutc ASC) as rn
                            FROM weather_data
                            WHERE date >= ? AND date <= ?
                        )
                        WHERE (rn - 1) % ? = 0
                        ORDER BY dateutc ASC
                    """
                    result = conn.execute(
                        query, [start_date, end_date, sample_interval]
                    ).fetchall()

                # Convert to list of dictionaries
                records = []
                if result:
                    columns = [desc[0] for desc in conn.description]
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

        except ValueError:
            # Re-raise ValueError for date validation
            raise
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            log_database_operation(
                logger, "SELECT", "weather_data", duration_ms=duration_ms, error=str(e)
            )
            raise RuntimeError(f"Database error: {str(e)}")

    @staticmethod
    def get_all_readings(
        limit: int = 100,
        offset: int = 0,
        start_date: str | None = None,
        end_date: str | None = None,
        order: str = "desc",
    ) -> list[dict[str, Any]]:
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
                conn = db._get_conn()
                # Build query
                query = "SELECT * FROM weather_data WHERE 1=1"
                params: list[Any] = []

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

                result = conn.execute(query, params).fetchall()

                # Convert to list of dictionaries
                records = []
                if result:
                    columns = [desc[0] for desc in conn.description]
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
    def get_latest_reading() -> dict[str, Any] | None:
        """
        Get the most recent weather data reading

        Returns:
            Latest weather data record as dictionary, or None if no data exists
        """
        start_time = time.time()
        try:
            with WeatherDatabase(DB_PATH) as db:
                conn = db._get_conn()
                result = conn.execute(
                    """
                    SELECT * FROM weather_data
                    ORDER BY dateutc DESC
                    LIMIT 1
                """
                ).fetchone()

                record = None
                if result:
                    columns = [desc[0] for desc in conn.description]
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
    def get_stats() -> dict[str, Any]:
        """
        Get statistics about the weather database

        Returns:
            Dictionary with total_records, min_date, max_date, and date_range_days
        """
        start_time = time.time()
        try:
            with WeatherDatabase(DB_PATH) as db:
                conn = db._get_conn()
                # Get total count
                count_result = conn.execute(
                    "SELECT COUNT(*) as count FROM weather_data"
                ).fetchone()
                total_records = count_result[0] if count_result else 0

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
                date_result = conn.execute(
                    "SELECT MIN(date) as min_date, MAX(date) as max_date FROM weather_data"
                ).fetchone()

                min_date = date_result[0] if date_result else None
                max_date = date_result[1] if date_result else None

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
