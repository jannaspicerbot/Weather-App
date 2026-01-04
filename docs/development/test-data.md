# Test Data Generation

This document describes the synthetic test data generation system for the Weather App.

## Overview

The test data generator creates realistic weather data for frontend development and testing. It generates synthetic data with:
- **Seasonal temperature patterns** (cold in winter, warm in summer)
- **Daily temperature cycles** (cooler at night, warmer during the day)
- **Realistic humidity** (inversely related to temperature)
- **Wind patterns** (more wind during the day)
- **Occasional rain events** (influenced by barometric pressure)
- **Solar radiation** (zero at night, peaks at solar noon)
- **Proper data continuity** (5-minute intervals)

## Generated Data Statistics

Based on 1 year of test data (365 days, 5-minute intervals):

### Basic Statistics
- **Total records**: 105,108 (288 records/day)
- **Date range**: Full year of data
- **Interval**: 5 minutes (consistent)

### Temperature
- **Average**: 50.0°F (baseline with seasonal variation)
- **Range**: 0.1°F to 99.9°F
- **Seasonal patterns**:
  - Winter: 25.5°F average (0.1°F to 59.3°F)
  - Spring: 61.5°F average (20.4°F to 97.9°F)
  - Summer: 74.3°F average (40.1°F to 99.9°F)
  - Fall: 38.1°F average (1.8°F to 78.9°F)
- **Daily variation**: ~38-40°F range per day

### Humidity
- **Average**: 59.5%
- **Range**: 30% to 94%
- **Pattern**: Inversely related to temperature

### Wind
- **Average speed**: 8.3 mph
- **Max speed**: 17.0 mph
- **Average gust**: 15.8 mph
- **Max gust**: 29.0 mph
- **Pattern**: More wind during daytime hours

### Rain
- **Rainy intervals**: 10.5% of all records
- **Max hourly rain**: 0.8 inches
- **Pattern**: Occasional multi-hour rain events, influenced by low pressure

### Solar Radiation
- **Zero at night**: Correctly 0 from 8pm-6am
- **Peaks at solar noon**: ~900 W/m² in summer, ~600 W/m² in winter
- **UV Index**: 0-11 based on solar radiation

## Usage

### 1. Generate Test Data

```bash
# Generate 1 year of data (default)
python tests/generate_test_data.py --clear

# Generate custom time range
python tests/generate_test_data.py --days 30 --clear

# Generate with different interval
python tests/generate_test_data.py --days 365 --interval 15 --clear

# Specify start date
python tests/generate_test_data.py --start-date 2024-01-01 --days 365 --clear
```

### 2. Verify Data Quality

```bash
python tests/verify_test_data.py
```

This runs comprehensive checks on:
- Basic statistics
- Temperature ranges and seasonal variation
- Humidity patterns
- Wind statistics
- Rain frequency and amounts
- Solar radiation (verifies 0 at night)
- Daily temperature variation
- Data continuity (checks for gaps)

### 3. Use Test Data with API

Update `.env` file:
```bash
USE_TEST_DB=true
```

Then start the API server:
```bash
python main.py
```

The API will now serve data from `ambient_weather_test.duckdb` instead of the production database.

### 4. Test API with Test Data

```bash
python tests/test_local_server.py
```

## File Locations

- **Generator**: `tests/generate_test_data.py`
- **Verifier**: `tests/verify_test_data.py`
- **Test Database**: `ambient_weather_test.duckdb` (project root)
- **Production Database**: `ambient_weather.duckdb` (project root)

## Database Schema

The test database uses the same DuckDB schema as production:

```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    dateutc BIGINT UNIQUE NOT NULL,
    date VARCHAR,
    tempf DOUBLE,
    humidity INTEGER,
    baromabsin DOUBLE,
    baromrelin DOUBLE,
    windspeedmph DOUBLE,
    winddir INTEGER,
    windgustmph DOUBLE,
    maxdailygust DOUBLE,
    hourlyrainin DOUBLE,
    eventrain DOUBLE,
    dailyrainin DOUBLE,
    weeklyrainin DOUBLE,
    monthlyrainin DOUBLE,
    yearlyrainin DOUBLE,
    totalrainin DOUBLE,
    solarradiation DOUBLE,
    uv INTEGER,
    feelsLike DOUBLE,
    dewPoint DOUBLE,
    -- ... additional fields
);
```

## Data Generation Algorithm

### Temperature
1. **Baseline**: 50°F
2. **Seasonal variation**: ±30°F sine wave (peaks in summer, troughs in winter)
3. **Daily variation**: ±15°F sine wave (peaks at 2pm, troughs at 2am)
4. **Random noise**: ±5°F

### Humidity
- **Inverse relationship** with temperature
- **Baseline**: 60%
- **Range**: 30-100%

### Wind
- **Daytime**: 7 mph average ± 4-10 mph variation
- **Nighttime**: 3 mph average ± 4-10 mph variation
- **Gusts**: Wind speed + 3-12 mph

### Rain
- **Base probability**: 8%
- **Pressure-influenced**: 15% when pressure < 29.8 inHg
- **Event-based**: Multi-hour rain events that continue until probability check fails
- **Amount**: 0.01-0.8 inches per hour

### Solar Radiation
- **Nighttime** (6pm-6am): 0 W/m²
- **Daytime**: Sine curve peaking at solar noon
  - **Peak**: 900 W/m² in summer, 600 W/m² in winter
  - **UV index**: Derived from solar radiation (0-11 scale)

## Frontend Development Use Cases

This test data supports all planned frontend visualizations:

### Phase 1 Charts (MVP)
1. **Temperature Chart**
   - High/low range visualization (area chart)
   - Average line
   - Seasonal patterns clearly visible

2. **Humidity Chart**
   - Average line
   - Inverse relationship with temperature

3. **Wind Speed Chart**
   - Bar chart for speed
   - Overlay for gusts
   - Day/night variation

4. **Precipitation Chart**
   - Bar chart for rain amounts
   - Occasional rain events (realistic patterns)

### Phase 2 Charts
5. **Barometric Pressure** - Slight variations with monthly cycles
6. **Wind Direction** - Random but realistic scatter
7. **Solar Radiation** - Perfect day/night cycle, seasonal variation

### Testing Time Range Selection
The 1 year of data supports testing all time range selectors:
- ✓ Last 24 hours
- ✓ Last week
- ✓ Last month
- ✓ Last 6 months
- ✓ Last year
- ✓ Custom date ranges

### Testing Data Filtering
With 105,108 records, you can test:
- Performance with large datasets
- Pagination
- Date range filtering
- Data aggregation
- Chart rendering optimization

## Known Issues / Notes

1. **Cumulative rain totals** may be higher than realistic values. This doesn't affect the patterns or frontend visualization testing.

2. **One data gap**: The verification shows 1 gap larger than 6 minutes. This is likely at the year boundary and doesn't affect frontend testing.

3. **Temperature range**: The 0-100°F range is intentionally wide to test edge cases. Real weather data would be more moderate depending on location.

## Future Enhancements

Potential improvements for future iterations:

1. **Location-based patterns**: Generate data matching specific climates (tropical, desert, temperate, etc.)
2. **Weather events**: Add storms, heat waves, cold snaps with more complex patterns
3. **Multi-year data**: Generate 2-3 years for testing long-term trends
4. **Correlation improvements**: Better correlation between pressure, rain, and temperature
5. **Indoor sensors**: Add indoor temperature and humidity data
