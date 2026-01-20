# CLI Reference

**Command:** `weather-app`
**Framework:** Click
**Python Version:** 3.13+

---

## Installation

### pip (Editable Install)

```bash
# Clone repository
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Verify installation
weather-app --help
```

### Docker

```bash
# Run CLI commands via Docker Compose
docker-compose exec backend weather-app --help
```

---

## Configuration

All commands read configuration from `.env` file in current directory or parent directories.

### Required Environment Variables

```bash
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APPLICATION_KEY=your_application_key_here
STATION_MAC_ADDRESS=00:11:22:33:44:55
```

### Optional Environment Variables

```bash
DATABASE_PATH=./weather.db          # Default: ./weather.db
LOG_LEVEL=INFO                       # Default: INFO (options: DEBUG, INFO, WARNING, ERROR)
API_TIMEOUT=30                       # Default: 30 seconds
RETRY_MAX_ATTEMPTS=5                 # Default: 5
```

---

## Commands

### `weather-app --help`

Display help for all commands.

**Usage:**
```bash
weather-app --help
```

**Output:**
```
Usage: weather-app [OPTIONS] COMMAND [ARGS]...

  Weather App CLI - Manage weather data collection and export

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init-db   Initialize the database schema
  fetch     Fetch latest weather data from Ambient Weather API
  backfill  Backfill historical weather data
  info      Show database information
  export    Export weather data to CSV
```

---

### `weather-app init-db`

Initialize the DuckDB database with the weather_data table schema.

**Usage:**
```bash
weather-app init-db
```

**Behavior:**
1. Creates database file at `DATABASE_PATH` (default: `./weather.db`)
2. Creates `weather_data` table with full schema
3. Creates `idx_timestamp` index
4. Idempotent (safe to run multiple times)

**Output:**
```
Database initialized successfully at /path/to/weather.db
Created table: weather_data
Created index: idx_timestamp
```

**Example:**
```bash
# Initialize database
weather-app init-db

# Verify
ls -lh weather.db
# -rw-r--r-- 1 user user 12K Jan 2 2026 weather.db
```

**Docker:**
```bash
docker-compose exec backend weather-app init-db
```

---

### `weather-app fetch`

Fetch latest weather data from Ambient Weather API and insert into database.

**Usage:**
```bash
weather-app fetch
```

**Behavior:**
1. Queries database for latest timestamp
2. If no records exist, fetches last 24 hours
3. Calls Ambient Weather API: `GET /v1/devices/{macAddress}?limit=288`
4. Parses JSON response
5. Upserts records to database (idempotent via `INSERT OR REPLACE`)
6. Logs: fetched count, inserted count, duplicates skipped

**Output:**
```
Fetching latest weather data...
Latest timestamp in database: 2024-12-31 23:55:00
Calling Ambient Weather API...
Fetched 12 readings from API
Inserted 12 new records (0 duplicates skipped)
```

**Error Handling:**
- API timeout: Retries with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Rate limit (HTTP 429): Respects `Retry-After` header
- Network errors: Logs and exits with error code

**Example:**
```bash
# Fetch latest data
weather-app fetch

# Schedule via cron (every 5 minutes)
crontab -e
*/5 * * * * cd /path/to/Weather-App && /path/to/venv/bin/weather-app fetch >> /var/log/weather-fetch.log 2>&1
```

**Docker:**
```bash
# One-time fetch
docker-compose exec backend weather-app fetch

# Schedule via cron
*/5 * * * * cd /path/to/Weather-App && docker-compose exec -T backend weather-app fetch >> /var/log/weather-fetch.log 2>&1
```

---

### `weather-app backfill`

Backfill historical weather data for a date range with checkpoint support.

**Usage:**
```bash
weather-app backfill --start START_DATE --end END_DATE [--checkpoint CHECKPOINT_FILE]
```

**Arguments:**
- `--start START_DATE` (required): Start date in `YYYY-MM-DD` format
- `--end END_DATE` (required): End date in `YYYY-MM-DD` format
- `--checkpoint CHECKPOINT_FILE` (optional): Path to checkpoint JSON file (default: `backfill_checkpoint.json`)

**Behavior:**
1. Validates date range (start < end)
2. Checks for existing checkpoint file
3. Resumes from last processed date if checkpoint exists
4. For each day in range:
   - Calls Ambient Weather API: `GET /v1/devices/{macAddress}?endDate={date}&limit=288`
   - Parses JSON response (up to 288 readings/day)
   - Batch inserts to database (1000 records/batch)
   - Updates checkpoint file: `{"last_processed": "2024-05-12", "total_inserted": 51840}`
5. Logs progress every 10 days
6. Final report: total days processed, total records inserted, errors

**Output:**
```
Starting backfill from 2024-01-01 to 2024-12-31
Checkpoint file: backfill_checkpoint.json
Resuming from checkpoint: last processed = 2024-06-15
Processing date: 2024-06-16 (150/365 days)
  Fetched 288 readings
  Inserted 288 records
Processing date: 2024-06-17 (151/365 days)
  Fetched 288 readings
  Inserted 288 records
...
Backfill complete!
  Total days processed: 365
  Total records inserted: 105,120
  Errors: 0
```

**Checkpoint File Format:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "last_processed": "2024-06-16",
  "total_inserted": 51840,
  "errors": []
}
```

**Resuming After Interruption:**
```bash
# Start backfill
weather-app backfill --start 2024-01-01 --end 2024-12-31

# [Ctrl+C to interrupt after 6 months]

# Resume from checkpoint (automatic)
weather-app backfill --start 2024-01-01 --end 2024-12-31
# Resuming from checkpoint: last processed = 2024-06-16
```

**Example:**
```bash
# Backfill 1 year
weather-app backfill --start 2024-01-01 --end 2024-12-31

# Backfill 10 years (longer, interruptible)
weather-app backfill --start 2014-01-01 --end 2024-12-31

# Custom checkpoint location
weather-app backfill --start 2024-01-01 --end 2024-12-31 --checkpoint /backups/checkpoint.json
```

**Docker:**
```bash
# Backfill via Docker
docker-compose exec backend weather-app backfill --start 2024-01-01 --end 2024-12-31

# Checkpoint file is stored in /app/backfill_checkpoint.json (container)
# Map to host: docker-compose.yml volumes: ./data:/app/data
```

**Rate Limits:**
Ambient Weather API has rate limits. Backfill respects these:
- 1 request/second (avg)
- Exponential backoff on HTTP 429
- Progress saved to checkpoint on each day (safe to interrupt)

---

### `weather-app info`

Display database statistics and information.

**Usage:**
```bash
weather-app info
```

**Output:**
```
Database Information
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Database path:     /path/to/weather.db
Total records:     125,432
Oldest reading:    2024-01-01 00:00:00
Latest reading:    2024-12-31 23:55:00
Date range:        365 days
Database size:     6.2 MB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Example:**
```bash
# Check database stats
weather-app info

# Verify backfill completion
weather-app info | grep "Total records"
# Total records: 105,120
```

**Docker:**
```bash
docker-compose exec backend weather-app info
```

---

### `weather-app export`

Export weather data to CSV file.

**Usage:**
```bash
weather-app export --start START_DATE --end END_DATE --output OUTPUT_FILE
```

**Arguments:**
- `--start START_DATE` (required): Start date in `YYYY-MM-DD` format
- `--end END_DATE` (required): End date in `YYYY-MM-DD` format
- `--output OUTPUT_FILE` (required): Path to output CSV file

**Behavior:**
1. Validates date range (start < end)
2. Queries database for all records in range
3. Writes CSV with header row
4. Includes all 14 columns (timestamp, temperature, humidity, ...)
5. Logs: total records exported, file size

**Output:**
```
Exporting weather data...
Date range: 2024-01-01 to 2024-12-31
Exported 105,120 records to weather_2024.csv
File size: 12.5 MB
```

**CSV Format:**
```csv
timestamp,temperature,feels_like,humidity,dew_point,wind_speed,wind_gust,wind_direction,pressure,precipitation_rate,precipitation_total,solar_radiation,uv_index,battery_ok
2024-01-01T00:00:00,45.2,43.1,65.0,35.8,5.2,8.1,270,30.12,0.0,0.0,0.0,0,true
2024-01-01T00:05:00,45.1,43.0,65.2,35.7,5.1,7.9,268,30.11,0.0,0.0,0.0,0,true
...
```

**Example:**
```bash
# Export 1 year
weather-app export --start 2024-01-01 --end 2024-12-31 --output weather_2024.csv

# Export 1 month
weather-app export --start 2024-01-01 --end 2024-01-31 --output weather_2024_jan.csv

# Export all data (use oldest/latest from info command)
weather-app export --start 2020-01-01 --end 2024-12-31 --output weather_all.csv
```

**Docker:**
```bash
# Export via Docker (writes to /app/data in container)
docker-compose exec backend weather-app export --start 2024-01-01 --end 2024-12-31 --output /app/data/export.csv

# File is accessible at ./data/export.csv on host
ls -lh ./data/export.csv
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (invalid arguments, file not found, etc.) |
| 2 | Database error (connection failed, query error) |
| 3 | API error (network failure, authentication failed, rate limit exceeded) |

**Example:**
```bash
# Check exit code
weather-app fetch
echo $?
# 0 (success)

# Handle errors in scripts
if weather-app fetch; then
    echo "Fetch succeeded"
else
    echo "Fetch failed with code $?"
fi
```

---

## Logging

### Log Levels

Set via `LOG_LEVEL` environment variable:
- `DEBUG`: Verbose output (SQL queries, API requests/responses)
- `INFO`: Standard output (default)
- `WARNING`: Warnings only
- `ERROR`: Errors only

**Example:**
```bash
# Debug logging
LOG_LEVEL=DEBUG weather-app fetch

# Output:
# DEBUG: Connecting to database at /path/to/weather.db
# DEBUG: Executing query: SELECT MAX(timestamp) FROM weather_data
# DEBUG: Latest timestamp: 2024-12-31 23:55:00
# DEBUG: Calling API: https://api.ambientweather.net/v1/devices/00:11:22:33:44:55?limit=288
# DEBUG: API response: 200 OK (12 readings)
# INFO: Fetched 12 readings from API
# INFO: Inserted 12 new records (0 duplicates skipped)
```

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s

Example:
2024-12-31 23:55:00,123 - weather_app.cli - INFO - Fetching latest weather data...
```

### Log Output

- **stdout**: Normal messages (info, success)
- **stderr**: Errors and warnings

**Example (redirect to file):**
```bash
# Capture all output
weather-app fetch >> weather-fetch.log 2>&1

# Capture only errors
weather-app fetch 2>> weather-errors.log
```

---

## Scheduling

### cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add entry (fetch every 5 minutes)
*/5 * * * * cd /path/to/Weather-App && /path/to/venv/bin/weather-app fetch >> /var/log/weather-fetch.log 2>&1

# Add entry (daily backfill for yesterday)
0 2 * * * cd /path/to/Weather-App && /path/to/venv/bin/weather-app backfill --start $(date -d "yesterday" +\%Y-\%m-\%d) --end $(date -d "yesterday" +\%Y-\%m-\%d) >> /var/log/weather-backfill.log 2>&1
```

### systemd (Linux)

**Service file:** `/etc/systemd/system/weather-fetch.service`
```ini
[Unit]
Description=Weather App Data Fetch
After=network.target

[Service]
Type=oneshot
User=weather
WorkingDirectory=/home/weather/Weather-App
Environment="PATH=/home/weather/Weather-App/venv/bin"
ExecStart=/home/weather/Weather-App/venv/bin/weather-app fetch
StandardOutput=journal
StandardError=journal
```

**Timer file:** `/etc/systemd/system/weather-fetch.timer`
```ini
[Unit]
Description=Weather App Data Fetch Timer
Requires=weather-fetch.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-fetch.timer
sudo systemctl start weather-fetch.timer

# Check status
sudo systemctl status weather-fetch.timer
sudo journalctl -u weather-fetch.service -f
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Repeat every 5 minutes
4. Action: Start a program
   - Program: `C:\Weather-App\venv\Scripts\weather-app.exe`
   - Arguments: `fetch`
   - Start in: `C:\Weather-App`
5. Settings: Allow task to run on demand

---

## Troubleshooting

### Command Not Found

```bash
# Error: weather-app: command not found

# Fix 1: Activate virtual environment
source venv/bin/activate

# Fix 2: Use full path
/path/to/venv/bin/weather-app --help

# Fix 3: Reinstall in editable mode
pip install -e .
```

### Database Locked

```bash
# Error: database is locked

# Cause: Multiple processes accessing database
# Fix: Stop other processes (API server, other CLI commands)
pkill -f uvicorn
pkill -f weather-app
```

### API Authentication Failed

```bash
# Error: 401 Unauthorized

# Fix: Check .env file has correct keys
cat .env | grep AMBIENT

# Verify keys at https://ambientweather.net/account
```

### API Rate Limit

```bash
# Error: 429 Too Many Requests

# Fix: Wait for rate limit to reset (backfill has automatic retry)
# Or: Reduce backfill chunk size (future enhancement)
```

---

## References

- [Click Documentation](https://click.palletsprojects.com/)
- [Ambient Weather API Documentation](https://ambientweather.docs.apiary.io/)
- [Cron Expression Generator](https://crontab.guru/)

---

## Document Changelog

- **2026-01-02:** Initial CLI reference extracted from specifications.md
