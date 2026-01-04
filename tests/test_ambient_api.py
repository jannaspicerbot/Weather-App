#!/usr/bin/env python3
"""
Simple test script to fetch just a few recent weather records
This helps diagnose API issues without hitting rate limits
"""

import os
import sys
from pathlib import Path

import requests

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Look for .env in project root (parent of tests directory)
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print(
        "Warning: python-dotenv not installed. Install it with: pip install python-dotenv"
    )


def test_api_connection():
    """Test the Ambient Weather API with minimal requests"""

    # Get API credentials from environment variables
    API_KEY = os.getenv("AMBIENT_API_KEY")
    APPLICATION_KEY = os.getenv("AMBIENT_APP_KEY")

    if not API_KEY or not APPLICATION_KEY:
        print("ERROR: Environment variables not set!")
        print("Run these first:")
        print('  $env:AMBIENT_API_KEY="your_key"')
        print('  $env:AMBIENT_APP_KEY="your_key"')
        sys.exit(1)

    print("=" * 60)
    print("Ambient Weather API Test")
    print("=" * 60)
    print(f"\nAPI Key: {API_KEY[:10]}...{API_KEY[-4:]}")
    print(f"App Key: {APPLICATION_KEY[:10]}...{APPLICATION_KEY[-4:]}")

    # Step 1: Get devices
    print("\n[Step 1] Fetching device list...")
    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": API_KEY, "applicationKey": APPLICATION_KEY}

    try:
        response = requests.get(url, params=params)
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 429:
            print("\n❌ RATE LIMIT ERROR")
            print("  This usually means:")
            print("  1. You've made too many requests recently")
            print("  2. Your account has API restrictions")
            print("  3. The Application Key might not be fully activated")
            print("\n  Try:")
            print("  - Wait 1 hour and try again")
            print("  - Check your account status on ambientweather.net")
            print("  - Delete and recreate your Application Key")
            return

        response.raise_for_status()
        devices = response.json()

        print(f"  ✅ Success! Found {len(devices)} device(s)")

        if not devices:
            print("\n❌ No devices found in your account!")
            return

        # Show device info
        for i, device in enumerate(devices):
            print(f"\n  Device {i+1}:")
            print(f"    Name: {device['info']['name']}")
            print(f"    MAC: {device['macAddress']}")
            print(
                f"    Location: {device['info'].get('coords', {}).get('address', 'N/A')}"
            )

        # Step 2: Fetch just the last 5 records from first device
        print("\n[Step 2] Fetching last 5 records from first device...")
        device = devices[0]
        mac = device["macAddress"]

        url = f"https://api.ambientweather.net/v1/devices/{mac}"
        params = {
            "apiKey": API_KEY,
            "applicationKey": APPLICATION_KEY,
            "limit": 5,  # Just 5 records
        }

        response = requests.get(url, params=params)
        print(f"  Status Code: {response.status_code}")

        if response.status_code == 429:
            print("\n❌ RATE LIMIT ERROR on data fetch")
            print("  You've hit the rate limit even on minimal requests.")
            print("  This suggests your API access might be throttled.")
            return

        response.raise_for_status()
        data = response.json()

        print(f"  ✅ Success! Retrieved {len(data)} records")

        if data:
            latest = data[0]
            print("\n  Latest reading:")
            print(f"    Date: {latest.get('date', 'N/A')}")
            print(f"    Temp: {latest.get('tempf', 'N/A')}°F")
            print(f"    Humidity: {latest.get('humidity', 'N/A')}%")
            print(f"    Wind: {latest.get('windspeedmph', 'N/A')} mph")

            print("\n  All fields available:")
            for key in sorted(latest.keys()):
                if key not in ["dateutc", "date"]:
                    print(f"    - {key}")

        print("\n" + "=" * 60)
        print("✅ API TEST SUCCESSFUL!")
        print("=" * 60)
        print("\nYour API connection is working. You can now run the full")
        print("data fetching script, but consider:")
        print("  - Starting with a smaller date range")
        print("  - Waiting a bit between runs to avoid rate limits")

    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        print(f"  Response: {response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    test_api_connection()
