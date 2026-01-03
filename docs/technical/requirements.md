# Weather App — PRD (Finalized)
Date: 2026-01-01  
Author: Drafted from repository jannaspicerbot/Weather-App and conversation with jannaspicerbot

## Title
Weather App — Ambient Weather data collection, processing, and visualization

## Summary
A lightweight, local-first Python application for Ambient Weather station owners who prefer owning their data and avoiding subscription dashboards. The app collects, backfills, stores, visualizes, and exports Ambient Weather station data for personal use (hobbyists). MVP runs locally on devices such as Raspberry Pi / local PC or in Docker containers. Supports single station with 50-year full-resolution retention using DuckDB's columnar storage and compression.

## Background & Context
- Language: Python (backend) and TypeScript (frontend). Repository contains CLI (Click framework), FastAPI backend, React+TypeScript frontend with Recharts visualization, DuckDB database, comprehensive docs, and test fixtures.
- Motivation: Owners dissatisfied with Ambient Weather's dashboard/subscription offering need reliable, local control over accurate weather data for decision-making (agriculture, environmental/industrial controls, research).

## Problem Statement & JTBD
- Problem: Station owners need a reliable, local pipeline that ingests, backfills, stores, and visualizes sensor data with long-term retention and export capabilities.
- JTBD:
  - “As a station owner I want automated ingestion and reliable backfill so I can analyze trends and make operational decisions.”
  - “As a station owner I want a local, secure web dashboard to visualize data and export CSVs.”

## Goals & Outcomes
- Deliver a local-first product that:
  - Fetches and stores native-cadence readings from Ambient Weather.
  - Performs resumable backfills with checkpoint support.
  - Provides an interactive web dashboard (React+TypeScript+Recharts) and CLI tools.
  - Keeps CSV export as the canonical export format.
  - Implements 50-year full-resolution retention using DuckDB's columnar storage.
  - One-command deployment via Docker Compose.
- Measurable outcomes:
  - Software-level availability target: 99.9% (document hardware/network caveats).
  - Ingestion success rate (software-level): 99.9%.
  - Visualization responsiveness: small ranges <1s; 50-year full dataset queries <5s (DuckDB optimization).

## User Experience

Interfaces
1. CLI (existing scripts; fetch/update/backfill/visualize/export)
2. Web Dashboard (required for MVP)
3. iPad (future; responsive web UI or native app later)

UX Flows
1. CLI
   - Install via Docker Compose or pip
   - Configure API key and station MAC (via .env file)
   - Initialize database: `weather-app init-db`
   - Run backfill: `weather-app backfill --start 2024-01-01 --end 2024-12-31`
   - Fetch latest: `weather-app fetch`
   - Export data: `weather-app export --start 2024-01-01 --end 2024-12-31 --output data.csv`
   - View database info: `weather-app info`

2. Web Dashboard
   - Visit http://localhost:3000 (Vite dev) or http://localhost:8000 (Docker)
   - View real-time weather data and interactive charts
   - Select date ranges for historical analysis
   - Download CSV exports
   - Responsive design works on desktop, tablet, and mobile

3. Docker Deployment
   - Run `docker-compose up -d`
   - Access dashboard at http://localhost:8000
   - All data persisted in Docker volumes

## High-Level Flow
1. Configure environment (API keys, station MAC) via .env file.
2. Initialize DuckDB database with schema.
3. Run initial backfill to populate historical data (resumable with checkpoints).
4. Optionally schedule periodic fetches via cron/systemd (or run manually).
5. Store native-cadence data in DuckDB with 50-year full-resolution retention.
6. Web dashboard (React+TypeScript) queries FastAPI backend, renders interactive Recharts visualizations.
7. Export data to CSV on demand via CLI or web UI.

## Functional Requirements (final)
- Fetch latest measurements from Ambient Weather API at native device cadence.
- Support resumable, chunked backfill by date range with checkpoint files.
- Store data in DuckDB (embedded analytical database, 10-100x faster than SQLite for time-series).
- Implement 50-year full-resolution retention using DuckDB's columnar compression.
- Provide interactive web dashboard (React+TypeScript+Recharts), FastAPI backend, CLI (Click), and CSV export.
- Store API/App keys in .env file (local device only, never transmitted).
- Scheduling handled by external scheduler (optional); provide sample cron/systemd files.
- Docker Compose for one-command deployment.
- CI/CD: GitHub Actions for tests, linting, Docker builds.

## Non-Functional Requirements
- Portability: runs on Linux/macOS/Windows via Docker Compose or native Python.
- Minimum development hardware: HP Pavilion Laptop 16-ag0xxx with 15 GB RAM (development environment). Tested on Raspberry Pi 4 / 4GB + SSD for broader compatibility.
- Scalability: Currently supports 1 station (future: multi-station support).
- Reliability: idempotent writes (UNIQUE constraint on timestamp), retries with exponential backoff, resumable backfill with checkpoints.
- Performance: DuckDB provides 10-100x speedup over SQLite for analytical queries; visualization <1s for small ranges, <5s for 50-year dataset.
- Observability: structured logging (Python logging), health endpoint (/api/health), database metrics.
- Security: secrets stored in .env file (never transmitted off-device, .env is .gitignored).

## Storage & Retention (final decisions)
- Database: DuckDB (single-file, embedded analytical database with columnar storage).
- Retention policy: 50 years full-resolution storage (no aggregation needed - "storage is cheap").
- Storage estimate: 5-minute cadence for 50 years = ~5.2M readings = ~500MB-1GB with DuckDB compression.
- Backup: DuckDB file can be copied directly; provide backup documentation.
- Future migration: DuckDB supports Parquet export for migration to InfluxDB/TimescaleDB if needed.

## Data Model
- weather_data table:
  - timestamp: TIMESTAMP PRIMARY KEY (indexed for time-series queries)
  - temperature: DOUBLE (Fahrenheit)
  - feels_like: DOUBLE (Fahrenheit)
  - humidity: DOUBLE (percentage)
  - dew_point: DOUBLE (Fahrenheit)
  - wind_speed: DOUBLE (mph)
  - wind_gust: DOUBLE (mph)
  - wind_direction: INTEGER (degrees)
  - pressure: DOUBLE (inHg)
  - precipitation_rate: DOUBLE (in/hr)
  - precipitation_total: DOUBLE (inches)
  - solar_radiation: DOUBLE (W/m²)
  - uv_index: INTEGER
  - battery_ok: BOOLEAN
  - No daily_aggregates table (full resolution only)

## API Keys & Configuration
- API keys stored in .env file (AMBIENT_API_KEY, AMBIENT_APPLICATION_KEY, STATION_MAC_ADDRESS).
- .env file is .gitignored to prevent accidental commit.
- Keys never transmitted off local device.
- Future: Web UI configuration interface with secure storage.

## Scheduling
- Optional external scheduling via cron/systemd for automated fetches.
- Manual CLI execution supported.
- Future: Built-in scheduler with APScheduler.

## Exports
- CSV export via CLI: `weather-app export --start DATE --end DATE --output file.csv`
- Future: Web UI export with date range selector.

## Observability & Monitoring
- FastAPI /api/health endpoint returns database status and record counts.
- Python logging with INFO/DEBUG levels.
- Future: Structured JSON logging, Prometheus metrics endpoint.

## Testing & CI/CD
- Python unit tests with pytest for API client, database operations, CLI commands.
- TypeScript tests with Vitest for frontend components.
- Integration tests with test DuckDB database.
- GitHub Actions CI: pytest, black, mypy, frontend build and test.
- Docker image builds on tags.

## Acceptance Criteria (MVP)
- A new user can:
  - Run `docker-compose up -d` and access dashboard at http://localhost:8000.
  - Configure .env file with API keys and station MAC.
  - Initialize DuckDB database with `weather-app init-db`.
  - Run backfill with `weather-app backfill --start DATE --end DATE`.
  - View interactive charts in web dashboard (React+TypeScript+Recharts).
  - Export data to CSV with `weather-app export`.
- All tests pass on CI (pytest, frontend tests, Docker build).

## Risk Assessment & Mitigations
- Ambient Weather API changes/rate limits → retries, backoff, chunked backfill, and robust error logging.
- Local hardware failures → recommend SSD, UPS, periodic backups.
- Uptime expectations → document realistic hardware-bound limits; target software-level 99.9% initially.

## Technical Decisions (Resolved)
- Database: DuckDB (10-100x faster than SQLite for analytics)
- Frontend: React + TypeScript + Vite + Recharts
- Backend: FastAPI with OpenAPI schema generation
- Retention: 50 years full-resolution (no aggregation - "storage is cheap")
- Deployment: Docker Compose for one-command setup
- CLI: Click framework with commands: init-db, fetch, backfill, export, info
- Type Safety: End-to-end with Pydantic (backend) and TypeScript (frontend)
- Sampling: Native device cadence (typically 5 minutes)
- Export: CSV only (additional formats possible in future)
- CI/CD: GitHub Actions for all testing and builds

## Changelog
- 2026-01-01: Finalized PRD with confirmed retention, sampling, web UI auth, and hardware minimum.
- 2026-01-02: Updated to reflect implemented architecture - DuckDB, FastAPI, React+TypeScript, 50-year full-resolution retention, Docker Compose deployment.
