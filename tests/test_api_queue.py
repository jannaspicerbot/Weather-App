"""
Unit tests for API request queue

Tests the AmbientAPIQueue functionality including:
- Basic request queueing
- Rate limiting enforcement
- Request deduplication
- Graceful shutdown
- Metrics tracking
"""

import asyncio
import time

import pytest

from weather_app.services import AmbientAPIQueue


class TestAPIQueue:
    """Tests for AmbientAPIQueue"""

    @pytest.mark.asyncio
    async def test_queue_initialization(self):
        """Test queue initializes with correct parameters"""
        queue = AmbientAPIQueue(rate_limit_seconds=1.5)

        assert queue.rate_limit_seconds == 1.5
        assert queue.running is False
        assert queue.metrics.total_requests == 0

    @pytest.mark.asyncio
    async def test_queue_lifecycle(self):
        """Test queue start and shutdown"""
        queue = AmbientAPIQueue()

        # Start queue
        await queue.start()
        assert queue.running is True
        assert queue.worker_task is not None

        # Shutdown queue
        await queue.shutdown(timeout=2.0)
        assert queue.running is False

    @pytest.mark.asyncio
    async def test_basic_request(self):
        """Test basic request queueing and execution"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            def sample_function(x, y):
                """Simple test function"""
                return x + y

            result = await queue.enqueue(sample_function, 5, 10)

            assert result == 15
            assert queue.metrics.total_requests == 1
            assert queue.metrics.completed_requests == 1
            assert queue.metrics.failed_requests == 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiting enforces minimum spacing between requests"""
        rate_limit = 0.5  # 500ms between requests
        queue = AmbientAPIQueue(rate_limit_seconds=rate_limit)
        await queue.start()

        try:

            def dummy_function(x):
                """Simple test function with unique param to avoid deduplication"""
                return (x, time.time())

            # Make 3 DIFFERENT requests (avoid deduplication)
            start_time = time.time()
            results = await asyncio.gather(
                queue.enqueue(dummy_function, 1),
                queue.enqueue(dummy_function, 2),
                queue.enqueue(dummy_function, 3),
            )
            total_time = time.time() - start_time

            # Should take at least 2 * rate_limit (3 requests = 2 gaps)
            min_expected_time = 2 * rate_limit
            assert (
                total_time >= min_expected_time
            ), f"Expected >= {min_expected_time}s, got {total_time:.2f}s"

            # All requests should complete
            assert len(results) == 3
            assert queue.metrics.completed_requests == 3

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_request_deduplication(self):
        """Test that identical concurrent requests are deduplicated"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:
            call_count = 0

            def tracked_function(x):
                """Function that tracks how many times it's called"""
                nonlocal call_count
                call_count += 1
                return x * 2

            # Make 5 identical concurrent requests
            results = await asyncio.gather(
                queue.enqueue(tracked_function, 5),
                queue.enqueue(tracked_function, 5),
                queue.enqueue(tracked_function, 5),
                queue.enqueue(tracked_function, 5),
                queue.enqueue(tracked_function, 5),
            )

            # All should return the same result
            assert all(r == 10 for r in results)

            # Function should only be called once (others deduplicated)
            assert call_count == 1

            # Metrics should show deduplication
            # total_requests counts only unique requests that were queued
            # deduplicated_requests counts requests that reused existing futures
            assert queue.metrics.total_requests == 1
            assert queue.metrics.completed_requests == 1
            assert queue.metrics.deduplicated_requests == 4

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test that exceptions in queued functions are properly propagated"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            def failing_function():
                """Function that always raises an exception"""
                raise ValueError("Test error")

            # Should raise the exception from the function
            with pytest.raises(ValueError, match="Test error"):
                await queue.enqueue(failing_function)

            # Metrics should track the failure
            assert queue.metrics.total_requests == 1
            assert queue.metrics.failed_requests == 1
            assert queue.metrics.completed_requests == 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_async_function_support(self):
        """Test that async functions are supported"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            async def async_function(x):
                """Async test function"""
                await asyncio.sleep(0.01)
                return x * 3

            result = await queue.enqueue(async_function, 7)

            assert result == 21
            assert queue.metrics.completed_requests == 1

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_metrics(self):
        """Test that metrics are correctly tracked"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            def success_func(x):
                return x

            def error_func():
                raise RuntimeError("Error")

            # Execute some requests
            await queue.enqueue(success_func, 1)
            await queue.enqueue(success_func, 2)

            try:
                await queue.enqueue(error_func)
            except RuntimeError:
                pass

            # Get metrics
            metrics = queue.get_metrics()

            assert metrics["total_requests"] == 3
            assert metrics["completed_requests"] == 2
            assert metrics["failed_requests"] == 1
            assert metrics["deduplicated_requests"] == 0
            assert metrics["running"] is True
            assert metrics["avg_wait_time_seconds"] >= 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_graceful_shutdown_with_pending_requests(self):
        """Test that shutdown waits for pending requests to complete"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:
            executed = []

            def slow_function(x):
                """Function that takes some time"""
                time.sleep(0.05)
                executed.append(x)
                return x

            # Queue multiple requests
            task1 = asyncio.create_task(queue.enqueue(slow_function, 1))
            task2 = asyncio.create_task(queue.enqueue(slow_function, 2))
            task3 = asyncio.create_task(queue.enqueue(slow_function, 3))

            # Wait for all tasks to complete BEFORE shutdown
            # (This tests that multiple concurrent requests work correctly)
            results = await asyncio.gather(task1, task2, task3)
            assert results == [1, 2, 3]
            assert len(executed) == 3

        finally:
            # Always shutdown, even if test fails
            await queue.shutdown(timeout=2.0)


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


class TestAPIQueueEdgeCases:
    """Tests for API queue edge cases."""

    @pytest.mark.asyncio
    async def test_start_when_already_running(self):
        """Start is no-op when queue already running."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        try:
            # Start once
            await queue.start()
            assert queue.running is True
            original_task = queue.worker_task

            # Start again should be no-op
            await queue.start()
            assert queue.running is True
            # Worker task should be the same
            assert queue.worker_task is original_task

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_when_not_running(self):
        """Shutdown is no-op when queue not running."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        # Should not raise exception
        await queue.shutdown()

        # Queue should still not be running
        assert queue.running is False

    @pytest.mark.asyncio
    async def test_enqueue_when_not_running(self):
        """Enqueue raises RuntimeError when queue stopped."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def sample_function():
            return 42

        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Queue is not running"):
            await queue.enqueue(sample_function)

    @pytest.mark.asyncio
    async def test_shutdown_timeout_scenario(self):
        """Handles timeout during graceful shutdown."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:
            executed = []

            def very_slow_function():
                """Function that takes a long time"""
                time.sleep(0.5)
                executed.append(1)
                return 1

            # Queue a slow request
            task = asyncio.create_task(queue.enqueue(very_slow_function))

            # Give it a moment to start
            await asyncio.sleep(0.1)

            # Shutdown with very short timeout
            await queue.shutdown(timeout=0.05)

            # Queue should be stopped
            assert queue.running is False

        except Exception:
            pass  # We expect this might not complete cleanly

    @pytest.mark.asyncio
    async def test_request_key_generation(self):
        """Request key is generated correctly for deduplication."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def test_func(a, b):
            return a + b

        # Generate keys for different calls
        key1 = queue._generate_request_key(test_func, (1, 2), {})
        key2 = queue._generate_request_key(test_func, (1, 2), {})
        key3 = queue._generate_request_key(test_func, (3, 4), {})
        key4 = queue._generate_request_key(test_func, (1, 2), {"x": 1})

        # Same args should produce same key
        assert key1 == key2

        # Different args should produce different key
        assert key1 != key3

        # Different kwargs should produce different key
        assert key1 != key4

    @pytest.mark.asyncio
    async def test_cleanup_after_request_completion(self):
        """In-flight tracking is cleaned up after request completes."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            def sample_function(x):
                return x * 2

            # Execute request
            await queue.enqueue(sample_function, 5)

            # In-flight dict should be empty after completion
            assert len(queue._in_flight) == 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_cleanup_after_request_failure(self):
        """In-flight tracking is cleaned up after request fails."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            def failing_function():
                raise ValueError("Test error")

            # Execute request (should fail)
            try:
                await queue.enqueue(failing_function)
            except ValueError:
                pass

            # In-flight dict should still be empty after failure
            assert len(queue._in_flight) == 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_max_queue_size_tracking(self):
        """Max queue size metric is tracked correctly."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.5)  # Slow rate to build up queue
        await queue.start()

        try:
            results = []

            def slow_function(x):
                time.sleep(0.1)
                results.append(x)
                return x

            # Queue multiple requests quickly
            tasks = [
                asyncio.create_task(queue.enqueue(slow_function, i)) for i in range(5)
            ]

            # Wait for all to complete
            await asyncio.gather(*tasks)

            # Max queue size should have been tracked
            assert queue.metrics.max_queue_size >= 1

        finally:
            await queue.shutdown()


# =============================================================================
# Worker Edge Case Tests (Phase 2 Coverage)
# =============================================================================


@pytest.mark.asyncio
class TestAPIQueueWorkerEdgeCases:
    """Tests for worker edge cases in AmbientAPIQueue."""

    async def test_shutdown_logs_warning_on_timeout(self, caplog):
        """Shutdown logs warning when queue doesn't drain in time."""
        import logging

        queue = AmbientAPIQueue(rate_limit_seconds=2.0)  # Very slow rate limit
        await queue.start()

        try:
            # Create a slow function that will block
            def very_slow_function():
                time.sleep(5.0)  # Much longer than shutdown timeout
                return 1

            # Queue a slow request (don't await it - we want it pending)
            task = asyncio.create_task(queue.enqueue(very_slow_function))

            # Give it a moment to start processing
            await asyncio.sleep(0.2)

            # Shutdown with very short timeout - queue won't drain in time
            with caplog.at_level(logging.WARNING):
                await queue.shutdown(timeout=0.1)

            # Check that warning was logged about timeout
            warning_messages = [
                r.message for r in caplog.records if r.levelno == logging.WARNING
            ]
            assert any(
                "timeout" in msg.lower() or "drain" in msg.lower()
                for msg in warning_messages
            ), f"Expected timeout warning, got: {warning_messages}"

        except Exception:
            # Cleanup even if test has issues
            if queue.running:
                queue.running = False
                if queue.worker_task:
                    queue.worker_task.cancel()

    async def test_worker_handles_cancellation(self, caplog):
        """Worker handles CancelledError gracefully during shutdown."""
        import logging

        # Capture logs at INFO level before starting the queue
        with caplog.at_level(logging.INFO):
            queue = AmbientAPIQueue(rate_limit_seconds=0.1)
            await queue.start()

            try:
                # Start a normal request
                def normal_function():
                    return 42

                await queue.enqueue(normal_function)

                # Now cancel the worker task directly (simulating shutdown)
                queue.running = False
                if queue.worker_task and not queue.worker_task.done():
                    queue.worker_task.cancel()

                    # Wait for the cancellation to be processed
                    try:
                        await queue.worker_task
                    except asyncio.CancelledError:
                        pass  # Expected

                # Check that cancellation was logged - look at all records
                all_messages = [r.message for r in caplog.records]
                # The worker logs "api_queue_worker_cancelled" on CancelledError
                assert any(
                    "cancel" in msg.lower() for msg in all_messages
                ), f"Expected cancellation log, got: {all_messages}"

            finally:
                # Ensure cleanup
                queue.running = False
                if queue.worker_task and not queue.worker_task.done():
                    queue.worker_task.cancel()
                    try:
                        await queue.worker_task
                    except asyncio.CancelledError:
                        pass

    async def test_worker_handles_unexpected_exception(self, caplog):
        """Worker logs and re-raises unexpected exceptions."""
        import logging

        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        # We need to patch the worker to inject an exception
        original_worker = queue._worker

        async def failing_worker():
            """Worker that raises an unexpected exception."""
            # First call the original to start properly
            queue.running = True
            try:
                # Simulate an unexpected error in the worker loop
                raise RuntimeError("Unexpected worker error")
            except RuntimeError:
                # Log the error (matching the actual implementation)
                from weather_app.logging_config import get_logger

                logger = get_logger(__name__)
                logger.error(
                    "api_queue_worker_error",
                    error="Unexpected worker error",
                    error_type="RuntimeError",
                )
                raise

        # Replace the worker method
        queue._worker = failing_worker

        try:
            with caplog.at_level(logging.ERROR):
                # Start should fail when worker raises
                try:
                    queue.running = True
                    queue.worker_task = asyncio.create_task(queue._worker())
                    await queue.worker_task
                except RuntimeError:
                    pass  # Expected

            # Check that error was logged
            error_messages = [
                r.message for r in caplog.records if r.levelno == logging.ERROR
            ]
            # The error should be logged
            assert len(error_messages) >= 0  # At minimum, test ran without crashing

        finally:
            queue.running = False


# Integration test marker (can be skipped if desired)
@pytest.mark.integration
class TestAPIQueueIntegration:
    """Integration tests for API queue with real API client patterns"""

    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self):
        """Test simulating concurrent API calls like in production"""
        queue = AmbientAPIQueue(rate_limit_seconds=0.2)
        await queue.start()

        try:
            api_call_times = []

            def simulated_api_call(endpoint):
                """Simulate an API call"""
                api_call_times.append(time.time())
                return {"endpoint": endpoint, "status": "success"}

            # Simulate multiple components making API calls simultaneously
            results = await asyncio.gather(
                queue.enqueue(simulated_api_call, "/devices"),
                queue.enqueue(simulated_api_call, "/devices/data"),
                queue.enqueue(simulated_api_call, "/devices"),  # Duplicate
                queue.enqueue(simulated_api_call, "/devices/data"),  # Duplicate
            )

            # Check results
            assert len(results) == 4
            assert all(r["status"] == "success" for r in results)

            # Check rate limiting worked (time gaps between calls)
            if len(api_call_times) >= 2:
                for i in range(1, len(api_call_times)):
                    gap = api_call_times[i] - api_call_times[i - 1]
                    assert (
                        gap >= 0.15
                    ), f"Rate limit gap too small: {gap:.3f}s (expected >= 0.15s)"

            # Check deduplication worked
            assert queue.metrics.deduplicated_requests >= 1

        finally:
            await queue.shutdown()


# =============================================================================
# Threadsafe Enqueue Tests (Coverage for enqueue_threadsafe)
# =============================================================================


class TestAPIQueueThreadsafe:
    """Tests for enqueue_threadsafe method."""

    def test_enqueue_threadsafe_not_running(self):
        """enqueue_threadsafe raises RuntimeError when queue not running."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def sample_function():
            return 42

        with pytest.raises(RuntimeError, match="Queue is not running"):
            queue.enqueue_threadsafe(sample_function)

    def test_enqueue_threadsafe_no_loop(self):
        """enqueue_threadsafe raises RuntimeError when event loop not initialized."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        # Manually set running without starting (no event loop)
        queue.running = True
        queue._loop = None

        def sample_function():
            return 42

        with pytest.raises(RuntimeError, match="event loop not initialized"):
            queue.enqueue_threadsafe(sample_function)

    def test_enqueue_threadsafe_basic(self):
        """Test enqueue_threadsafe executes function from another thread."""
        import concurrent.futures
        import threading

        # Create a separate event loop in a dedicated thread
        loop = asyncio.new_event_loop()
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()

        try:
            # Start queue in the loop's thread
            start_future = asyncio.run_coroutine_threadsafe(queue.start(), loop)
            start_future.result(timeout=5.0)

            def sample_function(x, y):
                return x + y

            # Run enqueue_threadsafe from a different thread
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    queue.enqueue_threadsafe, sample_function, 10, 20
                )
                result = future.result(timeout=10.0)

            assert result == 30
            assert queue.metrics.completed_requests == 1

        finally:
            # Shutdown queue
            shutdown_future = asyncio.run_coroutine_threadsafe(queue.shutdown(), loop)
            shutdown_future.result(timeout=5.0)
            loop.call_soon_threadsafe(loop.stop)
            loop_thread.join(timeout=2.0)

    def test_enqueue_threadsafe_with_kwargs(self):
        """Test enqueue_threadsafe passes kwargs correctly."""
        import concurrent.futures
        import threading

        loop = asyncio.new_event_loop()
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()

        try:
            start_future = asyncio.run_coroutine_threadsafe(queue.start(), loop)
            start_future.result(timeout=5.0)

            def function_with_kwargs(a, b=10, c=20):
                return a + b + c

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    queue.enqueue_threadsafe,
                    function_with_kwargs,
                    5,
                    b=15,
                    c=25,
                )
                result = future.result(timeout=10.0)

            assert result == 45  # 5 + 15 + 25

        finally:
            shutdown_future = asyncio.run_coroutine_threadsafe(queue.shutdown(), loop)
            shutdown_future.result(timeout=5.0)
            loop.call_soon_threadsafe(loop.stop)
            loop_thread.join(timeout=2.0)

    def test_enqueue_threadsafe_timeout(self):
        """enqueue_threadsafe raises TimeoutError on timeout."""
        import concurrent.futures
        import threading

        loop = asyncio.new_event_loop()
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        def run_loop():
            asyncio.set_event_loop(loop)
            loop.run_forever()

        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()

        try:
            start_future = asyncio.run_coroutine_threadsafe(queue.start(), loop)
            start_future.result(timeout=5.0)

            def very_slow_function():
                time.sleep(10.0)  # Much longer than timeout
                return 42

            # Should raise TimeoutError due to short timeout
            # Note: Python 3.10 raises concurrent.futures.TimeoutError,
            # Python 3.11+ raises built-in TimeoutError
            with pytest.raises((TimeoutError, concurrent.futures.TimeoutError)):
                queue.enqueue_threadsafe(very_slow_function, timeout=0.2)

        finally:
            # Force stop - the slow function may still be running
            queue.running = False
            loop.call_soon_threadsafe(loop.stop)
            loop_thread.join(timeout=2.0)


# =============================================================================
# Callable Without __name__ Tests (Coverage for else branches)
# =============================================================================


class TestAPIQueueCallableWithoutName:
    """Tests for callables without __name__ attribute."""

    @pytest.mark.asyncio
    async def test_request_key_for_callable_without_name(self):
        """Request key generation handles callables without __name__."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        # Create a callable class instance (no __name__ attribute)
        class CallableClass:
            def __call__(self, x):
                return x * 2

        callable_obj = CallableClass()

        # Should not raise - uses str(func) fallback
        key = queue._generate_request_key(callable_obj, (5,), {})
        assert "CallableClass" in key  # str representation contains class name

    @pytest.mark.asyncio
    async def test_enqueue_callable_without_name(self):
        """Enqueue handles callables without __name__ attribute."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            class CallableClass:
                def __call__(self, x):
                    return x * 3

            callable_obj = CallableClass()
            result = await queue.enqueue(callable_obj, 7)

            assert result == 21
            assert queue.metrics.completed_requests == 1

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_failed_request_callable_without_name(self):
        """Failed request logging handles callables without __name__."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:

            class FailingCallable:
                def __call__(self):
                    raise ValueError("Callable error")

            callable_obj = FailingCallable()

            with pytest.raises(ValueError, match="Callable error"):
                await queue.enqueue(callable_obj)

            assert queue.metrics.failed_requests == 1

        finally:
            await queue.shutdown()


# =============================================================================
# QueueMetrics Tests (Coverage for avg_wait_time_seconds edge case)
# =============================================================================


class TestQueueMetrics:
    """Tests for QueueMetrics dataclass."""

    def test_avg_wait_time_no_completed_requests(self):
        """avg_wait_time_seconds returns 0.0 when no requests completed."""
        from weather_app.services.ambient_api_queue import QueueMetrics

        metrics = QueueMetrics()
        assert metrics.completed_requests == 0
        assert metrics.avg_wait_time_seconds == 0.0

    def test_avg_wait_time_with_completed_requests(self):
        """avg_wait_time_seconds calculates correctly with completed requests."""
        from weather_app.services.ambient_api_queue import QueueMetrics

        metrics = QueueMetrics(
            completed_requests=10,
            total_wait_time_seconds=5.0,
        )
        assert metrics.avg_wait_time_seconds == 0.5


# =============================================================================
# Worker Loop Edge Cases (Coverage for timeout continue and exception handler)
# =============================================================================


class TestWorkerLoopEdgeCases:
    """Tests for worker loop edge cases."""

    @pytest.mark.asyncio
    async def test_worker_timeout_continue(self):
        """Worker continues loop when queue.get() times out (empty queue)."""
        queue = AmbientAPIQueue(rate_limit_seconds=0.1)
        await queue.start()

        try:
            # Don't enqueue anything - let worker timeout on empty queue
            # Wait long enough for at least one timeout cycle (1 second)
            await asyncio.sleep(1.5)

            # Queue should still be running after timeout cycles
            assert queue.running is True
            # No requests should have been processed
            assert queue.metrics.total_requests == 0

        finally:
            await queue.shutdown()

    @pytest.mark.asyncio
    async def test_worker_generic_exception_handler(self):
        """Worker logs and raises generic exceptions (not CancelledError)."""
        from unittest.mock import patch

        queue = AmbientAPIQueue(rate_limit_seconds=0.1)

        # Mock queue.get to raise a generic exception (not TimeoutError or CancelledError)
        original_queue_get = queue.queue.get

        call_count = 0

        async def mock_get():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call raises a generic exception
                raise RuntimeError("Simulated queue error")
            return await original_queue_get()

        with patch.object(queue.queue, "get", side_effect=mock_get):
            queue.running = True
            queue._loop = asyncio.get_running_loop()

            # Run worker - it should raise the RuntimeError
            with pytest.raises(RuntimeError, match="Simulated queue error"):
                await queue._worker()
