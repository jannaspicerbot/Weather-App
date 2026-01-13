# Plan: Fix Backfill Thread/Async Deadlock

## Problem
The backfill is stuck at "Fetching current weather data... 0%" because:

1. `backfill_service._run_backfill()` runs in a **separate thread** (line 310 in backfill_service.py)
2. It uses `AmbientWeatherAPI` with `request_queue=api_queue`
3. `api_queue` is an **async queue** running in FastAPI's main event loop
4. When the thread calls `loop.run_until_complete(queue.enqueue(...))`, it deadlocks - the async Future can't be resolved across different event loops

## Solution: Option A - Bypass Queue in Backfill Thread

The simplest fix is to have the backfill thread make direct API calls without using the async queue. The backfill already has its own rate limiting (`delay=1.0` parameter).

### Changes Required

**File: `weather_app/web/backfill_service.py`**

1. **Line 89-91** - In `validate_credentials()`, don't pass `request_queue`:
```python
# Before
api = AmbientWeatherAPI(api_key, app_key, request_queue=api_queue)

# After
api = AmbientWeatherAPI(api_key, app_key)  # No queue - direct calls
```

2. **Line 341** - In `_run_backfill()`, don't pass `request_queue`:
```python
# Before
api = AmbientWeatherAPI(api_key, app_key, request_queue=api_queue)

# After
api = AmbientWeatherAPI(api_key, app_key)  # No queue - direct calls
```

3. **Remove the import** of `api_queue` from `weather_app.web.app` (lines 89 and 339)

### Why This Works

- The backfill already rate-limits via `delay=1.0` in `fetch_all_historical_data()`
- Direct HTTP calls work fine in threads (no async/await needed)
- The async queue remains for scheduler and web routes (which run in async context)

### Files to Modify

1. `weather_app/web/backfill_service.py` - Remove queue usage (2 places)

### Testing

1. Delete `.env` to reset credentials
2. Restart backend
3. Go through onboarding flow
4. Verify backfill shows progress > 0%
5. Verify records are being inserted

## Alternative: Option B - Async Backfill (More Complex)

Convert backfill to run as async task instead of thread. This is more complex and requires:
- Converting `_run_backfill` to async
- Using `asyncio.create_task()` instead of `threading.Thread`
- Coordinating with FastAPI's event loop lifecycle

**Recommendation: Use Option A** - simpler, isolated change, lower risk.
