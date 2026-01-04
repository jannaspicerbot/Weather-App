#!/usr/bin/env python3
"""
check_retry_after.py - Check the 429 response for Retry-After header
"""

import requests
import os
import sys
from datetime import datetime


API_KEY = os.getenv("AMBIENT_API_KEY")
APPLICATION_KEY = os.getenv("AMBIENT_APP_KEY")

if not API_KEY or not APPLICATION_KEY:
    print("ERROR: Environment variables not set")
    sys.exit(1)

# Get device
print("Fetching device...")
url = "https://api.ambientweather.net/v1/devices"
params = {"apiKey": API_KEY, "applicationKey": APPLICATION_KEY}

response = requests.get(url, params=params)
devices = response.json()
mac_address = devices[0]["macAddress"]
print(f"Device: {mac_address}\n")

# Make request that will likely get rate limited
print("Making data request (expecting 429)...")
url = f"https://api.ambientweather.net/v1/devices/{mac_address}"
params = {"apiKey": API_KEY, "applicationKey": APPLICATION_KEY, "limit": 1}

response = requests.get(url, params=params)

print(f"Status Code: {response.status_code}")
print(f"\nAll Response Headers:")
print("-" * 50)
for header, value in response.headers.items():
    print(f"{header}: {value}")

print(f"\nResponse Body:")
print("-" * 50)
print(response.text[:200])

if "Retry-After" in response.headers:
    retry_after = response.headers["Retry-After"]
    print(f"\n🔑 Retry-After header found: {retry_after}")

    try:
        # Try as seconds
        seconds = int(retry_after)
        print(f"   Wait {seconds} seconds ({seconds/60:.1f} minutes)")
    except ValueError:
        # It's a datetime string
        print(f"   Retry at: {retry_after}")
else:
    print("\n⚠️  No Retry-After header in response")
    print("The API doesn't tell us when to retry!")
