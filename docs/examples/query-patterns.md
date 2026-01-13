# Database Query Pattern Examples

**Real examples from Weather App project**
**Reference:** Use these as templates for new queries
**Load after:** DATABASE-PATTERNS.md

---

## Table of Contents

1. [Simple SELECT Queries](#simple-select-queries)
2. [Parameterized Queries](#parameterized-queries)
3. [Date Range Queries](#date-range-queries)
4. [Aggregation Queries](#aggregation-queries)
5. [Window Functions](#window-functions)
6. [Batch Operations](#batch-operations)
7. [Complex Queries](#complex-queries)

---

## Simple SELECT Queries

### Get Latest Reading

```python
from typing import Dict, Any, Optional
import duckdb

def get_latest_reading(
    conn: duckdb.DuckDBPyConnection
) -> Optional[Dict[str, Any]]:
    """Get the most recent weather reading."""
    query = """
        SELECT *
        FROM weather_data
        ORDER BY timestamp DESC
        LIMIT 1
    """

    result = conn.execute(query).fetchone()

    if not result:
        return None

    columns = [desc[0] for desc in conn.description]
    return dict(zip(columns, result))
```

### Get Latest by Station

```python
def get_latest_by_station(
    conn: duckdb.DuckDBPyConnection,
    station_id: str
) -> Optional[Dict[str, Any]]:
    """Get most recent reading for specific station."""
    query = """
        SELECT *
        FROM weather_data
        WHERE station_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    """

    result = conn.execute(query, [station_id]).fetchone()

    if not result:
        return None

    columns = [desc[0] for desc in conn.description]
    return dict(zip(columns, result))
```

---

## Parameterized Queries

### Single Parameter

```python
def get_readings_by_station(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get readings for a station with parameterized query.

    SECURE: Uses parameterized query (prevents SQL injection)
    """
    query = """
        SELECT
            timestamp,
            station_id,
            temperature_f,
            humidity,
            wind_speed_mph
        FROM weather_data
        WHERE station_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """

    result = conn.execute(query, [station_id, limit]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Multiple Parameters with Optional Filters

```python
def query_weather(
    conn: duckdb.DuckDBPyConnection,
    station_id: Optional[str] = None,
    min_temp: Optional[float] = None,
    max_temp: Optional[float] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Query weather with optional filters.

    Uses NULL handling for optional parameters.
    """
    query = """
        SELECT *
        FROM weather_data
        WHERE
            (? IS NULL OR station_id = ?)
            AND (? IS NULL OR temperature_f >= ?)
            AND (? IS NULL OR temperature_f <= ?)
        ORDER BY timestamp DESC
        LIMIT ?
    """

    result = conn.execute(query, [
        station_id, station_id,      # Station filter
        min_temp, min_temp,           # Min temp filter
        max_temp, max_temp,           # Max temp filter
        limit                         # Limit
    ]).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

---

## Date Range Queries

### Simple Date Range

```python
from datetime import datetime

def get_weather_range(
    conn: duckdb.DuckDBPyConnection,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Get weather readings within date range."""
    query = """
        SELECT *
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """

    result = conn.execute(query, [start_date, end_date]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Date Range with Station Filter

```python
def get_station_range(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Get station readings within date range."""
    query = """
        SELECT *
        FROM weather_data
        WHERE station_id = ?
          AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp DESC
    """

    result = conn.execute(
        query,
        [station_id, start_date, end_date]
    ).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Recent Data (Last N Days)

```python
def get_recent_weather(
    conn: duckdb.DuckDBPyConnection,
    days: int = 7
) -> List[Dict[str, Any]]:
    """Get weather from last N days using INTERVAL."""
    query = """
        SELECT *
        FROM weather_data
        WHERE timestamp >= NOW() - INTERVAL ? DAYS
        ORDER BY timestamp DESC
    """

    result = conn.execute(query, [days]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

---

## Aggregation Queries

### Daily Statistics

```python
from datetime import date

def get_daily_stats(
    conn: duckdb.DuckDBPyConnection,
    start_date: date,
    end_date: date,
    station_id: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Calculate daily weather statistics.

    Returns avg/min/max temperature per day.
    """
    query = """
        SELECT
            DATE_TRUNC('day', timestamp) as day,
            station_id,
            COUNT(*) as reading_count,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed_mph) as avg_wind_speed
        FROM weather_data
        WHERE timestamp BETWEEN ? AND ?
          AND (? IS NULL OR station_id = ?)
        GROUP BY day, station_id
        ORDER BY day DESC
    """

    result = conn.execute(
        query,
        [start_date, end_date, station_id, station_id]
    ).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Hourly Aggregation

```python
def get_hourly_averages(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    target_date: date
) -> List[Dict[str, Any]]:
    """Get hourly average temperatures for a specific day."""
    query = """
        SELECT
            DATE_TRUNC('hour', timestamp) as hour,
            AVG(temperature_f) as avg_temp,
            AVG(humidity) as avg_humidity,
            COUNT(*) as sample_count
        FROM weather_data
        WHERE station_id = ?
          AND DATE_TRUNC('day', timestamp) = ?
        GROUP BY hour
        ORDER BY hour
    """

    result = conn.execute(query, [station_id, target_date]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Station Summary

```python
def get_station_summary(
    conn: duckdb.DuckDBPyConnection
) -> List[Dict[str, Any]]:
    """Get summary statistics for all stations."""
    query = """
        SELECT
            station_id,
            COUNT(*) as total_readings,
            MIN(timestamp) as first_reading,
            MAX(timestamp) as last_reading,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            STDDEV(temperature_f) as temp_stddev
        FROM weather_data
        GROUP BY station_id
        ORDER BY station_id
    """

    result = conn.execute(query).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

---

## Window Functions

### Temperature Trends (Moving Average)

```python
def get_temperature_trends(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    Calculate 24-hour moving average temperature.

    Uses window function for rolling average.
    """
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
            ) as temp_change_1h,
            temperature_f - LAG(temperature_f, 24) OVER (
                ORDER BY timestamp
            ) as temp_change_24h
        FROM weather_data
        WHERE station_id = ?
          AND timestamp >= NOW() - INTERVAL ? DAYS
        ORDER BY timestamp
    """

    result = conn.execute(query, [station_id, days]).fetchall()
    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Ranking (Hottest/Coldest Days)

```python
def get_extreme_days(
    conn: duckdb.DuckDBPyConnection,
    limit: int = 10
) -> Dict[str, List[Dict[str, Any]]]:
    """Get hottest and coldest days on record."""

    # Hottest days
    hottest_query = """
        SELECT
            DATE_TRUNC('day', timestamp) as day,
            station_id,
            MAX(temperature_f) as max_temp
        FROM weather_data
        GROUP BY day, station_id
        ORDER BY max_temp DESC
        LIMIT ?
    """

    # Coldest days
    coldest_query = """
        SELECT
            DATE_TRUNC('day', timestamp) as day,
            station_id,
            MIN(temperature_f) as min_temp
        FROM weather_data
        GROUP BY day, station_id
        ORDER BY min_temp ASC
        LIMIT ?
    """

    hottest = conn.execute(hottest_query, [limit]).fetchall()
    coldest = conn.execute(coldest_query, [limit]).fetchall()

    columns_hot = [desc[0] for desc in conn.description]

    return {
        'hottest': [dict(zip(columns_hot, row)) for row in hottest],
        'coldest': [dict(zip(columns_hot, row)) for row in coldest]
    }
```

---

## Batch Operations

### Batch Insert

```python
def batch_insert_readings(
    conn: duckdb.DuckDBPyConnection,
    readings: List[Dict[str, Any]]
) -> int:
    """
    Insert multiple readings efficiently.

    Uses executemany for batch insert.
    """
    query = """
        INSERT INTO weather_data (
            timestamp, station_id, temperature_f,
            humidity, wind_speed_mph, pressure_inhg
        ) VALUES (?, ?, ?, ?, ?, ?)
    """

    # Prepare data as list of tuples
    data = [
        (
            r['timestamp'],
            r['station_id'],
            r['temperature_f'],
            r['humidity'],
            r.get('wind_speed_mph'),
            r.get('pressure_inhg')
        )
        for r in readings
    ]

    conn.executemany(query, data)
    return len(data)
```

### Batch Update

```python
def batch_update_readings(
    conn: duckdb.DuckDBPyConnection,
    updates: List[Dict[str, Any]]
) -> int:
    """Update multiple readings in batch."""
    query = """
        UPDATE weather_data
        SET
            temperature_f = ?,
            humidity = ?,
            wind_speed_mph = ?
        WHERE id = ?
    """

    data = [
        (
            u['temperature_f'],
            u['humidity'],
            u.get('wind_speed_mph'),
            u['id']
        )
        for u in updates
    ]

    conn.executemany(query, data)
    return len(data)
```

### Batch Delete

```python
def batch_delete_old_readings(
    conn: duckdb.DuckDBPyConnection,
    older_than_days: int
) -> int:
    """Delete readings older than N days."""
    query = """
        DELETE FROM weather_data
        WHERE timestamp < NOW() - INTERVAL ? DAYS
    """

    result = conn.execute(query, [older_than_days])
    return result.fetchone()[0] if result else 0
```

---

## Complex Queries

### Multi-Station Comparison

```python
def compare_stations(
    conn: duckdb.DuckDBPyConnection,
    station_ids: List[str],
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """
    Compare statistics across multiple stations.

    Uses UNNEST for dynamic station list.
    """
    query = """
        SELECT
            station_id,
            COUNT(*) as reading_count,
            AVG(temperature_f) as avg_temp,
            MIN(temperature_f) as min_temp,
            MAX(temperature_f) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_speed_mph) as avg_wind_speed
        FROM weather_data
        WHERE station_id IN (SELECT UNNEST(?))
          AND timestamp BETWEEN ? AND ?
        GROUP BY station_id
        ORDER BY station_id
    """

    result = conn.execute(
        query,
        [station_ids, start_date, end_date]
    ).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

### Correlation Analysis

```python
def analyze_temp_humidity_correlation(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Analyze correlation between temperature and humidity.

    Uses statistical functions.
    """
    query = """
        SELECT
            COUNT(*) as sample_count,
            AVG(temperature_f) as avg_temp,
            AVG(humidity) as avg_humidity,
            STDDEV(temperature_f) as temp_stddev,
            STDDEV(humidity) as humidity_stddev,
            CORR(temperature_f, humidity) as correlation
        FROM weather_data
        WHERE station_id = ?
          AND timestamp >= NOW() - INTERVAL ? DAYS
    """

    result = conn.execute(query, [station_id, days]).fetchone()
    columns = [desc[0] for desc in conn.description]
    return dict(zip(columns, result))
```

### Gap Detection

```python
def find_data_gaps(
    conn: duckdb.DuckDBPyConnection,
    station_id: str,
    expected_interval_minutes: int = 60
) -> List[Dict[str, Any]]:
    """
    Find gaps in data collection.

    Identifies periods with missing readings.
    """
    query = """
        WITH time_diffs AS (
            SELECT
                timestamp as current_time,
                LAG(timestamp) OVER (ORDER BY timestamp) as prev_time,
                EXTRACT(EPOCH FROM (
                    timestamp - LAG(timestamp) OVER (ORDER BY timestamp)
                )) / 60 as gap_minutes
            FROM weather_data
            WHERE station_id = ?
        )
        SELECT
            prev_time as gap_start,
            current_time as gap_end,
            gap_minutes
        FROM time_diffs
        WHERE gap_minutes > ?
        ORDER BY gap_start DESC
    """

    result = conn.execute(
        query,
        [station_id, expected_interval_minutes]
    ).fetchall()

    columns = [desc[0] for desc in conn.description]
    return [dict(zip(columns, row)) for row in result]
```

---

## Performance Optimization Examples

### Using Indexes Effectively

```python
def create_performance_indexes(conn: duckdb.DuckDBPyConnection):
    """Create indexes for common query patterns."""

    # Index for timestamp queries (DESC for recent data)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_timestamp
        ON weather_data(timestamp DESC)
    """)

    # Index for station queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station
        ON weather_data(station_id)
    """)

    # Composite index for common filter pattern
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_weather_station_timestamp
        ON weather_data(station_id, timestamp DESC)
    """)
```

### Query Plan Analysis

```python
def analyze_query_performance(
    conn: duckdb.DuckDBPyConnection,
    query: str,
    params: List[Any]
) -> str:
    """
    Analyze query execution plan.

    Use this to optimize slow queries.
    """
    explain_query = f"EXPLAIN ANALYZE {query}"
    result = conn.execute(explain_query, params).fetchall()

    # Pretty print the plan
    plan = '\n'.join([row[0] for row in result])
    return plan

# Usage
query = """
    SELECT * FROM weather_data
    WHERE station_id = ?
      AND timestamp >= ?
    ORDER BY timestamp DESC
"""
plan = analyze_query_performance(conn, query, ['STATION001', '2026-01-01'])
print(plan)
```

### Materialized View Pattern

```python
def create_daily_summary_table(conn: duckdb.DuckDBPyConnection):
    """
    Create precomputed daily summaries.

    Query this instead of aggregating raw data every time.
    """
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

def refresh_daily_summary(
    conn: duckdb.DuckDBPyConnection,
    target_date: date
):
    """Refresh summary for a specific date."""
    # Delete existing
    conn.execute(
        "DELETE FROM daily_weather_summary WHERE date = ?",
        [target_date]
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
    """, [target_date])
```

---

## Common Anti-Patterns to Avoid

### DON'T: String Formatting

```python
# DANGEROUS - SQL Injection vulnerability!
def bad_query(conn, station_id):
    query = f"SELECT * FROM weather_data WHERE station_id = '{station_id}'"
    return conn.execute(query).fetchall()
```

### DO: Parameterized Queries

```python
def good_query(conn, station_id):
    query = "SELECT * FROM weather_data WHERE station_id = ?"
    return conn.execute(query, [station_id]).fetchall()
```

### DON'T: SELECT *

```python
# Wasteful - reads all columns
def bad_select(conn):
    query = "SELECT * FROM weather_data"
    return conn.execute(query).fetchall()
```

### DO: Select Only Needed Columns

```python
def good_select(conn):
    # Only reads needed columns (columnar storage benefit)
    query = "SELECT timestamp, temperature_f FROM weather_data"
    return conn.execute(query).fetchall()
```

---

## Common Patterns Summary

### 1. Always Use
- Parameterized queries (NEVER string formatting)
- Try/except for error handling
- Type hints for function parameters
- Column selection (avoid SELECT *)

### 2. Performance Tips
- Create indexes for common filters
- Use window functions for analytics
- Batch operations for bulk changes
- Precompute frequently accessed aggregations

### 3. Query Organization
- One query per function
- Clear function names
- Document expected results
- Return typed dictionaries

---

**See also:**
- DATABASE-PATTERNS.md - Full standards
- API-STANDARDS.md - API integration patterns
- TESTING.md - Query testing strategies

**Questions?** Check CLAUDE.md or ask before implementing.
