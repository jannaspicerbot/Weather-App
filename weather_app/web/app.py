"""
FastAPI application factory
Creates and configures the FastAPI app with middleware, routes, scheduler, and API queue
"""

import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from weather_app.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    DEMO_DB_PATH,
)
from weather_app.logging_config import get_logger
from weather_app.scheduler import WeatherScheduler
from weather_app.services import AmbientAPIQueue

if TYPE_CHECKING:
    from weather_app.demo import DemoService

logger = get_logger(__name__)


def _get_initial_demo_mode() -> bool:
    """
    Check if demo mode should be enabled at startup.

    Reads directly from environment variable to ensure we get the current value,
    even if config.py was imported before the env var was set (e.g., CLI --demo flag).
    """
    return os.getenv("DEMO_MODE", "false").lower() == "true"


# Global instances
api_queue = AmbientAPIQueue(rate_limit_seconds=1.0)
scheduler = WeatherScheduler(api_queue=api_queue)

# Demo service instance (initialized lazily)
_demo_service: "DemoService | None" = None
_demo_mode_enabled: bool = False  # Set during create_app()


def get_demo_service() -> "DemoService | None":
    """Get or create the demo service instance."""
    global _demo_service
    if _demo_service is None and _demo_mode_enabled:
        from weather_app.demo import DemoService

        _demo_service = DemoService(DEMO_DB_PATH)
    return _demo_service


def is_demo_mode() -> bool:
    """Check if demo mode is currently enabled."""
    return _demo_mode_enabled


def enable_demo_mode() -> tuple[bool, str]:
    """
    Enable demo mode at runtime.

    Returns:
        Tuple of (success, message)
    """
    global _demo_mode_enabled, _demo_service

    if not DEMO_DB_PATH.exists():
        return False, f"Demo database not found at {DEMO_DB_PATH}"

    from weather_app.demo import DemoService

    _demo_service = DemoService(DEMO_DB_PATH)

    if not _demo_service.is_available:
        _demo_service = None
        return False, "Failed to initialize demo service"

    _demo_mode_enabled = True
    logger.info("demo_mode_enabled", message="Demo mode enabled")
    return True, "Demo mode enabled successfully"


def disable_demo_mode() -> tuple[bool, str]:
    """
    Disable demo mode at runtime.

    Returns:
        Tuple of (success, message)
    """
    global _demo_mode_enabled, _demo_service

    if _demo_service:
        _demo_service.close()
        _demo_service = None

    _demo_mode_enabled = False
    logger.info("demo_mode_disabled", message="Demo mode disabled")
    return True, "Demo mode disabled"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application

    Handles startup and shutdown events:
    - Startup: Start the API queue and background scheduler (or demo mode)
    - Shutdown: Gracefully stop the scheduler and API queue
    """
    # Startup
    logger.info("application_startup", message="Starting Weather App")

    if _demo_mode_enabled:
        # Initialize demo service
        logger.info("demo_mode_startup", message="Starting in demo mode")
        get_demo_service()
    else:
        # Start API queue first (scheduler depends on it)
        await api_queue.start()

        # Start scheduler
        scheduler.start()

    yield

    # Shutdown (reverse order)
    logger.info("application_shutdown", message="Shutting down Weather App")

    if _demo_mode_enabled:
        # Clean up demo service
        if _demo_service:
            _demo_service.close()
    else:
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


def _check_demo_generation_cleanup() -> None:
    """
    Check for incomplete demo database generation on startup.

    If a previous process crashed mid-generation, the status would still show
    "generating" but no thread would be running. Clean up the partial database
    and reset status in this case.
    """
    from weather_app.demo.generation_service import DemoGenerationService

    service = DemoGenerationService.get_instance()
    status = service.get_status()

    if status["state"] == "generating":
        # Previous process crashed mid-generation - no thread running
        logger.warning(
            "demo_generation_incomplete_detected",
            message="Detected incomplete demo generation from previous process, cleaning up",
            started_at=status["started_at"],
        )
        service._cleanup_partial_database()
        service.reset_status()


def create_app() -> FastAPI:
    """
    Application factory function that creates and configures FastAPI app

    Returns:
        Configured FastAPI application with scheduler integration
    """
    global _demo_mode_enabled

    # Check demo mode from environment variable (read fresh, not from cached config)
    _demo_mode_enabled = _get_initial_demo_mode()

    # Check for incomplete demo generation from previous process crash
    _check_demo_generation_cleanup()

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
