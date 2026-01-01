# Weather App — Technical Specification
Date: 2026-01-02  
Based on finalized PRD for jannaspicerbot/Weather-App

Purpose
- Provide concrete implementation details for the MVP: local-first Python app that ingests Ambient Weather data at native cadence, supports resumable backfill, stores data in SQLite with hybrid retention (3 years full-resolution, daily aggregates to 50 years), exposes an interactive web dashboard (Flask + Plotly), supports CLI operations, uses OS keyring for secret storage (with encrypted fallback), and is scheduled externally (cron/systemd).
- Serve as the authoritative reference for the upcoming implementation tasks and GitHub issue creation.

Contents
1. High-level architecture
2. Technology choices
3. Project layout
4. DB schema and retention strategy
5. Data ingestion and backfill behavior
6. Aggregation / downsampling pipeline
7. Web API and Web UI (endpoints, pages, auth)
8. CLI commands and examples
9. Configuration and secrets management
10. Scheduling, deployment, and run examples
11. Logging, observability, and health checks
12. Testing strategy and CI/CD
13. Backup & restore
14. Migration path
15. Security considerations
16. Acceptance criteria & milestones
17. Implementation epics and tasks (high level)
18. Appendix: sample snippets (SQL, systemd, cron, Dockerfile)

---

1. High-level architecture
- Components (local-only):
  - Fetcher (CLI script run by external scheduler): contacts Ambient Weather API, writes raw readings to DB.
  - Backfill (CLI script): chunked/resumable retrieval of historical records, writes to DB idempotently.
  - Aggregator (periodic job or ad-hoc CLI): computes daily aggregates and prunes/archives raw older-than-threshold data.
  - Web app (Flask): renders dashboard pages and serves JSON endpoints used by Plotly charts; provides CSV export.
  - Key store: OS keyring (primary) + encrypted-file fallback.
  - Storage: SQLite DB by default; DB file stored locally (configurable path).
- All components share the same DB and run on the user's local machine (development machine: HP Pavilion 16; verified/test on Raspberry Pi 4+).

2. Technology choices (rationale)
- Python 3.10+ (modern features, widespread support).
- Web: Flask + Jinja + Plotly.js — fastest route to ship interactive dashboard given existing Plotly usage.
- DB: SQLite via SQLAlchemy ORM — zero-config and portable for single-user local deployments.
- Migrations: Alembic for schema versioning.
- Secrets: python-keyring for OS keyring integration; fallback to encrypted local file (Fernet) using a user passphrase.
- Testing: pytest + pytest-fixtures; use sqlite in-memory or test DB copies for integration tests.
- CI: GitHub Actions for tests and linters.
- Packaging: pip-installable package, optional Dockerfile for local containerized use.
- Linting: black, isort, flake8.

3. Project layout (recommended repo structure)
- weather_app/ (package)
  - __init__.py
  - config.py               # config loader (env + defaults)
  - db/
    - models.py             # SQLAlchemy models
    - session.py            # DB session factory
    - migrations/           # Alembic managed
    - migration_scripts/    # helper scripts (create DB)
  - fetch/
    - ambient_client.py     # API client wrappers and rate-limit handling
    - fetcher.py            # fetch latest records
    - backfill.py           # backfill logic with checkpointing
  - storage/
    - repository.py         # DB interactions (inserts, upserts, aggregates)
    - retention.py          # downsampling/policy helpers
  - web/
    - app.py                # Flask app factory
    - views.py              # page views
    - api.py                # JSON endpoints (readings, export, health)
    - templates/
    - static/
    - auth.py               # local auth (user management)
  - cli/
    - cli.py                # Click-based CLI entrypoints
  - utils/
    - keyring_store.py      # keyring + encrypted fallback
    - logging_config.py
    - retry.py              # retry/backoff helpers
    - metrics.py            # basic metrics counters
  - tests/
    - unit/
    - integration/
- scripts/
  - db_init.py
  - sample_cron_entries/
  - systemd_units/
- docs/
  - QUICKSTART.md
  - ENV_SETUP_GUIDE.md
  - SCRIPTS_USAGE_GUIDE.md
- requirements.txt
- Dockerfile (optional)
- .github/workflows/ci.yml

4. DB schema and retention strategy
- Using SQLAlchemy models. Primary tables:

SQL (expressed conceptually)
- readings
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - station_mac: TEXT NOT NULL
  - timestamp_utc: DATETIME NOT NULL
  - temperature_c: REAL
  - humidity_pct: REAL
  - pressure_hpa: REAL
  - wind_speed_mps: REAL
  - wind_dir_deg: INTEGER
  - rainfall_mm: REAL
  - solar_lux: REAL
  - battery_level: REAL
  - raw_payload: JSON  -- stringified JSON
  - created_at: DATETIME DEFAULT CURRENT_TIMESTAMP
  - UNIQUE(station_mac, timestamp_utc)

- daily_aggregates
  - id: INTEGER PRIMARY KEY
  - station_mac: TEXT NOT NULL
  - date: DATE NOT NULL
  - avg_temp: REAL
  - min_temp: REAL
  - max_temp: REAL
  - total_rain_mm: REAL
  - measurement_count: INTEGER
  - created_at: DATETIME

Indexes:
- readings: index on (station_mac, timestamp_utc)
- daily_aggregates: index on (station_mac, date)

Retention policy (configurable in config.py):
- FULL_RESOLUTION_YEARS = 3 (default)
- AGGREGATION_HOLD_YEARS = 50
- Aggregator job computes daily_aggregates for range older than FULL_RESOLUTION_YEARS and then optionally removes raw readings older than FULL_RESOLUTION_YEARS (or moves them to an archive file), depending on user preference (config option: PURGE_RAW_AFTER_AGGREGATION=true/false).

5. Data ingestion and backfill behavior (detailed)
Fetcher (update workflow)
- Behavior:
  - On each run, the fetcher reads the latest timestamp for each configured station from readings table.
  - If no record exists, it requests data for a default fallback window (configurable, e.g., last 24-48 hours) or triggers backfill.
  - Calls Ambient Weather API via ambient_client with exponential backoff and jitter on failures.
  - Parses records and writes them with upsert semantics (INSERT OR IGNORE OR REPLACE pattern in SQLite). Use a transactional bulk insert for performance.
  - Logs metrics: fetched_count, inserted_count, duplicate_count, last_success_timestamp.

Backfill
- Inputs: start_date, end_date, station_mac (optional), checkpoint_file (optional)
- Behavior:
  - Break requested date range to API-safe chunks (e.g., day-by-day if API returns per-day data or use API paging).
  - After each chunk processed successfully, write/update a checkpoint JSON file that contains: { "station_mac": "...", "last_processed": "YYYY-MM-DDTHH:MM:SSZ", "chunks_done": [ ... ] }
  - On restart, read checkpoint and continue from last_processed.
  - On errors: retry per-chunk N times (configurable), escalate/log and continue or abort based on --abort-on-error flag.

Idempotency and concurrency
- Use UNIQUE constraint on (station_mac, timestamp_utc). Inserts that conflict should be ignored or cause UPDATE if the new payload is more complete. Provide both behaviors via config (INSERT_ONLY vs UPSERT).

Retry/backoff
- Use a retry helper (exponential backoff with cap and jitter). Sensitive to Ambient Weather rate-limits. Respect HTTP 429 and Retry-After headers.

6. Aggregation / downsampling pipeline
Method:
- For each station and for each day older than FULL_RESOLUTION_YEARS:
  - SELECT date(timestamp_utc) as date, COUNT(*) as n, AVG(temperature_c), MIN(temperature_c), MAX(temperature_c), SUM(rainfall_mm) FROM readings WHERE timestamp_utc BETWEEN day_start AND day_end GROUP BY date;
  - INSERT into daily_aggregates if not exists (or UPSERT).
- Optionally prune raw readings older than FULL_RESOLUTION_YEARS after successful aggregate insert (configurable).
Implementation:
- Implement aggregator.py that can be run manually or scheduled nightly to compute aggregates for windows (e.g., process last day's aggregates for older chunks).
- Use efficient SQL queries to avoid loading large amounts of data in Python where possible.

7. Web API and Web UI
Design decision: Flask app for MVP
- Flask app factory pattern: create_app(config_name)
- Use Blueprints: web.views (pages) and web.api (JSON endpoints)

Pages (templates):
- / (dashboard) — latest readings summary + charts
- /history — interactive charts with date-range selector
- /export — export page allowing CSV downloads
- /settings — profile, station config, credentials (stores via keyring), schedule instructions
- /backfill — run backfill, show progress logs (trigger asynchronous job or spawn sub-process; provide progress through polling endpoint)

API endpoints (JSON)
- GET /api/health -> { status: "ok", last_fetch: "...", db_size: ... }
- GET /api/stations -> list station metadata
- GET /api/readings?station_mac=&start=&end=&agg=raw|hour|day -> paged JSON readings or aggregated buckets (agg param)
- GET /api/summary?station_mac=&period=last24h|last7d|last30d -> summary stats
- GET /api/export?station_mac=&start=&end&format=csv -> returns CSV file download
- POST /api/backfill -> start backfill job (request body: start,end,station_mac) -> returns job_id
- GET /api/backfill/<job_id> -> status/progress logs

Web UI behavior
- Dashboard loads page and uses /api/readings to populate Plotly charts via AJAX.
- For long-running tasks (backfill), UI polls /api/backfill/<job_id> for progress updates.
- Provide user setting to enable/disable auto-downsampling/purge.
- Auth: login page if UI auth enabled; session cookies use Flask-Login with secure cookie settings.

Web UI auth specifics
- Optional local username/password:
  - Use Werkzeug security helpers (generate_password_hash, check_password_hash) or bcrypt (py-bcrypt) for stronger hashing.
  - Admin user created during setup: CLI command to create user: weather_app-cli user create --username alice
  - Password hash stored in users table in SQLite.
  - Use Flask-Login for session management.
  - Provide option to lock UI to localhost only by default (config: BIND_ADDRESS=127.0.0.1) and allow binding to 0.0.0.0 if user decides.

Key storage in Web UI
- On settings page, user enters Ambient Weather API Key & App Key.
- Store keys in OS keyring via python-keyring:
  - keyring.set_password('weather-app', username, api_key)
  - keyring.get_password('weather-app', username)
- For environments where keyring is unavailable, fallback to encrypted file:
  - Use cryptography.Fernet with user-provided passphrase to encrypt/decrypt JSON blob saved at $XDG_CONFIG_HOME/weather-app/keys.enc
  - Provide CLI helper to set/get keys and prompt for passphrase as needed.

8. CLI commands and examples
- CLI implemented with Click (weather_app.cli)
Commands (examples):
- weather-app init-db --db /path/to/weather.db
- weather-app fetch --station MAC --limit 100
- weather-app update --stations all
- weather-app backfill --station MAC --start 2024-01-01 --end 2024-01-31 --checkpoint /var/lib/weather/backfill.checkpoint.json
- weather-app aggregate --since 2023-01-01 --until 2024-01-01
- weather-app export --station MAC --start ... --end ... --out /tmp/export.csv
- weather-app user create --username alice
- weather-app key set --service ambient --username alice   (prompts for key, stores in keyring)

9. Configuration and secrets management
Configuration precedence:
1) Environment variables
2) .env file loaded by python-dotenv (ignored in Git)
3) config.py defaults

Example config options (config.py)
- DB_PATH=/var/lib/weather/weather.db
- BIND_HOST=127.0.0.1
- BIND_PORT=8080
- FULL_RESOLUTION_YEARS=3
- AGGREGATION_HOLD_YEARS=50
- PURGE_RAW_AFTER_AGGREGATION=True
- FETCH_RETRY_MAX=5
- FETCH_RETRY_BACKOFF_FACTOR=2
- LOG_LEVEL=INFO

.env.template (example)
- DB_PATH=./weather.db
- BIND_HOST=127.0.0.1
- BIND_PORT=8080
- AMBIENT_APP_KEY=
- AMBIENT_API_KEY=

Secrets management
- Preferred flow for web UI:
  - User creates local profile (username).
  - On settings page user enters Ambient keys.
  - App uses python-keyring to store keys keyed by (service='weather-app', username).
- CLI flow:
  - CLI will accept --key via stdin prompt and store to keyring if available, otherwise write to encrypted file if user chooses.

10. Scheduling, deployment, and run examples
Scheduling (external)
- Cron example (run update every 5 minutes):
  - */5 * * * * /usr/bin/env /usr/local/bin/weather-app update --stations all >> /var/log/weather/update.log 2>&1
- systemd timer example:
  - Provide unit files in scripts/systemd_units/weather-update.service and weather-update.timer (see appendix).

Deployment
- Recommended for MVP: run on local machine using Python venv:
  - python -m venv venv
  - source venv/bin/activate
  - pip install -r requirements.txt
  - weather-app init-db
  - weather-app web run   # launches Flask dev server (in production use a WSGI server below)
- Production local run (systemd + gunicorn):
  - Use gunicorn + systemd service to run Flask app; provide systemd unit skeleton.

Optional Dockerfile (skeleton) included for users preferring containerized local run (document caveats re: keyring access).

11. Logging, observability, and health checks
Logging
- Use structured JSON logs via python-json-logger or similar.
- Log rotation via logging.handlers.RotatingFileHandler + external logrotate examples.

Health endpoint
- GET /api/health returns:
  - { status: "ok", db_file_size_bytes, last_fetch_iso, last_fetch_successful: true/false }

Metrics
- Basic in-process counters (fetch_success, fetch_fail, backfill_jobs_running, last_backfill_status).
- Expose /metrics (Prometheus format) optional if user wants to run Prometheus locally (deferred MVP).

12. Testing strategy and CI/CD
Unit tests
- Parser tests for Ambient API response -> internal model conversion.
- DB repository tests (insert/upsert behavior).
- Auth tests (password hashing and login).
- Keyring fallback tests (mock keyring and encrypted store).

Integration tests
- Use synthetic test DB with generated 2 years of sample data (tool included to generate synthetic dataset).
- End-to-end test: run backfill on generated dataset and verify counts, run aggregator and verify daily aggregates, run web app test client and verify endpoints.

CI pipeline (GitHub Actions - skeleton)
- on: [push, pull_request]
- jobs:
  - lint: run black/isort/flake8
  - test: setup python, install requirements, run pytest
  - build: optional (prepare wheel / Docker build)

13. Backup & restore
Backup script (scripts/backup_db.py)
- Copies DB file to configured backup location (timestamped) and optionally compresses it.
- Provide restore script to move backup file back to DB path and run alembic downgrade/upgrade if necessary.

Recommendation: daily backup to external drive or NAS; document schedule in docs.

14. Migration path
- Provide export scripts to dump into CSV/Parquet for import into InfluxDB/TimescaleDB.
- Provide a migration tool (scripts/migrate_to_influx.py, scripts/migrate_to_timescaledb.py) that reads SQLite and writes to chosen target.

15. Security considerations
- Secrets never transmitted off-device by default.
- Use OS keyring where available; fallback to encrypted file (Fernet).
- Web UI default bind to 127.0.0.1 to avoid exposing to LAN; optional local auth recommended if binding to 0.0.0.0.
- Use CSRF protection for forms (Flask-WTF) and secure cookie settings.
- Document that user is responsible for device network security and firewall settings.

16. Acceptance criteria & milestones
MVP acceptance criteria (repeat for clarity)
- DB initialization works and schema created by db_init.
- Backfill inserts expected counts for generated sample dataset and supports resume via checkpoint.
- Update/fetch script runs idempotently and inserts no duplicates on repeated runs.
- Web dashboard runs locally, shows interactive charts for last 24h, and supports CSV export.
- Keys can be stored & retrieved via OS keyring. Fallback encrypted store works.
- Unit and integration tests pass in CI.

Milestones
- M1: Repo refactor and package layout + DB init + core fetch/upsert
- M2: Backfill with checkpointing + aggregator for daily aggregates + retention enforcement
- M3: Web app skeleton + API endpoints + Plotly charts + export
- M4: Auth + keyring integration + scheduling docs + backup/restore
- M5: Tests + CI + docs + release packaging

17. Implementation epics and tasks (high level)
Epic A — Core library & DB
- Refactor existing scripts into package modules.
- Implement DB models + Alembic migrations.
- Implement repository layer for CRUD/upsert operations.
Epic B — Fetcher & Backfill
- ambient_client with retry, fetcher CLI, backfill CLI with checkpoint.
- Tests for idempotency/resume.
Epic C — Aggregation & Retention
- Implement aggregator CLI, downsample logic, purge/archive logic.
Epic D — Web app (MVP)
- Flask app factory, templates, API endpoints, Plotly integration, CSV export.
Epic E — Auth & Key storage
- Implement user management, keyring storage, encrypted fallback.
Epic F — Packaging, CI, docs
- Create requirements, setup.py/pyproject, GitHub Actions, docs and quickstart.
Epic G — Backup, migration, and optional Dockerfile

18. Appendix: sample snippets

A. SQLite upsert (SQLAlchemy example)
- Use ON CONFLICT clause for SQLite:
  - INSERT INTO readings (...) VALUES (...) ON CONFLICT(station_mac, timestamp_utc) DO UPDATE SET raw_payload=excluded.raw_payload;

B. Backfill checkpoint JSON (example)
{
  "job_id": "backfill-20260102-001",
  "station_mac": "00:11:22:33:44:55",
  "last_processed": "2024-05-12T00:00:00Z",
  "chunks_done": ["2024-05-12", "2024-05-13"]
}

C. systemd unit (service + timer) skeleton
- scripts/systemd_units/weather-update.service
[Unit]
Description=Weather App periodic update
After=network.target

[Service]
Type=oneshot
User=weather
Group=weather
ExecStart=/usr/bin/env /usr/local/bin/weather-app update --stations all
WorkingDirectory=/home/weather
EnvironmentFile=/etc/weather-app/env

- scripts/systemd_units/weather-update.timer
[Unit]
Description=Run Weather App update every 5 minutes

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target

D. Cron example (5-minute)
*/5 * * * * /usr/bin/env /usr/local/bin/weather-app update --stations all >> /var/log/weather/update.log 2>&1

E. Dockerfile (skeleton)
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app
ENV FLASK_APP=weather_app.web.app:create_app
CMD ["gunicorn", "weather_app.web.app:app", "-b", "0.0.0.0:8080", "--workers", "2"]

---

Questions / confirmation needed from you before I convert this spec into issue drafts:
1. Confirm web framework choice: Flask + Jinja + Plotly for MVP (approved by PRD earlier). Proceed?
2. Confirm default DB path and config choices:
   - Default DB path: ./weather.db (user-local) or /var/lib/weather/weather.db (system-wide)? Recommend ./weather.db for quickstart and allow override.
3. Decide default behavior for PURGE_RAW_AFTER_AGGREGATION:
   - Default = True (to limit DB size) or False (preserve raw data but risk larger DB)? Recommend True with a configurable retention window and an option to archive raw data instead of deleting.
4. Do you want the aggregator to run automatically (via scheduler) by default or triggered manually? Recommendation: manual by default; provide sample scheduled entry for nightly aggregate job.

Next actions once you confirm these:
- Break the epics and tasks into discrete GitHub issue drafts (title, description, acceptance criteria, estimate) and present them for review.
- Implement the repo refactor plan and create initial PR drafts (or create issues first per your earlier preference).

If you want, I can also produce the initial list of GitHub issue drafts now (without creating them in repo) so you can review before I create them. Which would you prefer?