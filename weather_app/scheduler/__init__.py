"""
Scheduler module for automated data collection
Provides APScheduler integration for periodic weather data fetching
"""

from weather_app.scheduler.scheduler import WeatherScheduler

__all__ = ['WeatherScheduler']
