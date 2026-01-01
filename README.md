# Ambient Weather Data Manager

A complete solution for retrieving, storing, and visualizing data from your Ambient Weather Network device.

## 🌟 Features

- **Data Retrieval**: Fetch historical and real-time data via the Ambient Weather API
- **SQLite Storage**: Store all weather data in a local database
- **Interactive Visualizations**: Create beautiful, interactive graphs with Plotly
- **Comprehensive Metrics**: Track temperature, humidity, wind, rain, pressure, solar radiation, and UV

## 📋 What You Need

1. An Ambient Weather account with a weather station
2. API credentials from Ambient Weather
3. Python 3.8 or higher

## 🚀 Quick Start

### Step 1: Get Your API Credentials

1. Go to https://ambientweather.net/account
2. Log in to your account
3. Navigate to the "API Keys" section
4. Generate an Application Key and note your API Key
5. You'll need both:
   - **API Key** (unique to your account)
   - **Application Key** (you create this)

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests pandas plotly numpy
```

### Step 3: Configure the Fetcher Script

Edit `ambient_weather_fetcher.py` and replace the placeholder credentials:

```python
API_KEY = 'your_actual_api_key_here'
APPLICATION_KEY = 'your_actual_application_key_here'
```

### Step 4: Fetch Your Data

Run the fetcher script to download all your historical data:

```bash
python ambient_weather_fetcher.py
```

This will:
- Connect to the Ambient Weather API
- Fetch all data since March 2024
- Store it in a SQLite database (`weather_data.db`)
- Show you a summary of the data

**Note**: The script is respectful of API rate limits and may take several minutes to fetch all historical data.

### Step 5: Create Visualizations

Run the visualizer script to generate interactive graphs:

```bash
python ambient_weather_visualizer.py
```

This will:
- Load data from the database
- Create interactive HTML graphs for all metrics
- Save them to the `weather_plots/` directory
- Generate an `index.html` dashboard

### Step 6: View Your Graphs

Open `weather_plots/index.html` in your web browser to see all your visualizations!

## 📊 Available Visualizations

The system creates these interactive graphs:

1. **Temperature Analysis** - Outdoor temp, feels like, dew point, and indoor temp
2. **Wind Analysis** - Wind speed and gusts over time
3. **Wind Direction** - Dominant wind direction scatter plot
4. **Rainfall** - Daily rainfall and hourly rates
5. **Barometric Pressure** - Relative pressure trends
6. **Humidity** - Indoor and outdoor humidity levels
7. **Solar Radiation** - Solar radiation measurements
8. **UV Index** - UV index over time

All graphs are interactive - you can:
- Zoom in/out
- Pan across time
- Hover for exact values
- Toggle data series on/off
- Download as images

## 🗄️ Database Schema

The SQLite database stores data in the `weather_data` table with these fields:

**Temperature & Feels Like:**
- `tempf` - Outdoor temperature (°F)
- `feelsLike` - Feels like temperature (°F)
- `dewPoint` - Dew point (°F)
- `tempinf` - Indoor temperature (°F)

**Humidity:**
- `humidity` - Outdoor humidity (%)
- `humidityin` - Indoor humidity (%)

**Pressure:**
- `baromrelin` - Relative barometric pressure (inHg)
- `baromabsin` - Absolute barometric pressure (inHg)

**Wind:**
- `windspeedmph` - Wind speed (mph)
- `windgustmph` - Wind gust speed (mph)
- `winddir` - Wind direction (degrees)
- `winddir_avg10m` - 10-minute average wind direction

**Rain:**
- `hourlyrainin` - Hourly rainfall (inches)
- `dailyrainin` - Daily rainfall (inches)
- `weeklyrainin` - Weekly rainfall (inches)
- `monthlyrainin` - Monthly rainfall (inches)
- `yearlyrainin` - Yearly rainfall (inches)
- `totalrainin` - Total rainfall (inches)

**Solar:**
- `solarradiation` - Solar radiation (W/m²)
- `uv` - UV index

**Timestamps:**
- `dateutc` - Unix timestamp (milliseconds)
- `date_local` - Local datetime string

## 🔧 Advanced Usage

### Fetch Only Recent Data

Modify the script to fetch data from a specific date:

```python
from datetime import datetime

start_date = datetime(2024, 11, 1)  # November 1, 2024
fetcher.fetch_all_historical_data(mac_address, start_date)
```

### Create Graphs for Specific Date Range

```python
visualizer = WeatherVisualizer()
figs = visualizer.create_comprehensive_dashboard(
    start_date='2024-11-01', 
    end_date='2024-12-30'
)
visualizer.save_plots(figs)
```

### Query the Database Directly

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('weather_data.db')
df = pd.read_sql_query('''
    SELECT date_local, tempf, humidity, windspeedmph
    FROM weather_data
    WHERE date_local >= '2024-12-01'
    ORDER BY date_local
''', conn)
conn.close()

print(df.head())
```

### Export Data to CSV

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('weather_data.db')
df = pd.read_sql_query('SELECT * FROM weather_data ORDER BY dateutc', conn)
df.to_csv('weather_data_export.csv', index=False)
conn.close()
print("✓ Data exported to weather_data_export.csv")
```

## 🔄 Keeping Data Updated

### Manual Update

Run the fetcher script periodically to get new data:

```bash
python ambient_weather_fetcher.py
```

The script automatically avoids duplicates, so it's safe to run multiple times.

### Automated Updates (Linux/Mac)

Set up a cron job to fetch data hourly:

```bash
crontab -e
```

Add this line:
```
0 * * * * cd /path/to/your/project && python ambient_weather_fetcher.py >> fetch.log 2>&1
```

### Automated Updates (Windows)

Use Task Scheduler to run the script on a schedule.

## 🎨 Customizing Visualizations

Edit `ambient_weather_visualizer.py` to customize:

- **Colors**: Modify the `color` parameter in each trace
- **Date ranges**: Pass `start_date` and `end_date` to functions
- **Graph types**: Change from line to scatter, bar, etc.
- **Titles and labels**: Update the layout dictionaries

Example - Change temperature line color:
```python
line=dict(color='#FF6B6B', width=2)  # Red instead of blue
```

## 📝 API Rate Limits

The Ambient Weather API has rate limits:
- 1 request per second
- 288 records per request maximum

The fetcher script respects these limits with built-in delays.

## 🐛 Troubleshooting

**"No devices found"**
- Check your API credentials are correct
- Ensure your device is online and reporting to Ambient Weather

**"No data in database"**
- Run the fetcher script first before the visualizer
- Check the database file exists: `weather_data.db`

**"Import errors"**
- Install all requirements: `pip install -r requirements.txt`
- Use a virtual environment if you have dependency conflicts

**"API errors"**
- Check your internet connection
- Verify your API keys haven't expired
- Check Ambient Weather's API status

## 📚 File Structure

```
ambient-weather-manager/
├── ambient_weather_fetcher.py      # Main data fetching script
├── ambient_weather_visualizer.py   # Visualization script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── weather_data.db                 # SQLite database (created on first run)
└── weather_plots/                  # Generated graphs (created on first run)
    ├── index.html                  # Dashboard index
    ├── temperature.html
    ├── wind.html
    ├── rain.html
    └── ...
```

## 🔗 Resources

- [Product Requirements](Product-Requirements.md) - Project specifications and requirements
- [Ambient Weather API Documentation](https://ambientweather.docs.apiary.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/)

## 📄 License

This is a personal project tool. Use it freely for your own weather data management.

## 🤝 Contributing

Feel free to modify and enhance these scripts for your specific needs!

## 💡 Next Steps

Once you have the basic system working, you might want to:

1. **Create a web dashboard** - Use Flask or Dash to create a live web interface
2. **Add alerts** - Set up email/SMS notifications for weather conditions
3. **Export reports** - Generate PDF reports with weather summaries
4. **Compare data** - Analyze trends across months or years
5. **Machine learning** - Predict weather patterns from historical data

Happy weather tracking! 🌤️
