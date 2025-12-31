# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get Your API Keys
1. Go to https://ambientweather.net
2. Log in to your account
3. Click **Account** → **API Keys**
4. Copy your **API Key** and **Application Key**

### 3. Configure
Edit `ambient_weather_fetch.py` and add your keys:
```python
API_KEY = "your_api_key_here"
APPLICATION_KEY = "your_application_key_here"
```

### 4. Fetch Data
```bash
python ambient_weather_fetch.py
```
Wait for it to complete (may take a few minutes for historical data)

### 5. Create Visualizations
```bash
python ambient_weather_visualize.py
```

### 6. View Your Data
Open any HTML file in the `output/` directory with your web browser!

## 📊 What You Get

After running the scripts, you'll have:
- **7 interactive charts** showing all your weather data
- **SQLite database** with all historical records
- **Zoom, pan, and explore** your weather trends

## 🔄 Keeping Data Updated

Run the fetch script regularly (daily or hourly):
```bash
python ambient_weather_fetch.py
```

The script is smart - it only downloads new data, not everything again!

## ⚠️ Common Issues

**"No devices found"** → Check your API keys are correct

**"Database not found"** → Run the fetch script first

**Charts are empty** → Make sure fetch completed successfully

## 💡 Tips

- Initial fetch takes time - be patient!
- Charts are interactive - hover, zoom, pan
- Database stores everything - visualizations can filter date ranges
- Run fetch script on a schedule for automatic updates

## 📚 Need More Help?

See the full README.md for detailed information!
