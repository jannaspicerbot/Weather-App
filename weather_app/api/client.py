"""
Ambient Weather API client
"""

import requests
import time
from datetime import datetime
from weather_app.logging_config import get_logger

logger = get_logger(__name__)


class AmbientWeatherAPI:
    """Client for interacting with Ambient Weather API"""

    def __init__(self, api_key, application_key):
        """
        Initialize API client

        Args:
            api_key: Ambient Weather API key
            application_key: Ambient Weather Application key
        """
        self.api_key = api_key
        self.application_key = application_key
        self.base_url = "https://api.ambientweather.net/v1"

    def get_devices(self):
        """
        Get list of user's weather devices

        Returns:
            List of device dictionaries
        """
        url = f"{self.base_url}/devices"
        params = {"apiKey": self.api_key, "applicationKey": self.application_key}

        logger.info("api_request", method="GET", endpoint="/devices")
        start_time = time.time()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "api_response",
                method="GET",
                endpoint="/devices",
                status_code=response.status_code,
                devices=len(data),
                duration_ms=round(duration_ms, 2),
            )

            return data
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "api_error",
                method="GET",
                endpoint="/devices",
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise

    def get_device_data(self, mac_address, end_date=None, limit=288):
        """
        Get weather data for a specific device

        Args:
            mac_address: Device MAC address
            end_date: End date in milliseconds (Unix timestamp * 1000)
            limit: Number of records to fetch (max 288)

        Returns:
            List of weather data records
        """
        url = f"{self.base_url}/devices/{mac_address}"
        params = {
            "apiKey": self.api_key,
            "applicationKey": self.application_key,
            "limit": limit,
        }

        if end_date:
            params["endDate"] = end_date

        logger.info(
            "api_request",
            method="GET",
            endpoint=f"/devices/{mac_address[:8]}...",
            limit=limit,
            end_date=end_date,
        )
        start_time = time.time()

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(
                "api_response",
                method="GET",
                endpoint=f"/devices/{mac_address[:8]}...",
                status_code=response.status_code,
                records=len(data),
                duration_ms=round(duration_ms, 2),
            )

            return data
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "api_error",
                method="GET",
                endpoint=f"/devices/{mac_address[:8]}...",
                error=str(e),
                duration_ms=round(duration_ms, 2),
            )
            raise

    def fetch_all_historical_data(
        self,
        mac_address,
        start_date=None,
        end_date=None,
        batch_size=288,
        delay=1.0,
        progress_callback=None,
    ):
        """
        Fetch all historical data for a device with pagination

        Args:
            mac_address: Device MAC address
            start_date: Start date (datetime object)
            end_date: End date (datetime object)
            batch_size: Records per API call (max 288)
            delay: Delay between API calls in seconds
            progress_callback: Optional callback function(records_fetched, requests_made)

        Returns:
            List of all weather data records
        """
        all_data = []
        requests_made = 0
        current_end_date = None

        if end_date:
            current_end_date = int(end_date.timestamp() * 1000)

        while True:
            try:
                data = self.get_device_data(mac_address, current_end_date, batch_size)
                requests_made += 1

                if not data:
                    break

                # Filter by start_date if provided
                if start_date:
                    start_timestamp = int(start_date.timestamp() * 1000)
                    data = [d for d in data if d.get("dateutc", 0) >= start_timestamp]

                if not data:
                    break

                all_data.extend(data)

                if progress_callback:
                    progress_callback(len(all_data), requests_made)

                # Check if we have all data
                if len(data) < batch_size:
                    break

                # Get timestamp of oldest record for next batch
                oldest_timestamp = min(d.get("dateutc", float("inf")) for d in data)
                if oldest_timestamp == float("inf"):
                    break

                # If we've reached the start date, we're done
                if start_date and oldest_timestamp <= int(
                    start_date.timestamp() * 1000
                ):
                    break

                # Move end_date back for next batch (subtract 1ms to avoid duplicates)
                current_end_date = oldest_timestamp - 1

                # Rate limiting delay
                time.sleep(delay)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    logger.warning(
                        "rate_limit_hit", requests_made=requests_made, wait_seconds=60
                    )
                    time.sleep(60)
                    continue
                raise

        return all_data
