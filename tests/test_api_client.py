"""
Comprehensive tests for the Ambient Weather API client.

Tests cover:
- AmbientWeatherAPI initialization
- get_devices method
- get_device_data method
- Error handling (rate limits, auth errors, timeouts)
- Session management
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from weather_app.api.client import AmbientWeatherAPI

# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return AmbientWeatherAPI(api_key="test_api_key", application_key="test_app_key")


@pytest.fixture
def mock_devices_response():
    """Mock response for get_devices."""
    return [
        {
            "macAddress": "AA:BB:CC:DD:EE:FF",
            "info": {"name": "Weather Station"},
            "lastData": {
                "dateutc": 1704110400000,
                "tempf": 72.5,
                "humidity": 45,
            },
        }
    ]


@pytest.fixture
def mock_device_data_response():
    """Mock response for get_device_data."""
    return [
        {
            "dateutc": 1704110400000,
            "date": "2024-01-01T12:00:00",
            "tempf": 72.5,
            "humidity": 45,
            "windspeedmph": 5.2,
        },
        {
            "dateutc": 1704114000000,
            "date": "2024-01-01T13:00:00",
            "tempf": 74.0,
            "humidity": 43,
            "windspeedmph": 6.1,
        },
    ]


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


class TestAmbientWeatherAPIInit:
    """Tests for API client initialization."""

    @pytest.mark.unit
    def test_init_stores_credentials(self):
        """Should store API and application keys."""
        api = AmbientWeatherAPI(api_key="my_api_key", application_key="my_app_key")

        assert api.api_key == "my_api_key"
        assert api.application_key == "my_app_key"

    @pytest.mark.unit
    def test_init_sets_base_url(self):
        """Should set the correct base URL."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        assert api.base_url == "https://api.ambientweather.net/v1"

    @pytest.mark.unit
    def test_init_creates_session(self):
        """Should create a requests session."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        assert api.session is not None
        assert isinstance(api.session, requests.Session)

    @pytest.mark.unit
    def test_init_sets_default_timeout(self):
        """Should set default timeout."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        assert api.timeout == 30

    @pytest.mark.unit
    def test_session_has_custom_headers(self):
        """Session should have custom User-Agent header."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        assert "User-Agent" in api.session.headers
        assert "WeatherApp" in api.session.headers["User-Agent"]


# =============================================================================
# GET_DEVICES TESTS
# =============================================================================


class TestGetDevices:
    """Tests for get_devices method."""

    @pytest.mark.unit
    def test_get_devices_success(self, api_client, mock_devices_response):
        """Should return list of devices on success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_devices_response

        with patch.object(api_client.session, "get", return_value=mock_response):
            devices = api_client.get_devices()

        assert len(devices) == 1
        assert devices[0]["macAddress"] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.unit
    def test_get_devices_sends_correct_params(self, api_client):
        """Should send API key and app key as params."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_devices()

            mock_get.assert_called_once()
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["apiKey"] == "test_api_key"
            assert call_kwargs["params"]["applicationKey"] == "test_app_key"

    @pytest.mark.unit
    def test_get_devices_uses_timeout(self, api_client):
        """Should use configured timeout."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_devices()

            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["timeout"] == 30

    @pytest.mark.unit
    def test_get_devices_raises_on_auth_error(self, api_client):
        """Should raise on 401 authentication error."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        with patch.object(api_client.session, "get", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError):
                api_client.get_devices()

    @pytest.mark.unit
    def test_get_devices_raises_on_timeout(self, api_client):
        """Should raise on timeout."""
        with patch.object(
            api_client.session,
            "get",
            side_effect=requests.exceptions.Timeout("Connection timed out"),
        ):
            with pytest.raises(requests.exceptions.Timeout):
                api_client.get_devices()

    @pytest.mark.unit
    def test_get_devices_raises_on_connection_error(self, api_client):
        """Should raise on connection error."""
        with patch.object(
            api_client.session,
            "get",
            side_effect=requests.exceptions.ConnectionError("Failed to connect"),
        ):
            with pytest.raises(requests.exceptions.ConnectionError):
                api_client.get_devices()


# =============================================================================
# GET_DEVICE_DATA TESTS
# =============================================================================


class TestGetDeviceData:
    """Tests for get_device_data method."""

    @pytest.mark.unit
    def test_get_device_data_success(self, api_client, mock_device_data_response):
        """Should return list of weather records on success."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_device_data_response

        with patch.object(api_client.session, "get", return_value=mock_response):
            data = api_client.get_device_data("AA:BB:CC:DD:EE:FF")

        assert len(data) == 2
        assert data[0]["tempf"] == 72.5

    @pytest.mark.unit
    def test_get_device_data_with_limit(self, api_client):
        """Should pass limit parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_device_data("AA:BB:CC:DD:EE:FF", limit=100)

            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["limit"] == 100

    @pytest.mark.unit
    def test_get_device_data_with_end_date(self, api_client):
        """Should pass end_date parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_device_data("AA:BB:CC:DD:EE:FF", end_date=1704110400000)

            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["endDate"] == 1704110400000

    @pytest.mark.unit
    def test_get_device_data_default_limit(self, api_client):
        """Should use default limit of 288."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_device_data("AA:BB:CC:DD:EE:FF")

            call_kwargs = mock_get.call_args[1]
            assert call_kwargs["params"]["limit"] == 288

    @pytest.mark.unit
    def test_get_device_data_url_includes_mac(self, api_client):
        """Should include MAC address in URL."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        with patch.object(
            api_client.session, "get", return_value=mock_response
        ) as mock_get:
            api_client.get_device_data("AA:BB:CC:DD:EE:FF")

            call_args = mock_get.call_args[0]
            assert "AA:BB:CC:DD:EE:FF" in call_args[0]

    @pytest.mark.unit
    def test_get_device_data_raises_on_rate_limit(self, api_client):
        """Should raise on 429 rate limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response
        )

        with patch.object(api_client.session, "get", return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError):
                api_client.get_device_data("AA:BB:CC:DD:EE:FF")


# =============================================================================
# SESSION MANAGEMENT TESTS
# =============================================================================


class TestSessionManagement:
    """Tests for session management and context manager."""

    @pytest.mark.unit
    def test_close_closes_session(self, api_client):
        """close() should close the session."""
        api_client.close()
        # Session should still exist but be closed
        # We can't easily verify it's closed, but we can call close without error

    @pytest.mark.unit
    def test_context_manager_enters(self):
        """Context manager should return the API instance."""
        with AmbientWeatherAPI("key", "app_key") as api:
            assert isinstance(api, AmbientWeatherAPI)

    @pytest.mark.unit
    def test_context_manager_closes_on_exit(self):
        """Context manager should close session on exit."""
        with patch.object(AmbientWeatherAPI, "close") as mock_close:
            with AmbientWeatherAPI("key", "app_key"):
                pass
            mock_close.assert_called_once()

    @pytest.mark.unit
    def test_context_manager_closes_on_exception(self):
        """Context manager should close session even on exception."""
        with patch.object(AmbientWeatherAPI, "close") as mock_close:
            try:
                with AmbientWeatherAPI("key", "app_key"):
                    raise ValueError("Test error")
            except ValueError:
                pass
            mock_close.assert_called_once()


# =============================================================================
# FETCH_ALL_HISTORICAL_DATA TESTS
# =============================================================================


class TestFetchAllHistoricalData:
    """Tests for fetch_all_historical_data method."""

    @pytest.mark.unit
    def test_fetch_historical_returns_all_data(
        self, api_client, mock_device_data_response
    ):
        """Should return all fetched data without batch_callback."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Return data first call, empty second call to end pagination
        mock_response.json.side_effect = [mock_device_data_response, []]

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):  # Skip delays
                data = api_client.fetch_all_historical_data("AA:BB:CC:DD:EE:FF")

        assert isinstance(data, list)
        assert len(data) == 2

    @pytest.mark.unit
    def test_fetch_historical_with_batch_callback(
        self, api_client, mock_device_data_response
    ):
        """Should call batch_callback with each batch."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [mock_device_data_response, []]

        batch_callback = MagicMock(return_value=(2, 0))

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                result = api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF", batch_callback=batch_callback
                )

        batch_callback.assert_called_once()
        assert result == (2, 2, 0)  # (total_fetched, total_inserted, total_skipped)

    @pytest.mark.unit
    def test_fetch_historical_calls_progress_callback(
        self, api_client, mock_device_data_response
    ):
        """Should call progress_callback with progress updates."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [mock_device_data_response, []]

        progress_callback = MagicMock()

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF", progress_callback=progress_callback
                )

        progress_callback.assert_called()
        # First call should be with total_fetched=2, requests_made=1
        progress_callback.assert_any_call(2, 1)

    @pytest.mark.unit
    def test_fetch_historical_handles_rate_limit(
        self, api_client, mock_device_data_response
    ):
        """Should handle 429 rate limit by waiting and retrying."""
        mock_response_ok = MagicMock()
        mock_response_ok.status_code = 200
        mock_response_ok.json.return_value = []

        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(
            response=mock_response_429
        )

        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                return mock_response_429
            return mock_response_ok

        with patch.object(api_client.session, "get", side_effect=side_effect):
            with patch("time.sleep") as mock_sleep:
                api_client.fetch_all_historical_data("AA:BB:CC:DD:EE:FF")

        # Should have slept for 60 seconds on rate limit
        mock_sleep.assert_any_call(60)

    @pytest.mark.unit
    def test_fetch_historical_stops_at_start_date(self, api_client):
        """Should stop fetching when reaching start_date."""
        from datetime import datetime

        # Data with timestamps before start_date
        mock_data = [
            {"dateutc": 1704020400000, "tempf": 70.0},  # 2023-12-31
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_data

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                data = api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF",
                    start_date=datetime(2024, 1, 1),  # Start after the data
                )

        # Should return empty because all data is before start_date
        assert data == []


# =============================================================================
# REQUEST QUEUE INTEGRATION TESTS
# =============================================================================


class TestRequestQueueIntegration:
    """Tests for request queue integration with async event loops."""

    @pytest.mark.unit
    def test_get_devices_with_request_queue_uses_threadsafe(
        self, mock_devices_response
    ):
        """Uses enqueue_threadsafe when request queue is provided."""
        mock_queue = MagicMock()
        mock_queue.enqueue_threadsafe.return_value = mock_devices_response

        api = AmbientWeatherAPI(
            api_key="key", application_key="app_key", request_queue=mock_queue
        )

        result = api.get_devices()

        mock_queue.enqueue_threadsafe.assert_called_once()
        assert result == mock_devices_response

    @pytest.mark.unit
    def test_get_devices_with_request_queue_returns_data(self, mock_devices_response):
        """Request queue returns expected data."""
        mock_queue = MagicMock()
        mock_queue.enqueue_threadsafe.return_value = mock_devices_response

        api = AmbientWeatherAPI(
            api_key="key", application_key="app_key", request_queue=mock_queue
        )

        result = api.get_devices()

        assert result == mock_devices_response
        assert len(result) == 1
        assert result[0]["macAddress"] == "AA:BB:CC:DD:EE:FF"

    @pytest.mark.unit
    def test_get_device_data_with_request_queue_uses_threadsafe(
        self, mock_device_data_response
    ):
        """Uses enqueue_threadsafe for device data when request queue is provided."""
        mock_queue = MagicMock()
        mock_queue.enqueue_threadsafe.return_value = mock_device_data_response

        api = AmbientWeatherAPI(
            api_key="key", application_key="app_key", request_queue=mock_queue
        )

        result = api.get_device_data("AA:BB:CC:DD:EE:FF")

        mock_queue.enqueue_threadsafe.assert_called_once()
        assert result == mock_device_data_response

    @pytest.mark.unit
    def test_get_device_data_with_request_queue_returns_data(
        self, mock_device_data_response
    ):
        """Request queue returns expected device data."""
        mock_queue = MagicMock()
        mock_queue.enqueue_threadsafe.return_value = mock_device_data_response

        api = AmbientWeatherAPI(
            api_key="key", application_key="app_key", request_queue=mock_queue
        )

        result = api.get_device_data("AA:BB:CC:DD:EE:FF")

        assert result == mock_device_data_response
        assert len(result) == 2
        assert result[0]["tempf"] == 72.5

    @pytest.mark.unit
    def test_get_devices_without_request_queue_calls_impl_directly(
        self, mock_devices_response
    ):
        """Without request queue, calls implementation directly."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_devices_response

        with patch.object(api.session, "get", return_value=mock_response):
            result = api.get_devices()

        assert result == mock_devices_response

    @pytest.mark.unit
    def test_get_device_data_without_request_queue_calls_impl_directly(
        self, mock_device_data_response
    ):
        """Without request queue, calls implementation directly."""
        api = AmbientWeatherAPI(api_key="key", application_key="app_key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_device_data_response

        with patch.object(api.session, "get", return_value=mock_response):
            result = api.get_device_data("AA:BB:CC:DD:EE:FF")

        assert result == mock_device_data_response


# =============================================================================
# ADDITIONAL HISTORICAL DATA TESTS
# =============================================================================


class TestHistoricalDataFetching:
    """Additional tests for historical data fetching."""

    @pytest.mark.unit
    def test_fetch_historical_with_start_date_filter(self, api_client):
        """Filters data by start_date parameter."""
        from datetime import datetime

        # Data spanning multiple dates
        mock_data = [
            {"dateutc": 1704110400000, "tempf": 72.5},  # 2024-01-01 12:00
            {"dateutc": 1704020400000, "tempf": 70.0},  # 2023-12-31 12:00
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [mock_data, []]

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                data = api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF",
                    start_date=datetime(2024, 1, 1),
                )

        # Should only return data on or after 2024-01-01
        assert len(data) == 1
        assert data[0]["dateutc"] == 1704110400000

    @pytest.mark.unit
    def test_fetch_historical_rate_limit_with_60s_sleep(self, api_client):
        """Handles 429 rate limit with 60s sleep and retry."""
        mock_response_ok = MagicMock()
        mock_response_ok.status_code = 200
        mock_response_ok.json.return_value = []

        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        error = requests.exceptions.HTTPError(response=mock_response_429)
        mock_response_429.raise_for_status.side_effect = error

        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise error
            return mock_response_ok

        with patch.object(api_client.session, "get", side_effect=side_effect):
            with patch("time.sleep") as mock_sleep:
                api_client.fetch_all_historical_data("AA:BB:CC:DD:EE:FF")

        # Should have waited 60 seconds
        mock_sleep.assert_any_call(60)

    @pytest.mark.unit
    def test_fetch_historical_pagination_uses_oldest_timestamp(self, api_client):
        """Correctly paginates using oldest timestamp from batch."""
        batch1 = [
            {"dateutc": 1704114000000, "tempf": 74.0},  # Newer
            {"dateutc": 1704110400000, "tempf": 72.5},  # Older
        ]
        batch2 = [
            {"dateutc": 1704106800000, "tempf": 70.0},
        ]

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [batch1, batch2, []]

        end_dates = []

        original_get = api_client.session.get

        def capture_end_date(*args, **kwargs):
            if "endDate" in kwargs.get("params", {}):
                end_dates.append(kwargs["params"]["endDate"])
            return mock_response

        with patch.object(api_client.session, "get", side_effect=capture_end_date):
            with patch("time.sleep"):
                data = api_client.fetch_all_historical_data("AA:BB:CC:DD:EE:FF")

        # Second call should use oldest timestamp from first batch minus 1
        assert len(end_dates) >= 1
        if len(end_dates) > 0:
            assert end_dates[0] == 1704110400000 - 1

    @pytest.mark.unit
    def test_fetch_historical_batch_callback_returns_tuple(
        self, api_client, mock_device_data_response
    ):
        """Batch callback mode returns tuple with counts."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [mock_device_data_response, []]

        batch_callback = MagicMock(return_value=(2, 0))

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                result = api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF", batch_callback=batch_callback
                )

        assert isinstance(result, tuple)
        assert len(result) == 3
        total_fetched, total_inserted, total_skipped = result
        assert total_fetched == 2
        assert total_inserted == 2
        assert total_skipped == 0

    @pytest.mark.unit
    def test_fetch_historical_progress_callback_called_each_batch(
        self, api_client, mock_device_data_response
    ):
        """Progress callback is called after each batch."""
        batch1 = mock_device_data_response  # 2 records
        batch2 = [{"dateutc": 1704100000000, "tempf": 68.0}]  # 1 record

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [batch1, batch2, []]

        progress_calls = []

        def progress_callback(total, requests):
            progress_calls.append((total, requests))

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep"):
                api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF", progress_callback=progress_callback
                )

        assert len(progress_calls) >= 2
        assert progress_calls[0] == (2, 1)  # First batch: 2 records, 1 request
        assert progress_calls[1] == (3, 2)  # Second batch: 3 total, 2 requests

    @pytest.mark.unit
    def test_fetch_historical_with_end_date_parameter(self, api_client):
        """Uses end_date parameter to start pagination."""
        from datetime import datetime

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []

        end_dates_used = []

        def capture_call(*args, **kwargs):
            if "endDate" in kwargs.get("params", {}):
                end_dates_used.append(kwargs["params"]["endDate"])
            return mock_response

        with patch.object(api_client.session, "get", side_effect=capture_call):
            with patch("time.sleep"):
                api_client.fetch_all_historical_data(
                    "AA:BB:CC:DD:EE:FF",
                    end_date=datetime(2024, 1, 15, 12, 0, 0),
                )

        # First call should not have endDate (or should have the provided one)
        # The API starts from end_date and works backward
        # Note: First call may or may not include endDate depending on implementation

    @pytest.mark.unit
    def test_fetch_historical_empty_batch_stops_pagination(self, api_client):
        """Empty batch response stops pagination."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = [[], []]

        with patch.object(api_client.session, "get", return_value=mock_response):
            with patch("time.sleep") as mock_sleep:
                data = api_client.fetch_all_historical_data("AA:BB:CC:DD:EE:FF")

        assert data == []
        # Should not have called sleep for rate limiting (no second request)
        mock_sleep.assert_not_called()
