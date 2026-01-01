#!/usr/bin/env python3
"""
FastAPI Backend for Weather Application
Provides REST API endpoints for querying weather data from SQLite database
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import json
from config import DB_PATH, API_TITLE, API_DESCRIPTION, API_VERSION, CORS_ORIGINS, get_db_info

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Response models
class WeatherData(BaseModel):
    id: int
    dateutc: int
    date: str
    tempf: Optional[float] = None
    feelsLike: Optional[float] = None
    dewPoint: Optional[float] = None
    tempinf: Optional[float] = None
    humidity: Optional[int] = None
    humidityin: Optional[int] = None
    baromrelin: Optional[float] = None
    baromabsin: Optional[float] = None
    windspeedmph: Optional[float] = None
    windgustmph: Optional[float] = None
    winddir: Optional[int] = None
    maxdailygust: Optional[float] = None
    hourlyrainin: Optional[float] = None
    dailyrainin: Optional[float] = None
    weeklyrainin: Optional[float] = None
    monthlyrainin: Optional[float] = None
    totalrainin: Optional[float] = None
    solarradiation: Optional[float] = None
    uv: Optional[int] = None
    battout: Optional[int] = None
    battin: Optional[int] = None
    raw_json: Optional[str] = None


class DatabaseStats(BaseModel):
    total_records: int
    min_date: Optional[str] = None
    max_date: Optional[str] = None
    date_range_days: Optional[int] = None


# Database helper functions
def get_db_connection():
    """Create a database connection"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")


def row_to_dict(row):
    """Convert SQLite row to dictionary"""
    return dict(row) if row else None


# API Endpoints

@app.get("/")
def read_root():
    """Root endpoint with API information"""
    db_info = get_db_info()
    return {
        "message": "Weather API",
        "version": API_VERSION,
        "database": {
            "mode": db_info["mode"],
            "path": db_info["database_path"]
        },
        "endpoints": {
            "/weather": "Get weather data with optional filters",
            "/weather/latest": "Get the latest weather reading",
            "/weather/stats": "Get database statistics",
        }
    }


@app.get("/weather", response_model=List[WeatherData])
def get_weather_data(
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of records to return"),
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    start_date: Optional[str] = Query(default=None, description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (ISO format: YYYY-MM-DD)"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order by date (asc or desc)")
):
    """
    Query weather data from the database

    Parameters:
    - limit: Maximum number of records (1-1000, default: 100)
    - offset: Number of records to skip (for pagination)
    - start_date: Filter by start date (YYYY-MM-DD format)
    - end_date: Filter by end date (YYYY-MM-DD format)
    - order: Sort order - 'asc' or 'desc' (default: desc)
    """
    try:
        conn = get_db_connection()
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
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                # Add 23:59:59 to include the entire end date
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
                end_timestamp = int(end_dt.timestamp() * 1000)
                query += " AND dateutc <= ?"
                params.append(end_timestamp)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/weather/latest", response_model=WeatherData)
def get_latest_weather():
    """
    Get the most recent weather data reading
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM weather_data
            ORDER BY dateutc DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        conn.close()

        if row is None:
            raise HTTPException(status_code=404, detail="No weather data found in database")

        return dict(row)

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/weather/stats", response_model=DatabaseStats)
def get_database_stats():
    """
    Get statistics about the weather database
    """
    try:
        conn = get_db_connection()
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
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "detail": "The requested resource was not found",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "error": "Internal Server Error",
        "detail": "An internal server error occurred",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
