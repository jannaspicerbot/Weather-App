"""
API routes for weather data
Defines all endpoints for the FastAPI application
"""

from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from weather_app.web.models import WeatherData, DatabaseStats
from weather_app.storage.repository import WeatherRepository
from weather_app.config import get_db_info


def register_routes(app: FastAPI):
    """Register all API routes with the app"""
    
    @app.get("/")
    def read_root():
        """Root endpoint with API information"""
        db_info = get_db_info()
        return {
            "message": "Weather API",
            "version": "1.0.0",
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
        order: str = Query(default="desc", pattern="^(asc|desc)$", description="Sort order by date (asc or desc)")
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
            return WeatherRepository.get_all_readings(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                order=order
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/weather/latest", response_model=WeatherData)
    def get_latest_weather():
        """
        Get the most recent weather data reading
        """
        try:
            result = WeatherRepository.get_latest_reading()
            if result is None:
                raise HTTPException(status_code=404, detail="No weather data found in database")
            return result
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/weather/stats", response_model=DatabaseStats)
    def get_database_stats():
        """
        Get statistics about the weather database
        """
        try:
            return WeatherRepository.get_stats()
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/health")
    def health_check():
        """
        Health check endpoint for monitoring
        """
        db_info = get_db_info()
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": db_info["database_engine"],
                "mode": db_info["mode"]
            }
        }

    # Add API prefix routes for frontend compatibility
    @app.get("/api/weather/latest")
    def api_get_latest_weather(limit: int = Query(default=100, ge=1, le=10000)):
        """
        Get the latest weather readings (API route)
        """
        try:
            results = WeatherRepository.get_all_readings(limit=limit, order="desc")
            return results
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/weather/range")
    def api_get_weather_range(
        start_date: Optional[str] = Query(default=None),
        end_date: Optional[str] = Query(default=None),
        limit: int = Query(default=1000, ge=1, le=10000)
    ):
        """
        Get weather data within a date range (API route)
        """
        try:
            return WeatherRepository.get_all_readings(
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                order="desc"
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/weather/stats")
    def api_get_stats():
        """
        Get database statistics (API route)
        """
        try:
            return WeatherRepository.get_stats()
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        """Handle 404 errors"""
        return {
            "error": "Not Found",
            "detail": "The requested resource was not found",
            "status_code": 404
        }

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        """Handle 500 errors"""
        return {
            "error": "Internal Server Error",
            "detail": "An internal server error occurred",
            "status_code": 500
        }
