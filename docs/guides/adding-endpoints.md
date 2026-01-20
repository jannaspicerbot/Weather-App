# Guide: Adding New API Endpoints

**Step-by-step guide for adding FastAPI endpoints to Weather App**
**Time estimate:** 30-60 minutes for complete endpoint
**Prerequisites:** API-STANDARDS.md, api-patterns.md

---

## Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [Step-by-Step Guide](#step-by-step-guide)
3. [Example Walkthrough](#example-walkthrough)
4. [Testing Your Endpoint](#testing-your-endpoint)
5. [Common Patterns](#common-patterns)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start Checklist

Use this checklist while building your endpoint:

**Planning:**
- [ ] Identify endpoint purpose and HTTP method
- [ ] Design request/response models
- [ ] Plan database queries needed
- [ ] Consider security requirements

**Implementation:**
- [ ] Create Pydantic models (request/response)
- [ ] Write database function
- [ ] Create endpoint handler
- [ ] Add input validation
- [ ] Implement error handling
- [ ] Add docstring with examples

**Testing:**
- [ ] Write unit tests (database functions)
- [ ] Write integration tests (endpoint)
- [ ] Test in Swagger UI
- [ ] Test error cases
- [ ] Verify performance

**Documentation:**
- [ ] Update API documentation
- [ ] Add example to api-patterns.md if novel pattern
- [ ] Update CHANGELOG

---

## Step-by-Step Guide

### Step 1: Plan Your Endpoint

**Questions to answer:**

1. **What does this endpoint do?**
   - Example: "Export weather data as CSV for a date range"

2. **What HTTP method?**
   - GET: Retrieve data (read-only)
   - POST: Create new resources
   - PUT/PATCH: Update existing resources
   - DELETE: Remove resources

3. **What's the URL path?**
   - Follow REST conventions
   - Use nouns, not verbs
   - Example: `/api/weather/export` (not `/api/get-weather-export`)

4. **What inputs does it need?**
   - Path parameters: `/api/weather/{station_id}`
   - Query parameters: `?start_date=2026-01-01&format=csv`
   - Request body: JSON payload for POST/PUT

5. **What does it return?**
   - Single object: `WeatherResponse`
   - List: `List[WeatherResponse]`
   - Paginated: `PaginatedResponse[WeatherResponse]`
   - File: `StreamingResponse` or `FileResponse`

6. **What can go wrong?**
   - 400: Invalid input (bad date format)
   - 404: Resource not found (station doesn't exist)
   - 500: Database error

---

### Step 2: Create Pydantic Models

**Location:** `weather_app/models.py`

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

# Request model (if POST/PUT)
class WeatherExportRequest(BaseModel):
    """Request model for weather export."""
    start_date: datetime = Field(..., description="Start of date range")
    end_date: datetime = Field(..., description="End of date range")
    format: str = Field("csv", regex="^(csv|json)$")
    station_id: Optional[str] = Field(None, max_length=50)

    @validator('end_date')
    def end_after_start(cls, v, values):
        """Validate end_date is after start_date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    class Config:
        schema_extra = {
            "example": {
                "start_date": "2026-01-01T00:00:00Z",
                "end_date": "2026-01-31T23:59:59Z",
                "format": "csv",
                "station_id": "STATION001"
            }
        }

# Response model
class WeatherExportResponse(BaseModel):
    """Response model for weather export."""
    success: bool
    record_count: int
    download_url: Optional[str] = None
    message: str
```

**Key points:**
- Add validation with `@validator`
- Include `schema_extra` for OpenAPI docs
- Use descriptive field descriptions
- Set appropriate constraints (max_length, regex, etc.)

---

### Step 3: Create Database Function

**Location:** `weather_app/database.py`

```python
from typing import List, Dict, Any, Optional
from datetime import datetime
import duckdb

async def get_weather_for_export(
    conn: duckdb.DuckDBPyConnection,
    start_date: datetime,
    end_date: datetime,
    station_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Query weather data for export.

    Args:
        conn: Database connection
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        station_id: Optional station filter

    Returns:
        List of weather readings as dictionaries

    Raises:
        Exception: If database query fails
    """
    # Build query with optional station filter
    query = """
        SELECT
            timestamp,
            station_id,
            temperature_f,
            humidity,
            wind_speed_mph,
            pressure_inhg
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
    """

    params = [start_date, end_date]

    # Add optional station filter
    if station_id:
        query += " AND station_id = ?"
        params.append(station_id)

    query += " ORDER BY timestamp DESC"

    # Execute query
    result = conn.execute(query, params).fetchall()

    # Convert to list of dicts
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

**Key points:**
- Use parameterized queries (ALWAYS!)
- Add comprehensive docstring
- Type hints for all parameters
- Return consistent data structure

---

### Step 4: Create Endpoint Handler

**Location:** `weather_app/api/weather.py`

```python
from fastapi import APIRouter, HTTPException, status, Response
from typing import Optional
import logging
import csv
from io import StringIO

from weather_app.models import WeatherExportRequest, WeatherExportResponse
from weather_app.database import get_weather_for_export, get_db

router = APIRouter(prefix="/api/weather", tags=["weather"])
logger = logging.getLogger(__name__)

@router.post("/export", response_model=WeatherExportResponse)
async def export_weather_data(
    request: WeatherExportRequest
) -> WeatherExportResponse:
    """
    Export weather data for a date range.

    Exports weather readings in CSV or JSON format for the specified
    date range. Optionally filter by station ID.

    **Request Body:**
    - start_date: Beginning of date range (ISO format)
    - end_date: End of date range (ISO format)
    - format: Export format ("csv" or "json")
    - station_id: Optional station filter

    **Returns:**
    - success: Whether export succeeded
    - record_count: Number of records exported
    - download_url: URL to download file (if applicable)
    - message: Status message

    **Errors:**
    - 400: Invalid date range or parameters
    - 404: No data found for specified range
    - 500: Internal server error

    **Example:**
    ```json
    {
        "start_date": "2026-01-01T00:00:00Z",
        "end_date": "2026-01-31T23:59:59Z",
        "format": "csv",
        "station_id": "STATION001"
    }
    ```
    """
    try:
        # Validate business logic
        range_days = (request.end_date - request.start_date).days
        if range_days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Date range cannot exceed 365 days"
            )

        # Query data
        db = get_db()
        data = await get_weather_for_export(
            conn=db,
            start_date=request.start_date,
            end_date=request.end_date,
            station_id=request.station_id
        )

        # Check if data exists
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No weather data found for range {request.start_date.date()} to {request.end_date.date()}"
            )

        # Format based on request
        if request.format == "csv":
            # Generate CSV (in production, might save to file/S3)
            csv_data = generate_csv(data)
            # Here you might save to storage and return URL
            download_url = None  # Or URL to file
        else:
            # JSON format
            download_url = None

        return WeatherExportResponse(
            success=True,
            record_count=len(data),
            download_url=download_url,
            message=f"Successfully exported {len(data)} records"
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Log unexpected errors
        logger.error(f"Error exporting weather data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export weather data"
        )

def generate_csv(data: List[Dict[str, Any]]) -> str:
    """Generate CSV string from data."""
    if not data:
        return ""

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

    return output.getvalue()
```

**Key points:**
- Comprehensive docstring with examples
- Input validation (business logic)
- Clear error messages with appropriate status codes
- Proper exception handling (re-raise pattern)
- Logging for debugging

---

### Step 5: Register Router

**Location:** `weather_app/api/main.py`

```python
from fastapi import FastAPI
from weather_app.api import weather

app = FastAPI(
    title="Weather API",
    description="Weather data collection and analysis API",
    version="1.0.0"
)

# Register routers
app.include_router(weather.router)
```

---

### Step 6: Write Tests

**Location:** `tests/test_weather_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_export_weather_success(client: TestClient, test_db_with_data):
    """Test successful weather data export."""
    response = client.post(
        "/api/weather/export",
        json={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "format": "csv"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["record_count"] > 0
    assert "exported" in data["message"].lower()

def test_export_weather_invalid_date_range(client: TestClient):
    """Test error when end_date before start_date."""
    response = client.post(
        "/api/weather/export",
        json={
            "start_date": "2026-01-31T00:00:00Z",
            "end_date": "2026-01-01T00:00:00Z",  # Before start
            "format": "csv"
        }
    )

    assert response.status_code == 422  # Validation error
    assert "end_date must be after start_date" in response.text

def test_export_weather_no_data(client: TestClient, empty_db):
    """Test 404 when no data exists."""
    response = client.post(
        "/api/weather/export",
        json={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "format": "csv"
        }
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_export_weather_excessive_range(client: TestClient):
    """Test error when date range too large."""
    start = datetime(2025, 1, 1)
    end = start + timedelta(days=400)  # > 365 days

    response = client.post(
        "/api/weather/export",
        json={
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "format": "csv"
        }
    )

    assert response.status_code == 400
    assert "exceed 365 days" in response.json()["detail"]

def test_export_weather_with_station_filter(client: TestClient, test_db_with_data):
    """Test export with station filter."""
    response = client.post(
        "/api/weather/export",
        json={
            "start_date": "2026-01-01T00:00:00Z",
            "end_date": "2026-01-31T23:59:59Z",
            "format": "csv",
            "station_id": "STATION001"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

**Key points:**
- Test success case
- Test validation errors (400, 422)
- Test not found (404)
- Test business logic constraints
- Test optional parameters

---

## Example Walkthrough

### Complete Example: Add "Get Weather Statistics" Endpoint

**Goal:** Create endpoint that returns min/max/avg temperature for a station.

#### 1. Plan

- **Purpose:** Get statistical summary for a station
- **Method:** GET (read-only)
- **Path:** `/api/weather/stats/{station_id}`
- **Query params:** `days` (number of days to analyze, default 7)
- **Response:** JSON with statistics
- **Errors:** 404 if station not found, 400 if days invalid

#### 2. Create Models

```python
# weather_app/models.py

class WeatherStatsResponse(BaseModel):
    """Weather statistics response."""
    station_id: str
    period_start: datetime
    period_end: datetime
    reading_count: int
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float

    class Config:
        schema_extra = {
            "example": {
                "station_id": "STATION001",
                "period_start": "2026-01-06T00:00:00Z",
                "period_end": "2026-01-13T23:59:59Z",
                "reading_count": 168,
                "avg_temperature": 72.5,
                "min_temperature": 45.2,
                "max_temperature": 95.8,
                "avg_humidity": 65.3
            }
        }
```

#### 3. Create Database Function

```python
# weather_app/database.py

async def get_station_statistics(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    days: int
) -> Optional[Dict[str, Any]]:
    """
    Calculate weather statistics for a station.

    Args:
        conn: Database connection
        station_id: Station identifier
        days: Number of days to analyze

    Returns:
        Dictionary with statistics, or None if no data
    """
    query = """
        SELECT
            ? as station_id,
            MIN(timestamp) as period_start,
            MAX(timestamp) as period_end,
            COUNT(*) as reading_count,
            AVG(temperature_f) as avg_temperature,
            MIN(temperature_f) as min_temperature,
            MAX(temperature_f) as max_temperature,
            AVG(humidity) as avg_humidity
        FROM weather_data
        WHERE station_id = ?
          AND timestamp >= NOW() - INTERVAL ? DAYS
    """

    result = conn.execute(query, [station_id, station_id, days]).fetchone()

    if not result or result[3] == 0:  # reading_count = 0
        return None

    columns = [desc[0] for desc in conn.description]
    return dict(zip(columns, result))
```

#### 4. Create Endpoint

```python
# weather_app/api/weather.py

@router.get("/stats/{station_id}", response_model=WeatherStatsResponse)
async def get_weather_statistics(
    station_id: str = Path(
        ...,
        description="Station identifier",
        regex="^[A-Za-z0-9_-]+$"
    ),
    days: int = Query(
        7,
        ge=1,
        le=365,
        description="Number of days to analyze"
    )
) -> WeatherStatsResponse:
    """
    Get weather statistics for a station.

    Calculates min/max/avg temperature and humidity for the
    specified number of days.

    **Path Parameters:**
    - station_id: Station identifier

    **Query Parameters:**
    - days: Number of days to analyze (1-365, default 7)

    **Returns:**
    Statistical summary including:
    - Reading count
    - Average/min/max temperature
    - Average humidity
    - Period dates

    **Errors:**
    - 400: Invalid station_id or days parameter
    - 404: Station not found or no data
    - 500: Internal server error
    """
    try:
        db = get_db()
        stats = await get_station_statistics(db, station_id, days)

        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for station '{station_id}' in last {days} days"
            )

        return WeatherStatsResponse(**stats)

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error calculating statistics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate statistics"
        )
```

#### 5. Write Tests

```python
# tests/test_weather_api.py

def test_get_weather_statistics_success(client, test_db_with_data):
    """Test successful statistics retrieval."""
    response = client.get("/api/weather/stats/STATION001?days=7")

    assert response.status_code == 200
    data = response.json()
    assert data["station_id"] == "STATION001"
    assert data["reading_count"] > 0
    assert "avg_temperature" in data

def test_get_weather_statistics_station_not_found(client, empty_db):
    """Test 404 for nonexistent station."""
    response = client.get("/api/weather/stats/NONEXISTENT")

    assert response.status_code == 404

def test_get_weather_statistics_invalid_days(client):
    """Test validation of days parameter."""
    response = client.get("/api/weather/stats/STATION001?days=1000")

    assert response.status_code == 422  # Validation error
```

#### 6. Test in Swagger UI

1. Start server: `python -m uvicorn weather_app.api.main:app --reload`
2. Navigate to: http://localhost:8000/docs
3. Find endpoint: `GET /api/weather/stats/{station_id}`
4. Click "Try it out"
5. Enter station_id: `STATION001`
6. Enter days: `7`
7. Click "Execute"
8. Verify response

---

## Common Patterns

### Pattern 1: Pagination

```python
from weather_app.models import PaginatedResponse

@router.get("/all", response_model=PaginatedResponse[WeatherResponse])
async def get_all_weather(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """Get paginated weather data."""
    offset = (page - 1) * page_size

    db = get_db()
    total = await db.count()
    items = await db.get_paginated(offset, page_size)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )
```

### Pattern 2: File Download

```python
from fastapi.responses import StreamingResponse

@router.get("/download/{station_id}")
async def download_station_data(station_id: str):
    """Download station data as CSV."""
    db = get_db()
    data = await db.get_all_by_station(station_id)

    async def generate():
        """Stream CSV data."""
        yield "timestamp,temperature,humidity\n"
        for row in data:
            yield f"{row['timestamp']},{row['temperature_f']},{row['humidity']}\n"

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=weather_{station_id}.csv"
        }
    )
```

### Pattern 3: Batch Operations

```python
@router.post("/batch", status_code=201)
async def batch_insert_readings(
    readings: List[WeatherReadingInput]
):
    """Insert multiple readings in batch."""
    # Validate batch size
    if len(readings) > 1000:
        raise HTTPException(400, "Maximum 1000 readings per batch")

    db = get_db()
    count = await db.batch_insert([r.dict() for r in readings])

    return {"success": True, "inserted": count}
```

---

## Troubleshooting

### Issue: "405 Method Not Allowed"

**Cause:** Wrong HTTP method or path doesn't match router

**Solution:**
1. Check decorator: `@router.get()` vs `@router.post()`
2. Verify path in router matches request
3. Check router is registered in main.py

### Issue: "422 Validation Error"

**Cause:** Request doesn't match Pydantic model

**Solution:**
1. Check Swagger UI for expected format
2. Verify field names match exactly
3. Check field types (str vs int, etc.)
4. Review validators in model

### Issue: "500 Internal Server Error"

**Cause:** Unhandled exception in endpoint

**Solution:**
1. Check server logs for stack trace
2. Verify database connection works
3. Add try/except around database calls
4. Check for None values being used

### Issue: Endpoint Not Appearing in Swagger

**Cause:** Router not registered or import error

**Solution:**
1. Verify `app.include_router(weather.router)` in main.py
2. Check for Python import errors
3. Restart server (uvicorn --reload)
4. Clear browser cache

---

## Checklist for PR

Before submitting PR for new endpoint:

- [ ] Models have type hints and validation
- [ ] Database function uses parameterized queries
- [ ] Endpoint has comprehensive docstring
- [ ] Error handling for all edge cases
- [ ] Unit tests for database function
- [ ] Integration tests for endpoint
- [ ] Tested manually in Swagger UI
- [ ] Updated API documentation
- [ ] Security review (if sensitive data)
- [ ] Performance considerations (pagination, limits)

---

**See also:**
- API-STANDARDS.md - Requirements and best practices
- api-patterns.md - Code examples and patterns
- TESTING.md - Testing strategies
- SECURITY.md - Security requirements

**Questions?** Check CLAUDE.md or ask before implementing.
