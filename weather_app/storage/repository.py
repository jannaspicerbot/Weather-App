"""
Repository pattern for database operations
Provides clean interface for querying and modifying weather data
"""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from weather_app.db.session import DatabaseConnection, row_to_dict


class WeatherRepository:
    """Repository for weather data operations"""
    
    @staticmethod
    def get_all_readings(
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Query weather data from the database
        
        Args:
            limit: Maximum number of records to return (1-1000)
            offset: Number of records to skip (for pagination)
            start_date: Filter by start date (ISO format: YYYY-MM-DD)
            end_date: Filter by end date (ISO format: YYYY-MM-DD)
            order: Sort order by date ('asc' or 'desc')
        
        Returns:
            List of weather data records as dictionaries
        """
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM weather_data WHERE 1=1"
            params = []
            
            # Add date filters if provided
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date)
                    start_timestamp = int(start_dt.timestamp() * 1000)
                    query += " AND dateutc >= ?"
                    params.append(start_timestamp)
                except ValueError:
                    raise ValueError("Invalid start_date format. Use YYYY-MM-DD")
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date)
                    # Add 23:59:59 to include the entire end date
                    end_dt = end_dt.replace(hour=23, minute=59, second=59)
                    end_timestamp = int(end_dt.timestamp() * 1000)
                    query += " AND dateutc <= ?"
                    params.append(end_timestamp)
                except ValueError:
                    raise ValueError("Invalid end_date format. Use YYYY-MM-DD")
            
            # Add sorting
            query += f" ORDER BY dateutc {order.upper()}"
            
            # Add limit and offset
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
    
    @staticmethod
    def get_latest_reading() -> Optional[Dict[str, Any]]:
        """
        Get the most recent weather data reading
        
        Returns:
            Latest weather data record as dictionary, or None if no data exists
        """
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM weather_data
                ORDER BY dateutc DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
        
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get statistics about the weather database
        
        Returns:
            Dictionary with total_records, min_date, max_date, and date_range_days
        """
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            # Get total count
            cursor.execute("SELECT COUNT(*) as count FROM weather_data")
            count_result = cursor.fetchone()
            total_records = count_result['count']
            
            if total_records == 0:
                conn.close()
                return {
                    "total_records": 0,
                    "min_date": None,
                    "max_date": None,
                    "date_range_days": None
                }
            
            # Get date range
            cursor.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM weather_data")
            date_result = cursor.fetchone()
            
            min_date = date_result['min_date']
            max_date = date_result['max_date']
            
            # Calculate date range in days
            date_range_days = None
            if min_date and max_date:
                try:
                    min_dt = datetime.fromisoformat(min_date)
                    max_dt = datetime.fromisoformat(max_date)
                    date_range_days = (max_dt - min_dt).days
                except:
                    pass
            
            conn.close()
            
            return {
                "total_records": total_records,
                "min_date": min_date,
                "max_date": max_date,
                "date_range_days": date_range_days
            }
        
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
