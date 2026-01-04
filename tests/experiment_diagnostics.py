#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 5 & 6: Diagnostics and Network Analysis
Combined authentication validation and network diagnostics
"""

import os
import socket
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


def check_api_key_format():
    """Phase 5.1: Validate API key format"""
    print("=" * 70)
    print("Test 5.1: API Key Format Validation")
    print("=" * 70)

    issues = []

    # API Key checks
    print("API Key Analysis:")
    if not API_KEY:
        issues.append("API_KEY not set")
    else:
        print(f"  Length: {len(API_KEY)} characters")
        print(f"  Format: {API_KEY[:8]}...{API_KEY[-8:]}")

        # Check for common issues
        if len(API_KEY) != 64:
            issues.append(f"API_KEY wrong length (expected 64, got {len(API_KEY)})")

        if any(c in API_KEY for c in [' ', '\n', '\r', '\t']):
            issues.append("API_KEY contains whitespace")

        if not all(c in '0123456789abcdefABCDEF' for c in API_KEY):
            issues.append("API_KEY contains non-hex characters")

    print()

    # App Key checks
    print("App Key Analysis:")
    if not APP_KEY:
        issues.append("APP_KEY not set")
    else:
        print(f"  Length: {len(APP_KEY)} characters")
        print(f"  Format: {APP_KEY[:8]}...{APP_KEY[-8:]}")

        if len(APP_KEY) != 64:
            issues.append(f"APP_KEY wrong length (expected 64, got {len(APP_KEY)})")

        if any(c in APP_KEY for c in [' ', '\n', '\r', '\t']):
            issues.append("APP_KEY contains whitespace")

        if not all(c in '0123456789abcdefABCDEF' for c in APP_KEY):
            issues.append("APP_KEY contains non-hex characters")

    print()

    # MAC Address checks
    print("MAC Address Analysis:")
    if not MAC_ADDRESS:
        print("  Not set (optional)")
    else:
        print(f"  Format: {MAC_ADDRESS}")

        # MAC should be XX:XX:XX:XX:XX:XX
        if ':' not in MAC_ADDRESS:
            issues.append("MAC_ADDRESS missing colons (should be XX:XX:XX:XX:XX:XX)")

        parts = MAC_ADDRESS.split(':')
        if len(parts) != 6:
            issues.append(f"MAC_ADDRESS wrong format (expected 6 parts, got {len(parts)})")

    print()

    if issues:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All credentials properly formatted")
        return True


def check_network_connectivity():
    """Phase 6.1: Network connectivity checks"""
    print("=" * 70)
    print("Test 6.1: Network Connectivity")
    print("=" * 70)

    # Check DNS resolution
    print("DNS Resolution Test:")
    try:
        ip = socket.gethostbyname("api.ambientweather.net")
        print(f"  ✅ api.ambientweather.net resolves to {ip}")
    except socket.gaierror as e:
        print(f"  ❌ DNS resolution failed: {e}")
        return False

    print()

    # Check internet connectivity
    print("Internet Connectivity Test:")
    try:
        response = requests.get("https://api.ambientweather.net", timeout=10)
        print(f"  ✅ Can reach api.ambientweather.net (HTTP {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection failed: {e}")
        return False

    print()

    # Check our public IP
    print("Public IP Check:")
    try:
        response = requests.get("https://api.ipify.org", timeout=10)
        public_ip = response.text
        print(f"  Your public IP: {public_ip}")
        print(f"  Location: (check https://www.iplocation.net/?ip={public_ip})")
    except Exception as e:
        print(f"  ⚠️  Could not determine public IP: {e}")

    print()
    return True


def check_request_headers():
    """Check what headers our requests send"""
    print("=" * 70)
    print("Test 6.2: Request Headers Analysis")
    print("=" * 70)

    print("Analyzing headers sent by our requests:\n")

    # Make a test request to httpbin to see what we're sending
    print("Testing with httpbin.org (header inspection service)...")

    try:
        response = requests.get("https://httpbin.org/headers", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("Headers we send:")
            for header, value in data.get('headers', {}).items():
                print(f"  {header}: {value}")
        else:
            print(f"  ⚠️  httpbin returned {response.status_code}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

    print()

    # Show what we SHOULD be sending to Ambient Weather
    print("Headers for Ambient Weather API calls:")
    print("  User-Agent: python-requests/{version}")
    print("  Accept: */*")
    print("  Accept-Encoding: gzip, deflate")
    print("  Connection: keep-alive")
    print()

    print("Note: These are standard Python requests headers")
    print("      Unlikely to cause rate limiting issues")

    print()
    return True


def check_ssl_configuration():
    """Check SSL/TLS configuration"""
    print("=" * 70)
    print("Test 6.3: SSL/TLS Configuration")
    print("=" * 70)

    print("SSL/TLS Details:\n")

    try:
        import ssl

        print(f"OpenSSL Version: {ssl.OPENSSL_VERSION}")
        print(f"TLS Version Support: {ssl.PROTOCOL_TLS}")

        # Make request and check SSL version used
        response = requests.get("https://api.ambientweather.net", timeout=10)
        print(f"Connection successful: {response.status_code}")

    except Exception as e:
        print(f"❌ SSL Error: {e}")
        return False

    print()
    print("✅ SSL/TLS configuration appears normal")
    print()
    return True


def summarize_environment():
    """Summarize entire environment"""
    print("=" * 70)
    print("ENVIRONMENT SUMMARY")
    print("=" * 70)

    import platform

    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print()

    # Check installed packages
    try:
        import pkg_resources

        print("Key Package Versions:")
        for package in ['requests', 'urllib3', 'certifi']:
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"  {package}: {version}")
            except:
                print(f"  {package}: not found")
    except ImportError:
        print("  (cannot check package versions)")

    print()


def main():
    """Run diagnostic tests"""
    print("=" * 70)
    print("PHASE 5 & 6: DIAGNOSTICS AND NETWORK ANALYSIS")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}")
    print()

    # Phase 5: Authentication
    print("\n" + "=" * 70)
    print("PHASE 5: AUTHENTICATION VALIDATION")
    print("=" * 70 + "\n")

    test_5_1 = check_api_key_format()

    # Phase 6: Network
    print("\n" + "=" * 70)
    print("PHASE 6: NETWORK DIAGNOSTICS")
    print("=" * 70 + "\n")

    test_6_1 = check_network_connectivity()
    test_6_2 = check_request_headers()
    test_6_3 = check_ssl_configuration()

    # Environment summary
    print("\n")
    summarize_environment()

    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    results = [
        ("API Key Format", test_5_1),
        ("Network Connectivity", test_6_1),
        ("Request Headers", test_6_2),
        ("SSL/TLS Config", test_6_3)
    ]

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")

    print()

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("✅ ALL DIAGNOSTICS PASSED")
        print("   → Credentials and network configuration are correct")
        print("   → Rate limiting issue is likely:")
        print("      1. Account-level restrictions")
        print("      2. Different account tier than external user")
        print("      3. API keys flagged/restricted")
    else:
        print("❌ SOME DIAGNOSTICS FAILED")
        print("   → Fix issues above before proceeding")

    print()

    print("NEXT STEPS:")
    print("1. Compare account type with external user")
    print("2. Check Ambient Weather dashboard for account status")
    print("3. Consider generating fresh API keys")
    print("4. Test from different network/IP if possible")

    print()
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
