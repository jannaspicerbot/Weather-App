# Weather Data Collection Scripts - Usage Guide

## Overview

You now have two scripts for collecting weather data:

1. **`update_weather.py`** - Quick updates with recent data (daily use)
2. **`backfill_weather.py`** - Slow historical data collection (overnight runs)

---

## Setup (One Time)

### Set Environment Variables

In PowerShell (same window where you'll run the scripts):

```powershell
$env:AMBIENT_API_KEY="your_api_key_here"
$env:AMBIENT_APP_KEY="your_application_key_here"
```

---

## Script 1: update_weather.py

**Purpose:** Fetch recent weather data (last few hours/days)
**When to run:** Daily or hourly to keep data current
**Speed:** Fast (1-2 minutes)

### Basic Usage

```powershell
python update_weather.py
```

**What it does:**
- Fetches last 200 records (default: 10 records × 20 requests)
- 3-second delays between requests
- Stops when it finds data you already have
- Perfect for daily updates

### Custom Settings

```powershell
# Fetch more aggressively (more records, fewer delays)
python update_weather.py --records-per-batch 15 --delay 2 --max-requests 30

# Fetch conservatively (fewer records, longer delays)
python update_weather.py --records-per-batch 5 --delay 5 --max-requests 10
```

**Parameters:**
- `--records-per-batch` (default: 10) - Records per API call
- `--delay` (default: 3) - Seconds between requests
- `--max-requests` (default: 20) - Maximum API calls

### Example Output

```
============================================================
Weather Update - Recent Data Fetch
============================================================
Configuration:
  Records per batch: 10
  Delay between requests: 3s
  Max requests: 20

Fetching devices...
Using device: Default ([DEVICE_MAC_ADDRESS])

Most recent data in database:
  Date: 2025-12-31T14:30:00.000Z
  (2025-12-31 02:30 PM)

Request 1/20: Fetching 10 records...
  Received 10 records
  Inserted: 8 new, Skipped: 2 duplicates

✅ All caught up! No new data available.

============================================================
Update Complete!
============================================================
Requests made: 3
New records inserted: 18
Duplicate records skipped: 12

Database totals:
  Total records: 1,245
  Date range: 2024-03-13 to 2025-12-31
```

---

## Script 2: backfill_weather.py

**Purpose:** Fill in historical data going back to March 13, 2024
**When to run:** Overnight or when PC will be idle for hours
**Speed:** Slow (designed to avoid rate limits)

### Basic Usage

```powershell
python backfill_weather.py
```

**What it does:**
- Starts from your oldest data and works backwards
- Fetches 5 records at a time (very conservative)
- 10-second delays between requests
- Max 500 requests per run (~2500 records)
- Saves progress automatically - can resume if stopped

### First Time Running

The first run initializes the backfill:
- Checks your oldest existing data
- Sets target to March 13, 2024
- Begins working backwards from your oldest record

### Resuming After Interruption

If stopped (rate limit, PC shutdown, etc.), just run again:

```powershell
python backfill_weather.py
```

It automatically resumes from where it left off!

### Custom Settings

```powershell
# Different start date
python backfill_weather.py --start-date 2024-01-01

# More aggressive (use with caution - may hit rate limits)
python backfill_weather.py --records-per-batch 10 --delay 5

# More conservative (slower but safer)
python backfill_weather.py --records-per-batch 3 --delay 15

# Longer run (more requests before stopping)
python backfill_weather.py --max-requests 1000

# Start fresh (ignore previous progress)
python backfill_weather.py --no-resume
```

**Parameters:**
- `--start-date` (default: 2024-03-13) - Target earliest date
- `--records-per-batch` (default: 5) - Records per API call
- `--delay` (default: 10) - Seconds between requests
- `--max-requests` (default: 500) - Requests per run
- `--no-resume` - Start fresh instead of resuming

### Example Output

```
======================================================================
Weather Backfill - Historical Data Collection
======================================================================
Configuration:
  Target start date: 2024-03-13
  Records per batch: 5
  Delay between requests: 10s
  Max requests this run: 500
  Resume from last position: True

Fetching devices...
Using device: Default ([DEVICE_MAC_ADDRESS])

Backfill Status:
  Target start: 2024-03-13
  Current position: 2024-12-20T08:00:00.000Z
  Records fetched so far: 12,450
  Total requests made: 2,490
  Status: in_progress

📊 Progress:
  Days remaining: 282
  Estimated requests needed: ~16,243

Starting backfill...
----------------------------------------------------------------------

[1/500] Fetching batch ending at 2024-12-20 08:00
  Received 5 records
  Inserted: 5 new, Skipped: 0 duplicates
  New position: 2024-12-20 07:35
  ⏳ Waiting 10s...

[2/500] Fetching batch ending at 2024-12-20 07:35
  Received 5 records
  Inserted: 5 new, Skipped: 0 duplicates
  New position: 2024-12-20 07:10
  ⏳ Waiting 10s...

...continues...

[500/500] Fetching batch ending at 2024-12-18 14:20
  Received 5 records
  Inserted: 5 new, Skipped: 0 duplicates
  New position: 2024-12-18 13:55

======================================================================
Backfill Run Complete!
======================================================================
Requests made this run: 500
New records inserted: 2,500
Duplicate records skipped: 0

Database totals:
  Total records: 14,950
  Date range: 2024-12-18 to 2025-12-31

📊 Backfill in progress:
  Current position: 2024-12-18T13:55:00.000Z
  Days remaining: 280
  Run again to continue
```

### If Rate Limited

```
[145/500] Fetching batch ending at 2024-11-15 10:20
  ⚠️  RATE LIMIT HIT!
  Stopping and saving progress...

======================================================================
❌ Backfill paused due to rate limit
======================================================================
  Inserted 720 records before stopping
  Current position saved: 2024-11-15T10:20:00.000Z
  Wait 1 hour and run again to resume
```

Just wait an hour and run the script again - it will resume automatically!

---

## Recommended Workflow

### Day 1: Get Started

1. **Run update script** to get recent data:
   ```powershell
   python update_weather.py
   ```

2. **Before bed, start backfill**:
   ```powershell
   python backfill_weather.py
   ```

3. **Prevent PC from sleeping** (Windows Settings → Power & Sleep)

### Day 2+: Maintain

1. **Each morning**, check backfill progress:
   ```powershell
   python backfill_weather.py
   ```

2. **Run update daily**:
   ```powershell
   python update_weather.py
   ```

3. **Continue backfill nightly** until complete

### After Backfill Complete

1. **Run update script** daily/hourly as needed
2. **Backfill script** no longer needed (unless you want older data)

---

## Troubleshooting

### "Environment variables not set"

Make sure you set them in the same PowerShell window:
```powershell
$env:AMBIENT_API_KEY="your_key"
$env:AMBIENT_APP_KEY="your_key"
```

### Rate Limit Errors

**For update_weather.py:**
- Use fewer records per batch: `--records-per-batch 5`
- Increase delay: `--delay 5`

**For backfill_weather.py:**
- Already conservative by default
- Wait 1 hour if rate limited
- Script will resume automatically

### PC Went to Sleep

Both scripts save their state:
- **update_weather.py**: Just run again, it will catch up
- **backfill_weather.py**: Automatically resumes from last position

### Check Progress

To see overall database stats without running a full update:

```powershell
python -c "from update_weather import AmbientWeatherDB; db = AmbientWeatherDB(); print(db.get_stats()); db.close()"
```

---

## Tips

1. **Start conservative** - You can always speed up later
2. **Monitor first few runs** - Make sure no rate limits
3. **Let backfill run overnight** - It's designed for this
4. **Update script is your daily driver** - Fast and reliable

---

## Next Steps

Once you have data:
1. Run visualization script: `python ambient_weather_visualize.py`
2. Build the web dashboard (Phase 2)
3. Automate with Task Scheduler (Phase 3)

Happy weather tracking! 🌤️
