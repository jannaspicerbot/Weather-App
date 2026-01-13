# Performance Optimization Guide

**Weather App Performance Standards**
**When to load:** Performance optimization tasks, slow queries, UI lag
**Reference:** Load when working on speed, efficiency, or scalability

---

## Table of Contents

1. [Performance Philosophy](#performance-philosophy)
2. [Backend Performance](#backend-performance)
3. [Frontend Performance](#frontend-performance)
4. [Database Performance](#database-performance)
5. [API Performance](#api-performance)
6. [Monitoring & Profiling](#monitoring--profiling)
7. [Common Performance Issues](#common-performance-issues)

---

## Performance Philosophy

### Guiding Principles

**1. Measure First, Optimize Second**
- Never optimize without profiling
- Use real data to identify bottlenecks
- Set performance budgets and track them
- Don't sacrifice readability for micro-optimizations

**2. Performance Budgets**
```
API Response Times:
- Simple GET: < 100ms (p95)
- Complex query: < 500ms (p95)
- Aggregation: < 1s (p95)

Frontend:
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Bundle size: < 200kb (gzipped)

Database:
- Simple query: < 10ms
- Aggregation: < 100ms
- Full table scan: Avoid entirely
```

**3. Optimization Priority**
1. Correctness (always first)
2. Security (never compromise)
3. Maintainability (readable code)
4. Performance (optimize when needed)

---

## Backend Performance

### FastAPI Best Practices

#### 1. Async Operations

```python
from fastapi import FastAPI
import asyncio

# ✅ DO: Use async for I/O-bound operations
@app.get("/weather/latest")
async def get_latest_weather():
    """Async allows handling multiple requests concurrently."""
    async with get_async_db() as db:
        result = await db.get_latest()
        return result

# ❌ DON'T: Use sync for I/O operations (blocks event loop)
@app.get("/weather/latest")
def get_latest_weather_sync():
    """Blocks entire process during I/O."""
    db = get_db()
    result = db.get_latest()
    return result
```

#### 2. Response Models & Serialization

```python
from pydantic import BaseModel
from typing import List

class WeatherMinimal(BaseModel):
    """Lightweight response for list endpoints."""
    timestamp: datetime
    temperature_f: float
    station_id: str

    class Config:
        orm_mode = True

class WeatherFull(BaseModel):
    """Complete response for detail endpoints."""
    timestamp: datetime
    temperature_f: float
    humidity: int
    wind_speed_mph: Optional[float]
    pressure_inhg: Optional[float]
    station_id: str
    # ... all fields

# ✅ DO: Use minimal models for list endpoints
@app.get("/weather/all", response_model=List[WeatherMinimal])
async def get_all_weather():
    """Returns only essential fields, faster serialization."""
    results = await db.get_all()
    return results

# ❌ DON'T: Return full objects in lists (wasteful)
@app.get("/weather/all", response_model=List[WeatherFull])
async def get_all_weather_heavy():
    """Serializes many unnecessary fields."""
    results = await db.get_all()
    return results
```

#### 3. Lazy Loading & Pagination

```python
from fastapi import Query

# ✅ DO: Always paginate large datasets
@app.get("/weather/history")
async def get_weather_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """Load data in chunks, not all at once."""
    offset = (page - 1) * page_size
    results = await db.get_paginated(offset, page_size)
    total = await db.count()

    return {
        "items": results,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size
    }

# ❌ DON'T: Load entire dataset
@app.get("/weather/history")
async def get_all_history():
    """Could return millions of records, OOM risk."""
    return await db.get_all()  # Memory explosion!
```

#### 4. Caching Strategy

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

# In-memory cache for expensive computations
@lru_cache(maxsize=128)
def calculate_statistics(station_id: str) -> dict:
    """Cache computed statistics."""
    # Expensive calculation
    return stats

# Redis cache for API responses
@app.get("/weather/stats/{station_id}")
@cache(expire=300)  # 5 minutes
async def get_station_stats(station_id: str):
    """Cache API responses in Redis."""
    stats = calculate_statistics(station_id)
    return stats

# Manual cache invalidation
@app.post("/weather/batch")
async def insert_batch(readings: List[WeatherReading]):
    """Invalidate cache after data changes."""
    await db.batch_insert(readings)

    # Clear relevant caches
    calculate_statistics.cache_clear()
    await FastAPICache.clear(namespace="weather")

    return {"success": True}
```

#### 5. Connection Pooling

```python
import duckdb
from contextlib import asynccontextmanager

# ✅ DO: Use connection pooling
class DatabasePool:
    def __init__(self, db_path: str, pool_size: int = 10):
        self.db_path = db_path
        self.pool = []
        self.pool_size = pool_size

    def get_connection(self):
        """Reuse existing connections."""
        if self.pool:
            return self.pool.pop()
        return duckdb.connect(self.db_path)

    def return_connection(self, conn):
        """Return connection to pool."""
        if len(self.pool) < self.pool_size:
            self.pool.append(conn)
        else:
            conn.close()

@asynccontextmanager
async def get_db():
    """Get pooled connection."""
    conn = db_pool.get_connection()
    try:
        yield conn
    finally:
        db_pool.return_connection(conn)

# ❌ DON'T: Create new connection every request
async def get_db_bad():
    """Opens new connection, wasteful."""
    conn = duckdb.connect("weather.db")
    return conn
```

---

## Frontend Performance

### React Optimization

#### 1. Component Memoization

```typescript
import React, { memo, useMemo, useCallback } from 'react';

// ✅ DO: Memoize expensive components
const WeatherCard = memo(({ data }: WeatherCardProps) => {
  return (
    <div className="weather-card">
      <h3>{data.station_id}</h3>
      <p>{data.temperature_f}°F</p>
    </div>
  );
});

// Only re-render if data actually changes
WeatherCard.displayName = 'WeatherCard';
```

#### 2. useMemo for Expensive Calculations

```typescript
function WeatherChart({ data }: { data: WeatherReading[] }) {
  // ✅ DO: Memoize expensive transformations
  const chartData = useMemo(() => {
    // Expensive transformation
    return data.map(reading => ({
      x: new Date(reading.timestamp),
      y: reading.temperature_f
    })).sort((a, b) => a.x.getTime() - b.x.getTime());
  }, [data]);

  // ❌ DON'T: Transform on every render
  // const chartData = data.map(...) // Runs every render!

  return <LineChart data={chartData} />;
}
```

#### 3. useCallback for Stable Functions

```typescript
function WeatherTable({ data }: { data: WeatherReading[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // ✅ DO: Memoize callbacks passed to children
  const handleRowClick = useCallback((reading: WeatherReading) => {
    setSelectedId(reading.station_id);
  }, []); // Stable reference

  return (
    <table>
      {data.map(reading => (
        <WeatherRow
          key={reading.station_id}
          data={reading}
          onClick={handleRowClick} // Stable, won't cause re-renders
        />
      ))}
    </table>
  );
}
```

#### 4. Lazy Loading & Code Splitting

```typescript
import { lazy, Suspense } from 'react';

// ✅ DO: Lazy load large components
const WeatherChart = lazy(() => import('./WeatherChart'));
const WeatherMap = lazy(() => import('./WeatherMap'));

function Dashboard() {
  return (
    <div>
      <Suspense fallback={<LoadingSpinner />}>
        <WeatherChart />
      </Suspense>

      <Suspense fallback={<LoadingSpinner />}>
        <WeatherMap />
      </Suspense>
    </div>
  );
}

// ❌ DON'T: Import everything upfront
// import WeatherChart from './WeatherChart'; // Large bundle
```

#### 5. Virtual Scrolling for Large Lists

```typescript
import { FixedSizeList } from 'react-window';

// ✅ DO: Virtualize long lists
function WeatherList({ data }: { data: WeatherReading[] }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      <WeatherCard data={data[index]} />
    </div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={data.length}
      itemSize={100}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}

// ❌ DON'T: Render 10,000 items
// {data.map(item => <WeatherCard key={item.id} data={item} />)}
```

#### 6. Debouncing & Throttling

```typescript
import { useMemo } from 'react';
import debounce from 'lodash/debounce';

function SearchInput() {
  // ✅ DO: Debounce expensive operations
  const debouncedSearch = useMemo(
    () => debounce(async (query: string) => {
      const results = await fetch(`/api/search?q=${query}`);
      // Update results
    }, 300),
    []
  );

  return (
    <input
      type="text"
      onChange={(e) => debouncedSearch(e.target.value)}
      placeholder="Search stations..."
    />
  );
}

// ❌ DON'T: Make API call on every keystroke
// onChange={(e) => fetchResults(e.target.value)}
```

---

## Database Performance

### DuckDB Optimization

#### 1. Proper Indexing

```python
def create_optimized_indexes(conn):
    """Create indexes for common query patterns."""

    # ✅ DO: Index frequently filtered columns
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_timestamp
        ON weather_data(timestamp DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station
        ON weather_data(station_id)
    """)

    # Composite index for common filter combination
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station_time
        ON weather_data(station_id, timestamp DESC)
    """)

    # ❌ DON'T: Index every column (overhead)
    # conn.execute("CREATE INDEX idx_humidity ON weather_data(humidity)")
```

#### 2. Query Optimization

```python
# ✅ DO: Select only needed columns (columnar benefit)
def get_temperature_data(conn, station_id: str):
    """DuckDB reads only temperature_f column."""
    query = """
        SELECT timestamp, temperature_f
        FROM weather_data
        WHERE station_id = ?
    """
    return conn.execute(query, [station_id]).fetchall()

# ❌ DON'T: SELECT * (reads all columns)
def get_temperature_data_bad(conn, station_id: str):
    """Reads unnecessary data."""
    query = "SELECT * FROM weather_data WHERE station_id = ?"
    return conn.execute(query, [station_id]).fetchall()
```

#### 3. Batch Operations

```python
# ✅ DO: Batch inserts
def batch_insert(conn, readings: List[dict]):
    """Insert 1000 rows in single transaction."""
    query = """
        INSERT INTO weather_data
        VALUES (?, ?, ?, ?, ?)
    """
    data = [(r['timestamp'], r['station_id'], ...) for r in readings]
    conn.executemany(query, data)
    # ~100x faster than individual inserts

# ❌ DON'T: Individual inserts in loop
def slow_insert(conn, readings: List[dict]):
    """1000 separate transactions, very slow!"""
    for reading in readings:
        conn.execute("INSERT INTO weather_data VALUES (?, ?, ...)",
                    [reading['timestamp'], ...])
```

#### 4. Materialized Views

```python
def create_daily_summary_table(conn):
    """
    Precompute expensive aggregations.

    Query this table instead of aggregating raw data every time.
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_summary AS
        SELECT
            DATE_TRUNC('day', timestamp) as date,
            station_id,
            AVG(temperature_f) as avg_temp,
            COUNT(*) as reading_count
        FROM weather_data
        GROUP BY date, station_id
    """)

    # Fast queries on summary table
    # vs. slow aggregations on millions of raw rows

def query_daily_stats(conn, start_date, end_date):
    """Fast: queries precomputed summary."""
    return conn.execute("""
        SELECT * FROM daily_summary
        WHERE date BETWEEN ? AND ?
    """, [start_date, end_date]).fetchall()
```

#### 5. Query Analysis

```python
def profile_query(conn, query: str, params: list):
    """
    Use EXPLAIN ANALYZE to find bottlenecks.
    """
    explain_query = f"EXPLAIN ANALYZE {query}"
    result = conn.execute(explain_query, params).fetchall()

    for row in result:
        print(row[0])

    # Look for:
    # - Sequential scans (add index)
    # - High row counts (add WHERE clause)
    # - Sort operations (add ORDER BY index)

# Example output:
"""
┌─────────────────────────────────────┐
│┌───────────────────────────────────┐│
││    Query Profiling Information    ││
│└───────────────────────────────────┘│
└─────────────────────────────────────┘
SEQ_SCAN                    3.2ms (97%)  <- BAD! Add index
FILTER                      0.1ms (3%)
"""
```

---

## API Performance

### Response Optimization

#### 1. Compression

```python
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# ✅ DO: Enable compression for responses > 1KB
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

#### 2. ETags & Caching Headers

```python
from fastapi import Response, Request
import hashlib

@app.get("/weather/latest")
async def get_latest(request: Request, response: Response):
    """Add caching headers."""
    data = await db.get_latest()

    # Generate ETag from data
    etag = hashlib.md5(str(data).encode()).hexdigest()

    # Check if client has cached version
    if request.headers.get("if-none-match") == etag:
        response.status_code = 304  # Not Modified
        return None

    # Set caching headers
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60"

    return data
```

#### 3. Response Streaming

```python
from fastapi.responses import StreamingResponse
import csv
from io import StringIO

@app.get("/weather/export")
async def export_csv(station_id: str):
    """Stream large datasets instead of loading all in memory."""

    async def generate():
        """Generator yields data in chunks."""
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Write header
        writer.writerow(['timestamp', 'temperature', 'humidity'])
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        # Stream rows
        async for reading in db.stream_readings(station_id):
            writer.writerow([
                reading['timestamp'],
                reading['temperature_f'],
                reading['humidity']
            ])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=weather.csv"}
    )
```

---

## Monitoring & Profiling

### Backend Profiling

#### 1. Request Timing Middleware

```python
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log request timing."""
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s"
    )

    # Add header for client-side monitoring
    response.headers["X-Process-Time"] = str(process_time)

    return response
```

#### 2. Python Profiling

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func):
    """Decorator to profile a function."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Print stats
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 slowest
        print(s.getvalue())

        return result
    return wrapper

@profile_function
def slow_operation():
    # Your code here
    pass
```

### Frontend Profiling

#### 1. React DevTools Profiler

```typescript
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number
) {
  if (actualDuration > 16) { // Slower than 60fps
    console.warn(`${id} took ${actualDuration}ms to render`);
  }
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}
```

#### 2. Performance API

```typescript
// Measure component render time
function WeatherChart({ data }: Props) {
  useEffect(() => {
    const mark = 'chart-render';
    performance.mark(mark);

    return () => {
      performance.measure('Chart Render Time', mark);
      const measure = performance.getEntriesByName('Chart Render Time')[0];
      if (measure.duration > 100) {
        console.warn(`Chart render took ${measure.duration}ms`);
      }
      performance.clearMarks(mark);
      performance.clearMeasures('Chart Render Time');
    };
  });

  return <LineChart data={data} />;
}
```

---

## Common Performance Issues

### Issue 1: N+1 Query Problem

```python
# ❌ BAD: N+1 queries (1 + N queries)
async def get_stations_with_latest():
    """Executes 1 + N queries!"""
    stations = await db.get_all_stations()  # 1 query

    result = []
    for station in stations:  # N queries
        latest = await db.get_latest_by_station(station.id)
        result.append({
            'station': station,
            'latest': latest
        })
    return result

# ✅ GOOD: Single query with JOIN
async def get_stations_with_latest_optimized():
    """Single optimized query."""
    query = """
        SELECT
            s.*,
            w.*
        FROM stations s
        LEFT JOIN LATERAL (
            SELECT * FROM weather_data
            WHERE station_id = s.id
            ORDER BY timestamp DESC
            LIMIT 1
        ) w ON TRUE
    """
    return await db.execute(query).fetchall()
```

### Issue 2: Unnecessary Re-renders

```typescript
// ❌ BAD: Creates new object every render
function WeatherDashboard() {
  const config = { refreshInterval: 60000 }; // New object every render!

  return <WeatherWidget config={config} />; // Causes re-render
}

// ✅ GOOD: Stable reference
function WeatherDashboard() {
  const config = useMemo(
    () => ({ refreshInterval: 60000 }),
    []
  );

  return <WeatherWidget config={config} />; // No unnecessary re-renders
}
```

### Issue 3: Memory Leaks

```typescript
// ❌ BAD: Doesn't cleanup
function WeatherWidget() {
  useEffect(() => {
    const interval = setInterval(fetchData, 60000);
    // Missing cleanup!
  }, []);
}

// ✅ GOOD: Proper cleanup
function WeatherWidget() {
  useEffect(() => {
    const interval = setInterval(fetchData, 60000);

    return () => clearInterval(interval); // Cleanup
  }, []);
}
```

---

## Performance Checklist

### Before Deploying

- [ ] All queries use indexes for filters
- [ ] API responses < 500ms (p95)
- [ ] Bundle size < 200kb gzipped
- [ ] Images optimized and lazy loaded
- [ ] Database queries profiled with EXPLAIN
- [ ] No N+1 query problems
- [ ] React components memoized where appropriate
- [ ] Large lists virtualized
- [ ] API responses compressed
- [ ] Caching strategy implemented
- [ ] Memory leaks checked (React DevTools)

---

**See also:**
- DATABASE-PATTERNS.md - Query optimization
- REACT-STANDARDS.md - Component patterns
- API-STANDARDS.md - API best practices

**Remember:** Profile before optimizing. Readable code first, fast code second.
