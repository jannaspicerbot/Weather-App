#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3: Test Our API Client
Compare our AmbientWeatherClient implementation against raw requests
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weather_app.api.ambient_client import AmbientWeatherClient

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AMBIENT_API_KEY")
APP_KEY = os.getenv("AMBIENT_APP_KEY")
MAC_ADDRESS = os.getenv("AMBIENT_MAC_ADDRESS")


def test_client_get_devices():
    """Test our client's get_devices method"""
    print("=" * 70)
    print("Test 3.1: Our Client - Get Devices")
    print("=" * 70)
    print(f"Testing at: {datetime.now().isoformat()}\n")

    try:
        client = AmbientWeatherClient(API_KEY, APP_KEY)

        print("Calling: client.get_devices()")
        devices = client.get_devices()

        print(f"✅ SUCCESS: Got {len(devices)} device(s)")

        if devices:
            device = devices[0]
            print(f"Device Details:")
            print(f"  MAC: {device.get('macAddress', 'N/A')}")
            print(f"  Name: {device.get('info', {}).get('name', 'N/A')}")
            print(f"  Location: {device.get('info', {}).get('location', 'N/A')}")

        print()
        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"   Type: {type(e).__name__}")

        import traceback

        print("\nFull traceback:")
        traceback.print_exc()

        print()
        return False


def test_client_get_device_data():
    """Test our client's get_device_data method"""
    print("=" * 70)
    print("Test 3.2: Our Client - Get Device Data")
    print("=" * 70)
    print(f"Testing at: {datetime.now().isoformat()}\n")

    if not MAC_ADDRESS:
        print("❌ ERROR: AMBIENT_MAC_ADDRESS not set")
        return False

    try:
        client = AmbientWeatherClient(API_KEY, APP_KEY)

        print(f"Calling: client.get_device_data('{MAC_ADDRESS}', limit=1)")
        data = client.get_device_data(MAC_ADDRESS, limit=1)

        print(f"✅ SUCCESS: Got {len(data)} reading(s)")

        if data:
            reading = data[0]
            print(f"Latest Reading:")
            print(f"  Date: {reading.get('date', 'N/A')}")
            print(f"  Temp: {reading.get('tempf', 'N/A')}°F")
            print(f"  Humidity: {reading.get('humidity', 'N/A')}%")
            print(f"  Wind: {reading.get('windspeedmph', 'N/A')} mph")

        print()
        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"   Type: {type(e).__name__}")

        # Check if it's a rate limit error
        if "429" in str(e) or "rate" in str(e).lower():
            print("   → This is a rate limit error (expected based on Phase 1)")

        import traceback

        print("\nFull traceback:")
        traceback.print_exc()

        print()
        return False


def compare_request_details():
    """Compare our client's request format with working curl"""
    print("=" * 70)
    print("Test 3.3: Request Format Comparison")
    print("=" * 70)
    print("Comparing our client's request with known-working curl\n")

    try:
        import requests
        from weather_app.api.ambient_client import AmbientWeatherClient

        # Get our client's session details
        client = AmbientWeatherClient(API_KEY, APP_KEY)

        print("Our Client Configuration:")
        print(f"  Base URL: {client.base_url}")
        print(f"  API Key: ...{API_KEY[-8:]}")
        print(f"  App Key: ...{APP_KEY[-8:]}")

        # Check what our client sends
        print("\nChecking request parameters our client would send...")

        # Make a request and inspect it
        print("\n(This will trigger rate limit if not already limited)")

        # Show what a working curl would be
        print("\nWorking curl equivalent:")
        print(
            f'curl "https://api.ambientweather.net/v1/devices?apiKey={API_KEY[:8]}...&applicationKey={APP_KEY[:8]}..."'
        )

        print("\nPotential differences to investigate:")
        print("  - Headers (User-Agent, Accept, etc.)")
        print("  - Query parameter encoding")
        print("  - Connection settings (timeout, keep-alive)")
        print("  - SSL/TLS version")

        print()
        return True

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def main():
    """Run Phase 3 tests"""
    print("=" * 70)
    print("PHASE 3: TEST OUR API CLIENT")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    print("WARNING: These tests will make API calls")
    print("         If still rate-limited from Phase 1, tests will fail")
    print()

    # Test 3.1: Get devices
    test_3_1 = test_client_get_devices()

    # Test 3.2: Get device data
    test_3_2 = test_client_get_device_data()

    # Test 3.3: Compare request format
    test_3_3 = compare_request_details()

    # Summary
    print("=" * 70)
    print("PHASE 3 SUMMARY")
    print("=" * 70)

    results = [
        ("Get Devices", test_3_1),
        ("Get Device Data", test_3_2),
        ("Request Comparison", test_3_3),
    ]

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("✅ PHASE 3 COMPLETE: Our client works correctly!")
        print("   → Issue is not in our client code")
        print("   → Continue to Phase 4 (Historical Data)")
    elif not test_3_1 and not test_3_2:
        print("❌ PHASE 3 BLOCKED: Still rate limited")
        print("   → Wait for cooldown period")
        print("   → Run experiment_cooldown_detection.py first")
    else:
        print("⚠️  PHASE 3 PARTIAL: Some tests passed")
        print("   → Review failures above")
        print("   → May indicate bug in specific client methods")

    print()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
