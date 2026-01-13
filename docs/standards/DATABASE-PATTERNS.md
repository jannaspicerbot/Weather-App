# Database Patterns & Best Practices

**Database:** DuckDB 0.10+
**Purpose:** Query patterns, schema design, and optimization
**Reference:** Load this doc when working with database queries
**Last Updated:** January 2026

---

## When to Use This Document

**Load before:**
- Writing new database queries
- Modifying schema
- Performance optimization
- Data migration tasks
- Adding indexes

**Referenced from:** CLAUDE.md → "Working on database queries"

---

## Table of Contents

1. [Connection Management](#connection-management)
2. [Query Patterns](#query-patterns)
3. [Schema Design](#schema-design)
4. [Performance Optimization](#performance-optimization)
5. [Data Validation](#data-validation)
6. [Migration Patterns](#migration-patterns)

---

## Connection Management

### Context Manager Pattern

```python
import duckdb
from contextlib import contextmanager
from typing import Generator

class WeatherDB:
    """Database access layer with connection pooling."""

    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """
        Context manager for database connections.

        Usage:
            with db.get_connection() as conn:
                result = conn.execute("SELECT * FROM weather").fetchall()
        """
        conn = duckdb.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
```

### Async Wrapper

```python
import asyncio
from typing import List, Dict, Any

async def execute_query(
    db_path: str,
    query: str,
    params: List[Any] = None
) -> List[Dict[str, Any]]:
    """
    Execute query asynchronously (using thread pool).

    DuckDB doesn't have native async, but we can use
    asyncio.to_thread for non-blocking operations.
    """
    def _execute():
        conn = duckdb.connect(db_path)
        try:
            if params:
                result = conn.execute(query, params).fetchall()
            else:
                result = conn.execute(query).fetchall()

            # Convert to dict
            columns = [desc[0] for desc in conn.description]
            return [dict(zip(columns, row)) for row in result]
        finally:
            conn.close()

    return await asyncio.to_thread(_execute)
```

---

## Query Patterns

### Parameterized Queries (REQUIRED)

```python
# ✅ CORRECT - Parameterized query (prevents SQL injection)
def get_weather_by_station(
    conn: duckdb.DuckDBPyConnection,
    station_id: str
) -> List[Dict[str, Any]]:
    query = """
        SELECT timestamp, temperature_f, humidity
        FROM weather_data
        WHERE station_id = ?
        ORDER BY timestamp DESC
        LIMIT 100
    """
    result = conn.execute(query, [station_id]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]

# ❌ WRONG - String formatting (SQL injection risk!)
def get_weather_bad(conn, station_id):
    query = f"SELECT * FROM weather_data WHERE station_id = '{station_id}'"
    return conn.execute(query).fetchall()
```

### Date Range Queries

```python
from datetime import datetime, timedelta
from typing import Optional

def get_weather_range(
    conn: duckdb.DuckDBPyConnection,
    start_date: datetime,
    end_date: datetime,
    station_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query weather data within date range."""
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
        AND (? IS NULL OR station_id = ?)
        ORDER BY timestamp DESC
    """

    result = conn.execute(
        query,
        [start_date, end_date, station_id, station_id]
    ).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Aggregation Queries

```python
def get_daily_statistics(
    conn: duckdb.DuckDBPyConnection,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Calculate daily temperature statistics."""
    query = """
        SELECT
            DATE_TRUNC('day', timestamp) as day,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            STDDEV(temperature_f) as stddev_temp,
            COUNT(*) as reading_count
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
        GROUP BY day
        ORDER BY day
    """

    result = conn.execute(query, [start_date, end_date]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Pagination

```python
def get_paginated_weather(
    conn: duckdb.DuckDBPyConnection,
    offset: int = 0,
    limit: int = 50
) -> tuple[List[Dict[str, Any]], int]:
    """
    Get paginated weather data with total count.

    Returns:
        (data, total_count) tuple
    """
    # Get total count
    count_query = "SELECT COUNT(*) FROM weather_data"
    total = conn.execute(count_query).fetchone()[0]

    # Get paginated data
    data_query = """
        SELECT *
        FROM weather_data
        ORDER BY timestamp DESC
        LIMIT ? OFFSET ?
    """
    result = conn.execute(data_query, [limit, offset]).fetchall()

    columns = [desc[0] for desc in conn.description]
    data = [dict(zip(columns, row)) for row in result]

    return data, total
```

### Window Functions

```python
def get_temperature_trends(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    days: int = 7
) -> List[Dict[str, Any]]:
    """Calculate moving average temperature."""
    query = """
        SELECT
            timestamp,
            temperature_f,
            AVG(temperature_f) OVER (
                ORDER BY timestamp
                ROWS BETWEEN 23 PRECEDING AND CURRENT ROW
            ) as temp_24h_avg,
            temperature_f - LAG(temperature_f, 1) OVER (
                ORDER BY timestamp
            ) as temp_change
        FROM weather_data
        WHERE station_id = ?
        AND timestamp >= NOW() - INTERVAL ? DAYS
        ORDER BY timestamp DESC
    """

    result = conn.execute(query, [station_id, days]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

---

## Schema Design

### Primary Table

```sql
CREATE TABLE IF NOT EXISTS weather_data (
    -- Primary key
    id INTEGER PRIMARY KEY,

    -- Timestamp (stored as TIMESTAMP, DuckDB handles timezones)
    timestamp TIMESTAMP NOT NULL,

    -- Station identifier
    station_id VARCHAR NOT NULL,

    -- Weather measurements (use appropriate numeric types)
    temperature_f DOUBLE,
    feels_like_f DOUBLE,
    humidity INTEGER CHECK (humidity BETWEEN 0 AND 100),
    dew_point_f DOUBLE,
    wind_speed_mph DOUBLE CHECK (wind_speed_mph >= 0),
    wind_gust_mph DOUBLE CHECK (wind_gust_mph >= 0),
    wind_direction INTEGER CHECK (wind_direction BETWEEN 0 AND 360),
    pressure_inhg DOUBLE,
    precipitation_in DOUBLE CHECK (precipitation_in >= 0),

    -- Solar measurements
    solar_radiation DOUBLE,
    uv_index INTEGER CHECK (uv_index BETWEEN 0 AND 15),

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(timestamp, station_id)
);
```

### Indexes for Performance

```python
def create_indexes(conn: duckdb.DuckDBPyConnection):
    """Create indexes for common query patterns."""

    # Index on timestamp for date range queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_timestamp
        ON weather_data(timestamp DESC)
    """)

    # Index on station_id for filtering
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station
        ON weather_data(station_id)
    """)

    # Composite index for common query pattern
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station_timestamp
        ON weather_data(station_id, timestamp DESC)
    """)
```

### Data Validation

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class WeatherReading(BaseModel):
    """Validated weather reading model."""

    timestamp: datetime
    station_id: str = Field(..., min_length=1, max_length=50)

    temperature_f: Optional[float] = Field(None, ge=-100, le=150)
    humidity: Optional[int] = Field(None, ge=0, le=100)
    wind_speed_mph: Optional[float] = Field(None, ge=0, le=200)
    wind_direction: Optional[int] = Field(None, ge=0, le=360)
    pressure_inhg: Optional[float] = Field(None, ge=20, le=35)

    @validator('timestamp')
    def timestamp_not_future(cls, v):
        if v > datetime.now():
            raise ValueError('Timestamp cannot be in the future')
        return v

    class Config:
        # Allow datetime to be parsed from string
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

def insert_weather_reading(
    conn: duckdb.DuckDBPyConnection,
    reading: WeatherReading
) -> int:
    """Insert validated weather reading."""
    query = """
        INSERT INTO weather_data (
            timestamp, station_id, temperature_f,
            humidity, wind_speed_mph, wind_direction, pressure_inhg
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        RETURNING id
    """

    result = conn.execute(query, [
        reading.timestamp,
        reading.station_id,
        reading.temperature_f,
        reading.humidity,
        reading.wind_speed_mph,
        reading.wind_direction,
        reading.pressure_inhg
    ]).fetchone()

    return result[0]
```

---

## Performance Optimization

### Columnar Storage Benefits

DuckDB's columnar storage is optimized for analytical queries:

```python
# ✅ GOOD - Query only needed columns
def get_temperature_only(conn):
    query = """
        SELECT timestamp, temperature_f
        FROM weather_data
        WHERE timestamp >= NOW() - INTERVAL 7 DAYS
    """
    return conn.execute(query).fetchall()

# ❌ WASTEFUL - Reads all columns
def get_temperature_bad(conn):
    query = "SELECT * FROM weather_data"  # Reads all 15+ columns
    return [(r[0], r[2]) for r in conn.execute(query).fetchall()]
```

### Batch Inserts

```python
def batch_insert_weather(
    conn: duckdb.DuckDBPyConnection,
    readings: List[WeatherReading]
) -> int:
    """Insert multiple readings efficiently."""

    # Prepare data as list of tuples
    data = [
        (
            r.timestamp,
            r.station_id,
            r.temperature_f,
            r.humidity,
            r.wind_speed_mph,
            r.wind_direction,
            r.pressure_inhg
        )
        for r in readings
    ]

    # Use executemany for batch insert
    query = """
        INSERT INTO weather_data (
            timestamp, station_id, temperature_f,
            humidity, wind_speed_mph, wind_direction, pressure_inhg
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    conn.executemany(query, data)
    return len(data)
```

### Query Analysis

```python
def analyze_query_performance(
    conn: duckdb.DuckDBPyConnection,
    query: str
):
    """Analyze query execution plan."""

    # Get query plan
    explain_query = f"EXPLAIN ANALYZE {query}"
    plan = conn.execute(explain_query).fetchall()

    print("Query Execution Plan:")
    for row in plan:
        print(row[0])
```

### Materialized Views (Precomputation)

```python
def create_daily_summary_table(conn: duckdb.DuckDBPyConnection):
    """Create precomputed daily summaries."""

    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_weather_summary AS
        SELECT
            DATE_TRUNC('day', timestamp) as date,
            station_id,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed_mph) as avg_wind_speed,
            COUNT(*) as reading_count
        FROM weather_data
        GROUP BY date, station_id
    """)

    # Create index on summary table
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_summary_date
        ON daily_weather_summary(date DESC)
    """)

def refresh_daily_summary(conn: duckdb.DuckDBPyConnection, date: datetime):
    """Refresh summary for a specific date."""

    # Delete existing
    conn.execute(
        "DELETE FROM daily_weather_summary WHERE date = ?",
        [date.date()]
    )

    # Recompute
    conn.execute("""
        INSERT INTO daily_weather_summary
        SELECT
            DATE_TRUNC('day', timestamp) as date,
            station_id,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed_mph) as avg_wind_speed,
            COUNT(*) as reading_count
        FROM weather_data
        WHERE DATE_TRUNC('day', timestamp) = ?
        GROUP BY date, station_id
    """, [date.date()])
```

---

## Migration Patterns

### Schema Versioning

```python
def get_schema_version(conn: duckdb.DuckDBPyConnection) -> int:
    """Get current schema version."""
    try:
        result = conn.execute(
            "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else 0
    except:
        # Table doesn't exist, version 0
        return 0

def apply_migrations(conn: duckdb.DuckDBPyConnection):
    """Apply pending database migrations."""

    current_version = get_schema_version(conn)

    migrations = [
        (1, create_weather_table),
        (2, add_station_table),
        (3, add_indexes),
        (4, add_daily_summary_table),
    ]

    for version, migration_func in migrations:
        if version > current_version:
            print(f"Applying migration {version}...")
            migration_func(conn)

            # Record migration
            conn.execute("""
                INSERT INTO schema_version (version, applied_at)
                VALUES (?, CURRENT_TIMESTAMP)
            """, [version])

            print(f"Migration {version} complete")

def create_weather_table(conn: duckdb.DuckDBPyConnection):
    """Migration 1: Create weather_data table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            station_id VARCHAR NOT NULL,
            temperature_f DOUBLE,
            humidity INTEGER,
            -- ... other columns
            UNIQUE(timestamp, station_id)
        )
    """)
```

---

## Error Handling

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def safe_query(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    params: Optional[List] = None
) -> Optional[List[Dict[str, Any]]]:
    """Execute query with error handling."""
    try:
        if params:
            result = conn.execute(query, params).fetchall()
        else:
            result = conn.execute(query).fetchall()

        columns = [desc[0] for desc in conn.description]
        return [dict(zip(columns, row)) for row in result]

    except duckdb.Error as e:
        logger.error(f"Database error: {e}")
        logger.error(f"Query: {query}")
        logger.error(f"Params: {params}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return None
```

---

## Testing Patterns

```python
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def test_db():
    """Create temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name

    conn = duckdb.connect(db_path)

    # Create schema
    conn.execute("""
        CREATE TABLE weather_data (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            station_id VARCHAR NOT NULL,
            temperature_f DOUBLE
        )
    """)

    # Seed test data
    conn.execute("""
        INSERT INTO weather_data VALUES
        (1, '2026-01-13 12:00:00', 'STATION001', 72.5),
        (2, '2026-01-13 13:00:00', 'STATION001', 73.2),
        (3, '2026-01-13 14:00:00', 'STATION001', 74.1)
    """)

    yield conn

    # Cleanup
    conn.close()
    Path(db_path).unlink(missing_ok=True)

def test_query_by_station(test_db):
    """Test querying by station ID."""
    result = test_db.execute("""
        SELECT * FROM weather_data WHERE station_id = ?
    """, ['STATION001']).fetchall()

    assert len(result) == 3
    assert result[0][3] == 72.5  # temperature_f
```

---

## Checklist for Database Changes

- [ ] Use parameterized queries (ALWAYS)
- [ ] Add appropriate indexes
- [ ] Include error handling
- [ ] Validate input with Pydantic
- [ ] Test with sample data
- [ ] Check query performance with EXPLAIN
- [ ] Document any new schema changes
- [ ] Create migration if changing schema
- [ ] Close connections properly

---

**See also:**
- docs/examples/query-patterns.md - Real query examples
- docs/standards/API-STANDARDS.md - API integration
- docs/architecture/decisions/002-duckdb-migration.md - Why DuckDB

**Questions?** Refer to CLAUDE.md or ask before implementing.
