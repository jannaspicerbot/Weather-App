#!/usr/bin/env python3
"""
Weather App Launcher

Main entry point for the packaged Weather App executable.
Launches the system tray application which manages the FastAPI server
and provides user interface through the system tray.

Usage:
    python launcher.py          # Run in development
    WeatherApp.exe              # Run as packaged executable (Windows)
    WeatherApp.app              # Run as packaged executable (macOS)
"""

if __name__ == '__main__':
    from weather_app.launcher.tray_app import main
    main()
