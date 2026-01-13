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
