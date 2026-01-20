"""
Demo Database Generation Service

Thread-safe singleton service for managing demo database generation with:
- Concurrent generation prevention (only one generation at a time)
- Real cancellation support
- Persistent status for polling
- Automatic cleanup on failure/cancellation
"""

import threading
from datetime import datetime, timedelta
from typing import Literal, TypedDict

from weather_app.config import DEMO_DB_PATH, DEMO_DEFAULT_DAYS
from weather_app.logging_config import get_logger

logger = get_logger(__name__)


class GenerationCancelledError(Exception):
    """Raised when generation is cancelled by user."""

    pass


GenerationState = Literal["idle", "generating", "completed", "failed", "cancelled"]


class GenerationStatus(TypedDict):
    """Type definition for generation status."""

    state: GenerationState
    current_day: int
    total_days: int
    percent: int
    records: int | None
    size_mb: float | None
    error: str | None
    started_at: str | None
    completed_at: str | None


class DemoGenerationService:
    """
    Thread-safe demo database generation with cancellation support.

    Singleton pattern prevents multiple instances. Thread lock prevents
    concurrent generation attempts. Uses threading.Event for cancellation
    signaling.

    Usage:
        service = DemoGenerationService.get_instance()
        success, message = service.start_generation(days=1095)
        if success:
            # Poll status or stream SSE
            status = service.get_status()
    """

    _instance: "DemoGenerationService | None" = None
    _instance_lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize the generation service. Use get_instance() instead."""
        self._lock = threading.Lock()
        self._status: GenerationStatus = {
            "state": "idle",
            "current_day": 0,
            "total_days": 0,
            "percent": 0,
            "records": None,
            "size_mb": None,
            "error": None,
            "started_at": None,
            "completed_at": None,
        }
        self._thread: threading.Thread | None = None
        self._cancel_requested = threading.Event()

    @classmethod
    def get_instance(cls) -> "DemoGenerationService":
        """
        Get the singleton instance of the generation service.

        Thread-safe singleton pattern using double-checked locking.

        Returns:
            The singleton DemoGenerationService instance
        """
        if cls._instance is None:
            with cls._instance_lock:
                # Double-check after acquiring lock
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance. Used for testing.

        Warning: This should only be called in tests.
        """
        with cls._instance_lock:
            if cls._instance is not None:
                # Cancel any running generation
                cls._instance._cancel_requested.set()
                if cls._instance._thread and cls._instance._thread.is_alive():
                    cls._instance._thread.join(timeout=2.0)
            cls._instance = None

    def get_status(self) -> GenerationStatus:
        """
        Get current generation status (thread-safe).

        Returns:
            Copy of current status dictionary
        """
        with self._lock:
            return self._status.copy()

    def _update_status(self, **kwargs: object) -> None:
        """Update status fields (thread-safe)."""
        with self._lock:
            for key, value in kwargs.items():
                if key in self._status:
                    self._status[key] = value  # type: ignore

    def start_generation(self, days: int = DEMO_DEFAULT_DAYS) -> tuple[bool, str]:
        """
        Start demo database generation if not already running.

        Args:
            days: Number of days of data to generate (default: 3 years)

        Returns:
            Tuple of (success, message).
            - If generation starts: (True, "Generation started")
            - If already running: (False, "Generation already in progress")
        """
        with self._lock:
            if self._status["state"] == "generating":
                return False, "Generation already in progress"

            # Reset status for new generation
            self._status = {
                "state": "generating",
                "current_day": 0,
                "total_days": days,
                "percent": 0,
                "records": None,
                "size_mb": None,
                "error": None,
                "started_at": datetime.now().isoformat(),
                "completed_at": None,
            }
            self._cancel_requested.clear()

        logger.info(
            "demo_generation_starting",
            days=days,
            db_path=str(DEMO_DB_PATH),
        )

        # Start generation in background thread
        self._thread = threading.Thread(
            target=self._run_generation,
            args=(days,),
            daemon=True,
        )
        self._thread.start()

        return True, "Generation started"

    def cancel_generation(self) -> tuple[bool, str]:
        """
        Request cancellation of ongoing generation.

        Returns:
            Tuple of (success, message).
            - If cancellation requested: (True, "Cancellation requested")
            - If no generation running: (False, "No generation in progress")
        """
        with self._lock:
            if self._status["state"] != "generating":
                return False, "No generation in progress"

        logger.info("demo_generation_cancel_requested")
        self._cancel_requested.set()
        return True, "Cancellation requested"

    def is_cancelled(self) -> bool:
        """
        Check if cancellation was requested.

        Used by the generator callback to check for cancellation.

        Returns:
            True if cancellation was requested
        """
        return self._cancel_requested.is_set()

    def _run_generation(self, days: int) -> None:
        """
        Background thread: run generator and update status.

        Args:
            days: Number of days of data to generate
        """
        try:
            # Import here to avoid circular imports
            from weather_app.demo.data_generator import SeattleWeatherGenerator

            # Remove existing database if present
            if DEMO_DB_PATH.exists():
                logger.info("demo_generation_removing_existing", path=str(DEMO_DB_PATH))
                DEMO_DB_PATH.unlink()

            # Ensure parent directory exists
            DEMO_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

            # Calculate start date so data ends "today"
            start_date = datetime.now() - timedelta(days=days)

            generator = SeattleWeatherGenerator(DEMO_DB_PATH)

            try:
                records = generator.generate(
                    start_date=start_date,
                    days=days,
                    progress_callback=self._on_progress,
                    cancel_check=self.is_cancelled,
                    quiet=True,
                )

                # Check if cancelled after generation completes
                if self._cancel_requested.is_set():
                    logger.info("demo_generation_cancelled")
                    self._update_status(state="cancelled")
                    self._cleanup_partial_database()
                    return

                # Get final stats
                size_mb = DEMO_DB_PATH.stat().st_size / 1024 / 1024

                self._update_status(
                    state="completed",
                    percent=100,
                    current_day=days,
                    records=records,
                    size_mb=round(size_mb, 1),
                    completed_at=datetime.now().isoformat(),
                )

                logger.info(
                    "demo_generation_completed",
                    records=records,
                    size_mb=round(size_mb, 1),
                )

            finally:
                generator.close()

        except GenerationCancelledError as e:
            logger.info("demo_generation_cancelled", message=str(e))
            self._update_status(state="cancelled", error=str(e))
            self._cleanup_partial_database()

        except Exception as e:
            logger.error("demo_generation_failed", error=str(e))
            self._update_status(
                state="failed",
                error=str(e),
            )
            self._cleanup_partial_database()

    def _on_progress(self, current_day: int, total_days: int) -> None:
        """
        Progress callback for the generator.

        Args:
            current_day: Current day being generated
            total_days: Total days to generate
        """
        percent = int((current_day / total_days) * 100) if total_days > 0 else 0
        self._update_status(
            current_day=current_day,
            total_days=total_days,
            percent=percent,
        )

    def _cleanup_partial_database(self) -> None:
        """Remove incomplete database file on failure/cancellation."""
        if DEMO_DB_PATH.exists():
            try:
                DEMO_DB_PATH.unlink()
                logger.info(
                    "demo_generation_cleanup_complete",
                    path=str(DEMO_DB_PATH),
                )
            except Exception as e:
                logger.error(
                    "demo_generation_cleanup_failed",
                    error=str(e),
                    path=str(DEMO_DB_PATH),
                )

    def reset_status(self) -> None:
        """
        Reset status to idle state.

        Used for cleanup after incomplete generation (e.g., process crash).
        """
        with self._lock:
            self._status = {
                "state": "idle",
                "current_day": 0,
                "total_days": 0,
                "percent": 0,
                "records": None,
                "size_mb": None,
                "error": None,
                "started_at": None,
                "completed_at": None,
            }
            self._cancel_requested.clear()


# Convenience function for getting the service instance
def get_generation_service() -> DemoGenerationService:
    """
    Get the demo generation service singleton.

    Returns:
        The singleton DemoGenerationService instance
    """
    return DemoGenerationService.get_instance()
