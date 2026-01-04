#!/usr/bin/env python3
"""
Quick API Tester
Tests the Weather API endpoints with the current database configuration
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_root():
    """Test root endpoint"""
    print_section("Testing Root Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        response.raise_for_status()
        data = response.json()

        print(f"✓ API is running")
        print(f"  Version: {data.get('version')}")
        print(f"  Database Mode: {data.get('database', {}).get('mode')}")
        print(f"  Database Path: {data.get('database', {}).get('path')}")
        return True
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: Cannot connect to API")
        print("  Make sure the API is running: python main.py")
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_stats():
    """Test stats endpoint"""
    print_section("Testing Stats Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/weather/stats")
        response.raise_for_status()
        data = response.json()

        print(f"✓ Stats endpoint working")
        print(f"  Total Records: {data.get('total_records'):,}")
        print(f"  Date Range: {data.get('min_date')} to {data.get('max_date')}")
        if data.get("date_range_days") is not None:
            print(f"  Days of Data: {data.get('date_range_days')}")

        return data.get("total_records", 0) > 0
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_latest():
    """Test latest weather endpoint"""
    print_section("Testing Latest Weather Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/weather/latest")
        response.raise_for_status()
        data = response.json()

        print(f"✓ Latest weather endpoint working")
        print(f"  Date: {data.get('date')}")
        print(f"  Temperature: {data.get('tempf')}°F")
        print(f"  Feels Like: {data.get('feelsLike')}°F")
        print(f"  Humidity: {data.get('humidity')}%")
        print(f"  Wind Speed: {data.get('windspeedmph')} mph")
        print(f"  Rain (daily): {data.get('dailyrainin')}\"")
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_weather_query():
    """Test weather query endpoint"""
    print_section("Testing Weather Query Endpoint")
    try:
        # Test basic query
        response = requests.get(f"{BASE_URL}/weather?limit=10")
        response.raise_for_status()
        data = response.json()

        print(f"✓ Weather query endpoint working")
        print(f"  Records returned: {len(data)}")

        if data:
            first = data[0]
            last = data[-1]
            print(f"  First record: {first.get('date')}")
            print(f"  Last record: {last.get('date')}")

        # Test with date filter
        print("\n  Testing date filter...")
        today = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{BASE_URL}/weather?start_date={today}&limit=5")
        response.raise_for_status()
        data = response.json()
        print(f"  ✓ Date filter working (found {len(data)} records for today)")

        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def test_pagination():
    """Test pagination"""
    print_section("Testing Pagination")
    try:
        # Get first page
        response1 = requests.get(f"{BASE_URL}/weather?limit=5&offset=0&order=asc")
        response1.raise_for_status()
        page1 = response1.json()

        # Get second page
        response2 = requests.get(f"{BASE_URL}/weather?limit=5&offset=5&order=asc")
        response2.raise_for_status()
        page2 = response2.json()

        print(f"✓ Pagination working")
        print(f"  Page 1 records: {len(page1)}")
        print(f"  Page 2 records: {len(page2)}")

        if page1 and page2:
            print(f"  Page 1 first date: {page1[0].get('date')}")
            print(f"  Page 2 first date: {page2[0].get('date')}")

            # Verify they're different
            if page1[0].get("id") != page2[0].get("id"):
                print(f"  ✓ Pages are different (correct)")
            else:
                print(f"  ✗ Pages are the same (incorrect)")

        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False


def main():
    print("=" * 60)
    print("Weather API Quick Test")
    print("=" * 60)
    print(f"Target: {BASE_URL}")

    # Run tests
    results = []

    if test_root():
        results.append(test_stats())
        results.append(test_latest())
        results.append(test_weather_query())
        results.append(test_pagination())
    else:
        print("\n✗ Cannot connect to API - stopping tests")
        return

    # Summary
    print_section("Test Summary")
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
    else:
        print(f"✗ {total - passed} test(s) failed")

    print("\n" + "=" * 60)
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
