"""
API Request Queue for Ambient Weather API

Provides rate limiting and request coordination across all API consumers
(web server, scheduler, CLI) to prevent 429 rate limit errors.

Architecture:
- FIFO async queue with 1-second minimum spacing between requests
- Request deduplication to avoid redundant calls
- Metrics tracking for monitoring queue performance
- Graceful shutdown handling

Usage:
    queue = AmbientAPIQueue(rate_limit_seconds=1.0)
    await queue.start()

    result = await queue.enqueue(api_function, *args, **kwargs)

    await queue.shutdown()
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from weather_app.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class QueueMetrics:
    """Metrics for monitoring queue performance"""

    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    deduplicated_requests: int = 0
    total_wait_time_seconds: float = 0.0
    max_queue_size: int = 0

    @property
    def avg_wait_time_seconds(self) -> float:
        """Calculate average wait time per request"""
        if self.completed_requests == 0:
            return 0.0
        return self.total_wait_time_seconds / self.completed_requests


@dataclass
class QueuedRequest:
    """Represents a queued API request"""

    func: Callable
    args: tuple
    kwargs: dict
    future: asyncio.Future
    enqueue_time: float
    request_key: str


class AmbientAPIQueue:
    """
    Async queue for rate-limiting Ambient Weather API requests

    Ensures all API calls are spaced by at least rate_limit_seconds to prevent
    hitting the Ambient Weather API rate limit (typically 1 request/second).
    """

    def __init__(self, rate_limit_seconds: float = 1.0):
        """
        Initialize the API request queue

        Args:
            rate_limit_seconds: Minimum seconds between API requests (default: 1.0)
        """
        self.rate_limit_seconds = rate_limit_seconds
        self.queue: asyncio.Queue = asyncio.Queue()
        self.metrics = QueueMetrics()
        self.worker_task: asyncio.Task | None = None
        self.running = False
        self.last_request_time: float = 0.0
        self._loop: asyncio.AbstractEventLoop | None = None

        # Request deduplication: map request keys to futures
        self._in_flight: dict[str, asyncio.Future] = {}

        logger.info("api_queue_initialized", rate_limit_seconds=self.rate_limit_seconds)

    def _generate_request_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """
        Generate a unique key for request deduplication

        Args:
            func: The function to call
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            String key representing this unique request
        """
        # Use function name and string representation of args
        func_name = func.__name__ if hasattr(func, "__name__") else str(func)
        args_str = str(args)
        kwargs_str = str(sorted(kwargs.items()))
        return f"{func_name}:{args_str}:{kwargs_str}"

    async def start(self):
        """Start the queue worker task"""
        if self.running:
            logger.warning("api_queue_start_skipped", reason="already_running")
            return

        self.running = True
        self._loop = asyncio.get_running_loop()
        self.worker_task = asyncio.create_task(self._worker())
        logger.info("api_queue_started")

    async def shutdown(self, timeout: float = 10.0):
        """
        Gracefully shutdown the queue

        Waits for queued requests to complete before stopping.

        Args:
            timeout: Maximum seconds to wait for queue to drain
        """
        if not self.running:
            return

        logger.info("api_queue_shutting_down", queued_requests=self.queue.qsize())

        self.running = False

        # Wait for queue to drain (with timeout)
        try:
            await asyncio.wait_for(self.queue.join(), timeout=timeout)
            logger.info("api_queue_drained")
        except asyncio.TimeoutError:
            logger.warning(
                "api_queue_drain_timeout",
                remaining_requests=self.queue.qsize(),
                timeout_seconds=timeout,
            )

        # Cancel worker task
        if self.worker_task and not self.worker_task.done():
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        logger.info(
            "api_queue_shutdown_complete",
            total_requests=self.metrics.total_requests,
            completed=self.metrics.completed_requests,
            failed=self.metrics.failed_requests,
            deduplicated=self.metrics.deduplicated_requests,
        )

    async def enqueue(self, func: Callable, *args, **kwargs) -> Any:
        """
        Enqueue an API request and wait for the result

        If an identical request is already in-flight, this will wait for that
        request's result instead of making a duplicate call.

        Args:
            func: The function to call (typically an AmbientWeatherAPI method)
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call

        Raises:
            Exception: Any exception raised by the function
        """
        if not self.running:
            raise RuntimeError("Queue is not running. Call start() first.")

        # Generate request key for deduplication
        request_key = self._generate_request_key(func, args, kwargs)

        # Check if identical request is already in-flight
        if request_key in self._in_flight:
            self.metrics.deduplicated_requests += 1
            logger.debug(
                "api_request_deduplicated",
                request_key=request_key,
                total_deduplicated=self.metrics.deduplicated_requests,
            )
            # Wait for the existing request to complete
            return await self._in_flight[request_key]

        # Create new request
        future = asyncio.Future()
        self._in_flight[request_key] = future

        request = QueuedRequest(
            func=func,
            args=args,
            kwargs=kwargs,
            future=future,
            enqueue_time=time.time(),
            request_key=request_key,
        )

        await self.queue.put(request)
        self.metrics.total_requests += 1

        # Update max queue size metric
        current_size = self.queue.qsize()
        if current_size > self.metrics.max_queue_size:
            self.metrics.max_queue_size = current_size

        logger.debug(
            "api_request_enqueued",
            func=func.__name__ if hasattr(func, "__name__") else str(func),
            queue_size=current_size,
        )

        # Wait for the request to complete
        try:
            result = await future
            return result
        finally:
            # Clean up in-flight tracking
            self._in_flight.pop(request_key, None)

    async def _worker(self):
        """
        Background worker that processes queued requests

        Enforces rate limiting by ensuring minimum spacing between requests.
        """
        logger.info("api_queue_worker_started")

        try:
            while self.running:
                try:
                    # Get next request (with timeout to allow checking running flag)
                    request = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue

                try:
                    # Enforce rate limiting
                    time_since_last_request = time.time() - self.last_request_time
                    if time_since_last_request < self.rate_limit_seconds:
                        wait_time = self.rate_limit_seconds - time_since_last_request
                        logger.debug("api_rate_limit_wait", wait_seconds=wait_time)
                        await asyncio.sleep(wait_time)

                    # Execute the request
                    start_time = time.time()
                    self.last_request_time = time.time()

                    logger.debug(
                        "api_request_executing",
                        func=(
                            request.func.__name__
                            if hasattr(request.func, "__name__")
                            else str(request.func)
                        ),
                    )

                    # Call the function (wrap sync functions in executor)
                    if asyncio.iscoroutinefunction(request.func):
                        result = await request.func(*request.args, **request.kwargs)
                    else:
                        loop = asyncio.get_event_loop()
                        # Bind request to lambda parameter to avoid late binding issues
                        result = await loop.run_in_executor(
                            None,
                            lambda req=request: req.func(*req.args, **req.kwargs),
                        )

                    # Calculate wait time and update metrics
                    wait_time = start_time - request.enqueue_time
                    self.metrics.total_wait_time_seconds += wait_time
                    self.metrics.completed_requests += 1

                    # Set result
                    if not request.future.done():
                        request.future.set_result(result)

                    logger.debug(
                        "api_request_completed",
                        func=(
                            request.func.__name__
                            if hasattr(request.func, "__name__")
                            else str(request.func)
                        ),
                        wait_time_seconds=round(wait_time, 3),
                        completed=self.metrics.completed_requests,
                    )

                except Exception as e:
                    # Set exception on future
                    if not request.future.done():
                        request.future.set_exception(e)

                    self.metrics.failed_requests += 1

                    logger.error(
                        "api_request_failed",
                        func=(
                            request.func.__name__
                            if hasattr(request.func, "__name__")
                            else str(request.func)
                        ),
                        error=str(e),
                        error_type=type(e).__name__,
                        failed=self.metrics.failed_requests,
                    )
                finally:
                    # Mark task as done
                    self.queue.task_done()

        except asyncio.CancelledError:
            logger.info("api_queue_worker_cancelled")
            raise
        except Exception as e:
            logger.error(
                "api_queue_worker_error", error=str(e), error_type=type(e).__name__
            )
            raise

    def enqueue_threadsafe(
        self, func: Callable, *args, timeout: float = 60.0, **kwargs
    ) -> Any:
        """
        Enqueue an API request from a non-async thread context.

        This method is safe to call from background threads (e.g., APScheduler jobs,
        BackfillService). It blocks until the request completes.

        Args:
            func: The function to call (typically an AmbientWeatherAPI method)
            *args: Positional arguments for the function
            timeout: Maximum seconds to wait for result (default: 60.0)
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call

        Raises:
            RuntimeError: If queue is not running
            TimeoutError: If request takes longer than timeout
            Exception: Any exception raised by the function
        """
        if not self.running:
            raise RuntimeError("Queue is not running. Call start() first.")

        if self._loop is None:
            raise RuntimeError("Queue event loop not initialized")

        # Submit coroutine to the queue's event loop from this thread
        concurrent_future = asyncio.run_coroutine_threadsafe(
            self.enqueue(func, *args, **kwargs),
            self._loop,
        )

        try:
            return concurrent_future.result(timeout=timeout)
        except TimeoutError:
            concurrent_future.cancel()
            raise TimeoutError(f"Request timed out after {timeout} seconds")

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current queue metrics

        Returns:
            Dictionary with queue performance metrics
        """
        return {
            "total_requests": self.metrics.total_requests,
            "completed_requests": self.metrics.completed_requests,
            "failed_requests": self.metrics.failed_requests,
            "deduplicated_requests": self.metrics.deduplicated_requests,
            "avg_wait_time_seconds": round(self.metrics.avg_wait_time_seconds, 3),
            "max_queue_size": self.metrics.max_queue_size,
            "current_queue_size": self.queue.qsize(),
            "running": self.running,
        }
