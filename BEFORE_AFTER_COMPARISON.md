# Before & After Comparison

## Entry Point: main.py

### BEFORE (Old - main.py)
```python
#!/usr/bin/env python3
"""
FastAPI Backend for Weather Application
Provides REST API endpoints for querying weather data from SQLite database
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import json
from config import DB_PATH, API_TITLE, ...

app = FastAPI(...)
app.add_middleware(CORSMiddleware, ...)

# Response models
class WeatherData(BaseModel):
    id: int
    dateutc: int
    # ... 20+ fields

class DatabaseStats(BaseModel):
    # ...

# Database helpers
def get_db_connection():
    # ...

def row_to_dict(row):
    # ...

# API Endpoints
@app.get("/")
def read_root():
    # ...

@app.get("/weather", response_model=List[WeatherData])
def get_weather_data(...):
    # 50+ lines of query logic
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... SQL building ...
    # ... error handling ...

@app.get("/weather/latest", response_model=WeatherData)
def get_latest_weather():
    # ...

@app.get("/weather/stats", response_model=DatabaseStats)
def get_database_stats():
    # ...

# Error handlers
@app.exception_handler(404)
async def not_found_handler(...):
    # ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```
**Total: 278 lines** - All logic in one file, hard to test/modify

---

### AFTER (New - main_refactored.py)
```python
#!/usr/bin/env python3
"""
Weather App Entry Point
Runs the FastAPI server using the refactored package structure
"""

import uvicorn
from weather_app.web.app import create_app
from weather_app.config import HOST, PORT

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host=HOST, port=PORT)
```
**Total: 11 lines** - Clean, delegated to modules

---

## Configuration

### BEFORE (config.py)
```python
import os

USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"

PRODUCTION_DB = "ambient_weather.db"
TEST_DB = "ambient_weather_test.db"
DB_PATH = TEST_DB if USE_TEST_DB else PRODUCTION_DB

API_TITLE = "Weather API"
API_DESCRIPTION = "API for querying Ambient Weather data"
API_VERSION = "1.0.0"

CORS_ORIGINS = ["*"]
HOST = "0.0.0.0"
PORT = 8000

def get_db_info():
    # ...
```

### AFTER (weather_app/config.py)
```python
import os
from pathlib import Path

# Base paths (better path handling)
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

# Database configuration
USE_TEST_DB = os.getenv("USE_TEST_DB", "false").lower() == "true"
PRODUCTION_DB = str(BASE_DIR / "ambient_weather.db")
TEST_DB = str(BASE_DIR / "ambient_weather_test.db")
DB_PATH = TEST_DB if USE_TEST_DB else PRODUCTION_DB

# API Configuration
API_TITLE = "Weather API"
API_DESCRIPTION = "API for querying Ambient Weather data"
API_VERSION = "1.0.0"

CORS_ORIGINS = ["*"]
HOST = os.getenv("BIND_HOST", "0.0.0.0")    # NEW: more flexible
PORT = int(os.getenv("BIND_PORT", 8000))    # NEW: more flexible

# NEW: Retention policy options (future-ready)
FULL_RESOLUTION_YEARS = 3
AGGREGATION_HOLD_YEARS = 50
PURGE_RAW_AFTER_AGGREGATION = True

# NEW: Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_db_info():
    # ... same as before ...
```
**Changes:**
- ✓ Better path handling (pathlib)
- ✓ Environment-variable driven host/port
- ✓ Future retention config options
- ✓ Logging configuration ready

---

## API Routes

### BEFORE (main.py - 50+ lines)
```python
@app.get("/weather", response_model=List[WeatherData])
def get_weather_data(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    order: str = Query(default="desc", regex="^(asc|desc)$")  # DEPRECATED!
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM weather_data WHERE 1=1"
        params = []
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                start_timestamp = int(start_dt.timestamp() * 1000)
                query += " AND dateutc >= ?"
                params.append(start_timestamp)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format...")
        
        # ... more query building ...
        
        query += f" ORDER BY dateutc {order.upper()}"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, ...)
    except Exception as e:
        raise HTTPException(status_code=500, ...)
```

### AFTER (weather_app/web/routes.py)
```python
@app.get("/weather", response_model=List[WeatherData])
def get_weather_data(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
    order: str = Query(default="desc", pattern="^(asc|desc)$")  # FIXED!
):
    try:
        return WeatherRepository.get_all_readings(  # Delegated to repository
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            order=order
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Changes:**
- ✓ Fixed deprecation: `regex=` → `pattern=`
- ✓ Query logic moved to repository layer
- ✓ Routes stay thin and focused
- ✓ Cleaner error handling

---

## Database Access

### BEFORE (main.py - Inline)
```python
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
```

### AFTER (weather_app/db/session.py - Proper module)
```python
class DatabaseConnection:
    @staticmethod
    def get_connection() -> sqlite3.Connection:
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection error: {str(e)}")
    
    @staticmethod
    def close_connection(conn: sqlite3.Connection) -> None:
        if conn:
            conn.close()

def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict]:
    return dict(row) if row else None
```

**Benefits:**
- ✓ Reusable from CLI, fetch, web layers
- ✓ Type hints for IDE support
- ✓ Static methods for clarity
- ✓ Proper separation

---

## Query Logic

### BEFORE (main.py - 50+ lines mixed with routes)
```python
# Inside get_weather_data() function - logic mixed with HTTP:
query = "SELECT * FROM weather_data WHERE 1=1"
params = []

if start_date:
    try:
        start_dt = datetime.fromisoformat(start_date)
        start_timestamp = int(start_dt.timestamp() * 1000)
        query += " AND dateutc >= ?"
        params.append(start_timestamp)
    except ValueError:
        raise HTTPException(...)  # HTTP error inside business logic!

# ... more build-ups ...

cursor.execute(query, params)
rows = cursor.fetchall()
conn.close()

return [dict(row) for row in rows]
```

### AFTER (weather_app/storage/repository.py - Pure business logic)
```python
class WeatherRepository:
    @staticmethod
    def get_all_readings(
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """Query weather data from the database"""
        try:
            conn = DatabaseConnection.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM weather_data WHERE 1=1"
            params = []
            
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date)
                    start_timestamp = int(start_dt.timestamp() * 1000)
                    query += " AND dateutc >= ?"
                    params.append(start_timestamp)
                except ValueError:
                    raise ValueError("Invalid start_date format. Use YYYY-MM-DD")  # Business error
            
            # ... rest of query building ...
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {str(e)}")
```

**Benefits:**
- ✓ Pure business logic (no HTTP concerns)
- ✓ Reusable by CLI, scheduled jobs, etc.
- ✓ Can be unit tested independently
- ✓ Proper separation of concerns
- ✓ Better error types (ValueError, RuntimeError, not HTTPException)

---

## File Size & Complexity

| Layer | Old | New | Change |
|-------|-----|-----|--------|
| **main.py** | 278 lines | 11 lines | -97% ↓ |
| **config.py** | 45 lines | 60 lines | +15 lines (features) |
| **Database** | Inline | session.py (25 lines) | Better structure |
| **Models** | In main.py | models.py (45 lines) | Clearer, reusable |
| **Routes** | In main.py | routes.py (85 lines) | Cleaner, delegated |
| **Storage** | Inline | repository.py (130 lines) | Pure business logic |
| **Total Lines** | 323 | 351 | +28 lines, **much better organized** |

---

## What Stayed the Same

✓ **Database behavior** - Same schema, same queries
✓ **API endpoints** - All 4 endpoints work identically
✓ **Response format** - Same JSON structure
✓ **Configuration** - Same env variables supported
✓ **CORS** - Same settings
✓ **Error handling** - Same error codes (400, 404, 500)

---

## What Improved

✓ **Code organization** - Clear separation of concerns
✓ **Testability** - Each module can be unit tested
✓ **Reusability** - Repository can be used by CLI, scheduler, etc.
✓ **Maintainability** - Changes are localized
✓ **Fixed deprecation** - `regex=` → `pattern=` ⚡
✓ **Better typing** - Type hints throughout
✓ **Configuration** - More flexible, environment-driven
✓ **Readability** - Each file has focused responsibility

---

## Summary

**Old approach:** Everything in one 278-line file
**New approach:** Organized modules with clear dependencies and single responsibilities

**Result:** Easier to maintain, test, extend, and reason about! 🎉
