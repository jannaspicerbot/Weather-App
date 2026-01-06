"""
Diagnostic Script: API Connection Issue Root Cause Analysis
Tests three high-probability fixes:
1. Request timeouts
2. Custom User-Agent header
3. Session reuse (connection pooling)

This script compares the CURRENT implementation against FIXED implementations
to identify which changes improve API connectivity.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class DiagnosticResults:
    """Stores test results for comparison"""
    def __init__(self):
        self.tests = []

    def add_test(self, name, status_code, duration_ms, error=None, headers=None):
        self.tests.append({
            'name': name,
            'status_code': status_code,
            'duration_ms': duration_ms,
            'error': error,
            'headers': headers or {},
            'timestamp': datetime.now().isoformat()
        })

    def print_summary(self):
        print("\n" + "="*80)
        print("DIAGNOSTIC TEST RESULTS SUMMARY")
        print("="*80)

        for test in self.tests:
            status_icon = "✅" if test['status_code'] == 200 else "❌"
            print(f"\n{status_icon} {test['name']}")
            print(f"   Status Code: {test['status_code']}")
            print(f"   Duration: {test['duration_ms']:.2f}ms")

            if test['error']:
                print(f"   Error: {test['error']}")

            if test['headers']:
                print(f"   Request Headers: {test['headers']}")

        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)

        success_count = sum(1 for t in self.tests if t['status_code'] == 200)
        total = len(self.tests)

        print(f"Success Rate: {success_count}/{total} ({(success_count/total)*100:.1f}%)")

        # Identify which fixes helped
        current_test = next((t for t in self.tests if 'Current' in t['name']), None)
        if current_test and current_test['status_code'] != 200:
            print("\n🔍 Root Cause Analysis:")
            print("   Current implementation failed. Testing fixes...")

            for test in self.tests:
                if test['name'] != current_test['name'] and test['status_code'] == 200:
                    print(f"   ✅ {test['name']} SUCCEEDED - This fix helps!")
                elif test['name'] != current_test['name'] and test['status_code'] != 200:
                    print(f"   ❌ {test['name']} FAILED - This fix doesn't help")


def test_current_implementation(api_key, app_key, results):
    """Test 1: Current implementation (no fixes)"""
    print("\n" + "-"*80)
    print("TEST 1: Current Implementation (Baseline)")
    print("-"*80)
    print("Testing with:")
    print("  - No timeout (default)")
    print("  - Default User-Agent (python-requests/X.X.X)")
    print("  - New connection per request")
    print()

    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": api_key, "applicationKey": app_key}

    start_time = time.time()
    try:
        # This mimics weather_app/api/client.py current implementation
        response = requests.get(url, params=params)  # NO TIMEOUT!
        duration_ms = (time.time() - start_time) * 1000

        print(f"✅ Status: {response.status_code}")
        print(f"   Duration: {duration_ms:.2f}ms")
        print(f"   Response size: {len(response.text)} bytes")

        results.add_test(
            "Current Implementation",
            response.status_code,
            duration_ms,
            headers={'User-Agent': response.request.headers.get('User-Agent')}
        )

        return response.status_code == 200

    except requests.exceptions.Timeout:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ TIMEOUT after {duration_ms:.2f}ms")
        results.add_test("Current Implementation", 0, duration_ms, error="Timeout")
        return False

    except requests.exceptions.RequestException as e:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ ERROR: {e}")
        results.add_test("Current Implementation", 0, duration_ms, error=str(e))
        return False


def test_with_timeout(api_key, app_key, results):
    """Test 2: Add timeout (Fix #1)"""
    print("\n" + "-"*80)
    print("TEST 2: Fix #1 - Add Request Timeout")
    print("-"*80)
    print("Testing with:")
    print("  - Timeout: 30 seconds")
    print("  - Default User-Agent (python-requests/X.X.X)")
    print("  - New connection per request")
    print()

    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": api_key, "applicationKey": app_key}

    start_time = time.time()
    try:
        response = requests.get(url, params=params, timeout=30)  # FIX #1: Add timeout
        duration_ms = (time.time() - start_time) * 1000

        print(f"✅ Status: {response.status_code}")
        print(f"   Duration: {duration_ms:.2f}ms")
        print(f"   Response size: {len(response.text)} bytes")

        results.add_test(
            "Fix #1: Timeout Only",
            response.status_code,
            duration_ms,
            headers={'User-Agent': response.request.headers.get('User-Agent')}
        )

        return response.status_code == 200

    except requests.exceptions.Timeout:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ TIMEOUT after {duration_ms:.2f}ms")
        results.add_test("Fix #1: Timeout Only", 0, duration_ms, error="Timeout")
        return False

    except requests.exceptions.RequestException as e:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ ERROR: {e}")
        results.add_test("Fix #1: Timeout Only", 0, duration_ms, error=str(e))
        return False


def test_with_user_agent(api_key, app_key, results):
    """Test 3: Add custom User-Agent (Fix #2)"""
    print("\n" + "-"*80)
    print("TEST 3: Fix #2 - Add Custom User-Agent Header")
    print("-"*80)
    print("Testing with:")
    print("  - Timeout: 30 seconds")
    print("  - Custom User-Agent: WeatherApp/1.0 (Diagnostic Test)")
    print("  - New connection per request")
    print()

    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": api_key, "applicationKey": app_key}

    # FIX #2: Add custom User-Agent
    headers = {
        'User-Agent': 'WeatherApp/1.0 (Diagnostic Test; Python)',
        'Accept': 'application/json'
    }

    start_time = time.time()
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        duration_ms = (time.time() - start_time) * 1000

        print(f"✅ Status: {response.status_code}")
        print(f"   Duration: {duration_ms:.2f}ms")
        print(f"   Response size: {len(response.text)} bytes")
        print(f"   User-Agent sent: {headers['User-Agent']}")

        results.add_test(
            "Fix #2: Custom User-Agent",
            response.status_code,
            duration_ms,
            headers=headers
        )

        return response.status_code == 200

    except requests.exceptions.Timeout:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ TIMEOUT after {duration_ms:.2f}ms")
        results.add_test("Fix #2: Custom User-Agent", 0, duration_ms, error="Timeout", headers=headers)
        return False

    except requests.exceptions.RequestException as e:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ ERROR: {e}")
        results.add_test("Fix #2: Custom User-Agent", 0, duration_ms, error=str(e), headers=headers)
        return False


def test_with_session(api_key, app_key, results):
    """Test 4: Use requests.Session for connection reuse (Fix #3)"""
    print("\n" + "-"*80)
    print("TEST 4: Fix #3 - Use Session (Connection Reuse)")
    print("-"*80)
    print("Testing with:")
    print("  - Timeout: 30 seconds")
    print("  - Custom User-Agent: WeatherApp/1.0 (Diagnostic Test)")
    print("  - Session with connection pooling (reuse)")
    print()

    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": api_key, "applicationKey": app_key}

    # FIX #3: Use Session
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'WeatherApp/1.0 (Diagnostic Test; Python)',
        'Accept': 'application/json'
    })

    start_time = time.time()
    try:
        response = session.get(url, params=params, timeout=30)
        duration_ms = (time.time() - start_time) * 1000

        print(f"✅ Status: {response.status_code}")
        print(f"   Duration: {duration_ms:.2f}ms")
        print(f"   Response size: {len(response.text)} bytes")
        print(f"   User-Agent sent: {session.headers['User-Agent']}")
        print(f"   Connection: Pooled/Reusable")

        results.add_test(
            "Fix #3: Session + All Fixes",
            response.status_code,
            duration_ms,
            headers=dict(session.headers)
        )

        session.close()
        return response.status_code == 200

    except requests.exceptions.Timeout:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ TIMEOUT after {duration_ms:.2f}ms")
        results.add_test("Fix #3: Session + All Fixes", 0, duration_ms, error="Timeout", headers=dict(session.headers))
        session.close()
        return False

    except requests.exceptions.RequestException as e:
        duration_ms = (time.time() - start_time) * 1000
        print(f"❌ ERROR: {e}")
        results.add_test("Fix #3: Session + All Fixes", 0, duration_ms, error=str(e), headers=dict(session.headers))
        session.close()
        return False


def test_burst_behavior(api_key, app_key, results, use_fixes=False):
    """Test 5: Burst behavior (multiple rapid requests)"""
    test_name = "Burst Test (WITH fixes)" if use_fixes else "Burst Test (WITHOUT fixes)"

    print("\n" + "-"*80)
    print(f"TEST 5: {test_name}")
    print("-"*80)
    print("Testing: 3 rapid consecutive calls (10-second intervals)")
    print()

    if use_fixes:
        print("Using fixes:")
        print("  - Timeout: 30 seconds")
        print("  - Custom User-Agent")
        print("  - Session with connection pooling")

        session = requests.Session()
        session.headers.update({
            'User-Agent': 'WeatherApp/1.0 (Burst Test; Python)',
            'Accept': 'application/json'
        })
    else:
        print("No fixes (baseline):")
        print("  - No timeout")
        print("  - Default User-Agent")
        print("  - New connection per request")
        session = None

    url = "https://api.ambientweather.net/v1/devices"
    params = {"apiKey": api_key, "applicationKey": app_key}

    burst_results = []

    for i in range(3):
        print(f"\n  Request {i+1}/3:")
        start_time = time.time()

        try:
            if use_fixes:
                response = session.get(url, params=params, timeout=30)
            else:
                response = requests.get(url, params=params)

            duration_ms = (time.time() - start_time) * 1000

            print(f"    ✅ Status: {response.status_code} ({duration_ms:.2f}ms)")
            burst_results.append({
                'request': i+1,
                'status': response.status_code,
                'duration_ms': duration_ms
            })

            if response.status_code == 429:
                print(f"    ⚠️  RATE LIMITED on request {i+1}")
                print(f"    Retry-After header: {response.headers.get('Retry-After', 'Not provided')}")
                break

        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            print(f"    ❌ ERROR: {e} ({duration_ms:.2f}ms)")
            burst_results.append({
                'request': i+1,
                'status': 0,
                'duration_ms': duration_ms,
                'error': str(e)
            })
            break

        # Wait 10 seconds between requests (except after last one)
        if i < 2:
            print(f"    Waiting 10 seconds...")
            time.sleep(10)

    if session:
        session.close()

    # Summary
    success_count = sum(1 for r in burst_results if r.get('status') == 200)
    print(f"\n  Burst Test Summary: {success_count}/3 successful")

    # Record aggregate result
    if success_count == 3:
        results.add_test(test_name, 200, 0, error=f"All {success_count}/3 succeeded")
    elif success_count > 0:
        results.add_test(test_name, 206, 0, error=f"Partial success: {success_count}/3")
    else:
        results.add_test(test_name, 429, 0, error="All requests failed/rate limited")


def main():
    print("="*80)
    print("AMBIENT WEATHER API DIAGNOSTIC TOOL")
    print("="*80)
    print("Purpose: Test high-probability fixes for API connection issues")
    print()
    print("Tests:")
    print("  1. Current implementation (baseline)")
    print("  2. Fix #1: Add request timeout")
    print("  3. Fix #2: Add custom User-Agent header")
    print("  4. Fix #3: Use session for connection pooling")
    print("  5. Burst behavior test (with and without fixes)")
    print()
    print("="*80)

    # Get credentials
    api_key = os.getenv("AMBIENT_API_KEY")
    app_key = os.getenv("AMBIENT_APP_KEY")

    if not api_key or not app_key:
        print("❌ ERROR: API credentials not found!")
        print("Please set environment variables:")
        print("  AMBIENT_API_KEY - Your API key")
        print("  AMBIENT_APP_KEY - Your Application key")
        print("\nOr create a .env file with these variables.")
        sys.exit(1)

    print(f"✅ Loaded credentials from environment")
    print(f"   API Key: {api_key[:8]}... ({len(api_key)} chars)")
    print(f"   App Key: {app_key[:8]}... ({len(app_key)} chars)")
    print()

    # Check for background processes
    print("🔍 Checking for background API clients...")
    print("   Note: If you see data at localhost:5173, a backend server is running")
    print("   This could cause concurrent API calls that burn through rate limits")
    print()

    input("Press Enter to start diagnostic tests (or Ctrl+C to cancel)...")

    results = DiagnosticResults()

    # Run all tests with delays to avoid rate limiting
    print("\n⏱️  Running tests with 10-second delays to minimize rate limit risk...")

    # Test 1: Current implementation
    test_current_implementation(api_key, app_key, results)
    time.sleep(10)

    # Test 2: With timeout
    test_with_timeout(api_key, app_key, results)
    time.sleep(10)

    # Test 3: With User-Agent
    test_with_user_agent(api_key, app_key, results)
    time.sleep(10)

    # Test 4: With session
    test_with_session(api_key, app_key, results)
    time.sleep(10)

    # Test 5a: Burst without fixes
    print("\n⚠️  WARNING: Next test may trigger rate limits!")
    input("Press Enter to run burst test WITHOUT fixes (or Ctrl+C to skip)...")
    test_burst_behavior(api_key, app_key, results, use_fixes=False)

    print("\n⏱️  Waiting 30 seconds before burst test with fixes...")
    time.sleep(30)

    # Test 5b: Burst with fixes
    print("\n⚠️  WARNING: Next test may trigger rate limits!")
    input("Press Enter to run burst test WITH fixes (or Ctrl+C to skip)...")
    test_burst_behavior(api_key, app_key, results, use_fixes=True)

    # Print results
    results.print_summary()

    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("Based on the results above:")
    print("1. If ALL tests failed → Account tier is likely the issue")
    print("2. If SOME tests succeeded → Implement the successful fixes")
    print("3. If tests improved over baseline → Each fix contributes")
    print()
    print("Save these results and discuss with the team.")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
