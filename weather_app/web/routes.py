"""
API routes for weather data
Defines all endpoints for the FastAPI application
"""

import time

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from weather_app.config import get_db_info
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
    DeviceInfo,
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
        start_time = time.time()
        try:
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
        start_time = time.time()
        try:
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
        try:
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
        Get weather data within a date range (API route)
        """
        try:
            return WeatherRepository.get_all_readings(
                start_date=start_date, end_date=end_date, limit=limit, order="desc"
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
        try:
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
        """
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
    def save_credentials(request: CredentialValidationRequest):
        """
        Save credentials to the .env file.

        Note: This does NOT re-validate credentials to avoid duplicate API calls.
        Frontend should call /api/credentials/validate first.
        """
        # Save directly without re-validating (frontend already validated)
        # This avoids duplicate calls to Ambient Weather API
        success, save_message = backfill_service.save_credentials(
            request.api_key, request.app_key
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
    def start_backfill(request: BackfillStartRequest = None):
        """
        Start background data backfill.

        Automatically fetches current data first, then backfills historical data.
        Uses credentials from request body or falls back to .env file.

        The backfill runs in the background. Poll /api/backfill/progress to monitor.
        """
        api_key = request.api_key if request else None
        app_key = request.app_key if request else None

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
