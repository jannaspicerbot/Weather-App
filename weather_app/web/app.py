"""
FastAPI application factory
Creates and configures the FastAPI app with middleware, routes, and scheduler
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from weather_app.config import (API_DESCRIPTION, API_TITLE, API_VERSION,
                                CORS_ORIGINS)
from weather_app.logging_config import get_logger
from weather_app.scheduler import WeatherScheduler

logger = get_logger(__name__)

# Global scheduler instance
scheduler = WeatherScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application

    Handles startup and shutdown events:
    - Startup: Start the background scheduler for automated data collection
    - Shutdown: Gracefully stop the scheduler
    """
    # Startup
    logger.info("application_startup", message="Starting Weather App")
    scheduler.start()

    yield

    # Shutdown
    logger.info("application_shutdown", message="Shutting down Weather App")
    scheduler.shutdown()


def create_app() -> FastAPI:
    """
    Application factory function that creates and configures FastAPI app

    Returns:
        Configured FastAPI application with scheduler integration
    """
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        lifespan=lifespan,
    )

    # Enable CORS for React frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import routes after app creation to avoid circular imports
    from weather_app.web import routes

    routes.register_routes(app)

    return app
