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

if __name__ == "__main__":
    # CRITICAL: Import crash logger FIRST to capture all startup errors
    # This must happen before any other imports that might fail
    from weather_app.launcher.crash_logger import CrashLogger

    # Use crash logger context manager to capture all exceptions
    with CrashLogger() as logger:
        logger.log("Importing tray_app module...")

        try:
            from weather_app.launcher.tray_app import main

            logger.log("Successfully imported tray_app")
            logger.log("Starting main application...")

            main()

            logger.log("Application main() returned normally")
        except Exception as e:
            logger.log(f"CRITICAL ERROR in main(): {e}", level="CRITICAL")
            raise  # Re-raise to trigger crash logger's exception hook
