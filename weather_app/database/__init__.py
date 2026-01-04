"""
Database module for Weather App
Provides unified DuckDB-based data storage and access
"""

from weather_app.database.engine import WeatherDatabase
from weather_app.database.repository import WeatherRepository

__all__ = ["WeatherDatabase", "WeatherRepository"]
