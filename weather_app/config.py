"""
Configuration for Weather API
Allows easy switching between test and production databases
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database configuration
# Set USE_TEST_DB environment variable to "true" to use test database
# Set USE_DUCKDB environment variable to "true" to use DuckDB instead of SQLite
USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"
USE_DUCKDB = os.getenv("USE_DUCKDB", "false").lower() == "true"

# Database engine selection
DB_ENGINE = "duckdb" if USE_DUCKDB else "sqlite"

# Database paths
if USE_DUCKDB:
    PRODUCTION_DB = str(BASE_DIR / "ambient_weather.duckdb")
    TEST_DB = str(BASE_DIR / "ambient_weather_test.duckdb")
else:
    PRODUCTION_DB = str(BASE_DIR / "ambient_weather.db")
    TEST_DB = str(BASE_DIR / "ambient_weather_test.db")

# Select the appropriate database
DB_PATH = TEST_DB if USE_TEST_DB else PRODUCTION_DB

# API Configuration
API_TITLE = "Weather API"
API_DESCRIPTION = "API for querying Ambient Weather data"
API_VERSION = "1.0.0"

# CORS Configuration
# For production, replace "*" with your specific frontend URL
CORS_ORIGINS = [
    "*",  # Allow all origins (development only)
    # "http://localhost:3000",  # React default
    # "http://localhost:5173",  # Vite default
]

# Server Configuration
HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("BIND_PORT", 8000))

# Retention policy
# Phase 1: Uses FULL_RESOLUTION_YEARS only (no aggregation or purging)
# Phase 2: Will implement aggregation using AGGREGATION_HOLD_YEARS
FULL_RESOLUTION_YEARS = 3
AGGREGATION_HOLD_YEARS = 50  # Phase 2 only
PURGE_RAW_AFTER_AGGREGATION = True  # Phase 2 only

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_db_info():
    """Get information about the current database configuration"""
    return {
        "using_test_db": USE_TEST_DB,
        "database_path": DB_PATH,
        "database_engine": DB_ENGINE,
        "mode": "TEST" if USE_TEST_DB else "PRODUCTION"
    }

def get_db_adapter():
    """Get the appropriate database adapter based on configuration"""
    if USE_DUCKDB:
        from weather_app.fetch.database_duckdb import AmbientWeatherDuckDB
        return AmbientWeatherDuckDB
    else:
        from weather_app.fetch.database import AmbientWeatherDB
        return AmbientWeatherDB
