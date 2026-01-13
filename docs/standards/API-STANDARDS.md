# API Standards & Patterns

**Framework:** FastAPI
**Purpose:** Detailed standards for building REST API endpoints
**Reference:** Load this doc when working on FastAPI routes
**Last Updated:** January 2026

---

## When to Use This Document

**Load before implementing:**
- New API endpoints
- Modifying existing endpoints
- Error handling changes
- Authentication/authorization features
- Request/response validation

**Referenced from:** CLAUDE.md → "Working on API endpoints"

---

## Table of Contents

1. [Endpoint Structure](#endpoint-structure)
2. [Type Safety & Validation](#type-safety--validation)
3. [Error Handling](#error-handling)
4. [Response Models](#response-models)
5. [Database Integration](#database-integration)
6. [Authentication](#authentication)
7. [Testing Requirements](#testing-requirements)
8. [Performance Patterns](#performance-patterns)

---

## Endpoint Structure

### Required Components

Every endpoint MUST have:
1. **Type hints** for all parameters and returns
2. **Pydantic response model** (unless returning primitive)
3. **Docstring** with description, args, returns, raises
4. **Error handling** (minimum: 404, 500)
5. **Integration test**

### Standard Pattern

```python
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
import logging

from weather_app.models import WeatherData, WeatherResponse
from weather_app.database import get_db

router = APIRouter(prefix="/api/weather", tags=["weather"])
logger = logging.getLogger(__name__)

@router.get("/range", response_model=List[WeatherResponse])
async def get_weather_range(
    start_date: datetime = Query(..., description="Start of date range"),
    end_date: datetime = Query(..., description="End of date range"),
    station_id: Optional[str] = Query(None, description="Optional station filter")
) -> List[WeatherResponse]:
    """
    Retrieve weather data for a date range.

    Args:
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        station_id: Optional station ID to filter results

    Returns:
        List of weather readings within the date range

    Raises:
        HTTPException:
            - 400 if date range is invalid
            - 404 if no data found
            - 500 if database error occurs
    """
    # Validate input
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be after start_date"
        )

    try:
        # Query database
        db = get_db()
        results = await db.query_range(start_date, end_date, station_id)

        # Handle empty results
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for range {start_date} to {end_date}"
            )

        # Transform and return
        return [WeatherResponse(**r) for r in results]

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Log and return 500 for unexpected errors
        logger.error(f"Error fetching weather range: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

## Type Safety & Validation

### Request Models (Pydantic)

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class WeatherQueryRequest(BaseModel):
    """Request model for weather queries."""

    start_date: datetime = Field(
        ...,
        description="Start of date range"
    )
    end_date: datetime = Field(
        ...,
        description="End of date range"
    )
    station_id: Optional[str] = Field(
        None,
        description="Station ID filter",
        min_length=1,
        max_length=50
    )
    limit: int = Field(
        100,
        ge=1,
        le=1000,
        description="Maximum results to return"
    )

    @validator('end_date')
    def end_date_after_start(cls, v, values):
        """Validate end_date is after start_date."""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('start_date', 'end_date')
    def no_future_dates(cls, v):
        """Validate dates are not in the future."""
        if v > datetime.now():
            raise ValueError('Future dates not allowed')
        return v

# Usage in endpoint
@router.post("/query")
async def query_weather(request: WeatherQueryRequest) -> List[WeatherResponse]:
    # Validation happens automatically
    # If validation fails, FastAPI returns 422 with details
    ...
```

### Query Parameters

```python
from fastapi import Query
from typing import Optional
from datetime import datetime

@router.get("/latest")
async def get_latest(
    # Required parameter
    station_id: str = Query(
        ...,
        description="Station ID",
        min_length=1,
        max_length=50
    ),

    # Optional with default
    limit: int = Query(
        10,
        ge=1,
        le=100,
        description="Number of results"
    ),

    # Optional nullable
    since: Optional[datetime] = Query(
        None,
        description="Only return data after this timestamp"
    )
) -> List[WeatherResponse]:
    ...
```

### Path Parameters

```python
from fastapi import Path

@router.get("/{station_id}/current")
async def get_current_weather(
    station_id: str = Path(
        ...,
        description="Station ID",
        min_length=1,
        max_length=50,
        regex="^[A-Za-z0-9_-]+$"  # Alphanumeric, underscore, hyphen only
    )
) -> WeatherResponse:
    ...
```

---

## Error Handling

### HTTP Status Codes

Use appropriate status codes:

| Code | When to Use | Example |
|------|-------------|---------|
| **200** | Successful GET/POST | Data retrieved successfully |
| **201** | Resource created | POST created new record |
| **204** | Success, no content | DELETE successful |
| **400** | Invalid request | Bad date range, invalid parameters |
| **401** | Not authenticated | Missing/invalid API key |
| **403** | Not authorized | User lacks permission |
| **404** | Not found | No data for query |
| **422** | Validation error | Pydantic validation failed |
| **500** | Server error | Database error, unexpected exception |
| **503** | Service unavailable | External API down |

### Error Response Format

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    """Standard error response format."""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# Usage
raise HTTPException(
    status_code=404,
    detail="Weather station not found"
)

# For custom error codes
raise HTTPException(
    status_code=400,
    detail=ErrorResponse(
        detail="Invalid date range",
        error_code="INVALID_DATE_RANGE"
    ).dict()
)
```

### Error Handling Pattern

```python
@router.get("/weather/{station_id}")
async def get_weather(station_id: str) -> WeatherResponse:
    try:
        # Business logic
        db = get_db()
        result = await db.get_by_station(station_id)

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for station {station_id}"
            )

        return WeatherResponse(**result)

    except HTTPException:
        # Re-raise HTTP exceptions (already formatted)
        raise

    except ValueError as e:
        # Handle known business logic errors
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
```

---

## Response Models

### Single Resource

```python
from pydantic import BaseModel, Field
from datetime import datetime

class WeatherResponse(BaseModel):
    """Single weather reading response."""

    timestamp: datetime
    station_id: str
    temperature_f: float = Field(..., ge=-100, le=150)
    humidity: int = Field(..., ge=0, le=100)
    pressure_inhg: float
    wind_speed_mph: float = Field(..., ge=0)
    wind_direction: Optional[int] = Field(None, ge=0, le=360)

    class Config:
        # Generate example for OpenAPI docs
        schema_extra = {
            "example": {
                "timestamp": "2026-01-13T12:00:00Z",
                "station_id": "STATION001",
                "temperature_f": 72.5,
                "humidity": 45,
                "pressure_inhg": 30.12,
                "wind_speed_mph": 5.2,
                "wind_direction": 180
            }
        }
```

### List Response with Metadata

```python
from typing import List, Generic, TypeVar
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

# Usage
@router.get("/weather/all", response_model=PaginatedResponse[WeatherResponse])
async def get_all_weather(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
) -> PaginatedResponse[WeatherResponse]:
    db = get_db()

    offset = (page - 1) * page_size
    items = await db.query_paginated(offset, page_size)
    total = await db.count()

    return PaginatedResponse(
        items=[WeatherResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=offset + page_size < total,
        has_prev=page > 1
    )
```

### Minimal Response

```python
class StatusResponse(BaseModel):
    """Simple status response."""
    success: bool
    message: str

@router.delete("/weather/{id}")
async def delete_weather(id: int) -> StatusResponse:
    db = get_db()
    deleted = await db.delete(id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")

    return StatusResponse(
        success=True,
        message=f"Deleted weather record {id}"
    )
```

---

## Database Integration

### Async Database Access

```python
from contextlib import asynccontextmanager
from typing import List, Optional
import duckdb

class WeatherDB:
    """Database access layer."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    @asynccontextmanager
    async def get_connection(self):
        """Context manager for database connections."""
        conn = duckdb.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    async def query_range(
        self,
        start: datetime,
        end: datetime,
        station_id: Optional[str] = None
    ) -> List[dict]:
        """Query weather data with parameterized SQL."""
        async with self.get_connection() as conn:
            query = """
                SELECT *
                FROM weather_data
                WHERE timestamp BETWEEN ? AND ?
                AND (? IS NULL OR station_id = ?)
                ORDER BY timestamp DESC
            """
            result = conn.execute(
                query,
                [start, end, station_id, station_id]
            ).fetchall()

            # Convert to dict
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]

# Usage in endpoint
db = WeatherDB("weather.db")

@router.get("/range")
async def get_range(start: datetime, end: datetime) -> List[WeatherResponse]:
    results = await db.query_range(start, end)
    return [WeatherResponse(**r) for r in results]
```

### Transaction Handling

```python
async def create_weather_batch(
    readings: List[WeatherReading]
) -> StatusResponse:
    """Insert multiple readings in a transaction."""
    async with db.get_connection() as conn:
        try:
            conn.execute("BEGIN TRANSACTION")

            for reading in readings:
                conn.execute(
                    "INSERT INTO weather_data VALUES (?, ?, ?, ?)",
                    (reading.timestamp, reading.station_id,
                     reading.temperature_f, reading.humidity)
                )

            conn.execute("COMMIT")
            return StatusResponse(
                success=True,
                message=f"Inserted {len(readings)} readings"
            )

        except Exception as e:
            conn.execute("ROLLBACK")
            logger.error(f"Transaction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to insert readings"
            )
```

---

## Authentication

### API Key Authentication

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from typing import Optional

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Verify API key from header."""
    # In production, check against database
    valid_keys = ["your-secret-key-here"]

    if api_key not in valid_keys:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return api_key

# Protected endpoint
@router.get("/protected")
async def protected_route(
    api_key: str = Security(verify_api_key)
) -> dict:
    return {"message": "Access granted"}
```

### Optional Authentication

```python
from typing import Optional

async def get_optional_api_key(
    api_key: Optional[str] = Security(APIKeyHeader(name="X-API-Key", auto_error=False))
) -> Optional[str]:
    """Get API key if provided, None otherwise."""
    if api_key and api_key in valid_keys:
        return api_key
    return None

@router.get("/weather/latest")
async def get_latest(
    api_key: Optional[str] = Security(get_optional_api_key)
) -> List[WeatherResponse]:
    # Different behavior based on authentication
    limit = 100 if api_key else 10
    ...
```

---

## Testing Requirements

### Integration Test Pattern

```python
from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta

def test_get_weather_range_success(client: TestClient, test_db):
    """Test successful weather range query."""
    # Arrange
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()

    # Act
    response = client.get(
        "/api/weather/range",
        params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "timestamp" in data[0]
    assert "temperature_f" in data[0]

def test_get_weather_range_invalid_dates(client: TestClient):
    """Test error handling for invalid date range."""
    start = datetime.now()
    end = datetime.now() - timedelta(days=7)  # End before start

    response = client.get(
        "/api/weather/range",
        params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
    )

    assert response.status_code == 400
    assert "end_date must be after start_date" in response.json()["detail"]

def test_get_weather_range_no_data(client: TestClient, empty_db):
    """Test 404 when no data exists."""
    start = datetime.now() - timedelta(days=7)
    end = datetime.now()

    response = client.get(
        "/api/weather/range",
        params={
            "start_date": start.isoformat(),
            "end_date": end.isoformat()
        }
    )

    assert response.status_code == 404
```

### Test Fixtures

```python
import pytest
from fastapi.testclient import TestClient
from weather_app.api.main import app
from weather_app.database import WeatherDB

@pytest.fixture
def client():
    """Test client for API."""
    return TestClient(app)

@pytest.fixture
def test_db(tmp_path):
    """Temporary test database."""
    db_path = tmp_path / "test.db"
    db = WeatherDB(str(db_path))
    db.initialize()

    # Seed with test data
    db.insert_sample_data()

    yield db

    # Cleanup
    db_path.unlink(missing_ok=True)

@pytest.fixture
def empty_db(tmp_path):
    """Empty database for testing edge cases."""
    db_path = tmp_path / "empty.db"
    db = WeatherDB(str(db_path))
    db.initialize()
    yield db
    db_path.unlink(missing_ok=True)
```

---

## Performance Patterns

### Response Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache expensive computations
@lru_cache(maxsize=100)
def calculate_statistics(station_id: str, date: str) -> dict:
    """Calculate and cache daily statistics."""
    # Expensive calculation here
    return {
        "avg_temp": 72.5,
        "max_temp": 85.3,
        "min_temp": 59.7
    }

@router.get("/stats/{station_id}/{date}")
async def get_daily_stats(
    station_id: str,
    date: str
) -> dict:
    return calculate_statistics(station_id, date)
```

### Pagination

```python
from fastapi import Query

@router.get("/weather/all")
async def get_all_weather(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> PaginatedResponse[WeatherResponse]:
    """Paginated weather data."""
    db = get_db()

    # Query with limit and offset
    items = await db.query_paginated(offset, limit)
    total = await db.count()

    return PaginatedResponse(
        items=[WeatherResponse(**item) for item in items],
        total=total,
        offset=offset,
        limit=limit
    )
```

### Async Operations

```python
import asyncio
from typing import List

@router.get("/stations/status")
async def get_all_station_status() -> List[StationStatus]:
    """Fetch status for all stations in parallel."""
    station_ids = ["STATION001", "STATION002", "STATION003"]

    # Fetch all stations concurrently
    tasks = [fetch_station_status(sid) for sid in station_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle errors gracefully
    statuses = []
    for sid, result in zip(station_ids, results):
        if isinstance(result, Exception):
            logger.error(f"Failed to fetch {sid}: {result}")
            statuses.append(StationStatus(id=sid, status="error"))
        else:
            statuses.append(result)

    return statuses
```

---

## OpenAPI Documentation

### Automatic Documentation

FastAPI generates OpenAPI docs automatically at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Enhancing Documentation

```python
from fastapi import FastAPI

app = FastAPI(
    title="Weather API",
    description="Real-time weather data API",
    version="1.0.0",
    contact={
        "name": "Weather App Team",
        "email": "support@weatherapp.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

@router.get(
    "/weather/latest",
    summary="Get latest weather reading",
    description="Retrieves the most recent weather reading from the specified station",
    response_description="Latest weather data",
    responses={
        200: {"description": "Success"},
        404: {"description": "Station not found"},
        500: {"description": "Server error"}
    }
)
async def get_latest_weather(station_id: str) -> WeatherResponse:
    ...
```

---

## Checklist for New Endpoints

Before submitting PR:

- [ ] Type hints for all parameters and returns
- [ ] Pydantic response model defined
- [ ] Docstring with description, args, returns, raises
- [ ] Error handling (minimum: 400, 404, 500)
- [ ] Input validation (Pydantic or Query validators)
- [ ] Database queries use parameterized SQL
- [ ] Integration test written
- [ ] Manual testing in Swagger UI
- [ ] OpenAPI docs generated correctly
- [ ] Logging for errors
- [ ] Follows naming conventions

---

**See also:**
- docs/examples/api-patterns.md - Real examples from this project
- docs/standards/TESTING.md - Testing strategies
- docs/standards/SECURITY.md - Security requirements

**Questions?** Refer to CLAUDE.md or ask before implementing.
