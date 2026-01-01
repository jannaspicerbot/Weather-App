# Refactored Architecture

## Package Structure & Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTRY POINT                              │
│              main_refactored.py                             │
│         (or run with: python main_refactored.py)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              WEB / API LAYER                                 │
│          weather_app.web.app.create_app()                  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ FastAPI Configuration                               │  │
│  │ - CORS Middleware                                    │  │
│  │ - Exception Handlers                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Routes (weather_app.web.routes)                     │  │
│  │ ├─ GET /                   (root)                   │  │
│  │ ├─ GET /weather            (filtered query)         │  │
│  │ ├─ GET /weather/latest     (latest reading)        │  │
│  │ └─ GET /weather/stats      (db statistics)         │  │
│  └─────────────┬──────────────────────────────────────┘  │
│                │                                            │
│                ▼                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Pydantic Models (weather_app.web.models)            │  │
│  │ ├─ WeatherData (response)                           │  │
│  │ └─ DatabaseStats (response)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│          STORAGE / REPOSITORY LAYER                          │
│       weather_app.storage.repository                        │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ WeatherRepository (abstraction layer)               │  │
│  │ ├─ get_all_readings()     (paginated query)        │  │
│  │ ├─ get_latest_reading()   (single latest)          │  │
│  │ └─ get_stats()            (aggregates)             │  │
│  └─────────────┬──────────────────────────────────────┘  │
│                │                                            │
│                ▼                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Database Session Manager                            │  │
│  │ (weather_app.db.session)                            │  │
│  │ ├─ DatabaseConnection.get_connection()             │  │
│  │ ├─ DatabaseConnection.close_connection()           │  │
│  │ └─ row_to_dict()                                    │  │
│  └─────────────┬──────────────────────────────────────┘  │
│                │                                            │
│                ▼                                            │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE LAYER                                  │
│           sqlite3 (ambient_weather.db)                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ weather_data table                                  │  │
│  │ ├─ id, dateutc, date                               │  │
│  │ ├─ tempf, humidity, pressure, etc.                 │  │
│  │ └─ indexes on (id), (dateutc), etc.               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              CONFIGURATION LAYER                             │
│            weather_app.config                               │
│                                                              │
│  Environment Variables → config.py → Application            │
│  - USE_TEST_DB          → DB_PATH                          │
│  - BIND_HOST, BIND_PORT → HOST, PORT                       │
│  - LOG_LEVEL            → Logging config                   │
│  - etc.                                                     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow: API Request → Database

```
HTTP Request (GET /weather?limit=10)
  │
  ├─> FastAPI Route Handler (routes.py)
  │    - Parse & validate query parameters
  │    - Handle errors (ValueError → 400, RuntimeError → 500)
  │
  ├─> Repository Layer (repository.py)
  │    - Converts parameters to SQL
  │    - Executes query
  │    - Returns list of dicts
  │
  ├─> Database Session (session.py)
  │    - Creates connection to SQLite
  │    - Executes cursor.execute()
  │    - Fetches rows
  │    - Returns as sqlite3.Row objects
  │
  ├─> Database File (ambient_weather.db)
  │    - SQL query executed
  │    - Results fetched from disk
  │
  └─> HTTP Response (JSON)
       - Pydantic model validates data
       - Converts to JSON (200 OK)
```

## Module Independence

```
weather_app/
├── config.py          [CORE] - No dependencies (except os, pathlib)
├── db/
│   ├── __init__.py
│   └── session.py     [CORE] - Depends on: config
├── web/
│   ├── __init__.py
│   ├── models.py      [CORE] - Depends on: pydantic (external)
│   ├── app.py         [APP]  - Depends on: routes
│   └── routes.py      [APP]  - Depends on: models, repository, config
├── storage/
│   ├── __init__.py
│   └── repository.py  [APP]  - Depends on: db.session
├── fetch/             [FUTURE] - Will contain: ambient_client, fetcher
└── utils/             [FUTURE] - Will contain: logging, retry helpers
```

## Benefits of This Architecture

1. **Separation of Concerns**
   - Routes don't know about SQL
   - Repository doesn't know about HTTP
   - Config is isolated and testable

2. **Reusability**
   - `storage/repository.py` can be used by:
     - Web routes (HTTP API)
     - CLI commands (future)
     - Scheduled jobs (fetch, aggregation)

3. **Testability**
   - Each module can be unit tested independently
   - Mock dependencies easily
   - Test database mode via `USE_TEST_DB` env var

4. **Maintainability**
   - New features go in appropriate module
   - Changes are localized
   - Code navigation is predictable

5. **Extensibility**
   - Add CLI layer without changing Web
   - Add Fetch layer without changing Storage
   - Add Retention logic in separate module
   - Switch database (SQLAlchemy ORM ready)

## Migration From Flat Structure

Old (Flat):
```
Weather-App/
├── main.py          (FastAPI + routes + models)
├── config.py        (config)
├── ambient_weather_fetch.py
├── ambient_weather_visualize.py
└── backfill_weather.py
```

New (Organized):
```
Weather-App/
├── main_refactored.py (entry point only - 9 lines)
├── weather_app/
│   ├── config.py     (same config, enhanced)
│   ├── web/
│   │   ├── app.py           (FastAPI setup)
│   │   ├── routes.py        (endpoints)
│   │   └── models.py        (Pydantic)
│   ├── storage/
│   │   └── repository.py    (queries)
│   ├── db/
│   │   └── session.py       (connection)
│   ├── fetch/        (future: ambient_client, fetcher)
│   └── utils/        (future: logging, retry)
```

**Next Phase:** Move fetch scripts into `weather_app/fetch/` with unified CLI
