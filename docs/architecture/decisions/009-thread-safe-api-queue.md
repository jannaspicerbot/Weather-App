# ADR 009: Thread-Safe API Queue for Background Tasks

**Status:** Accepted
**Date:** 2026-01-13
**Context:** Backfill service and scheduler running in background threads

## Problem

The backfill service runs in a separate `threading.Thread` and needs to make API calls to Ambient Weather. The application has an async `AmbientAPIQueue` that rate-limits all API calls to 1 request/second.

A deadlock occurred because:

1. Backfill thread calls the API with `request_queue=api_queue`
2. The original `AmbientWeatherAPI` client tried to call `await queue.enqueue()` using `loop.run_until_complete()`
3. `asyncio.get_event_loop()` in a background thread returns a **different** event loop than the one the queue worker runs in
4. The queue's `asyncio.Future` objects are tied to the main event loop
5. The background thread blocks waiting on futures that can only be resolved by the main loop's worker - **deadlock**

## Decision

Add a thread-safe bridge method `enqueue_threadsafe()` to `AmbientAPIQueue` that uses Python's `asyncio.run_coroutine_threadsafe()` to safely submit work from any thread to the queue's event loop.

## Implementation

### Changes Made

**1. `weather_app/services/ambient_api_queue.py`**

- Added `_loop: asyncio.AbstractEventLoop | None` attribute
- Store loop reference in `start()`: `self._loop = asyncio.get_running_loop()`
- Added `enqueue_threadsafe()` method:

```python
def enqueue_threadsafe(
    self, func: Callable, *args, timeout: float = 60.0, **kwargs
) -> Any:
    """Enqueue from a non-async thread context."""
    if not self.running:
        raise RuntimeError("Queue is not running. Call start() first.")
    if self._loop is None:
        raise RuntimeError("Queue event loop not initialized")

    concurrent_future = asyncio.run_coroutine_threadsafe(
        self.enqueue(func, *args, **kwargs),
        self._loop,
    )
    return concurrent_future.result(timeout=timeout)
```

**2. `weather_app/api/client.py`**

- Replaced broken pattern in `get_devices()` and `get_device_data()`:

```python
# Before (broken)
loop = asyncio.get_event_loop()
return loop.run_until_complete(self.request_queue.enqueue(...))

# After (working)
return self.request_queue.enqueue_threadsafe(self._get_devices_impl)
```

- Removed unused `asyncio` import

**3. `weather_app/web/backfill_service.py`**

- Re-enabled use of `api_queue` in `validate_credentials()` and `_run_backfill()`
- All API calls now go through the centralized queue

## How It Works

```
┌─────────────────────┐     ┌──────────────────────┐
│  Background Thread  │     │   Main Event Loop    │
│  (Backfill/Sched)   │     │   (FastAPI/Queue)    │
├─────────────────────┤     ├──────────────────────┤
│                     │     │                      │
│  api.get_devices()  │     │  queue._worker()     │
│         │           │     │       │              │
│         ▼           │     │       │              │
│  enqueue_threadsafe │     │       │              │
│         │           │     │       │              │
│         └───────────┼─────┼───────▼              │
│   run_coroutine_    │     │  enqueue()           │
│   threadsafe()      │     │       │              │
│         │           │     │       ▼              │
│         │           │     │  Rate limit wait     │
│    (blocks)         │     │       │              │
│         │           │     │       ▼              │
│         │           │     │  Execute API call    │
│         │           │     │       │              │
│         ◄───────────┼─────┼───────┘              │
│      result         │     │                      │
│                     │     │                      │
└─────────────────────┘     └──────────────────────┘
```

## Alternatives Considered

### Option B: Convert Backfill to Async
Run backfill as `asyncio.create_task()` instead of thread.

**Rejected because:**
- Major refactor (all `time.sleep()` → `await asyncio.sleep()`)
- Database operations are sync, would need `run_in_executor` everywhere
- APScheduler's `BackgroundScheduler` still uses threads for jobs

### Option C: Shared Threading Lock
Use `threading.Lock` between queue and background threads.

**Rejected because:**
- Doesn't solve the event loop mismatch problem
- Mixing threading locks with asyncio can cause deadlocks

### Option D: Direct API Calls (Bypass Queue)
Have backfill make direct API calls with its own rate limiting.

**Rejected because:**
- Loses centralized rate limiting
- Risk of simultaneous calls from scheduler + backfill hitting rate limits
- DRY violation (rate limiting logic in multiple places)

## Consequences

### Positive
- All API calls serialized through single queue
- Rate limiting works correctly across all consumers
- Request deduplication works across all callers
- Metrics capture all requests
- Works for both BackfillService and WeatherScheduler

### Negative
- Blocking call in background thread (acceptable for background tasks)
- Requires queue to be started before background tasks can use it

## References

- Python docs: [asyncio.run_coroutine_threadsafe](https://docs.python.org/3/library/asyncio-task.html#asyncio.run_coroutine_threadsafe)
- Original issue: Backfill stuck at "Fetching current weather data... 0%"
