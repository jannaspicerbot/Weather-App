"""
Demo Mode Module

Provides synthetic weather data for evaluating the Weather Dashboard
without requiring real Ambient Weather hardware or API credentials.
"""

from weather_app.demo.data_generator import GenerationCancelledError
from weather_app.demo.demo_service import DemoService
from weather_app.demo.generation_service import (
    DemoGenerationService,
    get_generation_service,
)

__all__ = [
    "DemoService",
    "DemoGenerationService",
    "GenerationCancelledError",
    "get_generation_service",
]
