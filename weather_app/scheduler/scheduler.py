"""
APScheduler integration for automated weather data collection
Manages periodic fetching of weather data from Ambient Weather API
"""

import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from weather_app.api import AmbientWeatherAPI
from weather_app.config import DB_PATH
from weather_app.database import WeatherDatabase
from weather_app.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


class WeatherScheduler:
    """
    Background scheduler for automated weather data collection

    Uses APScheduler to periodically fetch weather data from the
    Ambient Weather API and store it in the local database.
    """

    def __init__(self):
        """Initialize the scheduler with configuration from environment variables"""
        self.scheduler = BackgroundScheduler()
        self.api_key = os.getenv("AMBIENT_API_KEY")
        self.app_key = os.getenv("AMBIENT_APP_KEY")
        self.fetch_interval_minutes = int(
            os.getenv("SCHEDULER_FETCH_INTERVAL_MINUTES", 5)
        )
        self.enabled = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"

        logger.info(
            "scheduler_initialized",
            enabled=self.enabled,
            fetch_interval_minutes=self.fetch_interval_minutes,
        )

    def fetch_weather_job(self):
        """
        Job function that fetches latest weather data and stores it in the database

        This function is called periodically by the scheduler. It handles its own
        error logging and does not raise exceptions to prevent scheduler disruption.
        """
        job_start = datetime.now()
        logger.info("scheduled_fetch_started", timestamp=job_start.isoformat())

        try:
            # Validate API credentials
            if not self.api_key or not self.app_key:
                logger.error(
                    "scheduled_fetch_failed",
                    reason="missing_credentials",
                    message="AMBIENT_API_KEY or AMBIENT_APP_KEY not configured",
                )
                return

            # Initialize API client
            api = AmbientWeatherAPI(self.api_key, self.app_key)

            # Get devices
            devices = api.get_devices()
            if not devices:
                logger.warning("scheduled_fetch_no_devices", message="No devices found")
                return

            # Fetch data from first device (multi-device support is Phase 3)
            device = devices[0]
            mac_address = device.get("macAddress")
            device_name = device.get("info", {}).get("name", "Unknown")

            logger.info(
                "fetching_from_device", device_name=device_name, mac_address=mac_address
            )

            # Fetch latest data (limit=1 for most recent reading)
            data = api.get_device_data(mac_address, limit=1)

            if not data:
                logger.warning(
                    "scheduled_fetch_no_data",
                    device_name=device_name,
                    mac_address=mac_address,
                )
                return

            # Store in database
            with WeatherDatabase(DB_PATH) as db:
                inserted, skipped = db.insert_data(data)

            job_duration = (datetime.now() - job_start).total_seconds()

            logger.info(
                "scheduled_fetch_completed",
                device_name=device_name,
                inserted=inserted,
                skipped=skipped,
                duration_seconds=round(job_duration, 2),
            )

        except Exception as e:
            job_duration = (datetime.now() - job_start).total_seconds()
            logger.error(
                "scheduled_fetch_error",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=round(job_duration, 2),
            )

    def start(self):
        """
        Start the scheduler

        Adds the fetch job with configured interval and starts the background scheduler.
        Does nothing if scheduler is disabled via SCHEDULER_ENABLED=false.
        """
        if not self.enabled:
            logger.info(
                "scheduler_disabled",
                message="Scheduler is disabled via SCHEDULER_ENABLED=false",
            )
            return

        # Add the periodic fetch job
        self.scheduler.add_job(
            func=self.fetch_weather_job,
            trigger=IntervalTrigger(minutes=self.fetch_interval_minutes),
            id="fetch_weather",
            name="Fetch latest weather data",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping job executions
        )

        # Start the scheduler
        self.scheduler.start()

        logger.info(
            "scheduler_started",
            fetch_interval_minutes=self.fetch_interval_minutes,
            next_run=self.scheduler.get_job("fetch_weather").next_run_time.isoformat(),
        )

    def shutdown(self):
        """
        Gracefully shutdown the scheduler

        Waits for any running jobs to complete before shutting down.
        """
        if not self.enabled:
            return

        logger.info("scheduler_shutting_down")
        self.scheduler.shutdown(wait=True)
        logger.info("scheduler_shutdown_complete")

    def get_status(self):
        """
        Get current scheduler status

        Returns:
            dict: Scheduler status including enabled state, running jobs, and next run time
        """
        if not self.enabled:
            return {
                "enabled": False,
                "running": False,
                "message": "Scheduler is disabled",
            }

        fetch_job = self.scheduler.get_job("fetch_weather")

        return {
            "enabled": self.enabled,
            "running": self.scheduler.running,
            "fetch_interval_minutes": self.fetch_interval_minutes,
            "next_run_time": fetch_job.next_run_time.isoformat() if fetch_job else None,
            "job_id": fetch_job.id if fetch_job else None,
        }
