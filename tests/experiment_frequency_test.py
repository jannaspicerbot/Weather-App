#!/usr/bin/env python3
"""
Phase 2: Frequency Tolerance Test
Replicate external user's "every minute for 24 hours" success
Tests sliding window rate limiting behavior
"""

import os
import sys
import time
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


def test_one_minute_intervals(iterations=10, interval_seconds=60):
    """
    Test 2.1 & 2.2: Hit API at 1-minute intervals
    User reported: Can do this for 24 hours (1,440 requests) with no 429s
    """
    print("=" * 70)
    print(f"Test: {iterations} requests at {interval_seconds}s intervals")
    print("=" * 70)
    print(f"User reported: Can hit API every minute for 24 hours with no 429s")
    print(f"We're testing: {iterations} requests over {iterations * interval_seconds / 60:.1f} minutes")
    print()

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    results = []
    start_time = datetime.now()

    for i in range(iterations):
        iteration_start = datetime.now()
        print(f"[{i+1}/{iterations}] Request at {iteration_start.strftime('%H:%M:%S')}...")

        try:
            response = requests.get(url, params=params, timeout=30)
            elapsed = response.elapsed.total_seconds()

            results.append(
                {
                    "iteration": i + 1,
                    "timestamp": iteration_start,
                    "status_code": response.status_code,
                    "response_time": elapsed,
                    "retry_after": response.headers.get("Retry-After"),
                }
            )

            if response.status_code == 200:
                print(f"  ✅ 200 OK ({elapsed:.2f}s)")
            elif response.status_code == 429:
                retry_after = response.headers.get("Retry-After", "NOT PRESENT")
                print(f"  ❌ 429 RATE LIMITED (Retry-After: {retry_after})")
                print(f"     Failed at iteration {i+1}/{iterations}")
                break
            else:
                print(f"  ⚠️  {response.status_code}")

        except Exception as e:
            print(f"  ❌ ERROR: {str(e)}")
            results.append(
                {
                    "iteration": i + 1,
                    "timestamp": iteration_start,
                    "status_code": "ERROR",
                    "response_time": 0,
                    "error": str(e),
                }
            )

        # Sleep until next interval (unless last iteration)
        if i < iterations - 1:
            time.sleep(interval_seconds)

    # Summary
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)

    success_count = sum(1 for r in results if r["status_code"] == 200)
    rate_limited_count = sum(1 for r in results if r["status_code"] == 429)
    error_count = sum(1 for r in results if r["status_code"] == "ERROR")

    print(f"Total requests: {len(results)}")
    print(f"  ✅ Success (200): {success_count}")
    print(f"  ❌ Rate Limited (429): {rate_limited_count}")
    print(f"  ❌ Errors: {error_count}")
    print()

    if success_count == iterations:
        print(f"✅ PASS: All {iterations} requests succeeded!")
        print("   → Our behavior matches external user's experience")
        return True
    elif rate_limited_count > 0:
        first_429 = next(r for r in results if r["status_code"] == 429)
        print(f"❌ FAIL: Hit 429 at iteration {first_429['iteration']}")
        print("   → Our account has different limits than external user")
        print(f"   → Retry-After header: {first_429.get('retry_after', 'N/A')}")
        return False
    else:
        print(f"⚠️  PARTIAL: {success_count}/{iterations} succeeded")
        return False


def test_burst_sliding_window():
    """
    Test 2.3: Burst test to detect sliding window
    User reported:
    - 2 req/sec for 5 seconds = OK
    - 2 req/sec for 6 seconds = 429
    - 5 seconds of no requests needed to recover
    """
    print("=" * 70)
    print("Test: Sliding Window Burst Detection")
    print("=" * 70)
    print("User reported:")
    print("  - 2 req/sec for 5 seconds = OK")
    print("  - 2 req/sec for 6 seconds = 429")
    print("  - 5 second cooldown to recover")
    print()

    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    burst_durations = [5, 6, 7, 8]  # Test increasing burst lengths

    for duration in burst_durations:
        print(f"Testing {duration}-second burst (2 req/sec)...")

        for i in range(duration * 2):  # 2 requests per second
            try:
                response = requests.get(url, params=params, timeout=10)

                if response.status_code == 200:
                    print(f"  {i+1}. ✅ 200", end="", flush=True)
                elif response.status_code == 429:
                    print(f"  {i+1}. ❌ 429 - Burst failed after {i+1} requests ({(i+1)/2:.1f} seconds)")
                    retry_after = response.headers.get("Retry-After", "NOT PRESENT")
                    print(f"     Retry-After: {retry_after}")
                    break
                else:
                    print(f"  {i+1}. ⚠️  {response.status_code}")

                time.sleep(0.5)  # 2 requests per second

            except Exception as e:
                print(f"  {i+1}. ❌ ERROR: {str(e)}")
                break

        print()

        # Cooldown period
        if duration < burst_durations[-1]:
            print(f"  Cooling down for 10 seconds...")
            time.sleep(10)
            print()

    print("=" * 70)
    print("OBSERVATIONS")
    print("=" * 70)
    print("Compare results above to user's report:")
    print("  Expected: 5 seconds OK, 6+ seconds = 429")
    print("  If different: Our account has different burst limits")
    print()


def main():
    """Run all frequency tests"""
    print("=" * 70)
    print("PHASE 2: FREQUENCY TOLERANCE TEST")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    if not MAC_ADDRESS:
        print("❌ ERROR: AMBIENT_MAC_ADDRESS not set in .env")
        return False

    # Quick pre-check with 30-second cooldown wait
    print("Waiting 30 seconds for API cooldown...")
    time.sleep(30)

    print("Running quick connectivity check...")
    url = f"{BASE_URL}/devices/{MAC_ADDRESS}"
    params = {"apiKey": API_KEY, "applicationKey": APP_KEY, "limit": 1}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"❌ Pre-check failed: {response.status_code}")
            print("   Waiting another 30 seconds and retrying...")
            time.sleep(30)
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"❌ Still failing: {response.status_code}")
                print("   Run experiment_basic_connectivity.py first")
                return False
        print("✅ Pre-check passed\n")
    except Exception as e:
        print(f"❌ Pre-check error: {str(e)}")
        return False

    # Test 2.1: 10 requests at 1-minute intervals
    print("\n" + "=" * 70)
    print("TEST 2.1: 10 Requests at 1-Minute Intervals")
    print("=" * 70)
    test_2_1 = test_one_minute_intervals(iterations=10, interval_seconds=60)

    # If Test 2.1 passed, optionally run longer test
    if test_2_1:
        print("\n✅ Test 2.1 passed! Skipping 60-minute test (Test 2.2) for now.")
        # Uncomment to run the longer test:
        # print("\n" + "=" * 70)
        # print("TEST 2.2: 60 Requests at 1-Minute Intervals (1 Hour)")
        # print("=" * 70)
        # test_one_minute_intervals(iterations=60, interval_seconds=60)

    # Test 2.3: Sliding window burst test
    print("\n" + "=" * 70)
    print("TEST 2.3: Sliding Window Burst Test")
    print("=" * 70)
    print("Running burst test to test sliding window behavior...")
    test_burst_sliding_window()

    # Summary
    print("\n" + "=" * 70)
    print("PHASE 2 SUMMARY")
    print("=" * 70)

    if test_2_1:
        print("✅ Can hit API every minute (at least 10 times)")
        print("   → Similar to external user's experience")
        print("   → Our rate limits appear normal")
        print("   → Continue to Phase 3 (Test Our Code)")
    else:
        print("❌ Cannot sustain 1-minute interval requests")
        print("   → Different from external user (they do 24 hours)")
        print("   → Possible causes:")
        print("      1. Account type difference (free vs paid?)")
        print("      2. API keys flagged/restricted")
        print("      3. Geographic/IP-based limiting")
        print("   → May need to contact external user for account details")

    print()
    return test_2_1


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
