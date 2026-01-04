#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1: Basic Connectivity Test
Tests if our API credentials work at all with simple requests
"""

import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AMBIENT_API_KEY")
APP_KEY = os.getenv("AMBIENT_APP_KEY")
MAC_ADDRESS = os.getenv("AMBIENT_MAC_ADDRESS")

BASE_URL = "https://api.ambientweather.net/v1"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def test_device_list():
    """Test 1.1: Get device list"""
    print_section("Test 1.1: Device List API Call")

    url = f"{BASE_URL}/devices"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY}

    print(f"URL: {url}")
    print(f"Params: apiKey=...{API_KEY[-4:]}, applicationKey=...{APP_KEY[-4:]}")
    print(f"Making request at: {datetime.now().isoformat()}")
    print()

    try:
        response = requests.get(url, params=params, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        print()

        # Headers
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        print()

        # Body
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got {len(data)} device(s)")
            if data:
                print(f"Device MAC: {data[0].get('macAddress', 'N/A')}")
                print(f"Device Name: {data[0].get('info', {}).get('name', 'N/A')}")
            print()
            return True
        elif response.status_code == 429:
            print(f"❌ RATE LIMITED (429)")
            print(f"Retry-After header: {response.headers.get('Retry-After', 'NOT PRESENT')}")
            print(f"Response: {response.text[:200]}")
            print()
            return False
        elif response.status_code == 401:
            print(f"❌ UNAUTHORIZED (401) - Invalid API keys")
            print(f"Response: {response.text[:200]}")
            print()
            return False
        else:
            print(f"❌ UNEXPECTED STATUS: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            print()
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def test_device_data():
    """Test 1.2: Get device data (1 reading)"""
    print_section("Test 1.2: Device Data API Call (limit=1)")

    if not MAC_ADDRESS:
        print("❌ ERROR: AMBIENT_MAC_ADDRESS not set in .env")
        return False

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    print(f"URL: {url}")
    print(f"MAC: {MAC_ADDRESS}")
    print(f"Params: limit=1, apiKey=...{API_KEY[-4:]}, applicationKey=...{APP_KEY[-4:]}")
    print(f"Making request at: {datetime.now().isoformat()}")
    print()

    try:
        response = requests.get(url, params=params, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        print()

        # Headers
        print("Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        print()

        # Body
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got {len(data)} reading(s)")
            if data:
                reading = data[0]
                print(f"Date: {reading.get('date', 'N/A')}")
                print(f"Temp: {reading.get('tempf', 'N/A')}°F")
                print(f"Humidity: {reading.get('humidity', 'N/A')}%")
                # Check timestamp resolution
                if len(data) > 1:
                    time_diff = reading.get("dateutc", 0) - data[1].get("dateutc", 0)
                    print(f"Time between readings: {time_diff / 1000 / 60:.1f} minutes")
            print()
            return True
        elif response.status_code == 429:
            print(f"❌ RATE LIMITED (429)")
            print(f"Retry-After header: {response.headers.get('Retry-After', 'NOT PRESENT')}")
            print(f"Response: {response.text[:200]}")
            print()
            return False
        elif response.status_code == 401:
            print(f"❌ UNAUTHORIZED (401) - Invalid API keys")
            print(f"Response: {response.text[:200]}")
            print()
            return False
        else:
            print(f"❌ UNEXPECTED STATUS: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            print()
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False


def check_credentials():
    """Validate credential format"""
    print_section("Credential Validation")

    issues = []

    if not API_KEY:
        issues.append("AMBIENT_API_KEY not set")
    else:
        print(f"API Key: ...{API_KEY[-8:]} (length: {len(API_KEY)})")
        if " " in API_KEY or "\n" in API_KEY:
            issues.append("API Key contains whitespace")

    if not APP_KEY:
        issues.append("AMBIENT_APP_KEY not set")
    else:
        print(f"App Key: ...{APP_KEY[-8:]} (length: {len(APP_KEY)})")
        if " " in APP_KEY or "\n" in APP_KEY:
            issues.append("App Key contains whitespace")

    if not MAC_ADDRESS:
        print(f"MAC Address: (not set - will skip device data test)")
    else:
        print(f"MAC Address: {MAC_ADDRESS}")

    print()

    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Credentials look valid")
        return True


def main():
    """Run all basic connectivity tests"""
    print("=" * 70)
    print("PHASE 1: BASIC CONNECTIVITY TEST")
    print("=" * 70)
    print(f"Testing Ambient Weather API at: {datetime.now().isoformat()}")
    print()

    # Check credentials
    if not check_credentials():
        print("\n❌ Fix credential issues before proceeding")
        return False

    # Test 1: Device list
    test1_passed = test_device_list()

    # Test 2: Device data (if we have MAC)
    test2_passed = False
    if MAC_ADDRESS:
        test2_passed = test_device_data()
    else:
        print("\nSkipping Test 1.2 (no MAC address)")

    # Summary
    print_section("PHASE 1 SUMMARY")

    results = []
    results.append(("Credentials Valid", check_credentials()))
    results.append(("Device List API", test1_passed))
    if MAC_ADDRESS:
        results.append(("Device Data API", test2_passed))

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("✅ PHASE 1 COMPLETE: Basic connectivity works!")
        print("   → Continue to Phase 2 (Frequency Test)")
    else:
        print("❌ PHASE 1 FAILED: Fix basic connectivity before proceeding")
        print()
        print("Troubleshooting:")
        print("  1. Verify API keys in .env file are correct")
        print("  2. Check Ambient Weather dashboard for API key status")
        print("  3. Ensure no whitespace/newlines in API keys")
        print("  4. Try generating new API keys")

    print()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
