#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4: Historical Data Retrieval Test
Test if historical queries have different rate limits than real-time queries
"""

import os
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables
load_dotenv()

API_KEY = os.getenv("AMBIENT_API_KEY")
APP_KEY = os.getenv("AMBIENT_APP_KEY")
MAC_ADDRESS = os.getenv("AMBIENT_MAC_ADDRESS")

BASE_URL = "https://api.ambientweather.net/v1"


def test_small_date_range():
    """Test 4.1: Get 1 day of data"""
    print("=" * 70)
    print("Test 4.1: Small Date Range (1 Day)")
    print("=" * 70)
    print("Goal: See if small historical queries work differently\n")

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"

    # Get 1 day of data (288 5-minute readings)
    params = {
        "apiKey": API_KEY,
        "applicationKey": APP_KEY,
        "limit": 288,  # 1 day at 5-minute intervals
    }

    print(f"Requesting: {url}")
    print("Params: limit=288 (1 day of 5-min data)")
    print(f"Time: {datetime.now().isoformat()}\n")

    try:
        response = requests.get(url, params=params, timeout=30)

        print(f"Status: {response.status_code}")
        print(f"Response Time: {response.elapsed.total_seconds():.2f}s")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got {len(data)} readings")

            if len(data) >= 2:
                first = data[0]
                last = data[-1]
                print(f"  First: {first.get('date', 'N/A')}")
                print(f"  Last: {last.get('date', 'N/A')}")

                # Check time resolution
                if len(data) >= 2:
                    time_diff = (
                        (first.get("dateutc", 0) - data[1].get("dateutc", 0))
                        / 1000
                        / 60
                    )
                    print(f"  Resolution: {time_diff:.1f} minutes between readings")
                    print(
                        "  → External user noted: API gives 5-min data, not real-time"
                    )

            print()
            return True

        elif response.status_code == 429:
            print("❌ RATE LIMITED")
            print(
                f"  Retry-After: {response.headers.get('Retry-After', 'NOT PRESENT')}"
            )
            print(f"  Response: {response.text[:100]}")
            print()
            return False

        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            print(f"  Response: {response.text[:100]}")
            print()
            return False

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print()
        return False


def test_multiple_small_vs_one_large():
    """Test 4.2: Compare multiple small queries vs one large query"""
    print("=" * 70)
    print("Test 4.2: Multiple Small vs One Large Query")
    print("=" * 70)
    print("Testing which approach triggers rate limits faster\n")

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"

    print("Strategy A: One large query (1000 readings)")
    print("-" * 70)

    params_large = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1000}

    try:
        response = requests.get(url, params=params_large, timeout=30)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS: Got {len(data)} readings in one call")
        elif response.status_code == 429:
            print("❌ RATE LIMITED on large query")
        else:
            print(f"⚠️  Status: {response.status_code}")

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    print()

    # Wait before trying small queries
    print("Waiting 60 seconds before trying small queries...")
    time.sleep(60)

    print("\nStrategy B: Multiple small queries (10x 100 readings)")
    print("-" * 70)

    params_small = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 100}

    successes = 0
    for i in range(10):
        try:
            response = requests.get(url, params=params_small, timeout=30)
            print(f"  Query {i+1}/10: ", end="")

            if response.status_code == 200:
                print("✅ OK")
                successes += 1
            elif response.status_code == 429:
                print(f"❌ 429 - Rate limited at query {i+1}")
                break
            else:
                print(f"⚠️  {response.status_code}")

            # Small delay between requests
            time.sleep(1)

        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            break

    print()
    print(f"Result: {successes}/10 small queries succeeded")
    print()

    if successes == 10:
        print("✅ Multiple small queries work better than one large")
        return True
    else:
        print("⚠️  Rate limited before completing all small queries")
        return False


def test_date_range_variations():
    """Test 4.3: Different date range specifications"""
    print("=" * 70)
    print("Test 4.3: Date Range Variations")
    print("=" * 70)
    print("Testing different ways to specify date ranges\n")

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"

    # Test 1: No date parameters (default)
    print("Test 1: No date params (get latest)")
    params1 = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    try:
        response = requests.get(url, params=params1, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Works")
        elif response.status_code == 429:
            print("  ❌ Rate limited")
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")

    print()

    # Test 2: With endDate
    print("Test 2: With endDate parameter")
    end_date = datetime.now()
    params2 = {
        "apiKey": API_KEY,
        "applicationKey": APP_KEY,
        "endDate": int(end_date.timestamp() * 1000),
        "limit": 1,
    }

    print(f"  endDate: {end_date.isoformat()}")

    try:
        time.sleep(5)  # Wait a bit
        response = requests.get(url, params=params2, timeout=10)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Works")
        elif response.status_code == 429:
            print("  ❌ Rate limited")
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)}")

    print()
    return True


def main():
    """Run Phase 4 tests"""
    print("=" * 70)
    print("PHASE 4: HISTORICAL DATA RETRIEVAL TEST")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    print("WARNING: These tests will make multiple API calls")
    print("         May trigger additional rate limiting")
    print()

    if not MAC_ADDRESS:
        print("❌ ERROR: AMBIENT_MAC_ADDRESS not set")
        return False

    # Confirm before proceeding
    try:
        input("Press Enter to continue or Ctrl+C to cancel...")
    except KeyboardInterrupt:
        print("\n\nTest cancelled")
        return False

    print()

    # Test 4.1: Small date range
    test_4_1 = test_small_date_range()

    if not test_4_1:
        print("⚠️  Test 4.1 failed (rate limited)")
        print("   Skipping remaining tests")
        print("   Run experiment_cooldown_detection.py to find recovery time")
        return False

    # Test 4.2: Multiple small vs one large (if 4.1 passed)
    print("Waiting 60 seconds before Test 4.2...")
    time.sleep(60)
    test_4_2 = test_multiple_small_vs_one_large()

    # Test 4.3: Date range variations
    test_4_3 = test_date_range_variations()

    # Summary
    print("=" * 70)
    print("PHASE 4 SUMMARY")
    print("=" * 70)

    results = [
        ("Small Date Range (1 day)", test_4_1),
        ("Multiple Small vs Large", test_4_2),
        ("Date Range Variations", test_4_3),
    ]

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("✅ PHASE 4 COMPLETE: Historical queries work!")
        print("   → Continue to Phase 5 (Authentication)")
    else:
        print("❌ PHASE 4 INCOMPLETE: Some tests failed")
        print("   → Likely still rate limited")

    print()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
