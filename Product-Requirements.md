# Weather App — PRD (Finalized)
Date: 2026-01-01  
Author: Drafted from repository jannaspicerbot/Weather-App and conversation with jannaspicerbot

## Title
Weather App — Ambient Weather data collection, processing, and visualization

## Summary
A lightweight, local-first Python application for Ambient Weather station owners who prefer owning their data and avoiding subscription dashboards. The app collects, backfills, stores, visualizes, and exports Ambient Weather station data for personal use (hobbyists). MVP runs locally on devices such as Raspberry Pi / local PC, supports 1–5 stations, and implements a hybrid retention policy (full-resolution for recent 3 years, aggregated for older data).

## Background & Context
- Language: Python. Repository contains CLI scripts (ambient_weather_fetch.py, update_weather.py, backfill_weather.py), visualization code (ambient_weather_visualize.py using Plotly), docs (README, QUICKSTART, ENV_SETUP_GUIDE), and test fixtures.
- Motivation: Owners dissatisfied with Ambient Weather's dashboard/subscription offering need reliable, local control over accurate weather data for decision-making (agriculture, environmental/industrial controls, research).

## Problem Statement & JTBD
- Problem: Station owners need a reliable, local pipeline that ingests, backfills, stores, and visualizes sensor data with long-term retention and export capabilities.
- JTBD:
  - “As a station owner I want automated ingestion and reliable backfill so I can analyze trends and make operational decisions.”
  - “As a station owner I want a local, secure web dashboard to visualize data and export CSVs.”

## Goals & Outcomes
- Deliver a local-first product that:
  - Fetches and stores native-cadence readings from Ambient Weather.
  - Performs resumable backfills and supports scheduling via external schedulers.
  - Provides an interactive web dashboard (Plotly) and CLI tools.
  - Keeps CSV export as the canonical export format.
  - Implements hybrid 50-year retention: full-resolution for 3 years, daily aggregates for older data.
- Measurable outcomes:
  - Software-level availability target: realistically start at 99.9% (document hardware/network caveats; 99.999% is aspirational and depends on user hardware).
  - Ingestion success rate (software-level): start target 99.9%.
  - Visualization responsiveness: small ranges <1s; aggregated multi-year queries <5s (hardware-dependent).

## User Experience

Interfaces
1. CLI (existing scripts; fetch/update/backfill/visualize/export)
2. Web Dashboard (required for MVP)
3. iPad (future; responsive web UI or native app later)

UX Flows
1. CLI
   - Install dependencies
   - Configure API key and station ID (via .env or OS keyring)
   - Run initial backfill
   - Schedule periodic updates (cron/systemd)
   - Generate visualizations or download CSVs

2. Web Dashboard
   - Visit local dashboard URL
   - Create local profile
   - Enter Ambient Weather API Key and App Key
   - Specify date range
   - Run initial backfill (UI-triggered, uses backfill script)
   - Schedule periodic updates (UI provides cron/systemd snippets; scheduling remains external)
   - Generate visualizations (interactive charts)
   - Save preferences (date range, chart defaults, station selection)

   Security note: Web UI must provide a secure local method to store keys (see Security & Secrets).

3. iPad
   - Future flow TBD (dashboard will be responsive; later consider an iPad-optimized UI)

## High-Level Flow
1. Configure environment (API keys, station MAC, storage location). Keys stored locally and securely.
2. Run initial backfill to populate historical data.
3. Schedule periodic updates via external scheduler (cron/systemd).
4. Store native-cadence data in local DB; apply downsampling/aggregation for long-term retention.
5. Web dashboard queries DB and renders interactive charts; exports CSV on demand.

## Functional Requirements (final)
- Fetch latest measurements from Ambient Weather API at native device cadence.
- Support resumable, chunked backfill by date range.
- Store data in local DB (SQLite by default).
- Implement hybrid retention: full-resolution for 3 years, daily aggregates for years 4–50.
- Provide interactive web dashboard (Plotly), CLI, and CSV export (CSV only).
- Provide optional local username/password for Web UI access.
- Store user API/App keys securely on the local device (OS keyring preferred; optional encrypted store).
- Scheduling handled by external scheduler; provide sample cron/systemd files.
- CI/CD: GitHub Actions for tests, linting; publishable release artifacts (PyPI/Docker optional).

## Non-Functional Requirements
- Portability: runs on typical Linux/macOS PCs and local devices.
- Minimum development hardware: HP Pavilion Laptop 16-ag0xxx with 15 GB RAM (development environment). The application will be tested on simpler hardware (e.g., Raspberry Pi 4 / 4GB + SSD) to confirm broader compatibility; any limitations discovered will be documented and addressed.
- Scalability: support 1–5 stations in MVP.
- Reliability: idempotent writes, retries with exponential backoff, resumable backfill.
- Performance: visualization response targets described above.
- Observability: structured logging, health endpoint, basic metrics.
- Security: no secrets leave the local device. Keys are stored in OS keyring or encrypted local store.

## Storage & Retention (final decisions)
- Default DB: SQLite (single-file) for simplicity and portability.
- Retention policy:
  - Store native device cadence readings for the most recent 3 years (full resolution).
  - Compute and store daily aggregates (min/avg/max/totals) for older data up to 50 years.
- Backup: provide scripts for DB backup to local external storage (USB/NAS); document restore procedure.
- Migration: provide scripts to migrate to InfluxDB or TimescaleDB for advanced users later.

## Data Model (suggested)
- readings: id, station_mac, timestamp_utc (indexed), temperature_c, humidity_pct, pressure_hpa, wind_speed_mps, wind_dir_deg, rainfall_mm, solar_lux, battery_level, raw_payload (json)
- daily_aggregates: station_mac, date, avg_temp, min_temp, max_temp, total_rain, etc.
- Unique constraint/index on (station_mac, timestamp_utc) for idempotency.

## Web UI Authentication & Key Storage
- Web UI auth: optional local username/password (user-managed). Credentials stored hashed in local DB.
- Keys: use OS keyring (recommended) for storing Ambient API/App keys securely. Provide fallback: encrypted local store protected by user passphrase.
- Ensure .env is .gitignored and that CLI usage continues to support .env for advanced users.

## Scheduling
- External scheduling only (MVP). Provide examples for cron and systemd timers in repo docs.

## Exports
- CSV only for MVP. Export endpoint and UI download available.

## Observability & Monitoring
- /api/health endpoint for local checks.
- Structured logs with rotation.
- Metrics: last successful fetch timestamp, fetch success/failure counts, backfill progress, DB insert errors.

## Testing & CI/CD
- Unit tests: parser, DB upsert logic, backfill checkpointing.
- Integration tests: sample dataset (test DB), full backfill run on generated data.
- GitHub Actions: run tests and linters on PRs; pack releases (PyPI/Docker optional).

## Acceptance Criteria (MVP)
- A new user can:
  - Initialize DB and perform an initial backfill (or load sample dataset).
  - Run scheduled updates via cron/systemd and avoid duplicate inserts.
  - Start web dashboard locally, view recent interactive charts, and export CSVs.
  - Store API keys locally and securely; optional local auth protects the UI.
- Tests pass on CI; basic integration test available using the test DB.

## Risk Assessment & Mitigations
- Ambient Weather API changes/rate limits → retries, backoff, chunked backfill, and robust error logging.
- Local hardware failures → recommend SSD, UPS, periodic backups.
- Uptime expectations → document realistic hardware-bound limits; target software-level 99.9% initially.

## Open Questions (resolved / remaining)
Resolved from your input:
- Target users: hobbyists (personal device owners). Local-only for MVP.
- Storage preference: SQLite (recommended) with migration path.
- Scale: 1–5 stations supported.
- Retention strategy: hybrid — full-resolution for 3 years + daily aggregates up to 50 years.
- Sampling: store native device cadence.
- Web UI: interactive Plotly-based dashboard; optional local auth; keys stored locally (OS keyring).
- Export: CSV only.
- CI/CD: GitHub Actions yes.
- Stakeholders: you (solo developer) and community; you approve changes.

Remaining small decisions to finalize during implementation:
- Exact retention durations and thresholds configurable (default: 3 years for full-resolution).
- Default fetch cadence behavior (follow device cadence by default; allow override via config).

## Changelog
- 2026-01-01: Finalized PRD with confirmed retention, sampling, web UI auth, and hardware minimum updated to reflect developer environment and the need to test on simpler hardware.
