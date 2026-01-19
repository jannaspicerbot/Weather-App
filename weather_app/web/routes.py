"""
API routes for weather data
Defines all endpoints for the FastAPI application
"""

import time

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from weather_app.config import DEMO_DB_PATH, get_db_info, get_demo_info
from weather_app.database import WeatherRepository
from weather_app.logging_config import get_logger, log_api_request
from weather_app.web.backfill_service import backfill_service
from weather_app.web.models import (
    BackfillProgressResponse,
    BackfillStartRequest,
    CredentialStatusResponse,
    CredentialValidationRequest,
    CredentialValidationResponse,
    DatabaseStats,
    DemoStatusResponse,
    DeviceInfo,
    DeviceListResponse,
    DeviceSelectionRequest,
    GenerationStatusResponse,
    WeatherData,
)

logger = get_logger(__name__)


def register_routes(app: FastAPI):
    """Register all API routes with the app"""

    @app.get("/api")
    def read_root():
        """API information endpoint (moved from / to allow frontend at root)"""
        db_info = get_db_info()
        return {
            "message": "Weather API",
            "version": "1.0.0",
            "database": {"mode": db_info["mode"], "path": db_info["database_path"]},
            "endpoints": {
                "/api/weather/latest": "Get latest weather readings",
                "/api/weather/range": "Get weather data within date range",
                "/api/weather/stats": "Get database statistics",
                "/api/scheduler/status": "Get scheduler status and configuration",
                "/api/health": "Health check endpoint",
                "/weather": "Legacy: Get weather data with filters",
                "/weather/latest": "Legacy: Get latest reading",
                "/weather/stats": "Legacy: Get database statistics",
            },
        }

    @app.get("/weather", response_model=list[WeatherData])
    def get_weather_data(
        request: Request,
        limit: int = Query(
            default=100,
            ge=1,
            le=1000,
            description="Maximum number of records to return",
        ),
        offset: int = Query(default=0, ge=0, description="Number of records to skip"),
        start_date: str | None = Query(
            default=None, description="Start date (ISO format: YYYY-MM-DD)"
        ),
        end_date: str | None = Query(
            default=None, description="End date (ISO format: YYYY-MM-DD)"
        ),
        order: str = Query(
            default="desc",
            pattern="^(asc|desc)$",
            description="Sort order by date (asc or desc)",
        ),
    ):
        """
        Query weather data from the database

        Parameters:
        - limit: Maximum number of records (1-1000, default: 100)
        - offset: Number of records to skip (for pagination)
        - start_date: Filter by start date (YYYY-MM-DD format)
        - end_date: Filter by end date (YYYY-MM-DD format)
        - order: Sort order - 'asc' or 'desc' (default: desc)
        """
        start_time = time.time()
        try:
            result = WeatherRepository.get_all_readings(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                order=order,
            )

            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather",
                params={"limit": limit, "offset": offset},
                status_code=200,
                duration_ms=duration_ms,
            )

            return result
        except ValueError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather",
                params={"limit": limit, "offset": offset},
                status_code=400,
                duration_ms=duration_ms,
            )
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather",
                params={"limit": limit, "offset": offset},
                status_code=500,
                duration_ms=duration_ms,
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/weather/latest", response_model=WeatherData)
    def get_latest_weather(request: Request):
        """
        Get the most recent weather data reading
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        start_time = time.time()
        try:
            # Check for demo mode
            if is_demo_mode():
                demo_service = get_demo_service()
                if demo_service and demo_service.is_available:
                    result = demo_service.get_latest_reading()
                else:
                    raise HTTPException(
                        status_code=503, detail="Demo service unavailable"
                    )
            else:
                result = WeatherRepository.get_latest_reading()

            if result is None:
                duration_ms = (time.time() - start_time) * 1000
                log_api_request(
                    logger,
                    "GET",
                    "/weather/latest",
                    status_code=404,
                    duration_ms=duration_ms,
                )
                raise HTTPException(
                    status_code=404, detail="No weather data found in database"
                )

            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather/latest",
                status_code=200,
                duration_ms=duration_ms,
            )

            return result
        except RuntimeError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather/latest",
                status_code=500,
                duration_ms=duration_ms,
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/weather/stats", response_model=DatabaseStats)
    def get_database_stats(request: Request):
        """
        Get statistics about the weather database
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        start_time = time.time()
        try:
            # Check for demo mode
            if is_demo_mode():
                demo_service = get_demo_service()
                if demo_service and demo_service.is_available:
                    result = demo_service.get_stats()
                else:
                    raise HTTPException(
                        status_code=503, detail="Demo service unavailable"
                    )
            else:
                result = WeatherRepository.get_stats()

            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather/stats",
                status_code=200,
                duration_ms=duration_ms,
            )

            return result
        except RuntimeError as e:
            duration_ms = (time.time() - start_time) * 1000
            log_api_request(
                logger,
                "GET",
                "/weather/stats",
                status_code=500,
                duration_ms=duration_ms,
            )
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/health")
    def health_check():
        """
        Health check endpoint for monitoring
        """
        db_info = get_db_info()
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": db_info["database_engine"],
                "mode": db_info["mode"],
            },
        }

    # Add API prefix routes for frontend compatibility
    @app.get("/api/weather/latest")
    def api_get_latest_weather(limit: int = Query(default=100, ge=1, le=10000)):
        """
        Get the latest weather readings (API route)
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        try:
            # Check for demo mode
            if is_demo_mode():
                demo_service = get_demo_service()
                if demo_service and demo_service.is_available:
                    return demo_service.get_all_readings(limit=limit, order="desc")
                raise HTTPException(status_code=503, detail="Demo service unavailable")

            results = WeatherRepository.get_all_readings(limit=limit, order="desc")
            return results
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/weather/range")
    def api_get_weather_range(
        start_date: str | None = Query(default=None),
        end_date: str | None = Query(default=None),
        limit: int = Query(default=1000, ge=1, le=10000),
    ):
        """
        Get weather data within a date range (API route).

        For large date ranges, returns evenly sampled data distributed
        across the full range rather than just the most recent records.
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        try:
            # Check for demo mode
            if is_demo_mode():
                demo_service = get_demo_service()
                if not demo_service or not demo_service.is_available:
                    raise HTTPException(
                        status_code=503, detail="Demo service unavailable"
                    )

                if start_date and end_date:
                    return demo_service.get_sampled_readings(
                        start_date=start_date,
                        end_date=end_date,
                        target_count=limit,
                    )
                else:
                    return demo_service.get_all_readings(limit=limit, order="desc")

            if start_date and end_date:
                # Use sampling for date range queries to ensure even distribution
                return WeatherRepository.get_sampled_readings(
                    start_date=start_date,
                    end_date=end_date,
                    target_count=limit,
                )
            else:
                # No date range specified - return most recent records
                return WeatherRepository.get_all_readings(
                    limit=limit,
                    order="desc",
                )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/weather/stats")
    def api_get_stats():
        """
        Get database statistics (API route)
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        try:
            # Check for demo mode
            if is_demo_mode():
                demo_service = get_demo_service()
                if demo_service and demo_service.is_available:
                    return demo_service.get_stats()
                raise HTTPException(status_code=503, detail="Demo service unavailable")

            return WeatherRepository.get_stats()
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/scheduler/status")
    def get_scheduler_status():
        """
        Get scheduler status and configuration

        Returns information about the automated data collection scheduler
        including enabled state, fetch interval, and next run time.
        """
        from weather_app.web.app import scheduler

        return scheduler.get_status()

    # ===========================================
    # Onboarding & Credential Management Endpoints
    # ===========================================

    @app.get("/api/credentials/status", response_model=CredentialStatusResponse)
    def get_credential_status():
        """
        Check if API credentials are configured.

        Returns whether the .env file has API key and App key set.
        Used by frontend to determine if onboarding is needed.

        In demo mode, credentials are always considered "configured".
        """
        from weather_app.web.app import is_demo_mode

        # In demo mode, pretend credentials are configured
        if is_demo_mode():
            return CredentialStatusResponse(
                configured=True,
                has_api_key=True,
                has_app_key=True,
            )

        status = backfill_service.get_credential_status()
        return CredentialStatusResponse(**status)

    @app.post("/api/credentials/validate", response_model=CredentialValidationResponse)
    def validate_credentials(request: CredentialValidationRequest):
        """
        Validate API credentials by testing them against Ambient Weather API.

        Tests credentials by attempting to fetch the user's device list.
        Does NOT save credentials - use /api/credentials/save for that.
        """
        valid, message, devices = backfill_service.validate_credentials(
            request.api_key, request.app_key
        )

        device_infos = [DeviceInfo(**d) for d in devices]

        return CredentialValidationResponse(
            valid=valid,
            message=message,
            devices=device_infos,
        )

    @app.post("/api/credentials/save")
    def save_credentials(
        request: CredentialValidationRequest, device_mac: str | None = None
    ):
        """
        Save credentials to the .env file.

        Note: This does NOT re-validate credentials to avoid duplicate API calls.
        Frontend should call /api/credentials/validate first.

        Optional device_mac parameter can be provided to save device selection at the same time.
        """
        # Save directly without re-validating (frontend already validated)
        # This avoids duplicate calls to Ambient Weather API
        success, save_message = backfill_service.save_credentials(
            request.api_key, request.app_key, device_mac
        )

        if not success:
            raise HTTPException(status_code=500, detail=save_message)

        return {"success": True, "message": save_message}

    # ===========================================
    # Backfill Management Endpoints
    # ===========================================

    @app.get("/api/backfill/progress", response_model=BackfillProgressResponse)
    def get_backfill_progress():
        """
        Get current backfill progress.

        Returns status, records processed, estimated time remaining, etc.
        Poll this endpoint to update progress UI during backfill.
        """
        progress = backfill_service.get_progress()

        return BackfillProgressResponse(
            progress_id=progress.get("progress_id"),
            status=progress.get("status", "idle"),
            message=progress.get("message", ""),
            total_records=progress.get("total_records", 0),
            inserted_records=progress.get("inserted_records", 0),
            skipped_records=progress.get("skipped_records", 0),
            current_date=progress.get("current_date"),
            start_date=progress.get("start_date"),
            end_date=progress.get("end_date"),
            estimated_time_remaining_seconds=progress.get(
                "estimated_time_remaining_seconds"
            ),
            requests_made=progress.get("requests_made", 0),
        )

    @app.post("/api/backfill/start", response_model=BackfillProgressResponse)
    def start_backfill(request: BackfillStartRequest | None = None):
        """
        Start background data backfill.

        Automatically fetches current data first, then backfills historical data.
        Uses credentials from request body or falls back to .env file.

        The backfill runs in the background. Poll /api/backfill/progress to monitor.
        """
        api_key: str | None = request.api_key if request else None
        app_key: str | None = request.app_key if request else None

        started, message = backfill_service.start_backfill(api_key, app_key)

        if not started:
            # Return current progress if already running
            progress = backfill_service.get_progress()
            return BackfillProgressResponse(
                progress_id=progress.get("progress_id"),
                status=progress.get("status", "idle"),
                message=message,
                total_records=progress.get("total_records", 0),
                inserted_records=progress.get("inserted_records", 0),
                skipped_records=progress.get("skipped_records", 0),
            )

        # Return initial progress
        return BackfillProgressResponse(
            status="in_progress",
            message=message,
        )

    @app.post("/api/backfill/stop")
    def stop_backfill():
        """
        Stop the currently running backfill.

        Data already fetched will be preserved.
        """
        if not backfill_service.is_running():
            return {"success": False, "message": "No backfill in progress"}

        backfill_service.stop()
        return {"success": True, "message": "Backfill stop requested"}

    # ===========================================
    # Device Management Endpoints
    # ===========================================

    @app.get("/api/devices", response_model=DeviceListResponse)
    def get_devices():
        """
        Get list of available weather devices.

        Returns the list of devices associated with the configured credentials
        and indicates which device is currently selected.

        In demo mode, returns the demo device.
        Requires valid API credentials to be configured otherwise.
        """
        import os

        from weather_app.web.app import get_demo_service, is_demo_mode

        # In demo mode, return demo device
        if is_demo_mode():
            demo_service = get_demo_service()
            if demo_service:
                demo_devices = demo_service.get_devices()
                return DeviceListResponse(
                    devices=[DeviceInfo(**d) for d in demo_devices],
                    selected_device_mac="DEMO:SEATTLE:01",
                )
            raise HTTPException(status_code=503, detail="Demo service unavailable")

        from weather_app.api.client import AmbientWeatherAPI

        # Get credentials from environment
        api_key = os.getenv("AMBIENT_API_KEY")
        app_key = os.getenv("AMBIENT_APP_KEY")

        if not api_key or not app_key:
            raise HTTPException(
                status_code=400, detail="API credentials not configured"
            )

        try:
            # Fetch devices from API (with rate limiting via queue)
            from weather_app.web.app import api_queue

            api = AmbientWeatherAPI(api_key, app_key, request_queue=api_queue)
            devices = api.get_devices()

            # Convert to response model
            device_infos = []
            for device in devices:
                # Extract location from coords (prefer location over full address)
                coords = device.get("info", {}).get("coords", {})
                location = coords.get("location") or coords.get("address")

                device_infos.append(
                    DeviceInfo(
                        mac_address=device.get("macAddress", ""),
                        name=device.get("info", {}).get("name"),
                        last_data=device.get("lastData", {}).get("date"),
                        location=location,
                    )
                )

            # Get currently selected device
            selected_mac = os.getenv("AMBIENT_DEVICE_MAC")

            return DeviceListResponse(
                devices=device_infos, selected_device_mac=selected_mac
            )

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to fetch devices: {str(e)}"
            )

    @app.post("/api/devices/select")
    def select_device(request: DeviceSelectionRequest):
        """
        Save device selection.

        Updates the AMBIENT_DEVICE_MAC environment variable and saves it to .env file.
        All subsequent data fetching will use the selected device.
        """
        success, message = backfill_service.save_device_selection(request.device_mac)

        if not success:
            raise HTTPException(status_code=500, detail=message)

        return {"success": True, "message": message, "device_mac": request.device_mac}

    # ===========================================
    # Demo Mode Endpoints
    # ===========================================

    @app.get("/api/demo/status", response_model=DemoStatusResponse)
    def get_demo_status():
        """
        Get current demo mode status.

        Returns whether demo mode is enabled, available, and database info.
        """
        from weather_app.web.app import get_demo_service, is_demo_mode

        demo_info = get_demo_info()
        demo_service = get_demo_service() if is_demo_mode() else None

        stats = None
        if demo_service and demo_service.is_available:
            stats = demo_service.get_stats()

        return DemoStatusResponse(
            enabled=is_demo_mode(),
            available=bool(demo_info["demo_db_exists"]),
            message="Demo mode active" if is_demo_mode() else "Demo mode inactive",
            database_path=str(DEMO_DB_PATH) if demo_info["demo_db_exists"] else None,
            total_records=stats["total_records"] if stats else None,
            date_range_days=stats["date_range_days"] if stats else None,
        )

    @app.post("/api/demo/enable", response_model=DemoStatusResponse)
    def enable_demo():
        """
        Enable demo mode.

        Switches the application to use the pre-populated demo database
        with Seattle weather data. No credentials required.

        If the demo database doesn't exist, returns 202 Accepted with
        generation_required=True. Client should then call /api/demo/generate
        to create the database, then retry this endpoint.
        """
        from weather_app.web.app import enable_demo_mode, get_demo_service

        # Check if demo database exists first
        if not DEMO_DB_PATH.exists():
            # Return 202 Accepted - generation required
            return JSONResponse(
                status_code=202,
                content=DemoStatusResponse(
                    enabled=False,
                    available=False,
                    message="Demo database not found. Generation required.",
                    generation_required=True,
                    estimated_generation_minutes=10,
                ).model_dump(),
            )

        success, message = enable_demo_mode()

        if not success:
            raise HTTPException(status_code=400, detail=message)

        demo_service = get_demo_service()
        stats = demo_service.get_stats() if demo_service else None

        return DemoStatusResponse(
            enabled=True,
            available=True,
            message=message,
            database_path=str(DEMO_DB_PATH),
            total_records=stats["total_records"] if stats else None,
            date_range_days=stats["date_range_days"] if stats else None,
        )

    @app.post("/api/demo/disable", response_model=DemoStatusResponse)
    def disable_demo():
        """
        Disable demo mode.

        Returns the application to normal mode requiring credentials.
        """
        from weather_app.web.app import disable_demo_mode

        success, message = disable_demo_mode()

        return DemoStatusResponse(
            enabled=False,
            available=DEMO_DB_PATH.exists(),
            message=message,
        )

    @app.get(
        "/api/demo/generation/status",
        response_model=GenerationStatusResponse,
    )
    def get_generation_status():
        """
        Poll demo database generation progress.

        This endpoint provides an SSE fallback for clients that cannot maintain
        a persistent SSE connection. Poll every 500ms during generation.

        Returns current generation state, progress percentage, and final results
        when complete.
        """
        from weather_app.demo.generation_service import get_generation_service

        service = get_generation_service()
        status = service.get_status()

        return GenerationStatusResponse(**status)

    @app.post("/api/demo/generation/cancel")
    def cancel_generation():
        """
        Cancel ongoing demo database generation.

        Requests cancellation of the current generation. The generator will
        stop at the next checkpoint (approximately once per day of data).
        Partial database files are automatically cleaned up.

        Returns success status and message.
        """
        from weather_app.demo.generation_service import get_generation_service

        service = get_generation_service()
        success, message = service.cancel_generation()

        return {"success": success, "message": message}

    @app.post("/api/demo/generate")
    async def generate_demo_database():
        """
        Generate demo database with progress updates via Server-Sent Events (SSE).

        Uses the DemoGenerationService singleton to prevent concurrent generations.
        If a generation is already in progress, returns an SSE stream that watches
        the existing generation's progress.

        Streams progress events as the database is generated:
        - {"event": "progress", "current_day": 100, "total_days": 1095, "percent": 9}
        - {"event": "complete", "records": 315324, "size_mb": 140.5}
        - {"event": "error", "message": "..."}

        Client should use EventSource or fetch with streaming to receive updates.
        For unreliable connections, use /api/demo/generation/status polling as fallback.
        """
        import asyncio
        import json

        from fastapi.responses import StreamingResponse

        from weather_app.demo.generation_service import get_generation_service

        service = get_generation_service()

        # If database already exists, return immediately
        if DEMO_DB_PATH.exists():

            async def already_exists():
                yield f"data: {json.dumps({'event': 'complete', 'records': 0, 'size_mb': 0, 'message': 'Database already exists'})}\n\n"

            return StreamingResponse(
                already_exists(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                },
            )

        # Check current status - may already be generating from another request
        status = service.get_status()

        if status["state"] != "generating":
            # Start new generation
            success, message = service.start_generation()
            if not success:
                # Something unexpected - return error
                async def generation_error():
                    yield f"data: {json.dumps({'event': 'error', 'message': message})}\n\n"

                return StreamingResponse(
                    generation_error(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )

        async def watch_generation_stream():
            """SSE stream that watches generation service status."""
            last_percent = -1

            try:
                while True:
                    status = service.get_status()

                    # Only emit on progress change (to reduce network traffic)
                    if status["percent"] != last_percent:
                        last_percent = status["percent"]

                        # Convert status to SSE event format
                        if status["state"] == "generating":
                            event_data = {
                                "event": "progress",
                                "current_day": status["current_day"],
                                "total_days": status["total_days"],
                                "percent": status["percent"],
                            }
                        elif status["state"] == "completed":
                            event_data = {
                                "event": "complete",
                                "records": status["records"],
                                "size_mb": status["size_mb"],
                            }
                        elif status["state"] in ("failed", "cancelled"):
                            event_data = {
                                "event": "error",
                                "message": status["error"]
                                or f"Generation {status['state']}",
                            }
                        else:
                            # idle state - shouldn't happen during stream
                            event_data = {
                                "event": "error",
                                "message": "Generation not started",
                            }

                        yield f"data: {json.dumps(event_data)}\n\n"

                    # Exit loop when generation is no longer running
                    if status["state"] != "generating":
                        break

                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error("demo_generation_stream_error", error=str(e))
                yield f"data: {json.dumps({'event': 'error', 'message': str(e)})}\n\n"

        return StreamingResponse(
            watch_generation_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    # ===========================================
    # Error Handlers
    # ===========================================

    @app.exception_handler(404)
    async def not_found_handler(request, exc):
        """Handle 404 errors"""
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "detail": "The requested resource was not found",
                "status_code": 404,
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request, exc):
        """Handle 500 errors"""
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": "An internal server error occurred",
                "status_code": 500,
            },
        )
