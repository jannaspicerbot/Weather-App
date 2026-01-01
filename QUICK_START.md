# Quick Start Guide - Weather API with Test Data

Get up and running in 3 simple steps!

## Step 1: Generate Test Data

```bash
python generate_test_data.py --days 7
```

This creates 7 days of realistic weather data (~2,000 records).

## Step 2: Start the API (Test Mode)

**PowerShell:**
```powershell
$env:USE_TEST_DB="true"
python main.py
```

**Bash/Linux:**
```bash
USE_TEST_DB=true python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 3: Test the API

Open a new terminal and run:

```bash
python test_api_quick.py
```

Or visit in your browser:
- **API Root**: http://localhost:8000/
- **Latest Weather**: http://localhost:8000/weather/latest
- **API Docs**: http://localhost:8000/docs

## What's Next?

### View Your Data
```bash
# Get latest reading
curl http://localhost:8000/weather/latest

# Get last 100 readings
curl http://localhost:8000/weather?limit=100

# Get database stats
curl http://localhost:8000/weather/stats
```

### Interactive API Documentation
Visit http://localhost:8000/docs to try all endpoints with a nice UI

### Build Your React Frontend
The API has CORS enabled and is ready for your React app:

```javascript
const response = await fetch('http://localhost:8000/weather/latest');
const weather = await response.json();
console.log(`Current temp: ${weather.tempf}°F`);
```

## Switching to Production Data

When your Ambient Weather account is unlocked:

1. **Fetch real data:**
   ```powershell
   $env:AMBIENT_API_KEY="your_api_key"
   $env:AMBIENT_APP_KEY="your_app_key"
   python ambient_weather_fetch.py
   ```

2. **Start API in production mode:**
   ```bash
   python main.py
   ```
   (No `USE_TEST_DB` environment variable)

## File Reference

- `generate_test_data.py` - Generate synthetic weather data
- `main.py` - FastAPI server
- `config.py` - Database configuration
- `test_api_quick.py` - Quick API test script
- `ambient_weather_test.db` - Test database (synthetic data)
- `ambient_weather.db` - Production database (real data)

## Need Help?

- **Full API docs**: See [API_README.md](API_README.md)
- **Test data guide**: See [TEST_DATA_GUIDE.md](TEST_DATA_GUIDE.md)
- **API endpoints**: http://localhost:8000/docs

## Common Issues

**"Cannot connect to API"**
- Make sure you ran `python main.py` first
- Check that port 8000 is not in use

**"No data found"**
- Generate test data: `python generate_test_data.py`
- Make sure `USE_TEST_DB=true` is set

**"Module not found"**
- Install dependencies: `pip install -r requirements.txt`
