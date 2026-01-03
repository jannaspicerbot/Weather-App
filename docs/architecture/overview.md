# Weather App — Architecture Overview

**Version:** 2.0 (Phase 2 Complete)
**Date:** 2026-01-02
**Status:** ✅ Production-ready local deployment

---

## Executive Summary

The Weather App is a local-first Python + TypeScript application that ingests weather data from Ambient Weather stations, stores it in an embedded analytical database (DuckDB), and provides an interactive web dashboard for visualization and export.

**Key Characteristics:**
- **Local-first:** All data stays on user's device, no cloud dependencies
- **Fast analytics:** DuckDB provides 10-100x speedup over SQLite for time-series queries
- **Type-safe:** End-to-end type safety with Pydantic (backend) and TypeScript (frontend)
- **One-command deploy:** Docker Compose for easy installation
- **50-year retention:** Full-resolution storage with columnar compression

---

## Technology Stack

### Current State (Phase 2 Complete)

| Component | Technology | Status | Rationale |
|-----------|-----------|--------|-----------|
| **Backend** | FastAPI (Python 3.11+) | ✅ Phase 1 | Auto-generated OpenAPI, async support |
| **Database** | DuckDB 0.10+ | ✅ Phase 2 | **10-100x faster** than SQLite for analytics |
| **Frontend Lang** | TypeScript | ✅ Phase 2 | Type safety, 96% industry adoption |
| **Frontend Framework** | React 18 + Vite | ✅ Phase 2 | Modern build tools, fast dev server |
| **Charting** | Recharts | ✅ Phase 2 | React-native charts, D3-based |
| **CLI** | Click | ✅ Phase 1 | Elegant command-line interfaces |
| **Validation** | Pydantic | ✅ Phase 1 | Runtime type validation |
| **Deployment** | Docker Compose | ✅ Phase 2 | One-command orchestration |
| **Testing** | pytest + Vitest | ✅ Phase 2 | Backend + frontend coverage |
| **CI/CD** | GitHub Actions | ✅ Phase 2 | Automated testing and builds |

### Migration History

| Component | Phase 1 (Dec 2025) | Phase 2 (Jan 2026) |
|-----------|-------------------|-------------------|
| Database | SQLite | **DuckDB** (10-100x faster) |
| Frontend | None (CLI only) | **React + TypeScript** |
| Backend | Flask (planned) | **FastAPI** (OpenAPI) |
| Charts | Plotly (planned) | **Recharts** (React-native) |
| Deployment | Manual | **Docker Compose** |

---

## System Context (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────┐
│                      Weather Station                         │
│                   (Ambient Weather API)                      │
└────────────┬────────────────────────────────────────────────┘
             │ HTTPS/JSON
             │ (5-min cadence)
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Weather App                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   CLI Tool   │  │  Web API     │  │ Web Dashboard│     │
│  │   (Click)    │  │  (FastAPI)   │  │ (React+TS)   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┼──────────────────┘              │
│                            ▼                                 │
│                  ┌──────────────────┐                       │
│                  │   DuckDB         │                       │
│                  │ (weather.duckdb) │                       │
│                  └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                  User (via browser/terminal)                 │
└─────────────────────────────────────────────────────────────┘
```

**External Dependencies:**
- **Ambient Weather API:** Source of weather data (HTTPS REST API)
- **User Browser:** Web dashboard access (http://localhost:8000)
- **User Terminal:** CLI command execution

---

## Container Diagram (C4 Level 2)

```
┌───────────────────────────────────────────────────────────────┐
│                       Weather App System                       │
│                                                                │
│  ┌─────────────────────┐         ┌──────────────────────┐    │
│  │   Frontend          │  HTTP   │   Backend            │    │
│  │   Container         │◄────────│   Container          │    │
│  │                     │  JSON   │                      │    │
│  │  • React 18         │         │  • FastAPI          │    │
│  │  • TypeScript       │         │  • Python 3.11+     │    │
│  │  • Vite             │         │  • Uvicorn          │    │
│  │  • Recharts         │         │  • Pydantic         │    │
│  │  • TailwindCSS      │         │                      │    │
│  │                     │         │  Ports:             │    │
│  │  Port: 3000 (dev)   │         │  • 8000 (HTTP)      │    │
│  │  Port: 80 (prod)    │         │                      │    │
│  └─────────────────────┘         └──────────┬───────────┘    │
│                                              │                 │
│                                              │ SQL             │
│  ┌─────────────────────┐                    ▼                 │
│  │   CLI Container     │         ┌──────────────────────┐    │
│  │                     │  SQL    │   Database           │    │
│  │  • Click framework  │────────►│   Container          │    │
│  │  • Python 3.11+     │         │                      │    │
│  │  • API client       │         │  • DuckDB 0.10+     │    │
│  │  • Scheduling (ext) │         │  • Single file      │    │
│  │                     │         │  • Columnar storage │    │
│  └─────────────────────┘         │                      │    │
│                                   │  File:              │    │
│                                   │  ./data/weather.db  │    │
│                                   └──────────────────────┘    │
│                                                                │
└───────────────────────────────────────────────────────────────┘
              │                                  ▲
              │ HTTPS                            │
              ▼                                  │
┌──────────────────────────┐                    │
│  Ambient Weather API     │                    │
│  (External Service)      │                    │ User Access
└──────────────────────────┘                    │
                                                 │
                                    ┌────────────┴──────────┐
                                    │   User                │
                                    │  • Browser (dashboard)│
                                    │  • Terminal (CLI)     │
                                    └───────────────────────┘
```

---

## Component Diagram (C4 Level 3)

### Backend Components

```
┌────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  API Layer (weather_app/api/)                        │ │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │ │
│  │  │  routes.py │  │  main.py   │  │  models.py │    │ │
│  │  │  (FastAPI) │  │  (app)     │  │  (Pydantic)│    │ │
│  │  └─────┬──────┘  └────────────┘  └────────────┘    │ │
│  └────────┼───────────────────────────────────────────────┘ │
│           │                                                  │
│  ┌────────▼──────────────────────────────────────────────┐ │
│  │  Service Layer (weather_app/services/)               │ │
│  │  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │ │
│  │  │  ambient_    │  │  fetcher.py │  │ backfill.py│ │ │
│  │  │  client.py   │  │             │  │            │ │ │
│  │  └──────┬───────┘  └─────┬───────┘  └─────┬──────┘ │ │
│  └─────────┼─────────────────┼─────────────────┼────────────┘ │
│            │                 │                 │              │
│  ┌─────────▼─────────────────▼─────────────────▼──────────┐ │
│  │  Data Layer (weather_app/database/)                    │ │
│  │  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐ │ │
│  │  │ connection.py│  │  schema.py  │  │ repository.py│ │ │
│  │  │ (DuckDB ctx) │  │  (DDL)      │  │ (pragmatic)  │ │ │
│  │  └──────┬───────┘  └─────────────┘  └──────┬───────┘ │ │
│  └─────────┼─────────────────────────────────────┼──────────┘ │
│            │                                     │              │
│            └─────────────┬───────────────────────┘              │
│                          ▼                                      │
│                 ┌──────────────────┐                           │
│                 │   DuckDB File    │                           │
│                 │  (weather.duckdb)│                           │
│                 └──────────────────┘                           │
└────────────────────────────────────────────────────────────────┘
```

### Frontend Components

```
┌────────────────────────────────────────────────────────────┐
│                  React Frontend (web/)                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  App Shell (src/App.tsx)                             │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  WeatherDashboard (main container)             │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────┘ │
│                          │                                  │
│  ┌───────────────────────┼──────────────────────────────┐ │
│  │  Component Layer (src/components/)                   │ │
│  │  ┌──────────────┐  ┌────────────┐  ┌─────────────┐ │ │
│  │  │ Temperature  │  │ Humidity   │  │ Wind        │ │ │
│  │  │ Chart        │  │ Chart      │  │ Chart       │ │ │
│  │  └──────────────┘  └────────────┘  └─────────────┘ │ │
│  │  ┌──────────────┐  ┌────────────┐  ┌─────────────┐ │ │
│  │  │ Precipitation│  │ Current    │  │ DateRange   │ │ │
│  │  │ Chart        │  │ Conditions │  │ Picker      │ │ │
│  │  └──────────────┘  └────────────┘  └─────────────┘ │ │
│  └──────────────────────┬───────────────────────────────┘ │
│                         │                                  │
│  ┌──────────────────────▼───────────────────────────────┐ │
│  │  Data Layer (src/services/)                          │ │
│  │  ┌────────────────────────────────────────────────┐ │ │
│  │  │  WeatherAPI (TypeScript client)                │ │ │
│  │  │  • getLatest()                                 │ │ │
│  │  │  • getRange(start, end)                        │ │ │
│  │  │  • getStats(period)                            │ │ │
│  │  │  • exportCSV(start, end)                       │ │ │
│  │  └────────────────────────────────────────────────┘ │ │
│  └──────────────────────┬───────────────────────────────┘ │
│                         │ HTTP/JSON                        │
│                         ▼                                  │
│              ┌───────────────────────┐                     │
│              │  FastAPI Backend      │                     │
│              │  (port 8000)          │                     │
│              └───────────────────────┘                     │
└────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. Data Ingestion Flow (CLI)

```
User Terminal
    │
    │ weather-app fetch
    ▼
┌──────────────────────┐
│  CLI Entry Point     │
│  (cli/cli.py)        │
└──────┬───────────────┘
       │
       │ calls
       ▼
┌──────────────────────┐
│  FetchService        │
│  (services/fetcher)  │
└──────┬───────────────┘
       │
       │ 1. Get latest timestamp
       ▼
┌──────────────────────┐
│  WeatherDatabase     │
│  (database/repo)     │
└──────────────────────┘
       │
       │ 2. Fetch new data
       ▼
┌──────────────────────┐       HTTP GET
│  AmbientClient       │─────────────────►  Ambient Weather API
│  (services/client)   │◄─────────────────  JSON response
└──────┬───────────────┘
       │
       │ 3. Parse & validate
       ▼
┌──────────────────────┐
│  Pydantic Models     │
│  (api/models.py)     │
└──────┬───────────────┘
       │
       │ 4. Upsert records
       ▼
┌──────────────────────┐       INSERT OR REPLACE
│  WeatherDatabase     │─────────────────►  DuckDB File
│  (database/repo)     │                   (weather.duckdb)
└──────────────────────┘
       │
       │ 5. Return status
       ▼
┌──────────────────────┐
│  CLI Output          │
│  "Fetched 12 records"│
└──────────────────────┘
```

### 2. Dashboard Query Flow (Web)

```
User Browser
    │
    │ http://localhost:8000
    ▼
┌──────────────────────┐
│  React Frontend      │
│  (WeatherDashboard)  │
└──────┬───────────────┘
       │
       │ fetch('/api/weather/latest')
       ▼
┌──────────────────────┐
│  TypeScript API      │
│  Client (services)   │
└──────┬───────────────┘
       │
       │ HTTP GET /api/weather/latest
       ▼
┌──────────────────────┐
│  FastAPI Router      │
│  (api/routes.py)     │
└──────┬───────────────┘
       │
       │ calls
       ▼
┌──────────────────────┐       SELECT * FROM weather_data
│  WeatherDatabase     │─────────────────►  DuckDB File
│  (database/repo)     │◄─────────────────  Result rows
└──────┬───────────────┘
       │
       │ Pydantic serialize
       ▼
┌──────────────────────┐
│  WeatherReading      │
│  (Pydantic model)    │
└──────┬───────────────┘
       │
       │ JSON response
       ▼
┌──────────────────────┐
│  TypeScript Types    │
│  (frontend types)    │
└──────┬───────────────┘
       │
       │ render
       ▼
┌──────────────────────┐
│  Recharts Component  │
│  (TemperatureChart)  │
└──────────────────────┘
```

### 3. Backfill Flow (CLI with Checkpoints)

```
User Terminal
    │
    │ weather-app backfill --start 2024-01-01 --end 2024-12-31
    ▼
┌──────────────────────┐
│  Backfill Service    │
│  (services/backfill) │
└──────┬───────────────┘
       │
       │ 1. Check for checkpoint file
       ▼
┌──────────────────────┐
│  checkpoint.json     │
│  {"last_processed":  │
│   "2024-06-15", ...} │
└──────┬───────────────┘
       │
       │ 2. Resume from last date
       │    (or start from beginning)
       ▼
┌──────────────────────┐
│  For each day:       │
│  ┌────────────────┐ │
│  │ Fetch 288 recs │ │──► Ambient Weather API
│  └────────┬───────┘ │
│           │          │
│  ┌────────▼───────┐ │
│  │ Batch insert   │ │──► DuckDB (1000/batch)
│  └────────┬───────┘ │
│           │          │
│  ┌────────▼───────┐ │
│  │ Update chkpt   │ │──► checkpoint.json
│  └────────────────┘ │
│                     │
│  [Repeat 365 times] │
└──────┬───────────────┘
       │
       │ 3. Final report
       ▼
┌──────────────────────┐
│  CLI Output          │
│  "Processed 365 days"│
│  "Inserted 105,120"  │
└──────────────────────┘
```

---

## Database Schema

### weather_data Table

```sql
CREATE TABLE weather_data (
    timestamp TIMESTAMP PRIMARY KEY,      -- Reading time (UTC)
    temperature DOUBLE,                   -- °F
    feels_like DOUBLE,                    -- °F (heat index/wind chill)
    humidity DOUBLE,                      -- % (0-100)
    dew_point DOUBLE,                     -- °F
    wind_speed DOUBLE,                    -- mph
    wind_gust DOUBLE,                     -- mph (peak gust)
    wind_direction INTEGER,               -- degrees (0-360)
    pressure DOUBLE,                      -- inHg (barometric)
    precipitation_rate DOUBLE,            -- in/hr
    precipitation_total DOUBLE,           -- inches (cumulative)
    solar_radiation DOUBLE,               -- W/m²
    uv_index INTEGER,                     -- UV index (0-11+)
    battery_ok BOOLEAN                    -- Battery status
);

CREATE INDEX idx_timestamp ON weather_data(timestamp);
```

**Key Design Decisions:**
- **PRIMARY KEY on timestamp:** Ensures uniqueness, enables `INSERT OR REPLACE` for idempotency
- **No foreign keys:** Single-table design for simplicity
- **No daily_aggregates table:** DuckDB is fast enough to aggregate on-the-fly
- **Columnar storage:** DuckDB stores columns separately, enabling 10x+ compression
- **Full resolution:** No downsampling or aggregation needed for 50-year retention

**Storage Estimates:**
- 5-minute cadence: 288 readings/day
- 50 years: ~5.2 million readings
- Uncompressed: ~5.2 GB (1KB/reading)
- **DuckDB compressed: ~500MB-1GB** (columnar compression + dictionary encoding)

---

## API Design

### REST Endpoints (FastAPI)

**Base URL:** `http://localhost:8000/api`

#### Health Check
```
GET /api/health

Response 200 OK:
{
  "status": "ok",
  "database": "connected",
  "total_records": 125432,
  "latest_reading": "2024-12-31T23:55:00Z",
  "oldest_reading": "2024-01-01T00:00:00Z",
  "database_size_mb": 45.2
}
```

#### Latest Reading
```
GET /api/weather/latest

Response 200 OK:
{
  "timestamp": "2024-12-31T23:55:00Z",
  "temperature": 72.5,
  "feels_like": 71.8,
  "humidity": 65.0,
  ...
}
```

#### Historical Range
```
GET /api/weather/range?start=2024-01-01T00:00:00Z&end=2024-01-31T23:59:59Z

Response 200 OK:
[
  {"timestamp": "2024-01-01T00:00:00Z", "temperature": 45.2, ...},
  {"timestamp": "2024-01-01T00:05:00Z", "temperature": 45.1, ...},
  ...
]

Query Parameters:
- start: ISO 8601 timestamp (required)
- end: ISO 8601 timestamp (required)
- limit: Max records (default: 10000)
```

#### Statistics
```
GET /api/weather/stats?period=24h

Response 200 OK:
{
  "period": "24h",
  "avg_temperature": 68.5,
  "min_temperature": 62.3,
  "max_temperature": 75.2,
  "total_precipitation": 0.15,
  ...
}

Query Parameters:
- period: "24h" | "7d" | "30d" | "1y"
```

#### CSV Export
```
GET /api/export?start=2024-01-01T00:00:00Z&end=2024-12-31T23:59:59Z

Response 200 OK:
Content-Type: text/csv
Content-Disposition: attachment; filename="weather_data.csv"

timestamp,temperature,humidity,...
2024-01-01T00:00:00Z,45.2,65.0,...
...
```

**Type Safety:**
- Backend: Pydantic models validate request/response data
- Auto-generated OpenAPI schema at `/docs` (Swagger UI)
- Frontend: TypeScript types generated from OpenAPI schema (planned)

---

## Deployment Architecture

### Docker Compose (Recommended)

```yaml
version: '3.8'
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data          # DuckDB file persistence
      - ./.env:/app/.env          # API keys
    environment:
      - DATABASE_PATH=/app/data/weather.db
    restart: unless-stopped

  frontend:
    build:
      context: ./web
      dockerfile: ../Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

**User Experience:**
```bash
# One-command deployment
docker-compose up -d

# Access dashboard
open http://localhost:8000

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Native Python (Development)

**Backend:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn weather_app.api.main:app --reload --port 8000
```

**Frontend:**
```bash
cd web
npm install
npm run dev  # Vite dev server on port 3000
```

**CLI:**
```bash
pip install -e .
weather-app --help
```

---

## Configuration Management

### Environment Variables (.env file)

```bash
# Required
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APPLICATION_KEY=your_app_key_here
STATION_MAC_ADDRESS=00:11:22:33:44:55

# Optional
DATABASE_PATH=./weather.db          # Default: ./weather.db
LOG_LEVEL=INFO                       # Default: INFO
API_TIMEOUT=30                       # Default: 30 seconds
RETRY_MAX_ATTEMPTS=5                 # Default: 5
```

**Security:**
- `.env` file is `.gitignored` (never committed)
- Keys stored locally only (never transmitted)
- File permissions: `chmod 600 .env` (recommended)
- Future: Web UI configuration with encrypted storage

---

## Performance Characteristics

### DuckDB vs SQLite Benchmarks

| Operation | SQLite | DuckDB | Speedup |
|-----------|--------|--------|---------|
| **INSERT 10K rows** | 2.3s | 0.18s | **12.8x** |
| **SELECT AVG (1 year)** | 4.1s | 0.11s | **37.3x** |
| **SELECT AVG (50 years)** | 180s | 3.2s | **56.2x** |
| **Complex aggregation** | 12.5s | 0.25s | **50x** |
| **Full table scan** | 45s | 1.8s | **25x** |

**Query Example (1 year of daily averages):**
```sql
-- This query runs in 0.11s on DuckDB vs 4.1s on SQLite
SELECT date_trunc('day', timestamp) AS day,
       AVG(temperature) AS avg_temp,
       MIN(temperature) AS min_temp,
       MAX(temperature) AS max_temp
FROM weather_data
WHERE timestamp >= '2024-01-01'
GROUP BY day
ORDER BY day;
```

**Why DuckDB is Faster:**
- **Columnar storage:** Only reads temperature column (not all 14 columns)
- **Vectorized execution:** Processes 1000s of rows per CPU instruction
- **Compression:** Dictionary encoding, RLE, bit-packing reduce I/O
- **Parallel processing:** Multi-threaded query execution

---

## Design Philosophy

### Pragmatic Over Dogmatic

From peer review feedback:

> "Don't over-engineer Phase 1 - Your current approach is good"
> "Storage is cheap - don't obsess over complex retention"
> "Type safety end-to-end prevents entire classes of bugs"

**Applied Principles:**
1. **Direct SQL over ORM** - Repository pattern with static methods, no SQLAlchemy overhead
2. **Full resolution storage** - Simplified from 3yr+50yr hybrid to 50yr full resolution
3. **Type safety** - Pydantic (Python) + TypeScript (frontend) catch bugs at compile time
4. **Docker first** - One-command deployment for better UX

---

## Key Architectural Decisions

For detailed rationale on major technology choices, see:
- [ADR-001: FastAPI Backend](decisions/001-fastapi-backend.md)
- [ADR-002: DuckDB Migration](decisions/002-duckdb-migration.md)
- [ADR-003: TypeScript Frontend](decisions/003-typescript-frontend.md)
- [ADR-004: Docker Deployment](decisions/004-docker-deployment.md)
- [ADR-005: Retention Strategy](decisions/005-retention-strategy.md)

---

## Future Architecture (Phase 3)

### Planned Enhancements

```
┌───────────────────────────────────────────────────────────┐
│  Phase 3 Architecture (Q1 2026)                           │
│                                                            │
│  ┌──────────────┐     ┌──────────────┐                   │
│  │  Web Config  │     │  APScheduler │                   │
│  │  UI (auth)   │     │  (built-in)  │                   │
│  └──────────────┘     └──────────────┘                   │
│                                                            │
│  ┌──────────────────────────────────────────────┐        │
│  │  Multi-Station Support (2-5 stations)        │        │
│  │  • station_id column in database             │        │
│  │  • Station selector in UI                    │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
│  ┌──────────────────────────────────────────────┐        │
│  │  Real-time Updates (WebSocket)               │        │
│  │  • ws://localhost:8000/ws                    │        │
│  │  • Push new readings to dashboard            │        │
│  └──────────────────────────────────────────────┘        │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## Document Changelog

- **2026-01-02:** Initial architecture overview extracted from detailed architecture.md
- **2026-01-02:** Focused on high-level system design, deferred details to ADRs and technical guides
