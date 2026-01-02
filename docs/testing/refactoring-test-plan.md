# Testing Plan: DuckDB-Only Refactoring

**Branch:** `refactor/duckdb-only-simplification`
**PR:** #11
**Date:** January 2, 2026

## Overview

This testing plan validates that the DuckDB-only refactoring maintains all existing functionality while improving performance and simplifying the codebase.

---

## Pre-Testing Setup

### 1. Environment Preparation

```bash
# Checkout the refactoring branch
git checkout refactor/duckdb-only-simplification

# Pull latest changes
git pull origin refactor/duckdb-only-simplification

# Verify you're on the correct branch
git branch --show-current
# Should show: refactor/duckdb-only-simplification
```

### 2. Install Dependencies

```bash
# Install Python dependencies (including duckdb>=0.10.0)
pip install -r requirements.txt

# Verify DuckDB is installed
python -c "import duckdb; print(f'DuckDB version: {duckdb.__version__}')"

# Install package in editable mode
pip install -e .
```

### 3. Verify Environment Variables

```bash
# Check .env file exists
cat .env

# Should contain:
# AMBIENT_API_KEY=your_key_here
# AMBIENT_APP_KEY=your_app_key_here
```

---

## Test Suite

## ✅ Phase 1: Module Import Tests

**Purpose:** Verify new module structure works correctly

### Test 1.1: Import New Modules

```bash
python -c "from weather_app.database import WeatherDatabase; print('✓ WeatherDatabase imported')"
python -c "from weather_app.database import WeatherRepository; print('✓ WeatherRepository imported')"
python -c "from weather_app.api import AmbientWeatherAPI; print('✓ AmbientWeatherAPI imported')"
```

**Expected Result:** All imports succeed with no errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 1.2: Verify Old Modules Removed

```bash
python -c "from weather_app.fetch import AmbientWeatherDB" 2>&1 | grep "No module named"
python -c "from weather_app.storage.repository import WeatherRepository" 2>&1 | grep "No module named"
```

**Expected Result:** Both commands should show "No module named" errors (confirming old modules are removed)

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

## ✅ Phase 2: CLI Command Tests

**Purpose:** Verify all CLI commands work with new database structure

### Test 2.1: Database Initialization

```bash
# Remove any existing database
rm -f ambient_weather.duckdb

# Initialize new DuckDB database
weather-app init-db
```

**Expected Output:**
```
Initializing DuckDB database at: [path]/ambient_weather.duckdb
Creating weather_data and backfill_progress tables...
✅ Database initialized successfully at [path]/ambient_weather.duckdb
📊 Database engine: duckdb
📊 Database mode: PRODUCTION
```

**Verify:**
- [ ] Database file created: `ambient_weather.duckdb`
- [ ] No errors during initialization
- [ ] Correct database engine reported (duckdb)

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.2: Database Force Reinit

```bash
# Try to init again (should fail without --force)
weather-app init-db

# Should see error about existing database

# Force reinit
weather-app init-db --force
```

**Expected Behavior:**
- First command: Error message about existing database
- Second command: Successfully drops and recreates database

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.3: Fetch Command

```bash
# Fetch 1 latest record (default)
weather-app fetch

# Fetch 10 records
weather-app fetch --limit 10
```

**Expected Output (example):**
```
Fetching 10 latest weather record(s)...
📡 Fetching from device: [Your Station Name]
✅ Successfully fetched 10 records
💾 Inserted: 10, Skipped: 0

Latest Reading:
  Temperature: 72.5°F
  Humidity: 45%
  [other fields...]
```

**Verify:**
- [ ] API connection successful
- [ ] Data fetched from Ambient Weather API
- [ ] Records inserted into DuckDB
- [ ] Latest reading displayed

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.4: Backfill Command

```bash
# Backfill a small date range (1 week)
weather-app backfill --start 2024-12-01 --end 2024-12-07
```

**Expected Output:**
```
Starting backfill from 2024-12-01 to 2024-12-07...
📡 Fetching from device: [Your Station Name]
Progress: [======>     ] 50% | Date: 2024-12-04 | Records: 1008/2016
...
✅ Backfill completed successfully!
Total records inserted: [number]
Total records skipped: [number]
```

**Verify:**
- [ ] Progress bar displays correctly
- [ ] No errors during backfill
- [ ] Records inserted into database
- [ ] Completion message shows totals

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.5: Export Command

```bash
# Export to CSV
weather-app export --output test_export.csv

# Check the file was created
ls -lh test_export.csv
head -5 test_export.csv
```

**Expected Output:**
```
Exporting weather data to: test_export.csv
✅ Exported [number] records to test_export.csv
```

**Verify:**
- [ ] CSV file created
- [ ] File contains data (check with `head`)
- [ ] CSV has proper headers
- [ ] Data looks correct

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.6: Info Command

```bash
weather-app info
```

**Expected Output:**
```
==================================================
Weather App - Database Information
==================================================

📊 Database Configuration:
  Engine: duckdb
  Mode: PRODUCTION
  Path: [path]/ambient_weather.duckdb

📈 Database Statistics:
  Total Records: [number]
  Date Range: [start] to [end]
  Days of Data: [number]

🌡️  Temperature Statistics:
  Average: [value]°F
  Minimum: [value]°F
  Maximum: [value]°F

💧 Humidity Statistics:
  Average: [value]%
  Minimum: [value]%
  Maximum: [value]%
```

**Verify:**
- [ ] Database engine shows "duckdb"
- [ ] Statistics display correctly
- [ ] All sections present

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 2.7: Verify Migrate Command Removed

```bash
# This command should NOT exist
weather-app migrate --help
```

**Expected Output:**
```
Error: No such command 'migrate'
```

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

## ✅ Phase 3: Web API Tests

**Purpose:** Verify FastAPI backend works with new database module

### Test 3.1: Start Web Server

```bash
# Start the FastAPI server
uvicorn weather_app.web.app:create_app --factory --reload &

# Wait for server to start
sleep 3
```

**Expected:** Server starts without errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.2: Health Endpoint

```bash
curl http://localhost:8000/api/health | python -m json.tool
```

**Expected Output:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "duckdb",
    "mode": "PRODUCTION"
  }
}
```

**Verify:**
- [ ] Status is "healthy"
- [ ] Database shows "duckdb"
- [ ] Response is valid JSON

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.3: Latest Weather Endpoint

```bash
curl "http://localhost:8000/api/weather/latest?limit=5" | python -m json.tool
```

**Expected:** Array of 5 weather records with all fields

**Verify:**
- [ ] Returns array of records
- [ ] Each record has expected fields (tempf, humidity, etc.)
- [ ] Data matches database content

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.4: Weather Range Endpoint

```bash
curl "http://localhost:8000/api/weather/range?start_date=2024-12-01&end_date=2024-12-07" | python -m json.tool
```

**Expected:** Array of records within date range

**Verify:**
- [ ] Returns filtered records
- [ ] All records within specified date range
- [ ] Sorted correctly

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.5: Stats Endpoint

```bash
curl http://localhost:8000/api/weather/stats | python -m json.tool
```

**Expected Output:**
```json
{
  "total_records": [number],
  "min_date": "2024-12-01",
  "max_date": "2024-12-07",
  "date_range_days": 6
}
```

**Verify:**
- [ ] All stats fields present
- [ ] Values match database content
- [ ] No errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.6: API Documentation

```bash
# Open browser to:
# http://localhost:8000/docs
```

**Verify:**
- [ ] Swagger UI loads correctly
- [ ] All endpoints listed
- [ ] Can test endpoints interactively

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 3.7: Stop Web Server

```bash
# Stop the background server
pkill -f uvicorn
```

---

## ✅ Phase 4: Frontend Tests

**Purpose:** Verify React frontend works with updated backend

### Test 4.1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Expected:** Dependencies install without errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 4.2: Start Frontend Dev Server

```bash
# In frontend directory
npm run dev
```

**Expected:** Vite dev server starts on http://localhost:5173

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 4.3: Frontend Dashboard Test

**Manual Test:**
1. Open browser to http://localhost:5173
2. Verify dashboard loads
3. Check that stats cards show data
4. Verify chart displays
5. Try changing metric (temp → humidity → pressure → wind)
6. Try changing time range

**Verify:**
- [ ] Page loads without errors
- [ ] Stats cards show correct data
- [ ] Chart renders correctly
- [ ] Metric selector works
- [ ] Time range selector works
- [ ] No console errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 4.4: Frontend API Integration

**Check browser console:**
- [ ] API requests succeed (check Network tab)
- [ ] Data loads from `/api/weather/latest`
- [ ] Stats load from `/api/weather/stats`
- [ ] No CORS errors
- [ ] No TypeScript errors

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

## ✅ Phase 5: Docker Tests

**Purpose:** Verify Docker Compose setup works with refactoring

### Test 5.1: Build Docker Images

```bash
# From project root
docker-compose build
```

**Expected:** Both backend and frontend images build successfully

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.2: Start Docker Stack

```bash
docker-compose up -d

# Check logs
docker-compose logs backend
docker-compose logs frontend
```

**Expected:**
- Both services start successfully
- No error messages in logs
- Health checks pass

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.3: Docker Health Checks

```bash
# Check service status
docker-compose ps

# Should show both services as "healthy"
```

**Expected:** Both `backend` and `frontend` show status "Up" and healthy

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.4: Docker API Test

```bash
curl http://localhost:8000/api/health | python -m json.tool
curl http://localhost/api/health | python -m json.tool  # Through nginx
```

**Expected:** Both URLs return healthy status

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.5: Docker Frontend Test

**Manual Test:**
1. Open http://localhost in browser
2. Verify dashboard loads
3. Check data displays correctly

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.6: Docker Database Persistence

```bash
# Initialize database in container
docker-compose exec backend weather-app init-db

# Fetch some data
docker-compose exec backend weather-app fetch --limit 10

# Restart containers
docker-compose restart

# Verify data persists
docker-compose exec backend weather-app info
```

**Expected:** Data persists across container restarts

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 5.7: Stop Docker Stack

```bash
docker-compose down
```

---

## ✅ Phase 6: Performance Tests

**Purpose:** Verify DuckDB performance benefits

### Test 6.1: Query Performance

```bash
# Create a test database with significant data
weather-app backfill --start 2024-01-01 --end 2024-12-31

# Time a stats query
time weather-app info
```

**Record Results:**
- Total records: _______
- Query time: _______
- Performance acceptable: [ ] Yes [ ] No

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 6.2: Large Dataset Export

```bash
# Export all data
time weather-app export --output full_export.csv

# Check file size
ls -lh full_export.csv
```

**Record Results:**
- Export time: _______
- File size: _______
- Performance acceptable: [ ] Yes [ ] No

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

## ✅ Phase 7: Error Handling Tests

**Purpose:** Verify error conditions are handled gracefully

### Test 7.1: Missing API Credentials

```bash
# Temporarily rename .env
mv .env .env.backup

# Try to fetch (should fail gracefully)
weather-app fetch

# Restore .env
mv .env.backup .env
```

**Expected:** Clear error message about missing credentials

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 7.2: Invalid Date Range

```bash
# End date before start date
weather-app backfill --start 2024-12-31 --end 2024-01-01
```

**Expected:** Clear error message about invalid date range

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

### Test 7.3: Database Not Initialized

```bash
# Remove database
rm -f ambient_weather.duckdb

# Try to fetch without init
weather-app fetch
```

**Expected:** Error message telling user to run `init-db` first

**Status:** [ ] Pass [ ] Fail
**Notes:**

---

## Test Summary

### Results Overview

| Phase | Total Tests | Passed | Failed | Notes |
|-------|-------------|--------|--------|-------|
| 1: Module Imports | 2 | | | |
| 2: CLI Commands | 7 | | | |
| 3: Web API | 7 | | | |
| 4: Frontend | 4 | | | |
| 5: Docker | 7 | | | |
| 6: Performance | 2 | | | |
| 7: Error Handling | 3 | | | |
| **TOTAL** | **32** | | | |

### Critical Issues Found

_List any critical issues that block merge:_

1.
2.
3.

### Non-Critical Issues Found

_List any minor issues or improvements:_

1.
2.
3.

### Performance Metrics

- Database initialization time: _______
- Fetch 100 records time: _______
- Backfill 1 month time: _______
- Export 10k records time: _______
- Stats query time: _______

### Sign-Off

- [ ] All critical tests passed
- [ ] No blocking issues found
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Ready for merge

**Tested by:** _______________
**Date:** _______________
**Approval:** [ ] Approved [ ] Needs revision

---

## Post-Merge Validation

After merging to `main`, verify:

- [ ] Main branch builds successfully
- [ ] Docker images build
- [ ] Documentation is accurate
- [ ] No regressions in existing functionality

---

**End of Test Plan**
