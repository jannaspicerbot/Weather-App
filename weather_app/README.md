# Weather App Backend

Python backend for the Weather App, providing data collection from Ambient Weather API, storage in DuckDB, and a REST API for the frontend dashboard.

## Tech Stack

- **Framework:** FastAPI
- **Database:** DuckDB
- **Scheduler:** APScheduler
- **CLI:** Click
- **HTTP Client:** Requests

## Package Structure

```
weather_app/
├── __init__.py           # Package initialization
├── config.py             # Configuration and environment variables
├── logging_config.py     # Structured logging setup
├── api/                  # Ambient Weather API client
│   ├── __init__.py
│   └── client.py         # AmbientWeatherAPI class
├── cli/                  # Command-line interface
│   ├── __init__.py
│   ├── __main__.py       # Entry point for `python -m weather_app.cli`
│   └── cli.py            # Click commands (fetch, backfill, init-db, etc.)
├── database/             # Database layer
│   ├── __init__.py
│   ├── engine.py         # DuckDB connection management
│   └── repository.py     # WeatherDatabase class with queries
├── launcher/             # Desktop app launcher utilities
│   ├── __init__.py
│   ├── crash_logger.py   # Crash reporting
│   ├── resource_path.py  # PyInstaller resource handling
│   ├── setup_wizard.py   # First-run configuration
│   └── tray_app.py       # System tray application
├── scheduler/            # Background job scheduling
│   ├── __init__.py
│   └── scheduler.py      # WeatherScheduler (APScheduler)
└── web/                  # FastAPI web application
    ├── __init__.py
    ├── app.py            # Application factory
    ├── models.py         # Pydantic models
    └── routes.py         # API endpoints
```

## Key Components

### API Client (`api/client.py`)

`AmbientWeatherAPI` class handles communication with Ambient Weather REST API:
- Device listing
- Current weather data
- Historical data fetching
- Rate limiting (1.1s between calls)

### Database (`database/`)

`WeatherDatabase` class manages DuckDB operations:
- Schema creation and migrations
- Weather data insertion (with deduplication)
- Query methods for dashboard data
- Statistics and aggregations

### CLI (`cli/cli.py`)

Click-based command-line interface:
```bash
weather-app init-db          # Initialize database
weather-app fetch            # Fetch latest data
weather-app backfill         # Backfill historical data
weather-app db-info          # Show database statistics
weather-app export           # Export data to CSV
```

### Web API (`web/`)

FastAPI application with endpoints:
- `GET /api/weather/latest` - Most recent reading
- `GET /api/weather/history` - Historical data with date range
- `GET /api/weather/stats` - Aggregated statistics
- `GET /api/scheduler/status` - Background job status

### Scheduler (`scheduler/scheduler.py`)

APScheduler-based background job runner:
- Automated data collection every 5 minutes
- Graceful startup/shutdown with FastAPI lifespan

## Development

### Running the API Server

```bash
# Development mode with auto-reload
python -m uvicorn weather_app.web.app:create_app --factory --reload --port 8000

# Visit http://localhost:8000/docs for Swagger UI
```

### Running CLI Commands

```bash
# If installed with pip install -e .
weather-app --help

# Or run as module
python -m weather_app.cli --help
```

### Environment Variables

Required in `.env` file:
```
AMBIENT_API_KEY=your_api_key
AMBIENT_APP_KEY=your_app_key
DATABASE_PATH=./ambient_weather.duckdb  # Optional, has default
```

## Testing

```bash
# Run all backend tests
pytest tests/ -m "not requires_api_key"

# Run with API integration tests (requires credentials)
pytest tests/ -m "requires_api_key"
```

## Related Documentation

- [API Reference](../docs/technical/api-reference.md)
- [CLI Guide](../docs/technical/cli-guide.md)
- [Architecture Overview](../docs/architecture/overview.md)
- [Database Schema](../docs/architecture/adr-005-duckdb-schema.md)
