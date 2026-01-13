# API Pattern Examples

**Real examples from Weather App project**
**Reference:** Use these as templates for new endpoints
**Load after:** API-STANDARDS.md

---

## Table of Contents

1. [Simple GET Endpoint](#simple-get-endpoint)
2. [GET with Query Parameters](#get-with-query-parameters)
3. [GET with Date Range](#get-with-date-range)
4. [POST with Request Body](#post-with-request-body)
5. [Paginated Response](#paginated-response)
6. [Aggregation Endpoint](#aggregation-endpoint)
7. [Error Handling Examples](#error-handling-examples)

---

## Simple GET Endpoint

### Get Latest Weather Reading

```python
from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from weather_app.models import WeatherResponse
from weather_app.database import get_db

router = APIRouter(prefix="/api/weather", tags=["weather"])
logger = logging.getLogger(__name__)

@router.get("/latest", response_model=WeatherResponse)
async def get_latest_weather(
    station_id: Optional[str] = None
) -> WeatherResponse:
    """
    Get the most recent weather reading.

    Args:
        station_id: Optional station filter. If omitted, returns latest from any station.

    Returns:
        Most recent weather reading

    Raises:
        HTTPException: 404 if no data exists, 500 if database error
    """
    try:
        db = get_db()

        if station_id:
            result = await db.get_latest_by_station(station_id)
        else:
            result = await db.get_latest()

        if not result:
            raise HTTPException(
                status_code=404,
                detail="No weather data found"
            )

        return WeatherResponse(**result)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching latest weather: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

**Key points:**
- Type hints for all parameters
- Optional parameter with default
- Docstring with Args/Returns/Raises
- Error handling with re-raise pattern
- Logging for debugging

---

## GET with Query Parameters

### Query Weather by Station and Limit

```python
from fastapi import Query
from typing import List

@router.get("/station/{station_id}", response_model=List[WeatherResponse])
async def get_station_weather(
    station_id: str = Path(
        ...,
        description="Station identifier",
        min_length=1,
        max_length=50,
        regex="^[A-Za-z0-9_-]+$"
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Maximum number of readings to return"
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of readings to skip"
    )
) -> List[WeatherResponse]:
    """
    Get weather readings for a specific station.

    Args:
        station_id: Station identifier (alphanumeric, dash, underscore)
        limit: Maximum results (1-1000, default 100)
        offset: Pagination offset (default 0)

    Returns:
        List of weather readings, newest first

    Raises:
        HTTPException: 404 if station not found, 500 if database error
    """
    try:
        db = get_db()

        # Verify station exists
        station_exists = await db.station_exists(station_id)
        if not station_exists:
            raise HTTPException(
                status_code=404,
                detail=f"Station '{station_id}' not found"
            )

        # Get readings
        results = await db.query_by_station(
            station_id=station_id,
            limit=limit,
            offset=offset
        )

        if not results:
            # Station exists but no data yet - return empty list
            return []

        return [WeatherResponse(**r) for r in results]

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching station weather: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

**Key points:**
- Path parameter with regex validation
- Query parameters with constraints (ge, le)
- Distinguish between 404 (not found) and empty list (found but no data)
- Pagination support

---

## GET with Date Range

### Query Weather by Date Range

```python
from datetime import datetime
from typing import Optional

@router.get("/range", response_model=List[WeatherResponse])
async def get_weather_range(
    start_date: datetime = Query(
        ...,
        description="Start of date range (ISO format)"
    ),
    end_date: datetime = Query(
        ...,
        description="End of date range (ISO format)"
    ),
    station_id: Optional[str] = Query(
        None,
        description="Optional station filter"
    )
) -> List[WeatherResponse]:
    """
    Query weather data within a date range.

    Args:
        start_date: Start of range (inclusive), ISO format
        end_date: End of range (inclusive), ISO format
        station_id: Optional station filter

    Returns:
        List of weather readings within range

    Raises:
        HTTPException:
            - 400 if date range invalid
            - 404 if no data in range
            - 500 if database error
    """
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be after start_date"
        )

    # Check for future dates
    now = datetime.now()
    if start_date > now:
        raise HTTPException(
            status_code=400,
            detail="start_date cannot be in the future"
        )

    # Limit range to prevent excessive queries
    max_days = 365
    range_days = (end_date - start_date).days
    if range_days > max_days:
        raise HTTPException(
            status_code=400,
            detail=f"Date range cannot exceed {max_days} days"
        )

    try:
        db = get_db()
        results = await db.query_range(
            start_date=start_date,
            end_date=end_date,
            station_id=station_id
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for range {start_date.date()} to {end_date.date()}"
            )

        return [WeatherResponse(**r) for r in results]

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error fetching weather range: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

**Key points:**
- Multiple validations before database query
- Business logic validation (date range limits)
- Clear error messages
- DateTime parsing handled by FastAPI

---

## POST with Request Body

### Batch Insert Weather Readings

```python
from pydantic import BaseModel, Field, validator
from typing import List

class WeatherReadingRequest(BaseModel):
    """Request model for weather reading."""
    timestamp: datetime
    station_id: str = Field(..., min_length=1, max_length=50)
    temperature_f: float = Field(..., ge=-100, le=150)
    humidity: int = Field(..., ge=0, le=100)
    wind_speed_mph: Optional[float] = Field(None, ge=0, le=200)
    pressure_inhg: Optional[float] = Field(None, ge=20, le=35)

    @validator('timestamp')
    def timestamp_not_future(cls, v):
        if v > datetime.now():
            raise ValueError('timestamp cannot be in the future')
        return v

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2026-01-13T12:00:00Z",
                "station_id": "STATION001",
                "temperature_f": 72.5,
                "humidity": 45,
                "wind_speed_mph": 5.2,
                "pressure_inhg": 30.12
            }
        }

class BatchInsertResponse(BaseModel):
    """Response for batch insert."""
    success: bool
    inserted_count: int
    message: str

@router.post("/batch", response_model=BatchInsertResponse, status_code=201)
async def insert_weather_batch(
    readings: List[WeatherReadingRequest] = Body(
        ...,
        description="List of weather readings to insert"
    )
) -> BatchInsertResponse:
    """
    Insert multiple weather readings in a batch.

    Args:
        readings: List of weather readings (max 1000)

    Returns:
        Success status and count of inserted readings

    Raises:
        HTTPException:
            - 400 if validation fails or too many readings
            - 409 if duplicate timestamps exist
            - 500 if database error
    """
    # Validate batch size
    if len(readings) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one reading required"
        )

    if len(readings) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 readings per batch"
        )

    try:
        db = get_db()

        # Check for duplicates in request
        timestamps = [r.timestamp for r in readings]
        if len(timestamps) != len(set(timestamps)):
            raise HTTPException(
                status_code=400,
                detail="Duplicate timestamps in request"
            )

        # Insert batch
        count = await db.batch_insert([r.dict() for r in readings])

        return BatchInsertResponse(
            success=True,
            inserted_count=count,
            message=f"Successfully inserted {count} readings"
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error inserting batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to insert readings"
        )
```

**Key points:**
- Pydantic models for request/response validation
- Validators for business logic
- Batch size limits
- 201 status code for resource creation
- Example in schema for OpenAPI docs

---

## Paginated Response

### Get All Weather with Pagination

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

@router.get("/all", response_model=PaginatedResponse[WeatherResponse])
async def get_all_weather(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page")
) -> PaginatedResponse[WeatherResponse]:
    """
    Get all weather readings with pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page (1-100)

    Returns:
        Paginated list of weather readings

    Raises:
        HTTPException: 500 if database error
    """
    try:
        db = get_db()

        # Calculate offset
        offset = (page - 1) * page_size

        # Get total count (for pagination metadata)
        total = await db.count()

        # Get page of results
        results = await db.query_paginated(
            offset=offset,
            limit=page_size
        )

        # Calculate pagination metadata
        total_pages = (total + page_size - 1) // page_size
        has_next = page < total_pages
        has_prev = page > 1

        return PaginatedResponse(
            items=[WeatherResponse(**r) for r in results],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev
        )

    except Exception as e:
        logger.error(f"Error fetching paginated weather: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

**Key points:**
- Generic response model (reusable for other endpoints)
- Pagination metadata included
- Offset calculation
- Total count for UI pagination controls

---

## Aggregation Endpoint

### Get Daily Weather Statistics

```python
class DailyStatsResponse(BaseModel):
    """Daily weather statistics."""
    date: date
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    total_readings: int

@router.get("/stats/daily", response_model=List[DailyStatsResponse])
async def get_daily_stats(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    station_id: Optional[str] = Query(None, description="Optional station filter")
) -> List[DailyStatsResponse]:
    """
    Get daily weather statistics for a date range.

    Calculates average, min, max temperature and humidity for each day.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        station_id: Optional station filter

    Returns:
        List of daily statistics, one per day

    Raises:
        HTTPException:
            - 400 if date range invalid or too large
            - 404 if no data in range
            - 500 if database error
    """
    # Validate range
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be after start_date"
        )

    range_days = (end_date - start_date).days
    if range_days > 90:
        raise HTTPException(
            status_code=400,
            detail="Date range cannot exceed 90 days for statistics"
        )

    try:
        db = get_db()
        results = await db.get_daily_statistics(
            start_date=start_date,
            end_date=end_date,
            station_id=station_id
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for range {start_date} to {end_date}"
            )

        return [DailyStatsResponse(**r) for r in results]

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error calculating daily stats: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

**Key points:**
- Date type (not datetime) for daily aggregations
- Range limits for performance
- Aggregation happens in database layer
- Clear, structured response model

---

## Error Handling Examples

### Complete Error Handling Pattern

```python
from fastapi import HTTPException, status
from typing import Optional

class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

@router.get("/weather/{id}", response_model=WeatherResponse)
async def get_weather_by_id(
    id: int = Path(..., ge=1, description="Weather reading ID")
) -> WeatherResponse:
    """
    Get weather reading by ID.

    Demonstrates comprehensive error handling.
    """
    try:
        db = get_db()
        result = await db.get_by_id(id)

        if not result:
            # 404 - Resource not found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Weather reading {id} not found"
            )

        return WeatherResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise

    except ValueError as e:
        # 400 - Bad request (data validation)
        logger.warning(f"Validation error for ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except PermissionError as e:
        # 403 - Forbidden (authorization)
        logger.warning(f"Permission denied for ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    except TimeoutError as e:
        # 504 - Gateway timeout (external service)
        logger.error(f"Timeout fetching ID {id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request timeout"
        )

    except Exception as e:
        # 500 - Unexpected errors
        logger.error(f"Unexpected error for ID {id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

**Key points:**
- Different exceptions map to different status codes
- Re-raise pattern for HTTP exceptions
- Logging appropriate to severity
- No sensitive data in error messages
- Stack traces only in logs, not responses

---

## Testing Examples

### Integration Test for API Endpoint

```python
# tests/test_weather_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_get_latest_weather_success(client, test_db_with_data):
    """Test successful retrieval of latest weather."""
    response = client.get("/api/weather/latest")

    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "temperature_f" in data
    assert "station_id" in data

def test_get_latest_weather_no_data(client, empty_db):
    """Test 404 when no data exists."""
    response = client.get("/api/weather/latest")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_weather_range_invalid_dates(client):
    """Test validation of date range."""
    response = client.get(
        "/api/weather/range",
        params={
            "start_date": "2026-01-31",
            "end_date": "2026-01-01"  # End before start
        }
    )

    assert response.status_code == 400
    assert "end_date must be after start_date" in response.json()["detail"]

def test_batch_insert_success(client, test_db):
    """Test batch insert of weather readings."""
    readings = [
        {
            "timestamp": "2026-01-13T12:00:00Z",
            "station_id": "TEST001",
            "temperature_f": 72.5,
            "humidity": 45
        },
        {
            "timestamp": "2026-01-13T13:00:00Z",
            "station_id": "TEST001",
            "temperature_f": 73.2,
            "humidity": 43
        }
    ]

    response = client.post("/api/weather/batch", json=readings)

    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["inserted_count"] == 2
```

---

## Common Patterns Summary

### 1. Always Include
- Type hints for all parameters
- Docstring (Args, Returns, Raises)
- Error handling (try/except with re-raise)
- Logging for errors
- Input validation

### 2. Validation Order
1. Path/query parameter validation (FastAPI automatic)
2. Business logic validation (before DB call)
3. Database operation
4. Response formatting

### 3. Status Codes
- 200: Success (GET)
- 201: Created (POST)
- 204: No Content (DELETE)
- 400: Bad Request (invalid input)
- 401: Unauthorized (no auth)
- 403: Forbidden (no permission)
- 404: Not Found (resource missing)
- 409: Conflict (duplicate)
- 500: Internal Server Error
- 504: Gateway Timeout

### 4. Error Response Pattern
```python
try:
    # Do work
    result = await db.operation()
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return result
except HTTPException:
    raise  # Re-raise formatted errors
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

**See also:**
- API-STANDARDS.md - Full standards and requirements
- TESTING.md - Testing strategies
- DATABASE-PATTERNS.md - Database integration patterns

**Questions?** Check CLAUDE.md or ask before implementing.
