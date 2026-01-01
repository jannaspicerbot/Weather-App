# Quick Start Guide

Get your Weather App running in minutes - choose your path!

## Prerequisites

Install dependencies first:
```bash
pip install -r requirements.txt
```

---

## Option A: Quick Test with Synthetic Data (Recommended for First Run)

Perfect for testing without needing an Ambient Weather account.

### Step 1: Generate Test Data

```bash
python generate_test_data.py --days 7
```

This creates 7 days of realistic weather data (~2,000 records).

### Step 2: Start the API (Test Mode)

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

### Step 3: Test the API

Open a new terminal and run:

```bash
python test_api_quick.py
```

Or visit in your browser:
- **API Root**: http://localhost:8000/
- **Latest Weather**: http://localhost:8000/weather/latest
- **API Docs**: http://localhost:8000/docs

---

## Option B: Production Setup with Real Ambient Weather Data

For users with an Ambient Weather station and API access.

### Step 1: Get Your API Keys

1. Go to https://ambientweather.net
2. Log in to your account
3. Click **Account** → **API Keys**
4. Copy your **API Key** and **Application Key**

### Step 2: Create .env File (Secure Method)

Create a `.env` file in the project root:

```bash
# .env file (this is gitignored for security)
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APP_KEY=your_application_key_here
```

**Note**: The `.env` file is in `.gitignore` to keep your keys secure and prevent them from being committed to git.

### Step 3: Fetch Your Data

```bash
python ambient_weather_fetch.py
```

The script will automatically read keys from your `.env` file. Wait for it to complete (may take a few minutes for historical data). The script only downloads new data on subsequent runs!

**Alternative**: Set environment variables directly (temporary):

**PowerShell:**
```powershell
$env:AMBIENT_API_KEY="your_api_key"
$env:AMBIENT_APP_KEY="your_app_key"
python ambient_weather_fetch.py
```

**Bash/Linux:**
```bash
export AMBIENT_API_KEY="your_api_key"
export AMBIENT_APP_KEY="your_app_key"
python ambient_weather_fetch.py
```

### Step 4: Start the API (Production Mode)

```bash
python main.py
```

(No `USE_TEST_DB` environment variable needed - production is the default)

### Step 5: Create Visualizations (Optional)

```bash
python ambient_weather_visualize.py
```

Open any HTML file in the `output/` directory with your web browser to see interactive charts!

---

## What You Get

After running the setup, you'll have:
- **FastAPI server** running on http://localhost:8000
- **SQLite database** with all weather records
- **Interactive API docs** at http://localhost:8000/docs
- **4 REST endpoints** for querying weather data
- **(Optional) 7+ interactive charts** with Plotly visualizations

---

## Using the API

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

---

## Keeping Data Updated

Run the fetch script regularly (daily or hourly):
```bash
python ambient_weather_fetch.py
```

The script is smart - it only downloads new data, not everything again!

**Automation Tips:**
- **Linux/Mac**: Set up a cron job
- **Windows**: Use Task Scheduler
- See [SCRIPTS_USAGE_GUIDE.md](SCRIPTS_USAGE_GUIDE.md) for details

---

## Common Issues

**"Module not found"**
- Install dependencies: `pip install -r requirements.txt`

**"Cannot connect to API"**
- Make sure you ran `python main.py` first
- Check that port 8000 is not in use

**"No data found"** (Test mode)
- Generate test data: `python generate_test_data.py`
- Make sure `USE_TEST_DB=true` is set

**"No data found"** (Production mode)
- Run fetch script first: `python ambient_weather_fetch.py`
- Check your API keys are correct in `.env` file

**"No devices found"**
- Verify your Ambient Weather API keys are correct in `.env`
- Ensure your weather station is online and reporting data

**"Database not found"**
- Run the fetch script first to create the database

**"Charts are empty"**
- Make sure fetch completed successfully
- Check that you have data in the database

---

## Security Best Practices

- **Never commit API keys to git** - Use `.env` file (already in `.gitignore`)
- **Never share your `.env` file** - It contains sensitive credentials
- **Use environment variables** - More secure than hardcoding in Python files
- If you accidentally commit keys, regenerate them immediately in your Ambient Weather account

---

## File Reference

- `main.py` - FastAPI server entry point
- `weather_app/` - Refactored package structure
- `.env` - Your API keys (create this, never commit it!)
- `generate_test_data.py` - Generate synthetic weather data
- `ambient_weather_fetch.py` - Fetch real data from Ambient Weather API
- `ambient_weather_visualize.py` - Create interactive Plotly charts
- `test_api_quick.py` - Quick API test script
- `ambient_weather_test.db` - Test database (synthetic data)
- `ambient_weather.db` - Production database (real data)

---

## Need More Help?

- **Full API documentation**: [API_README.md](API_README.md)
- **Test data guide**: [TEST_DATA_GUIDE.md](TEST_DATA_GUIDE.md)
- **Scripts usage**: [SCRIPTS_USAGE_GUIDE.md](SCRIPTS_USAGE_GUIDE.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Interactive API docs**: http://localhost:8000/docs

---

## Tips

- Initial fetch takes time - be patient!
- Charts are interactive - hover, zoom, pan
- Database stores everything - visualizations can filter date ranges
- Use test mode for development, production mode for real monitoring
- Keep your `.env` file secure and never share it
