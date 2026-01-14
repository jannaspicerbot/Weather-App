"""
FastAPI application factory
Creates and configures the FastAPI app with middleware, routes, scheduler, and API queue
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from weather_app.config import API_DESCRIPTION, API_TITLE, API_VERSION, CORS_ORIGINS
from weather_app.logging_config import get_logger
from weather_app.scheduler import WeatherScheduler
from weather_app.services import AmbientAPIQueue

logger = get_logger(__name__)

# Global instances
api_queue = AmbientAPIQueue(rate_limit_seconds=1.0)
scheduler = WeatherScheduler(api_queue=api_queue)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application

    Handles startup and shutdown events:
    - Startup: Start the API queue and background scheduler
    - Shutdown: Gracefully stop the scheduler and API queue
    """
    # Startup
    logger.info("application_startup", message="Starting Weather App")

    # Start API queue first (scheduler depends on it)
    await api_queue.start()

    # Start scheduler
    scheduler.start()

    yield

    # Shutdown (reverse order)
    logger.info("application_shutdown", message="Shutting down Weather App")

    # Stop scheduler first
    scheduler.shutdown()

    # Stop API queue last (ensure all queued requests complete)
    await api_queue.shutdown()


def register_frontend(app: FastAPI) -> None:
    """
    Mount static frontend files to serve the React app.

    When running as a packaged executable, serves files from bundled location.
    In development mode, serves from web/dist directory.

    Args:
        app: FastAPI application instance
    """
    import sys
    from pathlib import Path

    from fastapi.staticfiles import StaticFiles

    if getattr(sys, "frozen", False):
        # Running as executable - static files bundled with app
        # PyInstaller extracts files to sys._MEIPASS temporary directory
        static_dir = Path(sys._MEIPASS) / "web" / "dist"  # type: ignore[attr-defined]
    else:
        # Development mode - serve from project's web/dist directory
        static_dir = Path(__file__).parent.parent.parent / "web" / "dist"

    if static_dir.exists():
        # Mount static files at root path with html=True to serve index.html
        app.mount(
            "/", StaticFiles(directory=str(static_dir), html=True), name="frontend"
        )
        logger.info("frontend_mounted", static_dir=str(static_dir))
    else:
        logger.warning(
            "frontend_not_found",
            static_dir=str(static_dir),
            message="Frontend not built. Run 'npm run build' in web/ directory",
        )


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

    # Register frontend static files (must be last to not override API routes)
    register_frontend(app)

    return app


# Create app instance for uvicorn
app = create_app()
