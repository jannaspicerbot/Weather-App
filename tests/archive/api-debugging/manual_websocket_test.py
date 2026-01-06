#!/usr/bin/env python3
"""
test_websocket.py - Test Ambient Weather Realtime WebSocket API
This tests if the WebSocket API has different rate limits than REST
"""

import os
import sys
import time
from datetime import datetime

import socketio


class AmbientWeatherWebSocket:
    def __init__(self, api_key, app_key=None):
        self.api_key = api_key
        self.app_key = app_key
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.connected = False
        self.subscribed = False
        self.data_received = False

        # Set up event handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Set up WebSocket event handlers"""

        @self.sio.on("connect")
        def on_connect():
            print("\n" + "=" * 70)
            print("✅ CONNECTED to Ambient Weather WebSocket!")
            print("=" * 70)
            self.connected = True

            # Subscribe to our devices
            print(f"\nSubscribing with API Key: {self.api_key[:20]}...")

            # Try with both keys if app key is provided
            if self.app_key:
                print(f"Also including Application Key: {self.app_key[:20]}...")
                self.sio.emit(
                    "subscribe",
                    {"apiKeys": [self.api_key], "applicationKey": self.app_key},
                )
            else:
                self.sio.emit("subscribe", {"apiKeys": [self.api_key]})

        @self.sio.on("subscribed")
        def on_subscribed(data):
            print("\n" + "=" * 70)
            print("✅ SUBSCRIPTION SUCCESSFUL!")
            print("=" * 70)
            print(f"Subscribed data: {data}")
            self.subscribed = True

            if "devices" in data:
                print(f"\nDevices subscribed: {len(data['devices'])}")
                for device in data["devices"]:
                    print(f"  - MAC: {device.get('macAddress')}")
                    print(f"    Name: {device.get('info', {}).get('name', 'Unknown')}")
                    print(
                        f"    Last Data: {device.get('lastData', {}).get('date', 'Unknown')}"
                    )

        @self.sio.on("data")
        def on_data(data):
            print("\n" + "=" * 70)
            print("🎉 NEW WEATHER DATA RECEIVED!")
            print("=" * 70)
            print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
            print(f"Data: {data}")
            self.data_received = True

            # Parse the data
            if isinstance(data, dict):
                mac = data.get("macAddress", "Unknown")
                print(f"\nDevice: {mac}")

                # Show key weather metrics
                if "dateutc" in data:
                    print(f"Date: {data.get('date')}")
                if "tempf" in data:
                    print(f"Temperature: {data.get('tempf')}°F")
                if "humidity" in data:
                    print(f"Humidity: {data.get('humidity')}%")
                if "windspeedmph" in data:
                    print(f"Wind Speed: {data.get('windspeedmph')} mph")

        @self.sio.on("disconnect")
        def on_disconnect():
            print("\n" + "=" * 70)
            print("❌ DISCONNECTED from WebSocket")
            print("=" * 70)
            self.connected = False

        @self.sio.on("connect_error")
        def on_connect_error(data):
            print("\n" + "=" * 70)
            print("❌ CONNECTION ERROR!")
            print("=" * 70)
            print(f"Error: {data}")

        @self.sio.on("error")
        def on_error(data):
            print("\n" + "=" * 70)
            print("❌ ERROR!")
            print("=" * 70)
            print(f"Error: {data}")

    def connect(self):
        """Connect to the WebSocket server"""
        try:
            print("=" * 70)
            print("Ambient Weather WebSocket Test")
            print("=" * 70)
            print("Connecting to: https://rt2.ambientweather.net")
            print(f"Using API Key: {self.api_key[:20]}...")
            print()

            self.sio.connect(
                "https://rt2.ambientweather.net",
                socketio_path="/socket.io/",
                transports=["websocket"],
            )

            return True
        except Exception as e:
            print(f"\n❌ Failed to connect: {e}")
            return False

    def wait_for_data(self, timeout=60):
        """Wait for data or timeout"""
        print(f"\nWaiting for data (timeout: {timeout}s)...")
        print("Note: Data only arrives when your weather station reports")
        print("(typically every 5-30 minutes)")
        print("\nPress Ctrl+C to stop early\n")

        start_time = time.time()

        try:
            while time.time() - start_time < timeout:
                if self.data_received:
                    print("\n✅ Data received! Test successful!")
                    return True

                # Show status every 10 seconds
                elapsed = int(time.time() - start_time)
                if elapsed % 10 == 0 and elapsed > 0:
                    print(f"  Still waiting... ({elapsed}s elapsed)")

                time.sleep(1)

            print(f"\n⏰ Timeout reached ({timeout}s)")
            print("No data received yet, but connection is active!")
            print("\nThis is NORMAL if your weather station hasn't reported recently.")
            print("The connection is working - you'd get data when station reports.")
            return False

        except KeyboardInterrupt:
            print("\n\n⏸️  Stopped by user")
            return False

    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.connected:
            self.sio.disconnect()


def main():
    # Get API credentials
    API_KEY = os.getenv("AMBIENT_API_KEY")
    APP_KEY = os.getenv("AMBIENT_APP_KEY")

    if not API_KEY:
        print("=" * 70)
        print("ERROR: API Key not found!")
        print("=" * 70)
        print("\nSet environment variable first:")
        print('  $env:AMBIENT_API_KEY="your_api_key"')
        sys.exit(1)

    # Create WebSocket client (with optional app key)
    ws = AmbientWeatherWebSocket(API_KEY, APP_KEY)

    # Try to connect
    if not ws.connect():
        print("\n❌ Connection failed")
        sys.exit(1)

    # Wait a moment for subscription
    time.sleep(2)

    # Check if subscription worked
    if not ws.subscribed:
        print("\n⚠️  Subscription may have failed")
        print("Check the connection output above for errors")

    # Wait for data (or timeout after 60 seconds)
    ws.wait_for_data(timeout=60)

    # Disconnect
    print("\nDisconnecting...")
    ws.disconnect()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Connected: {'✅ Yes' if ws.connected or ws.subscribed else '❌ No'}")
    print(f"Subscribed: {'✅ Yes' if ws.subscribed else '❌ No'}")
    print(f"Data Received: {'✅ Yes' if ws.data_received else '⏰ Timed out (normal)'}")

    if ws.subscribed:
        print("\n✅ WEBSOCKET API WORKS!")
        print("This is a viable alternative to REST API!")
        print("\nNext step: Build realtime_weather.py to collect data continuously")
    else:
        print("\n❌ WebSocket API also has issues")
        print("Wait for support response")


if __name__ == "__main__":
    main()
