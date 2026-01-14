"""
Debug launcher to test the Weather App with console output and error logging
"""

import logging
import sys
import traceback
from pathlib import Path

# Setup comprehensive logging
log_file = Path.home() / "weather_app_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

logger.info("=" * 60)
logger.info("Weather App Debug Launcher Starting")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Log file: {log_file}")
logger.info("=" * 60)

try:
    logger.info("Importing launcher module...")
    from weather_app.launcher.tray_app import main

    logger.info("Successfully imported launcher module")
    logger.info("Starting main application...")

    main()

except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")
    logger.error(f"sys.path: {sys.path}")
    print("\nERROR: Failed to import required modules")
    print(f"See log file for details: {log_file}")
    input("\nPress Enter to exit...")
    sys.exit(1)

except Exception as e:
    logger.error(f"Unexpected error: {e}")
    logger.error(f"Full traceback:\n{traceback.format_exc()}")
    print("\nERROR: Application crashed")
    print(f"See log file for details: {log_file}")
    input("\nPress Enter to exit...")
    sys.exit(1)
