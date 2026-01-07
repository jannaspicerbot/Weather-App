"""
Configuration for Weather API
DuckDB-based high-performance analytics database
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_user_data_dir() -> Path:
    """
    Get platform-specific user data directory.

    When running as a packaged executable, stores user data in OS-standard locations:
    - Windows: %APPDATA%/WeatherApp
    - macOS: ~/Library/Application Support/WeatherApp
    - Linux: ~/.local/share/WeatherApp

    When running in development mode, uses the project directory.

    Returns:
        Path: User data directory
    """
    if getattr(sys, "frozen", False):
        # Running as packaged executable
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            # Linux and other Unix-like systems
            base = Path.home() / ".local" / "share"

        user_dir = base / "WeatherApp"
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    else:
        # Development mode - use project directory
        return Path(__file__).parent.parent


# Base paths
BASE_DIR = get_user_data_dir()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Environment file location
ENV_FILE = BASE_DIR / ".env"

# Load environment variables from .env file in user data directory
load_dotenv(ENV_FILE)

# Database configuration
# Set USE_TEST_DB environment variable to "true" to use test database
USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"

# Database engine - DuckDB for high-performance analytics
DB_ENGINE = "duckdb"

# Database paths - Always use DuckDB
PRODUCTION_DB = str(BASE_DIR / "ambient_weather.duckdb")
TEST_DB = str(BASE_DIR / "ambient_weather_test.duckdb")

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

# Scheduler Configuration
# Enable/disable automatic data collection (default: true)
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"

# Fetch interval in minutes (default: 5 minutes)
SCHEDULER_FETCH_INTERVAL_MINUTES = int(os.getenv("SCHEDULER_FETCH_INTERVAL_MINUTES", 5))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


def get_db_info():
    """Get information about the current database configuration"""
    return {
        "using_test_db": USE_TEST_DB,
        "database_path": DB_PATH,
        "database_engine": DB_ENGINE,
        "mode": "TEST" if USE_TEST_DB else "PRODUCTION",
    }
