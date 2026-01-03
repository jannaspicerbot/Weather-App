# Database Schema Reference

**Database:** DuckDB 0.10+
**File Location:** `./data/weather.db` (configurable via `DATABASE_PATH` env var)
**Schema Version:** 1.0

---

## Overview

The Weather App uses DuckDB, an embedded analytical database optimized for time-series queries. The database stores all weather measurements at full resolution (typically 5-minute cadence) with 50-year retention.

**Key Features:**
- Columnar storage for 10-100x faster queries
- 10:1 compression ratio (5.2M rows = ~500MB)
- Single-file database (easy backup)
- No aggregation tables needed (compute on-the-fly)

---

## Tables

### weather_data

Primary table storing all weather measurements.

```sql
CREATE TABLE weather_data (
    timestamp TIMESTAMP PRIMARY KEY,      -- Reading timestamp (UTC)
    temperature DOUBLE,                   -- °F
    feels_like DOUBLE,                    -- °F (heat index or wind chill)
    humidity DOUBLE,                      -- % (0-100)
    dew_point DOUBLE,                     -- °F
    wind_speed DOUBLE,                    -- mph
    wind_gust DOUBLE,                     -- mph (peak gust)
    wind_direction INTEGER,               -- degrees (0-360, 0=North)
    pressure DOUBLE,                      -- inHg (barometric pressure)
    precipitation_rate DOUBLE,            -- in/hr (current rate)
    precipitation_total DOUBLE,           -- inches (cumulative daily)
    solar_radiation DOUBLE,               -- W/m² (solar irradiance)
    uv_index INTEGER,                     -- UV index (0-11+)
    battery_ok BOOLEAN                    -- Battery status (true=OK, false=low)
);

CREATE INDEX idx_timestamp ON weather_data(timestamp);
```

#### Column Details

| Column | Type | Nullable | Unit | Description |
|--------|------|----------|------|-------------|
| `timestamp` | TIMESTAMP | NO | UTC | Primary key, reading time |
| `temperature` | DOUBLE | YES | °F | Ambient air temperature |
| `feels_like` | DOUBLE | YES | °F | Apparent temperature (heat index if >80°F, wind chill if <50°F) |
| `humidity` | DOUBLE | YES | % | Relative humidity (0-100) |
| `dew_point` | DOUBLE | YES | °F | Dew point temperature |
| `wind_speed` | DOUBLE | YES | mph | Sustained wind speed (2-min average) |
| `wind_gust` | DOUBLE | YES | mph | Peak wind gust |
| `wind_direction` | INTEGER | YES | degrees | Wind direction (0=North, 90=East, 180=South, 270=West) |
| `pressure` | DOUBLE | YES | inHg | Barometric pressure (sea level adjusted) |
| `precipitation_rate` | DOUBLE | YES | in/hr | Current precipitation rate |
| `precipitation_total` | DOUBLE | YES | inches | Daily cumulative precipitation (resets at midnight) |
| `solar_radiation` | DOUBLE | YES | W/m² | Solar radiation intensity |
| `uv_index` | INTEGER | YES | index | UV index (0=minimal, 11+=extreme) |
| `battery_ok` | BOOLEAN | YES | boolean | Battery status (true=OK, false=replace) |

#### Constraints

- **PRIMARY KEY:** `timestamp` (ensures uniqueness, enables `INSERT OR REPLACE` for idempotency)
- **INDEX:** `idx_timestamp` (optimizes time-range queries)
- **No foreign keys:** Single-table design for simplicity

---

## Data Integrity

### Idempotent Writes

The database uses `INSERT OR REPLACE` to ensure idempotent writes. Re-running the same data ingestion will not create duplicates:

```sql
INSERT OR REPLACE INTO weather_data (timestamp, temperature, humidity, ...)
VALUES (?, ?, ?, ...);
```

**Behavior:**
- If `timestamp` already exists → Replace row with new data
- If `timestamp` is new → Insert new row
- No duplicates ever created

### NULL Handling

All measurement columns (except `timestamp`) are nullable. This handles:
- Sensor failures (e.g., wind sensor offline)
- Missing data from API
- Battery-powered sensors going offline

**Query Best Practice:**
```sql
-- Use COALESCE for missing data
SELECT timestamp,
       COALESCE(temperature, 0) AS temperature,
       COALESCE(humidity, 0) AS humidity
FROM weather_data;
```

---

## Storage Characteristics

### Columnar Storage

DuckDB stores data in columnar format (column-oriented, not row-oriented):

**SQLite (Row-Oriented):**
```
Row 1: [timestamp, temp, humidity, wind, ...]
Row 2: [timestamp, temp, humidity, wind, ...]
Row 3: [timestamp, temp, humidity, wind, ...]

Query: SELECT AVG(temperature) FROM weather_data;
→ Must read ALL columns for ALL rows (wasteful!)
```

**DuckDB (Columnar):**
```
timestamp column: [t1, t2, t3, ...]
temperature column: [72.5, 73.1, 72.8, ...]
humidity column: [65, 64, 66, ...]
wind column: [5.2, 6.1, 5.8, ...]

Query: SELECT AVG(temperature) FROM weather_data;
→ Only reads temperature column (10x faster!)
```

### Compression

DuckDB applies multiple compression algorithms:
- **Dictionary encoding:** Repeated values stored once
- **Run-length encoding (RLE):** Consecutive identical values compressed
- **Bit-packing:** Integers use minimal bits

**Real-World Example:**
```
Uncompressed: 5.2M rows × 112 bytes/row = 582 MB
Compressed: 5.2M rows → 59 MB (10:1 ratio)
```

---

## Query Patterns

### Time-Range Queries (Most Common)

```sql
-- Last 24 hours
SELECT * FROM weather_data
WHERE timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Specific date range
SELECT * FROM weather_data
WHERE timestamp BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY timestamp;

-- Performance: <1s for 1 year, 1.8s for 50 years (full scan)
```

### Aggregation Queries

```sql
-- Daily averages
SELECT date_trunc('day', timestamp) AS day,
       AVG(temperature) AS avg_temp,
       MIN(temperature) AS min_temp,
       MAX(temperature) AS max_temp
FROM weather_data
WHERE timestamp >= '2024-01-01'
GROUP BY day
ORDER BY day;

-- Performance: 0.11s for 1 year, 3.2s for 50 years
```

```sql
-- Monthly rainfall totals
SELECT date_trunc('month', timestamp) AS month,
       SUM(precipitation_total) AS total_rainfall
FROM weather_data
GROUP BY month
ORDER BY month;

-- Performance: <1s for 50 years
```

### Statistical Queries

```sql
-- Temperature statistics
SELECT COUNT(*) AS total_readings,
       AVG(temperature) AS avg_temp,
       STDDEV(temperature) AS std_temp,
       PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY temperature) AS median_temp,
       MIN(temperature) AS min_temp,
       MAX(temperature) AS max_temp
FROM weather_data
WHERE timestamp >= '2024-01-01';
```

### Window Functions (Advanced)

```sql
-- 7-day moving average
SELECT timestamp,
       temperature,
       AVG(temperature) OVER (
           ORDER BY timestamp
           ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS temp_7day_avg
FROM weather_data
WHERE timestamp >= '2024-01-01'
ORDER BY timestamp;
```

---

## Maintenance Operations

### Database Initialization

```bash
# CLI command
weather-app init-db

# SQL equivalent
duckdb weather.db "CREATE TABLE weather_data (...);"
```

### Database Info

```bash
# CLI command
weather-app info

# Output:
# Database: /path/to/weather.db
# Total records: 125,432
# Date range: 2024-01-01 to 2024-12-31
# Database size: 6.2 MB
```

### Vacuum (Reclaim Space)

```sql
-- Reclaim space after large deletes (rarely needed)
VACUUM;
```

### Checkpointing

DuckDB uses Write-Ahead Logging (WAL) for durability. Checkpoints flush WAL to main database file.

```sql
-- Force checkpoint (automatic by default)
CHECKPOINT;
```

---

## Backup and Restore

### Backup (Copy File)

```bash
# Stop writes (shutdown CLI/API)
# Copy database file
cp ./data/weather.db ./backups/weather_$(date +%Y%m%d).db

# Compress (optional)
gzip ./backups/weather_$(date +%Y%m%d).db
```

### Restore (Replace File)

```bash
# Stop writes (shutdown CLI/API)
# Replace database file
cp ./backups/weather_20241231.db ./data/weather.db

# Restart CLI/API
```

### Export to CSV (Portable Backup)

```bash
# CLI command
weather-app export --start 2024-01-01 --end 2024-12-31 --output backup.csv

# SQL equivalent
duckdb weather.db "COPY weather_data TO 'backup.csv' (HEADER, DELIMITER ',');"
```

### Export to Parquet (Efficient Backup)

```sql
-- Export to Parquet (10x smaller than CSV)
COPY weather_data TO 'backup.parquet' (FORMAT PARQUET);

-- Restore from Parquet
CREATE TABLE weather_data AS SELECT * FROM read_parquet('backup.parquet');
```

---

## Performance Benchmarks

### Query Performance (5.2M rows, 50 years)

| Query Type | DuckDB | SQLite | Speedup |
|------------|--------|--------|---------|
| Full table scan | 1.8s | 45s | 25x |
| 1-year aggregate | 0.11s | 4.1s | 37x |
| 50-year aggregate | 3.2s | 180s | 56x |
| Complex window function | 0.25s | 12.5s | 50x |

### Write Performance

| Operation | DuckDB | SQLite | Speedup |
|-----------|--------|--------|---------|
| INSERT 10K rows | 0.18s | 2.3s | 12.8x |
| Batch INSERT (1000/batch) | 0.015s | 0.23s | 15x |

---

## Schema Evolution

### Adding Columns (Future)

```sql
-- Add new column (e.g., PM2.5 air quality sensor)
ALTER TABLE weather_data ADD COLUMN pm25 DOUBLE;

-- Backfill NULL for existing rows (automatic)
-- New inserts will populate the column
```

### Renaming Columns (Future)

```sql
-- Rename column (rare, breaking change)
ALTER TABLE weather_data RENAME COLUMN temperature TO temp_fahrenheit;
```

### Migration Strategy (Future)

If major schema changes are needed:
1. Export to Parquet: `COPY weather_data TO 'backup.parquet'`
2. Drop and recreate table with new schema
3. Import from Parquet with transformation: `INSERT INTO weather_data SELECT ... FROM read_parquet('backup.parquet')`

---

## Multi-Station Support (Future)

Phase 3 may add support for multiple weather stations:

```sql
-- Future schema (Phase 3)
CREATE TABLE weather_data (
    station_id VARCHAR,               -- Station identifier
    timestamp TIMESTAMP,
    temperature DOUBLE,
    ...
    PRIMARY KEY (station_id, timestamp)
) PARTITION BY (station_id);

-- Query specific station
SELECT * FROM weather_data WHERE station_id = 'station1';
```

---

## References

- [DuckDB SQL Reference](https://duckdb.org/docs/sql/introduction)
- [DuckDB Data Types](https://duckdb.org/docs/sql/data_types/overview)
- [DuckDB Storage Format](https://duckdb.org/docs/internals/storage)
- [DuckDB Performance Guide](https://duckdb.org/docs/guides/performance/overview)

---

## Document Changelog

- **2026-01-02:** Initial database schema reference extracted from specifications.md
