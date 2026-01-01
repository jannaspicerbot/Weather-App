"""
Configuration for Weather API
Allows easy switching between test and production databases
"""

import os

# Database configuration
# Set USE_TEST_DB environment variable to "true" to use test database
USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"

# Database paths
PRODUCTION_DB = "ambient_weather.db"
TEST_DB = "ambient_weather_test.db"

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
HOST = "0.0.0.0"
PORT = 8000

def get_db_info():
    """Get information about the current database configuration"""
    return {
        "using_test_db": USE_TEST_DB,
        "database_path": DB_PATH,
        "mode": "TEST" if USE_TEST_DB else "PRODUCTION"
    }
