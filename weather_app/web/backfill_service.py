"""
Background backfill service for browser-based onboarding

Manages background data fetching with progress tracking for the web UI.
"""

import os
import threading
import time
from datetime import datetime, timedelta

from weather_app.api.client import AmbientWeatherAPI
from weather_app.config import AMBIENT_DEVICE_MAC, ENV_FILE
from weather_app.database import WeatherDatabase
from weather_app.logging_config import get_logger

logger = get_logger(__name__)


class BackfillService:
    """
    Manages background backfill operations with progress tracking.

    Designed for browser-based onboarding flow where users can:
    1. Validate credentials
    2. Start automatic backfill
    3. Monitor progress in real-time
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._progress = {
            "status": "idle",
            "message": "No backfill in progress",
            "progress_id": None,
            "total_records": 0,
            "inserted_records": 0,
            "skipped_records": 0,
            "current_date": None,
            "start_date": None,
            "end_date": None,
            "requests_made": 0,
            "estimated_time_remaining_seconds": None,
            "error": None,
        }
        self._thread = None
        self._stop_requested = False
        # Cache device info from validation to avoid redundant API calls
        self._cached_devices = None
        self._last_api_call_time = 0.0

    def get_progress(self) -> dict:
        """Get current backfill progress (thread-safe)."""
        with self._lock:
            return self._progress.copy()

    def _update_progress(self, **kwargs):
        """Update progress state (thread-safe)."""
        with self._lock:
            self._progress.update(kwargs)

    def is_running(self) -> bool:
        """Check if backfill is currently running."""
        with self._lock:
            return self._progress["status"] == "in_progress"

    def stop(self):
        """Request backfill to stop."""
        self._stop_requested = True

    def validate_credentials(
        self, api_key: str, app_key: str
    ) -> tuple[bool, str, list]:
        """
        Validate API credentials by attempting to fetch devices.

        Also caches the device list for use by start_backfill to avoid
        redundant API calls.

        Args:
            api_key: Ambient Weather API key
            app_key: Ambient Weather Application key

        Returns:
            Tuple of (valid: bool, message: str, devices: list)
        """
        try:
            # Use shared API queue for rate limiting (thread-safe)
            from weather_app.web.app import api_queue

            api = AmbientWeatherAPI(api_key, app_key, request_queue=api_queue)
            devices = api.get_devices()

            # Track when we made this API call
            self._last_api_call_time = time.time()

            if not devices:
                self._cached_devices = None
                return False, "No devices found for these credentials", []

            # Cache raw device data for backfill to use
            self._cached_devices = devices

            device_list = []
            for device in devices:
                info = device.get("info", {})
                last_data = device.get("lastData", {})
                device_list.append(
                    {
                        "mac_address": device.get("macAddress", ""),
                        "name": info.get("name", "Unknown Device"),
                        "last_data": last_data.get("date", None),
                    }
                )

            return True, f"Found {len(devices)} device(s)", device_list

        except Exception as e:
            self._cached_devices = None
            error_msg = str(e)
            if "401" in error_msg or "Unauthorized" in error_msg:
                return (
                    False,
                    "Invalid API credentials. Please check your API key and App key.",
                    [],
                )
            elif "403" in error_msg or "Forbidden" in error_msg:
                return (
                    False,
                    "Access denied. Please verify your credentials have proper permissions.",
                    [],
                )
            elif "429" in error_msg:
                return (
                    False,
                    "Rate limit exceeded. Please wait a moment and try again.",
                    [],
                )
            else:
                logger.error("credential_validation_error", error=error_msg)
                return False, f"Failed to validate credentials: {error_msg}", []

    def save_credentials(
        self, api_key: str, app_key: str, device_mac: str = None
    ) -> tuple[bool, str]:
        """
        Save credentials and optionally device MAC to the .env file.

        Args:
            api_key: Ambient Weather API key
            app_key: Ambient Weather Application key
            device_mac: Optional device MAC address to use

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Read existing .env content
            existing_lines = []
            if ENV_FILE.exists():
                with open(ENV_FILE) as f:
                    existing_lines = f.readlines()

            # Update or add API keys and device MAC
            new_lines = []
            api_key_found = False
            app_key_found = False
            device_mac_found = False

            for line in existing_lines:
                if line.startswith("AMBIENT_API_KEY="):
                    new_lines.append(f"AMBIENT_API_KEY={api_key}\n")
                    api_key_found = True
                elif line.startswith("AMBIENT_APP_KEY="):
                    new_lines.append(f"AMBIENT_APP_KEY={app_key}\n")
                    app_key_found = True
                elif line.startswith("AMBIENT_DEVICE_MAC="):
                    if device_mac:
                        new_lines.append(f"AMBIENT_DEVICE_MAC={device_mac}\n")
                        device_mac_found = True
                    # If device_mac is None, skip this line (remove it)
                else:
                    new_lines.append(line)

            # Add missing keys
            if not api_key_found:
                new_lines.append(f"AMBIENT_API_KEY={api_key}\n")
            if not app_key_found:
                new_lines.append(f"AMBIENT_APP_KEY={app_key}\n")
            if device_mac and not device_mac_found:
                new_lines.append(f"AMBIENT_DEVICE_MAC={device_mac}\n")

            # Write back to file
            with open(ENV_FILE, "w") as f:
                f.writelines(new_lines)

            # Update environment variables for current process
            os.environ["AMBIENT_API_KEY"] = api_key
            os.environ["AMBIENT_APP_KEY"] = app_key
            if device_mac:
                os.environ["AMBIENT_DEVICE_MAC"] = device_mac

            logger.info(
                "credentials_saved",
                env_file=str(ENV_FILE),
                has_device_mac=bool(device_mac),
            )
            return True, "Credentials saved successfully"

        except Exception as e:
            logger.error("save_credentials_error", error=str(e))
            return False, f"Failed to save credentials: {str(e)}"

    def save_device_selection(self, device_mac: str) -> tuple[bool, str]:
        """
        Save device MAC address selection to .env file.

        Args:
            device_mac: Device MAC address to save

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Read existing .env content
            existing_lines = []
            if ENV_FILE.exists():
                with open(ENV_FILE) as f:
                    existing_lines = f.readlines()

            # Update or add device MAC
            new_lines = []
            device_mac_found = False

            for line in existing_lines:
                if line.startswith("AMBIENT_DEVICE_MAC="):
                    new_lines.append(f"AMBIENT_DEVICE_MAC={device_mac}\n")
                    device_mac_found = True
                else:
                    new_lines.append(line)

            # Add if not found
            if not device_mac_found:
                new_lines.append(f"AMBIENT_DEVICE_MAC={device_mac}\n")

            # Write back to file
            with open(ENV_FILE, "w") as f:
                f.writelines(new_lines)

            # Update environment variable for current process
            os.environ["AMBIENT_DEVICE_MAC"] = device_mac

            logger.info(
                "device_selection_saved",
                device_mac=device_mac[:8],
                env_file=str(ENV_FILE),
            )
            return True, "Device selection saved successfully"

        except Exception as e:
            logger.error("save_device_selection_error", error=str(e))
            return False, f"Failed to save device selection: {str(e)}"

    def get_credential_status(self) -> dict:
        """
        Check if credentials are configured.

        Returns:
            Dictionary with configured status
        """
        api_key = os.getenv("AMBIENT_API_KEY", "")
        app_key = os.getenv("AMBIENT_APP_KEY", "")

        return {
            "configured": bool(api_key and app_key),
            "has_api_key": bool(api_key),
            "has_app_key": bool(app_key),
        }

    def start_backfill(
        self, api_key: str = None, app_key: str = None
    ) -> tuple[bool, str]:
        """
        Start background backfill process.

        Uses credentials from parameters or environment variables.
        First fetches current data, then backfills historical data.

        Args:
            api_key: Optional API key (uses env var if not provided)
            app_key: Optional App key (uses env var if not provided)

        Returns:
            Tuple of (started: bool, message: str)
        """
        if self.is_running():
            return False, "Backfill already in progress"

        # Get credentials
        api_key = api_key or os.getenv("AMBIENT_API_KEY")
        app_key = app_key or os.getenv("AMBIENT_APP_KEY")

        if not api_key or not app_key:
            return False, "API credentials not configured"

        # Reset stop flag
        self._stop_requested = False

        # Start background thread
        self._thread = threading.Thread(
            target=self._run_backfill,
            args=(api_key, app_key),
            daemon=True,
        )
        self._thread.start()

        return True, "Backfill started"

    def _run_backfill(self, api_key: str, app_key: str):
        """
        Background thread for backfill operation.

        1. Fetches current/latest data first
        2. Then backfills historical data
        3. Updates progress throughout
        """
        try:
            self._update_progress(
                status="in_progress",
                message="Initializing backfill...",
                total_records=0,
                inserted_records=0,
                skipped_records=0,
                requests_made=0,
                error=None,
            )

            # Use shared API queue for rate limiting (thread-safe)
            from weather_app.web.app import api_queue

            api = AmbientWeatherAPI(api_key, app_key, request_queue=api_queue)

            # Use cached devices from validation if available (avoid redundant API call)
            devices = self._cached_devices
            if devices:
                logger.info("backfill_using_cached_devices")
            else:
                # No manual rate limiting needed - queue handles it
                logger.info("backfill_getting_devices")
                devices = api.get_devices()
                self._last_api_call_time = time.time()

            if not devices:
                self._update_progress(
                    status="failed",
                    message="No devices found",
                    error="No weather devices found for this account",
                )
                return

            # Select device: use configured MAC or default to first device
            mac_address = None
            device_name = None

            if AMBIENT_DEVICE_MAC:
                # Find the configured device in the list
                for device in devices:
                    if device.get("macAddress") == AMBIENT_DEVICE_MAC:
                        mac_address = device.get("macAddress")
                        device_name = device.get("info", {}).get(
                            "name", "Weather Station"
                        )
                        logger.info(
                            "using_configured_device",
                            mac=mac_address[:8],
                            name=device_name,
                        )
                        break

                if not mac_address:
                    logger.warning(
                        "configured_device_not_found",
                        configured_mac=AMBIENT_DEVICE_MAC[:8],
                        available_count=len(devices),
                    )
                    # Fall back to first device
                    mac_address = devices[0].get("macAddress")
                    device_name = (
                        devices[0].get("info", {}).get("name", "Weather Station")
                    )
                    logger.info("falling_back_to_first_device", mac=mac_address[:8])
            else:
                # No device configured, use first device
                mac_address = devices[0].get("macAddress")
                device_name = devices[0].get("info", {}).get("name", "Weather Station")
                logger.info("using_first_device", mac=mac_address[:8], name=device_name)

            self._update_progress(message=f"Connected to {device_name}")

            # Clear cached devices after use
            self._cached_devices = None

            # Ensure we respect rate limit before fetching data
            time_since_last_call = time.time() - self._last_api_call_time
            if time_since_last_call < 1.0:
                time.sleep(1.0 - time_since_last_call)

            # Phase 1: Fetch latest data first (quick feedback for user)
            logger.info("backfill_fetching_latest", mac=mac_address[:8])
            self._update_progress(message="Fetching current weather data...")

            with WeatherDatabase() as db:
                latest_data = api.get_device_data(mac_address, limit=10)
                self._last_api_call_time = time.time()
                if latest_data:
                    inserted, skipped = db.insert_data(latest_data)
                    self._update_progress(
                        message=f"Latest data loaded ({inserted} readings)",
                        inserted_records=inserted,
                        skipped_records=skipped,
                        requests_made=1,
                    )

            if self._stop_requested:
                self._update_progress(status="idle", message="Backfill cancelled")
                return

            # Phase 2: Backfill historical data
            # Ambient Weather keeps ~2 years of data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # ~2 years

            self._update_progress(
                message="Starting historical data backfill...",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )

            # Calculate estimated total based on ~288 records/day for 2 years
            estimated_total_requests = (730 * 288) // 288  # ~730 requests

            def progress_callback(total_fetched: int, requests_made: int):
                """Update progress during backfill."""
                if self._stop_requested:
                    raise InterruptedError("Backfill cancelled by user")

                # Calculate ETA based on rate limit (1 request/second)
                remaining_requests = max(0, estimated_total_requests - requests_made)
                eta_seconds = remaining_requests  # 1 second per request

                self._update_progress(
                    total_records=total_fetched,
                    requests_made=requests_made,
                    estimated_time_remaining_seconds=int(eta_seconds),
                    message=f"Fetching historical data... ({requests_made} requests, {total_fetched:,} records)",
                )

            def batch_callback(batch_data: list) -> tuple[int, int]:
                """Save each batch as it arrives."""
                with WeatherDatabase() as db:
                    inserted, skipped = db.insert_data(batch_data)

                    # Update current date from newest record in batch
                    if batch_data:
                        newest = max(batch_data, key=lambda x: x.get("dateutc", 0))
                        current_date = (
                            newest.get("date", "")[:10] if newest.get("date") else None
                        )

                        with self._lock:
                            self._progress["inserted_records"] += inserted
                            self._progress["skipped_records"] += skipped
                            if current_date:
                                self._progress["current_date"] = current_date

                    return inserted, skipped

            try:
                total_fetched, total_inserted, total_skipped = (
                    api.fetch_all_historical_data(
                        mac_address,
                        start_date=start_date,
                        end_date=end_date,
                        batch_size=288,
                        delay=1.0,  # Respect rate limit
                        progress_callback=progress_callback,
                        batch_callback=batch_callback,
                    )
                )

                self._update_progress(
                    status="completed",
                    message=f"Backfill complete! {total_inserted:,} records added.",
                    total_records=total_fetched,
                    estimated_time_remaining_seconds=0,
                )
                logger.info(
                    "backfill_completed",
                    total_fetched=total_fetched,
                    total_inserted=total_inserted,
                    total_skipped=total_skipped,
                )

            except InterruptedError:
                self._update_progress(
                    status="idle",
                    message="Backfill cancelled by user",
                )
                logger.info("backfill_cancelled")

        except Exception as e:
            logger.error("backfill_error", error=str(e))
            self._update_progress(
                status="failed",
                message=f"Backfill failed: {str(e)}",
                error=str(e),
            )


# Global singleton instance
backfill_service = BackfillService()
