#!/usr/bin/env python3
"""
test_rate_limit_incremental.py - Systematic Rate Limit Testing
Tests one configuration at a time to understand exact behavior
"""

import requests
import time
import sys
import os
from datetime import datetime


def test_single_request(api_key, app_key, mac_address, limit, delay_before=0):
    """Test a single API call"""
    
    if delay_before > 0:
        print(f"  Waiting {delay_before}s before request...")
        time.sleep(delay_before)
    
    url = f"https://api.ambientweather.net/v1/devices/{mac_address}"
    params = {
        'apiKey': api_key,
        'applicationKey': app_key,
        'limit': limit
    }
    
    start_time = time.time()
    
    try:
        response = requests.get(url, params=params)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'status': 200,
                'count': len(data),
                'elapsed': elapsed,
                'message': f'SUCCESS - Got {len(data)} records in {elapsed:.2f}s'
            }
        elif response.status_code == 429:
            return {
                'success': False,
                'status': 429,
                'count': 0,
                'elapsed': elapsed,
                'message': f'RATE LIMITED (429) after {elapsed:.2f}s'
            }
        else:
            return {
                'success': False,
                'status': response.status_code,
                'count': 0,
                'elapsed': elapsed,
                'message': f'ERROR {response.status_code}: {response.text[:50]}'
            }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            'success': False,
            'status': 0,
            'count': 0,
            'elapsed': elapsed,
            'message': f'EXCEPTION: {str(e)}'
        }


def main():
    # Get API credentials
    API_KEY = os.getenv("AMBIENT_API_KEY")
    APPLICATION_KEY = os.getenv("AMBIENT_APP_KEY")
    
    if not API_KEY or not APPLICATION_KEY:
        print("=" * 70)
        print("ERROR: API credentials not found!")
        print("=" * 70)
        print("\nSet environment variables first:")
        print('  $env:AMBIENT_API_KEY="your_api_key"')
        print('  $env:AMBIENT_APP_KEY="your_application_key"')
        sys.exit(1)
    
    print("=" * 70)
    print("Incremental Rate Limit Test")
    print("=" * 70)
    print("We'll test step-by-step to understand exact behavior")
    print()
    
    # Get device
    print("Step 0: Fetching device info...")
    url = f"https://api.ambientweather.net/v1/devices"
    params = {
        'apiKey': API_KEY,
        'applicationKey': APPLICATION_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        devices = response.json()
        device = devices[0]
        mac_address = device['macAddress']
        print(f"  ✅ Using device: {device['info']['name']} ({mac_address})")
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 70)
    print("TEST 1: Single record, no delay before request")
    print("=" * 70)
    print("Testing: limit=1, delay_before=0")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=1, delay_before=0)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n❌ FAILED on first test!")
        print("This means even a single record with no delay fails.")
        print("Your account may have stricter limits or a temporary lockout.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 2: Single record, 1s delay before request")
    print("=" * 70)
    print("Testing: limit=1, delay_before=1")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=1, delay_before=1)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n⚠️ Interesting! limit=1 works without delay but fails WITH delay.")
        print("This suggests the previous request triggered a rate limit.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 3: Two records, 1s delay before request")
    print("=" * 70)
    print("Testing: limit=2, delay_before=1")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=2, delay_before=1)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n📊 FINDING: limit=1 works, but limit=2 fails!")
        print("Conclusion: The API limits you to 1 record per request.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 4: Three records, 1s delay before request")
    print("=" * 70)
    print("Testing: limit=3, delay_before=1")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=3, delay_before=1)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n📊 FINDING: limit=2 works, but limit=3 fails!")
        print("Conclusion: The API limits you to 2 records per request.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 5: Five records, 1s delay before request")
    print("=" * 70)
    print("Testing: limit=5, delay_before=1")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=5, delay_before=1)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n📊 FINDING: limit=3 works, but limit=5 fails!")
        print("Conclusion: The API limits you to 3-4 records per request.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 6: Ten records, 1s delay before request")
    print("=" * 70)
    print("Testing: limit=10, delay_before=1")
    result = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=10, delay_before=1)
    print(f"Result: {result['message']}")
    
    if not result['success']:
        print("\n📊 FINDING: limit=5 works, but limit=10 fails!")
        print("Conclusion: The API limits you to 5-9 records per request.")
        return
    
    print("\n" + "=" * 70)
    print("TEST 7: Test delay timing - Two requests with limit=1")
    print("=" * 70)
    print("Request A: limit=1, no delay")
    result_a = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=1, delay_before=0)
    print(f"  {result_a['message']}")
    
    print("Request B: limit=1, 0.5s delay (should fail)")
    result_b = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=1, delay_before=0.5)
    print(f"  {result_b['message']}")
    
    if not result_b['success']:
        print("\n📊 FINDING: 0.5s delay is too short!")
        print("Now testing with 1.0s delay...")
        
        print("Request C: limit=1, 1.0s delay")
        result_c = test_single_request(API_KEY, APPLICATION_KEY, mac_address, limit=1, delay_before=1.0)
        print(f"  {result_c['message']}")
        
        if result_c['success']:
            print("\n✅ FINDING: 1.0s delay works!")
            print("Minimum delay required: 1 second between requests")
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("All tests completed. Review results above.")


if __name__ == "__main__":
    main()
