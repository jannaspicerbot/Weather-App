# Weather App — Product Requirements Document (PRD)

**Version:** 1.0
**Date:** 2026-01-02
**Author:** Janna Spicer

---

## Executive Summary

A lightweight, local-first application for Ambient Weather station owners who prefer owning their data and avoiding subscription dashboards. The app collects, stores, visualizes, and exports weather station data for personal use by hobbyists, researchers, and small-scale operators.

**Target Users:** Homeowners, hobbyists, small farms, environmental researchers
**Deployment:** Local (Raspberry Pi, PC) or Docker containers
**Data Ownership:** 100% user-controlled, no cloud dependencies

---

## Problem Statement

**What problem are we solving?**

Ambient Weather station owners are dissatisfied with the vendor's dashboard and subscription model. They need reliable, local control over their weather data for decision-making in agriculture, environmental monitoring, industrial controls, and research.

**Jobs-to-be-Done (JTBD):**

1. *"As a station owner, I want automated data ingestion and reliable backfill so I can analyze historical trends and make operational decisions."*

2. *"As a station owner, I want a local, secure web dashboard to visualize my data and export it in standard formats (CSV) for use in other tools."*

---

## Goals & Success Criteria

### Business Goals

- Provide a free, open-source alternative to vendor dashboards
- Enable 100% local data ownership with no vendor lock-in
- Support long-term data retention (50 years) for trend analysis
- Make deployment simple enough for non-technical users (one-command Docker setup)

### Success Metrics

- **Availability:** 99.9% uptime (software-level; hardware/network are user responsibility)
- **Data Reliability:** 99.9% ingestion success rate (API calls that succeed when network/API are available)
- **Performance:** Dashboard loads in <1 second; 50-year dataset queries complete in <5 seconds
- **Adoption:** GitHub stars, Docker pulls, community contributions

---

## User Personas

### Primary Persona: Homeowner Hobbyist

- **Background:** Owns Ambient Weather station, tech-savvy but not a developer
- **Goals:** Track weather trends, share data with neighbors, export for personal records
- **Pain Points:** Vendor dashboard is slow, expensive, doesn't allow easy export
- **Technical Comfort:** Can follow Docker setup instructions, prefers GUI over CLI

### Secondary Persona: Small Farm Operator

- **Background:** Uses weather data for irrigation, frost protection, crop planning
- **Goals:** Historical analysis, real-time alerts, integration with farm management tools
- **Pain Points:** Needs reliable local data even when internet is unstable
- **Technical Comfort:** Comfortable with command-line tools, may run on Raspberry Pi

### Tertiary Persona: Environmental Researcher

- **Background:** Collecting long-term weather data for climate studies
- **Goals:** 50-year retention, high-resolution data, standard export formats (CSV)
- **Pain Points:** Vendor retention policies delete old data, export options limited
- **Technical Comfort:** Can write scripts, prefers open data formats

---

## User Experience

### Installation & Setup

**Docker (Recommended for Most Users):**
1. Download docker-compose.yml
2. Copy .env.example to .env and add API keys
3. Run: `docker-compose up -d`
4. Access dashboard at http://localhost:8000

**Native Python (For Developers):**
1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Configure .env file with API keys
5. Initialize database: `weather-app init-db`
6. Run backend: `uvicorn weather_app.api.main:app`
7. Run frontend: `cd web && npm run dev`

### Core User Flows

#### Flow 1: Initial Data Collection
1. User configures API keys in .env file
2. User runs backfill command to populate historical data
3. System fetches data in daily chunks with progress tracking
4. User can interrupt and resume backfill at any time (checkpoint support)

#### Flow 2: Ongoing Data Ingestion
1. User schedules periodic fetch command (via cron, systemd, or manually)
2. System automatically fetches latest readings every 5 minutes
3. Data is stored locally with deduplication
4. User can view latest data in web dashboard

#### Flow 3: Data Visualization
1. User opens web dashboard in browser
2. Dashboard displays current conditions and interactive charts
3. User selects date range for historical analysis
4. Charts update with zoom/pan controls
5. User exports selected data to CSV

#### Flow 3: iPad Dashboard Access
1. User opens Safari on iPad
2. Navigates to http://[local-ip]:8000
3. Responsive web interface adapts to tablet screen
4. Touch-friendly chart interactions (pinch-zoom, swipe)

---

## Functional Requirements

### Data Collection
- **REQ-1.1:** Fetch latest measurements from Ambient Weather API at native device cadence (typically 5 minutes)
- **REQ-1.2:** Support resumable backfill by date range with checkpoint files
- **REQ-1.3:** Handle API rate limits with exponential backoff and retry logic
- **REQ-1.4:** Deduplicate readings automatically (idempotent writes)

### Data Storage
- **REQ-2.1:** Store all weather measurements locally in embedded database
- **REQ-2.2:** Support 50-year full-resolution retention (no data aggregation required)
- **REQ-2.3:** Estimated storage: 500MB-1GB for 50 years of data (with compression)
- **REQ-2.4:** Single-file database for easy backup (copy file to backup location)

### Data Visualization
- **REQ-3.1:** Web dashboard with real-time data display
- **REQ-3.2:** Interactive charts for temperature, humidity, wind, precipitation, pressure
- **REQ-3.3:** Date range selector for historical analysis
- **REQ-3.4:** Responsive design (desktop, tablet, mobile)
- **REQ-3.5:** Auto-refresh every 5 minutes when viewing "latest" data

### Data Export
- **REQ-4.1:** Export to CSV format via CLI command
- **REQ-4.2:** Export to CSV format via web dashboard download button
- **REQ-4.3:** Support date range selection for exports
- **REQ-4.4:** Include all measured fields with timestamps

### CLI Tools
- **REQ-5.1:** `init-db` - Initialize database schema
- **REQ-5.2:** `fetch` - Fetch latest data from API
- **REQ-5.3:** `backfill --start DATE --end DATE` - Backfill historical data
- **REQ-5.4:** `export --start DATE --end DATE --output FILE` - Export to CSV
- **REQ-5.5:** `info` - Display database statistics (record count, date range, size)

### Configuration
- **REQ-6.1:** Store API keys in .env file (never committed to git)
- **REQ-6.2:** Provide .env.example template in repository
- **REQ-6.3:** Support configuration of database path, log level, API timeout, retry settings

---

## Non-Functional Requirements

### Performance
- **NFR-1.1:** Dashboard loads in <1 second for recent data (last 24 hours)
- **NFR-1.2:** Full 50-year dataset queries complete in <5 seconds
- **NFR-1.3:** API fetch operations complete in <10 seconds (network permitting)
- **NFR-1.4:** Backfill processes 1 year of data in <30 minutes

### Reliability
- **NFR-2.1:** Software-level availability target: 99.9% (excludes hardware/network failures)
- **NFR-2.2:** Ingestion success rate: 99.9% when API is available
- **NFR-2.3:** Automatic retry with exponential backoff for transient failures
- **NFR-2.4:** Idempotent writes prevent data duplication on retry

### Portability
- **NFR-3.1:** Runs on Linux, macOS, Windows via Docker Compose
- **NFR-3.2:** Tested on Raspberry Pi 4 with 4GB RAM + SSD
- **NFR-3.3:** Development environment: HP Pavilion Laptop 16-ag0xxx (15GB RAM)

### Security
- **NFR-4.1:** API keys stored locally in .env file (never transmitted off-device)
- **NFR-4.2:** .env file must be in .gitignore (prevent accidental commit)
- **NFR-4.3:** File permissions: chmod 600 .env recommended
- **NFR-4.4:** Future: Web UI configuration with encrypted storage

### Observability
- **NFR-5.1:** Structured logging with INFO/DEBUG levels
- **NFR-5.2:** Health endpoint returns database status and record counts
- **NFR-5.3:** Log all API errors with request/response details

---

## Out of Scope (Future Phases)

**Phase 3 Features (Planned but not in MVP):**
- Multi-station support (2-5 stations)
- Built-in scheduler (APScheduler) - currently requires cron/systemd
- Web UI configuration interface (currently .env file only)
- User authentication for web dashboard (currently open access)
- Real-time WebSocket updates (currently polling)
- Mobile app (React Native)
- Weather alerts and notifications
- Machine learning forecasting
- Additional export formats (JSON, Parquet)

**Not Planned:**
- Cloud hosting or SaaS offering
- Multi-user/multi-tenant support
- Integration with third-party weather services
- Advanced analytics or AI features (beyond basic charting)

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Ambient Weather API changes/deprecation | High | Medium | Decouple API client with adapter pattern; document API version |
| API rate limits during backfill | Medium | High | Implement exponential backoff, respect Retry-After headers, chunk backfill |
| Local hardware failures (SD card, power) | High | Medium | Recommend SSD over SD card, UPS, document backup procedures |
| User misconfiguration (.env errors) | Low | High | Provide .env.example, validation on startup, clear error messages |
| Database corruption | Medium | Low | Single-file design makes backups trivial; recommend periodic backups |

---

## Success Metrics (Detailed)

### Adoption Metrics
- GitHub stars: >100 in first 6 months
- Docker pulls: >500 in first 6 months
- Active users: >50 confirmed deployments

### Technical Metrics
- Test coverage: >70%
- Docker build success rate: 100%
- Documentation completeness: All user flows documented

### User Satisfaction
- GitHub issues response time: <48 hours
- User-reported bugs: <5 critical bugs in first 3 months
- Community contributions: >3 external contributors

---

## Acceptance Criteria

**MVP is complete when:**

1. ✅ A new user can run `docker-compose up -d` and access dashboard at http://localhost:8000
2. ✅ User can configure .env file with API keys and station MAC address
3. ✅ User can initialize database with `weather-app init-db`
4. ✅ User can backfill historical data with `weather-app backfill --start DATE --end DATE`
5. ✅ User can view interactive charts in web dashboard (temperature, humidity, wind, precipitation)
6. ✅ User can export data to CSV with `weather-app export`
7. ✅ All automated tests pass on CI (pytest, frontend tests, Docker build)
8. ✅ Documentation includes: README, setup guide, CLI reference, troubleshooting

---

## Timeline & Phases

### Phase 1: MVP Backend & CLI ✅ **COMPLETED**
- CLI with Click framework
- DuckDB database integration
- Ambient Weather API client
- Basic fetch and backfill commands
- **Completion:** December 2025

### Phase 2: Web Dashboard & Deployment ✅ **COMPLETED**
- FastAPI backend with OpenAPI schema
- React + TypeScript frontend
- Interactive charts with Recharts
- Docker Compose deployment
- End-to-end type safety
- **Completion:** January 2026

### Phase 3: Polish & Advanced Features 🔄 **PLANNED**
- Multi-station support
- Built-in scheduler (APScheduler)
- Web UI configuration
- User authentication
- Real-time WebSocket updates
- **Target:** Q1 2026

---

## Document Changelog

- **2026-01-01:** Initial PRD draft based on conversations and repository analysis
- **2026-01-02:** Updated to reflect Phase 2 completion (DuckDB, FastAPI, React+TypeScript)
- **2026-01-02:** Reorganized as focused PRD (extracted technical details to architecture docs)
