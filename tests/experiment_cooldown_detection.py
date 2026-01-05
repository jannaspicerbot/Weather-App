#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cooldown Detection Test
Tests how long we need to wait after hitting 429 before we can call API again
"""

import os
import sys
import time
from datetime import datetime, timedelta

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


def test_single_call(test_name=""):
    """Make a single API call and return status"""
    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        return {
            "test": test_name,
            "timestamp": datetime.now(),
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "retry_after": response.headers.get("Retry-After"),
            "body": response.text[:100],
        }
    except Exception as e:
        return {
            "test": test_name,
            "timestamp": datetime.now(),
            "status_code": "ERROR",
            "error": str(e),
        }


def test_cooldown_intervals():
    """
    Test API at increasing intervals to find cooldown period
    External user reported: 5 seconds of no requests needed to recover from burst 429
    """
    print("=" * 70)
    print("COOLDOWN DETECTION TEST")
    print("=" * 70)
    print("Goal: Find how long we need to wait after 429 to make successful call")
    print("User reported: 5 seconds after burst 429s")
    print()

    # Test intervals in seconds
    intervals = [30, 60, 120, 300, 600, 1800, 3600]  # 30s, 1m, 2m, 5m, 10m, 30m, 1h

    results = []

    print("Starting cooldown test...")
    print("This will make 1 call, then wait increasing intervals\n")

    for i, wait_seconds in enumerate(intervals):
        print(
            f"Test {i+1}/{len(intervals)}: Waiting {wait_seconds}s ({wait_seconds/60:.1f} min)..."
        )
        print(
            f"  Wait until: {(datetime.now() + timedelta(seconds=wait_seconds)).strftime('%H:%M:%S')}"
        )

        # Wait
        time.sleep(wait_seconds)

        # Make call
        result = test_single_call(f"After {wait_seconds}s wait")
        results.append(result)

        print(f"  Status: {result['status_code']}", end="")
        if result["status_code"] == 200:
            print(" ✅ SUCCESS!")
            print(
                f"  → Cooldown period: {wait_seconds}s ({wait_seconds/60:.1f} minutes)"
            )
            break
        elif result["status_code"] == 429:
            print(" ❌ Still rate limited")
            print(f"     Response: {result.get('body', 'N/A')[:50]}")
        else:
            print(f" ⚠️  Unexpected: {result.get('body', 'N/A')[:50]}")

        print()

    # Summary
    print("\n" + "=" * 70)
    print("COOLDOWN TEST RESULTS")
    print("=" * 70)

    successful = next((r for r in results if r["status_code"] == 200), None)

    if successful:
        wait_time = intervals[results.index(successful)]
        print(
            f"✅ Found cooldown period: {wait_time} seconds ({wait_time/60:.1f} minutes)"
        )
        print("   External user reported: 5 seconds")
        print(f"   Our experience: {wait_time} seconds ({wait_time/5}x longer)")
        return wait_time
    else:
        max_wait = intervals[-1] if results else 0
        print(f"❌ Still rate limited after {max_wait}s ({max_wait/60:.1f} minutes)")
        print("   May need to wait even longer (try 24 hours?)")
        return None


def test_progressive_intervals():
    """
    Test every minute for 10 minutes to find exact recovery point
    Use this after finding approximate cooldown from test_cooldown_intervals
    """
    print("=" * 70)
    print("PROGRESSIVE INTERVAL TEST")
    print("=" * 70)
    print("Testing every 1 minute for 10 minutes")
    print("This helps find the exact recovery time\n")

    results = []

    for i in range(10):
        print(f"Minute {i+1}/10 - Testing at {datetime.now().strftime('%H:%M:%S')}...")

        result = test_single_call(f"Minute {i+1}")
        results.append(result)

        if result["status_code"] == 200:
            print(f"  ✅ SUCCESS! Recovered after ~{i+1} minutes")
            break
        elif result["status_code"] == 429:
            print("  ❌ Still rate limited")
        else:
            print(f"  ⚠️  Status: {result['status_code']}")

        # Wait 1 minute (unless last iteration)
        if i < 9:
            time.sleep(60)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    successful = next((r for r in results if r["status_code"] == 200), None)
    if successful:
        recovery_time = (results.index(successful) + 1) * 60  # minutes * 60
        print(f"✅ Recovered after: ~{recovery_time/60:.0f} minutes")
        return recovery_time
    else:
        print("❌ Still rate limited after 10 minutes")
        return None


def main():
    """Run cooldown detection tests"""
    print("=" * 70)
    print("API COOLDOWN PERIOD DETECTION")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    if not MAC_ADDRESS:
        print("❌ ERROR: AMBIENT_MAC_ADDRESS not set in .env")
        return False

    print("This test will help us understand:")
    print("  1. How long to wait after hitting 429")
    print("  2. Whether our cooldown is different from external user")
    print("  3. If rate limits reset hourly, daily, or on sliding window")
    print()

    # Choose test strategy
    print("Test strategy: Running option 3 (both tests)")
    print("  1. Quick test (30s, 1m, 2m, 5m, 10m, 30m, 1h intervals)")
    print("  2. Progressive test (every 1 minute for 10 minutes)")
    print()

    choice = "3"

    if choice in ["1", "3"]:
        cooldown = test_cooldown_intervals()
        if cooldown and cooldown <= 600:  # If recovered in ≤10 minutes
            print(
                "\n✅ Found quick recovery! External user is right about fast cooldown."
            )
        elif cooldown:
            print(f"\n⚠️  Much longer cooldown than user reported (5s vs {cooldown}s)")

    if choice in ["2", "3"]:
        if choice == "3":
            print("\n\nRunning progressive test to confirm...")
            time.sleep(5)

        test_progressive_intervals()

    # Final summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print("Compare to external user:")
    print("  Their recovery: 5 seconds after burst 429")
    print("  Our experience: (see results above)")
    print()
    print("Next steps:")
    print("  1. Document cooldown period in phase-1-results.md")
    print("  2. Ask external user about account type")
    print("  3. Check Ambient Weather dashboard for account restrictions")
    print()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
