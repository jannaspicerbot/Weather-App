# API Reference

**Base URL:** `http://localhost:8000/api`
**Framework:** FastAPI
**OpenAPI Spec:** `http://localhost:8000/docs` (Swagger UI)
**Version:** 1.0

---

## Overview

The Weather App REST API provides programmatic access to weather data stored in the DuckDB database. All endpoints return JSON responses with Pydantic-validated schemas.

**Key Features:**
- Auto-generated OpenAPI 3.0 schema
- Type-safe request/response validation (Pydantic)
- Interactive documentation at `/docs`
- CORS enabled for `http://localhost:3000` (frontend)

---

## Authentication

**Current:** None (local-only deployment)

**Future (Phase 3):** OAuth2 password bearer token

---

## Endpoints

### Health Check

Check API and database status.

**Request:**
```http
GET /api/health
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "database": "connected",
  "total_records": 125432,
  "latest_reading": "2024-12-31T23:55:00Z",
  "oldest_reading": "2024-01-01T00:00:00Z",
  "database_size_mb": 45.2
}
```

**Example:**
```bash
curl http://localhost:8000/api/health
```

---

### Get Scheduler Status

Get information about the automated data collection scheduler.

**Request:**
```http
GET /api/scheduler/status
```

**Response:** `200 OK`
```json
{
  "enabled": true,
  "running": true,
  "fetch_interval_minutes": 5,
  "next_run_time": "2026-01-03T09:29:53.720924-08:00",
  "job_id": "fetch_weather"
}
```

**Response Fields:**
- `enabled`: Whether scheduler is enabled via `SCHEDULER_ENABLED` environment variable
- `running`: Whether the scheduler is currently running
- `fetch_interval_minutes`: Interval between automatic data fetches
- `next_run_time`: ISO 8601 timestamp of next scheduled fetch (null if disabled)
- `job_id`: Internal job identifier (`fetch_weather`)

**Example:**
```bash
curl http://localhost:8000/api/scheduler/status | jq
```

---

### Get Latest Reading

Retrieve the most recent weather reading.

**Request:**
```http
GET /api/weather/latest
```

**Response:** `200 OK`
```json
{
  "timestamp": "2024-12-31T23:55:00Z",
  "temperature": 72.5,
  "feels_like": 71.8,
  "humidity": 65.0,
  "dew_point": 58.3,
  "wind_speed": 5.2,
  "wind_gust": 8.1,
  "wind_direction": 270,
  "pressure": 30.12,
  "precipitation_rate": 0.0,
  "precipitation_total": 0.0,
  "solar_radiation": 0.0,
  "uv_index": 0,
  "battery_ok": true
}
```

**Error Responses:**
- `404 Not Found`: No readings in database

**Example:**
```bash
curl http://localhost:8000/api/weather/latest
```

---

### Get Weather Range

Retrieve weather readings for a date/time range.

**Request:**
```http
GET /api/weather/range?start={start_timestamp}&end={end_timestamp}&limit={limit}
```

**Query Parameters:**
- `start` (required): ISO 8601 timestamp (e.g., `2024-01-01T00:00:00Z`)
- `end` (required): ISO 8601 timestamp (e.g., `2024-01-31T23:59:59Z`)
- `limit` (optional): Max records to return (default: 10000)

**Response:** `200 OK`
```json
[
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "temperature": 45.2,
    "feels_like": 43.1,
    "humidity": 65.0,
    ...
  },
  {
    "timestamp": "2024-01-01T00:05:00Z",
    "temperature": 45.1,
    "feels_like": 43.0,
    "humidity": 65.2,
    ...
  }
]
```

**Error Responses:**
- `400 Bad Request`: Invalid date format or start > end
- `422 Unprocessable Entity`: Missing required parameters

**Example:**
```bash
# Get 24 hours of data
curl "http://localhost:8000/api/weather/range?start=2024-12-31T00:00:00Z&end=2024-12-31T23:59:59Z"

# Get 1 month (limited to 10K records)
curl "http://localhost:8000/api/weather/range?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z&limit=10000"
```

---

### Get Statistics

Retrieve aggregated statistics for a time period.

**Request:**
```http
GET /api/weather/stats?period={period}
```

**Query Parameters:**
- `period` (required): Time period (`24h`, `7d`, `30d`, `1y`)

**Response:** `200 OK`
```json
{
  "period": "24h",
  "avg_temperature": 68.5,
  "min_temperature": 62.3,
  "max_temperature": 75.2,
  "avg_humidity": 65.0,
  "total_precipitation": 0.15,
  "avg_wind_speed": 5.2,
  "max_wind_gust": 12.5
}
```

**Error Responses:**
- `400 Bad Request`: Invalid period

**Example:**
```bash
# 24-hour stats
curl "http://localhost:8000/api/weather/stats?period=24h"

# 30-day stats
curl "http://localhost:8000/api/weather/stats?period=30d"
```

---

### Export CSV

Export weather data as CSV file.

**Request:**
```http
GET /api/export?start={start_timestamp}&end={end_timestamp}&format=csv
```

**Query Parameters:**
- `start` (required): ISO 8601 timestamp
- `end` (required): ISO 8601 timestamp
- `format` (optional): Export format (`csv` only, default: `csv`)

**Response:** `200 OK`
```
Content-Type: text/csv
Content-Disposition: attachment; filename="weather_data.csv"

timestamp,temperature,feels_like,humidity,...
2024-01-01T00:00:00Z,45.2,43.1,65.0,...
2024-01-01T00:05:00Z,45.1,43.0,65.2,...
```

**Error Responses:**
- `400 Bad Request`: Invalid date range
- `422 Unprocessable Entity`: Missing parameters

**Example:**
```bash
# Download CSV
curl "http://localhost:8000/api/export?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z" -o weather_jan_2024.csv

# Or use browser:
open "http://localhost:8000/api/export?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z"
```

---

## Data Models

### WeatherReading

```typescript
interface WeatherReading {
  timestamp: string;          // ISO 8601 timestamp (UTC)
  temperature: number;        // °F
  feels_like: number | null;  // °F
  humidity: number | null;    // % (0-100)
  dew_point: number | null;   // °F
  wind_speed: number | null;  // mph
  wind_gust: number | null;   // mph
  wind_direction: number | null; // degrees (0-360)
  pressure: number | null;    // inHg
  precipitation_rate: number | null; // in/hr
  precipitation_total: number | null; // inches
  solar_radiation: number | null; // W/m²
  uv_index: number | null;    // 0-11+
  battery_ok: boolean | null; // true=OK, false=low
}
```

### WeatherStats

```typescript
interface WeatherStats {
  period: string;              // "24h", "7d", "30d", "1y"
  avg_temperature: number;     // °F
  min_temperature: number;     // °F
  max_temperature: number;     // °F
  avg_humidity: number;        // %
  total_precipitation: number; // inches
  avg_wind_speed: number;      // mph
  max_wind_gust: number;       // mph
}
```

### HealthStatus

```typescript
interface HealthStatus {
  status: string;              // "ok" or "error"
  database: string;            // "connected" or "disconnected"
  total_records: number;       // Total readings in database
  latest_reading: string;      // ISO 8601 timestamp
  oldest_reading: string;      // ISO 8601 timestamp
  database_size_mb: number;    // Database file size in MB
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Data returned successfully |
| 400 | Bad Request | Invalid date format, start > end |
| 404 | Not Found | No readings found |
| 422 | Unprocessable Entity | Missing required parameters |
| 500 | Internal Server Error | Database connection failed |

---

## CORS Configuration

**Allowed Origins:**
- `http://localhost:3000` (Vite dev server)
- `http://localhost:8000` (Production build served by FastAPI)

**Allowed Methods:** `GET, POST, PUT, DELETE, OPTIONS`

**Allowed Headers:** `*`

---

## Rate Limiting

**Current:** None (local-only deployment)

**Future (Phase 3):** 100 requests/minute per IP

---

## Interactive Documentation

### Swagger UI

Visit `http://localhost:8000/docs` for interactive API documentation:
- Try endpoints directly in browser
- View request/response schemas
- See example values
- Download OpenAPI schema

### ReDoc

Visit `http://localhost:8000/redoc` for alternative documentation UI:
- Better for reading (less interactive)
- Three-column layout
- Downloadable as single HTML file

---

## Code Examples

### JavaScript/TypeScript

```typescript
// Fetch latest reading
const response = await fetch('http://localhost:8000/api/weather/latest');
const data: WeatherReading = await response.json();
console.log(`Temperature: ${data.temperature}°F`);

// Fetch date range
const start = '2024-01-01T00:00:00Z';
const end = '2024-01-31T23:59:59Z';
const rangeResponse = await fetch(
  `http://localhost:8000/api/weather/range?start=${start}&end=${end}`
);
const readings: WeatherReading[] = await rangeResponse.json();
console.log(`Fetched ${readings.length} readings`);
```

### Python

```python
import requests
from datetime import datetime

# Fetch latest reading
response = requests.get('http://localhost:8000/api/weather/latest')
data = response.json()
print(f"Temperature: {data['temperature']}°F")

# Fetch date range
params = {
    'start': '2024-01-01T00:00:00Z',
    'end': '2024-01-31T23:59:59Z',
    'limit': 10000
}
response = requests.get('http://localhost:8000/api/weather/range', params=params)
readings = response.json()
print(f"Fetched {len(readings)} readings")
```

### curl

```bash
# Fetch latest
curl http://localhost:8000/api/weather/latest | jq

# Fetch range (pretty-print JSON)
curl "http://localhost:8000/api/weather/range?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z" | jq

# Download CSV
curl "http://localhost:8000/api/export?start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z" -o weather_2024.csv
```

---

## OpenAPI Schema

Download full OpenAPI 3.0 schema:

```bash
curl http://localhost:8000/openapi.json > openapi.json
```

Use for code generation:
```bash
# TypeScript client
npx openapi-typescript-codegen --input openapi.json --output ./src/api

# Python client
openapi-generator-cli generate -i openapi.json -g python -o ./api_client
```

---

## Future Enhancements (Phase 3)

- **WebSocket endpoint:** Real-time data push to dashboard
- **GraphQL API:** Flexible query language
- **Authentication:** OAuth2 password bearer tokens
- **Rate limiting:** 100 req/min per IP
- **Additional export formats:** JSON, Parquet
- **Batch operations:** Bulk inserts via POST

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## Document Changelog

- **2026-01-02:** Initial API reference extracted from specifications.md
