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
USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"

# Database paths
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

# Retention policy (future enhancements)
FULL_RESOLUTION_YEARS = 3
AGGREGATION_HOLD_YEARS = 50
PURGE_RAW_AFTER_AGGREGATION = True

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_db_info():
    """Get information about the current database configuration"""
    return {
        "using_test_db": USE_TEST_DB,
        "database_path": DB_PATH,
        "mode": "TEST" if USE_TEST_DB else "PRODUCTION"
    }
