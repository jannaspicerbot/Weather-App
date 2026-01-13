# Test Data Guide

This guide shows you how to generate and use synthetic weather data for testing and development.

**Note:** This guide is for **development/source code** usage only. If you're using the packaged executables:
- **Production build** (`WeatherApp.exe`) → Always uses production database (immutable)
- **Debug build** (`WeatherApp_Debug.exe`) → Always uses test database (immutable)

Database selection cannot be changed in packaged builds for safety reasons.

## Quick Start

### 1. Generate Test Data

Generate 30 days of test data (default):

```bash
python tests/data/generate_test_data.py
```

This creates `ambient_weather_test.db` with realistic weather data.

### 2. Run the API with Test Database

**Option A: Using environment variable (Recommended)**

PowerShell:
```powershell
$env:USE_TEST_DB="true"
python main.py
```

Bash/Linux:
```bash
USE_TEST_DB=true python main.py
```

**Option B: Using uvicorn directly**

PowerShell:
```powershell
$env:USE_TEST_DB="true"
uvicorn main:app --reload
```

### 3. Verify Test Database is Active

Open http://localhost:8000/ and check the response:

```json
{
  "message": "Weather API",
  "version": "1.0.0",
  "database": {
    "mode": "TEST",    ← Should show "TEST"
    "path": "ambient_weather_test.db"
  },
  ...
}
```

## Generation Options

### Custom Date Range

Generate data starting from a specific date:

```bash
python tests/data/generate_test_data.py --start-date 2024-01-01 --days 60
```

### Different Intervals

Generate data with different reading intervals:

```bash
# Every 5 minutes (default, realistic)
python tests/data/generate_test_data.py --interval 5

# Every minute (more data points)
python tests/data/generate_test_data.py --interval 1

# Every 15 minutes (less data)
python tests/data/generate_test_data.py --interval 15
```

### Custom Database Name

Use a different database file:

```bash
python tests/data/generate_test_data.py --db my_custom_test.db
```

Then update [config.py](config.py):
```python
TEST_DB = "my_custom_test.db"
```

### Clear Existing Data

Clear and regenerate all data:

```bash
python tests/data/generate_test_data.py --clear
```

## What Data is Generated?

The test data generator creates realistic weather patterns:

### Temperature
- **Seasonal variation**: Warmer in summer, cooler in winter
- **Daily cycles**: Warmer during afternoon, cooler at night
- **Range**: Approximately 40°F - 90°F depending on season
- **Indoor temp**: Slightly warmer and more stable than outdoor

### Humidity
- **Inversely related** to temperature
- **Range**: 20% - 95%
- **Indoor**: More stable (40-50%)

### Pressure
- **Barometric pressure**: ~29.7 - 30.3 inches Hg
- **Monthly cycles** with random variations

### Wind
- **Speed**: 0-15 mph typically, with occasional gusts
- **Gusts**: 2-10 mph above base wind speed
- **Direction**: Random (0-359 degrees)
- **More wind during daytime**

### Rain
- **10% chance** of rain at any reading
- **Accumulating totals**: hourly, daily, weekly, monthly
- **Realistic amounts**: 0.01 - 0.5 inches per hour when raining

### Solar
- **Solar radiation**: 0-800+ W/m² (based on time of day)
- **UV index**: 0-11 (correlated with solar radiation)
- **Zero at night** (6 PM - 6 AM)
- **Peak at solar noon**

### Battery
- **95% of readings**: Battery OK
- **5% of readings**: Low battery (for testing alerts)

## Example Scenarios

### Generate 1 Week of Recent Data

```bash
python tests/data/generate_test_data.py --days 7
```

Result: ~2,000 records (5-minute intervals)

### Generate 90 Days for Long-term Testing

```bash
python generate_test_data.py --days 90
```

Result: ~26,000 records

### Generate Sparse Data (Hourly Readings)

```bash
python generate_test_data.py --days 30 --interval 60
```

Result: ~720 records (much faster to generate and query)

## Switching Between Test and Production

### Use Test Database
```powershell
$env:USE_TEST_DB="true"
python main.py
```

### Use Production Database (Default)
```bash
python main.py
```

Or explicitly:
```powershell
$env:USE_TEST_DB="false"
python main.py
```

## Testing the API with Test Data

Once you've generated test data and started the API:

### Get Latest Reading
```bash
curl http://localhost:8000/weather/latest
```

### Get Last 24 Hours
```bash
curl "http://localhost:8000/weather?limit=288"
```
(288 readings = 24 hours at 5-minute intervals)

### Get Specific Date Range
```bash
curl "http://localhost:8000/weather?start_date=2024-12-01&end_date=2024-12-07"
```

### Check Database Stats
```bash
curl http://localhost:8000/weather/stats
```

## File Structure

- `ambient_weather.db` - Production database (real data from Ambient Weather API)
- `ambient_weather_test.db` - Test database (synthetic data)
- `config.py` - Configuration to switch between databases
- `generate_test_data.py` - Script to generate test data
- `main.py` - FastAPI application (automatically uses correct database)

## Tips

1. **Keep test and production separate**: Never overwrite your production database with test data
2. **Regenerate as needed**: Test data is cheap - regenerate whenever you need different scenarios
3. **Match production patterns**: Default 5-minute intervals match typical Ambient Weather station behavior
4. **Use for frontend development**: Test data lets you build UI without API rate limits
5. **Test edge cases**: Modify the generator to create extreme weather events for testing

## Troubleshooting

### API shows wrong database
- Check the environment variable: `echo $env:USE_TEST_DB` (PowerShell)
- Make sure you set it in the same terminal session where you run the API
- Restart the API server after changing the environment variable

### No data in test database
- Run the generator: `python generate_test_data.py`
- Check for errors in the output
- Verify the database file was created: `dir ambient_weather_test.db`

### Generator is slow
- Reduce days: `--days 7` instead of 30
- Increase interval: `--interval 15` instead of 5
- Each 1,000 records takes a few seconds to generate
