# Claude Code Best Practices & Guidelines

**Project:** Weather Dashboard Application
**Stack:** FastAPI + React + TypeScript + DuckDB
**Developer Level:** Learning modern app development
**Goals:** Fast prototype → Iterate for polish → Learn best practices

---

## 🤖 Model Selection Strategy

Choose the right Claude model to balance performance, speed, and cost:

- **Sonnet 4.5** - Default. Best for most development tasks.
- **Opus 4.5** - Complex reasoning, architectural planning, large refactoring.
- **Haiku 4** - Simple tasks, quick fixes, boilerplate generation.

### When to Use Each Model

| Task Type | Model | Why |
|-----------|-------|-----|
| Architectural planning & system design | **Opus** | Deep reasoning about trade-offs |
| Large-scale refactoring (multi-file) | **Opus** | Cross-file dependencies |
| Database schema design | **Opus** | Long-term performance implications |
| Performance optimization | **Opus** | Deep bottleneck analysis |
| Feature implementation | **Sonnet** | Balanced capability |
| Code reviews & debugging | **Sonnet** | Context understanding |
| API development | **Sonnet** | Pattern following |
| Documentation writing | **Sonnet** | Code comprehension |
| Simple edits & typo fixes | **Haiku** | Fast, straightforward |
| Boilerplate code generation | **Haiku** | Minimal reasoning |
| Quick file searches | **Haiku** | Simple operations |

### Quick Decision Tree

```
Is it a simple, well-defined task? (typo, search, boilerplate)
├─ YES → Haiku
└─ NO → Continue

Does it require deep architectural reasoning or cross-system analysis?
├─ YES → Opus
└─ NO → Sonnet (default)
```

### Examples

```bash
# Opus - Complex architectural decision
claude --model opus "Evaluate DuckDB vs PostgreSQL for our use case"

# Sonnet - Standard development (default)
claude "Add CSV export to weather API"

# Haiku - Simple fix
claude --model haiku "Fix typo in README line 42"
```

**Cost**: Haiku ~1x | Sonnet ~3-5x | Opus ~15-20x

**Default Rule**: When in doubt, use **Sonnet 4.5**.

---

## 🎯 Core Principles

1. **Write clean, readable code** - Prioritize clarity over cleverness
2. **Comment complex logic** - Explain WHY, not just WHAT
3. **Follow language conventions** - PEP 8 for Python, ESLint standards for TypeScript
4. **Test as you build** - Verify functionality immediately
5. **Keep it simple first** - Optimize later if needed

---

## 📁 Project Structure

### Current Structure
```
Weather-App/
├── weather_app/
│   ├── __init__.py
│   ├── config.py            # Configuration, environment variables
│   ├── cli/                 # CLI commands (Click framework)
│   │   ├── __init__.py
│   │   ├── __main__.py      # Module execution entry point
│   │   └── cli.py           # All CLI commands
│   ├── fetch/               # API and database operations
│   │   ├── __init__.py
│   │   ├── api.py           # AmbientWeatherAPI class
│   │   └── database.py      # AmbientWeatherDB class
│   └── backend/             # FastAPI app (future)
│       ├── main.py          # FastAPI app, routes
│       ├── database.py      # Database queries
│       └── models.py        # Pydantic models
├── scripts/                 # Standalone utility scripts
│   ├── ambient_weather_fetch.py
│   └── backfill_weather.py
├── tests/                   # Test scripts
├── web/                     # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── api/             # Auto-generated OpenAPI types
│   │   └── lib/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
├── setup.py                 # Package installation config
├── requirements.txt         # Python dependencies
├── ambient_weather.duckdb   # DuckDB database
└── .env                     # Environment variables
```

---

## 🐍 Python/FastAPI Best Practices

### Code Style
- Use **type hints** for all function parameters and returns
- Follow **PEP 8** naming conventions (snake_case for functions/variables)
- Keep functions **under 50 lines** when possible
- Use **meaningful variable names** (no single letters except in loops)

### FastAPI Specific
```python
# ✅ GOOD - Type hints, clear naming, error handling
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from datetime import datetime

@app.get("/api/weather/latest", response_model=WeatherData)
async def get_latest_weather() -> WeatherData:
    """
    Retrieve the most recent weather reading from the database.
    
    Returns:
        WeatherData: Latest weather observation
        
    Raises:
        HTTPException: If no data found or database error
    """
    try:
        result = db.query_latest_weather()
        if not result:
            raise HTTPException(status_code=404, detail="No weather data found")
        return WeatherData(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ❌ BAD - No types, unclear naming, no error handling
@app.get("/weather")
def get_w():
    return db.query()
```

### Database Queries
- **Always use parameterized queries** to prevent SQL injection
- **Close connections properly** using context managers
- **Handle errors gracefully** with try/except blocks
- **Validate input** before querying

```python
# ✅ GOOD - Parameterized, context manager, error handling
def get_weather_by_date(target_date: str) -> List[dict]:
    """Get weather data for a specific date."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM weather_data WHERE DATE(date) = ? ORDER BY date",
                (target_date,)
            )
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        return []

# ❌ BAD - SQL injection risk, no error handling
def get_weather(date):
    conn = sqlite3.connect("ambient_weather.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM weather_data WHERE date = '{date}'")
    return cursor.fetchall()
```

### Environment Variables
- **Never hardcode secrets** (API keys, passwords)
- Use **python-dotenv** to load `.env` file
- Provide **default values** for non-sensitive config

```python
# ✅ GOOD
from dotenv import load_dotenv
import os

load_dotenv()

AMBIENT_API_KEY = os.getenv("AMBIENT_API_KEY")
AMBIENT_APP_KEY = os.getenv("AMBIENT_APP_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "./ambient_weather.db")
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

if not AMBIENT_API_KEY:
    raise ValueError("AMBIENT_API_KEY environment variable is required")
```

---

## 🖥️ CLI Best Practices (Click Framework)

### Command Structure
- **Group related commands** under a main CLI group
- **Use clear command names** that describe the action
- **Provide helpful descriptions** for commands and options
- **Add --help text** for all commands and options

```python
# ✅ GOOD - Clear structure with Click
import click
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

@click.group()
@click.version_option(version='1.0.0', prog_name='weather-app')
def cli():
    """Weather App - Ambient Weather data collection and visualization"""
    pass

@cli.command()
@click.option('--limit', default=1, type=int, help='Number of records to fetch')
def fetch(limit):
    """Fetch latest weather data from Ambient Weather API"""
    click.echo(f"Fetching {limit} latest record(s)...")
    # Implementation here

@cli.command()
@click.option('--start', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end', required=True, help='End date (YYYY-MM-DD)')
def backfill(start, end):
    """Backfill historical weather data for a date range"""
    # Validate dates
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError as e:
        click.echo(f"❌ Invalid date format: {e}")
        sys.exit(1)

    # Implementation here
```

### User-Friendly Output
- **Use emoji** for visual feedback (with Windows encoding fix)
- **Show progress** for long-running operations
- **Provide clear error messages** with actionable guidance
- **Use colors** sparingly for emphasis (Click supports this)

```python
# ✅ GOOD - User-friendly messages
click.echo("✅ Database initialized successfully")
click.echo("📡 Fetching from device: Weather Station")
click.echo("❌ Error: API credentials not found!")
click.echo("Please set environment variables:")
click.echo("  AMBIENT_API_KEY - Your API key")
click.echo("  AMBIENT_APP_KEY - Your Application key")

# Progress indication
with click.progressbar(data, label='Processing records') as bar:
    for item in bar:
        process(item)
```

### Environment Variables
- **Load .env at module level** before defining commands
- **Validate required credentials** before making API calls
- **Provide helpful error messages** when credentials are missing

```python
# ✅ GOOD - Load and validate environment variables
from dotenv import load_dotenv
import os

load_dotenv()

def fetch(limit):
    api_key = os.getenv('AMBIENT_API_KEY')
    app_key = os.getenv('AMBIENT_APP_KEY')

    if not api_key or not app_key:
        click.echo("❌ Error: API credentials not found!")
        click.echo("Please set environment variables:")
        click.echo("  AMBIENT_API_KEY - Your API key")
        click.echo("  AMBIENT_APP_KEY - Your Application key")
        click.echo("\nOr create a .env file with these variables.")
        sys.exit(1)
```

### Error Handling
- **Catch specific exceptions** and provide context
- **Use sys.exit(1)** for error conditions
- **Clean up resources** in error cases
- **Save progress** before exiting on long operations

```python
# ✅ GOOD - Comprehensive error handling
@cli.command()
def backfill(start, end):
    try:
        # Operations here
        pass
    except KeyboardInterrupt:
        click.echo("\n⚠️  Backfill interrupted by user")
        click.echo("Progress has been saved. Run again to resume.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            click.echo("❌ Rate limit exceeded. Please wait and try again.")
        else:
            click.echo(f"❌ HTTP Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        sys.exit(1)
```

### Package Installation
- **Create setup.py** with console_scripts entry point
- **Use meaningful command names** for the CLI
- **Install in editable mode** during development

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="weather-app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        # ... other dependencies
    ],
    entry_points={
        'console_scripts': [
            'weather-app=weather_app.cli:cli',
        ],
    },
)
```

```bash
# Install in editable mode for development
pip install -e .

# Now you can run:
weather-app --help
weather-app fetch --limit 10
weather-app backfill --start 2024-01-01 --end 2024-12-31

# Or run as module:
python -m weather_app.cli fetch --limit 10
```

---

## ⚛️ React/TypeScript Best Practices

### Code Style
- Use **functional components** with hooks (not class components)
- Use **const** by default, **let** only when reassignment needed
- Keep components **under 200 lines** - split if larger
- Use **descriptive component names** (PascalCase)

### Component Structure
```jsx
// ✅ GOOD - Clear, modular, documented
import React, { useState, useEffect } from 'react';
import { fetchLatestWeather } from '../services/api';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

/**
 * Displays the current weather conditions
 * Fetches latest data from API on mount and every 5 minutes
 */
export default function CurrentWeather() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadWeather = async () => {
      try {
        setLoading(true);
        const data = await fetchLatestWeather();
        setWeather(data);
        setError(null);
      } catch (err) {
        setError('Failed to load weather data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadWeather();
    const interval = setInterval(loadWeather, 5 * 60 * 1000); // 5 min
    return () => clearInterval(interval);
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} />;
  if (!weather) return <p>No weather data available</p>;

  return (
    <div className="weather-card">
      <h2>Current Weather</h2>
      <p>Temperature: {weather.tempf}°F</p>
      <p>Humidity: {weather.humidity}%</p>
    </div>
  );
}

// ❌ BAD - Too much in one component, poor error handling
function Weather() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/weather').then(r => r.json()).then(d => setData(d));
  }, []);
  
  return <div>{data?.temp}</div>;
}
```

### API Calls
- **Centralize API calls** in a service layer
- **Handle errors** with try/catch
- **Show loading states** to users
- Use **async/await** instead of .then() chains

```typescript
// ✅ GOOD - Centralized, error handling, clear
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchLatestWeather() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/weather/latest`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch weather:', error);
    throw error;
  }
}

export async function fetchWeatherHistory(startDate, endDate) {
  const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
  
  try {
    const response = await fetch(`${API_BASE_URL}/api/weather/history?${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch weather history:', error);
    throw error;
  }
}
```

### State Management
- Start with **useState** for simple state
- Use **useReducer** for complex state logic
- Consider **Context API** for global state (if needed later)
- **Don't over-engineer** - keep it simple initially

---

## 📦 Module Organization & Architecture

### When to Create Packages vs Modules
- **Create a package (directory with __init__.py)** when:
  - Multiple related modules work together
  - You want to organize code by functionality
  - The feature will grow with multiple files

- **Use a single module (.py file)** when:
  - The functionality is self-contained
  - The code is small and unlikely to grow much

```python
# ✅ GOOD - weather_app/fetch/ is a package
weather_app/
├── fetch/
│   ├── __init__.py      # Exports main classes
│   ├── api.py           # AmbientWeatherAPI class
│   └── database.py      # AmbientWeatherDB class

# weather_app/fetch/__init__.py
from weather_app.fetch.api import AmbientWeatherAPI
from weather_app.fetch.database import AmbientWeatherDB

__all__ = ['AmbientWeatherAPI', 'AmbientWeatherDB']
```

### Context Managers for Resource Management
- **Use context managers** for database connections, file handles, API sessions
- **Implement __enter__ and __exit__** for custom classes
- **Clean up resources** in __exit__ even if errors occur

```python
# ✅ GOOD - Context manager for database
class AmbientWeatherDB:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Usage
with AmbientWeatherDB(db_path) as db:
    db.create_tables()
    inserted, skipped = db.insert_data(data)
# Connection automatically closed
```

### Separation of Concerns
- **Separate API logic from database logic**
- **Keep business logic out of CLI commands**
- **Create focused, single-responsibility classes**

```python
# ✅ GOOD - Separated concerns
# api.py - Only handles API communication
class AmbientWeatherAPI:
    def __init__(self, api_key, application_key):
        self.api_key = api_key
        self.application_key = application_key

    def get_devices(self):
        # API call logic
        pass

    def get_device_data(self, mac_address, limit=288):
        # API call logic
        pass

# database.py - Only handles database operations
class AmbientWeatherDB:
    def __init__(self, db_path):
        self.db_path = db_path

    def create_tables(self):
        # Database schema creation
        pass

    def insert_data(self, data):
        # Database insertion logic
        pass

# cli.py - Only handles user interaction
@cli.command()
def fetch(limit):
    """Fetch latest weather data"""
    api = AmbientWeatherAPI(api_key, app_key)
    data = api.get_device_data(mac, limit)

    with AmbientWeatherDB(db_path) as db:
        inserted, skipped = db.insert_data(data)

    click.echo(f"✅ Inserted: {inserted}, Skipped: {skipped}")
```

### Module-Level Initialization
- **Load environment variables once** at module level
- **Configure logging** at module level
- **Platform-specific setup** (like encoding) at module level

```python
# ✅ GOOD - Module-level initialization
# cli.py
import click
import sys
from dotenv import load_dotenv

# Load once when module is imported
load_dotenv()

# Platform-specific configuration
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Now define commands
@click.group()
def cli():
    pass
```

---

## 📊 Data Visualization (Recharts)

### Chart Best Practices
- **Responsive sizing** - charts should work on all screen sizes
- **Clear labels** - axis labels, tooltips, legends
- **Consistent colors** - use a defined color palette
- **Loading states** - show placeholders while data loads

```jsx
// ✅ GOOD - Responsive, accessible, clear
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function TemperatureChart({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-gray-500">No data available</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date" 
          label={{ value: 'Date', position: 'insideBottom', offset: -5 }}
        />
        <YAxis 
          label={{ value: 'Temperature (°F)', angle: -90, position: 'insideLeft' }}
        />
        <Tooltip />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="tempf" 
          stroke="#ef4444" 
          name="Temperature"
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

## 🎨 Styling with Tailwind CSS

### Best Practices
- Use **utility classes** for most styling
- Create **component classes** for repeated patterns
- Keep classes **organized and readable**
- Use **responsive prefixes** (sm:, md:, lg:)

```jsx
// ✅ GOOD - Organized, responsive, semantic
<div className="
  container mx-auto px-4 py-8
  max-w-6xl
  bg-white dark:bg-gray-800
  rounded-lg shadow-lg
">
  <h1 className="
    text-3xl md:text-4xl lg:text-5xl
    font-bold text-gray-900 dark:text-white
    mb-6
  ">
    Weather Dashboard
  </h1>
  
  <div className="
    grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3
    gap-6
  ">
    {/* Cards here */}
  </div>
</div>

// ❌ BAD - Inline styles, not responsive
<div style={{width: '800px', background: '#fff', padding: '20px'}}>
  <h1 style={{fontSize: '32px', fontWeight: 'bold'}}>Weather</h1>
</div>
```

---

## 🧪 Testing & Validation

### What to Test
- **API endpoints** return expected data
- **Database queries** work correctly
- **React components** render without errors
- **API calls** handle errors gracefully

### Quick Testing
```python
# Backend - Test endpoints manually first
# Run: uvicorn main:app --reload
# Visit: http://localhost:8000/docs (FastAPI auto-docs)
# Try each endpoint in the Swagger UI

# Frontend - Test in browser
# Run: npm run dev
# Check browser console for errors
# Test with real API and with mock data
```

---

## 🔒 Security Basics

### Backend Security
- **Validate all input** - use Pydantic models
- **Use CORS properly** - specify allowed origins
- **Don't expose sensitive data** in error messages
- **Rate limit** if deploying publicly (future)

```python
# ✅ GOOD - Proper CORS setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# When deploying to production, update to:
# allow_origins=["https://yourdomain.com"]
```

### Frontend Security
- **Don't store secrets** in frontend code
- **Validate user input** before sending to API
- **Use environment variables** for API URLs

---

## 📝 Documentation Strategy

### Documentation Structure

The project follows a **separation of concerns** approach for documentation:

```
docs/
├── README.md                      # Navigation guide
├── product/                       # Business & user-focused docs
│   └── requirements.md            # Product Requirements Document (PRD)
├── architecture/                  # System design & decisions
│   ├── overview.md                # High-level architecture
│   └── decisions/                 # Architecture Decision Records (ADRs)
│       ├── 001-fastapi-backend.md
│       ├── 002-duckdb-migration.md
│       ├── 003-typescript-frontend.md
│       ├── 004-docker-deployment.md
│       └── 005-retention-strategy.md
├── technical/                     # Implementation guides
│   ├── api-reference.md           # REST API documentation
│   ├── cli-reference.md           # CLI command reference
│   ├── database-schema.md         # DuckDB schema & queries
│   └── deployment-guide.md        # Installation & setup
└── archive/                       # Historical docs
```

### Documentation Types

#### 1. Product Documentation (docs/product/)

**Purpose:** Business context, user needs, project goals

**Content:**
- Executive summary
- Problem statement & Jobs-to-be-Done (JTBD)
- User personas
- Functional & non-functional requirements
- Success metrics & acceptance criteria
- Out of scope items
- Risk assessment

**Audience:** Product managers, stakeholders, business users

**When to update:** Per phase (quarterly) or when requirements change

#### 2. Architecture Documentation (docs/architecture/)

**Purpose:** System design, technology choices, trade-offs

**Content:**

**overview.md:**
- Technology stack with status table
- System diagrams (C4 model: Context → Container → Component)
- Data flow diagrams
- Database schema overview
- API design patterns
- Deployment architecture
- Performance benchmarks

**decisions/ (ADRs - Architecture Decision Records):**
- Context: Why this decision is needed
- Decision: What we're choosing
- Rationale: Why this over alternatives (with comparisons)
- Consequences: Positive, negative, neutral
- Alternatives Considered: What else was evaluated
- Validation: Success criteria & metrics

**Audience:** Architects, senior developers, technical leads

**When to update:**
- overview.md: Per phase (quarterly)
- ADRs: When making major technology decisions

#### 3. Technical Documentation (docs/technical/)

**Purpose:** Implementation details, usage guides, reference material

**Content:**

**api-reference.md:**
- All REST endpoints with request/response schemas
- Error codes and handling
- Code examples (TypeScript, Python, curl)
- OpenAPI schema reference

**cli-reference.md:**
- All CLI commands with arguments/options
- Usage examples
- Scheduling (cron, systemd, Task Scheduler)
- Troubleshooting common issues

**database-schema.md:**
- Table structures with column definitions
- Indexes and constraints
- Common query patterns
- Backup & restore procedures
- Performance characteristics

**deployment-guide.md:**
- Installation steps (Docker Compose, native)
- Configuration (environment variables)
- Automated data collection setup
- Monitoring & health checks
- Updates & maintenance
- Platform-specific notes

**Audience:** Developers, DevOps engineers, end users

**When to update:** Per release (monthly) or when implementation changes

### ADR (Architecture Decision Record) Pattern

**When to create an ADR:**
- Choosing between major technologies (database, framework, language)
- Significant architectural changes (data retention, deployment strategy)
- Decisions that affect multiple teams or future development
- Trade-offs that need to be documented for future reference

**ADR Template:**

```markdown
# ADR-XXX: Title

**Status:** 🟡 Proposed | ✅ Accepted | ❌ Rejected | ♻️ Superseded
**Date:** YYYY-MM-DD
**Deciders:** Names

## Context
What is the issue we're seeing that is motivating this decision?

## Decision
What is the change we're proposing?

## Rationale
Why this approach over alternatives?
- Include comparison tables
- Benchmarks where applicable
- Peer review feedback

## Consequences

### Positive
- ✅ Benefits of this decision

### Negative
- ⚠️ Drawbacks or limitations

### Neutral
- Other considerations

## Alternatives Considered
What other options were evaluated and why were they rejected?

## Validation
Success criteria and metrics to measure if this decision was correct.

## References
Links to relevant documentation, benchmarks, peer reviews.
```

**ADR Numbering:** Use sequential numbers (001, 002, 003...) in filename

**ADR Status:**
- 🟡 **Proposed:** Under discussion
- ✅ **Accepted:** Implemented and in use
- ❌ **Rejected:** Decided against
- ♻️ **Superseded:** Replaced by newer ADR (link to replacement)

### Documentation Best Practices

#### Separation of Concerns
- **DON'T** mix business requirements with technical implementation
- **DON'T** duplicate content across multiple docs
- **DO** link between related documents
- **DO** keep each document focused on its purpose

#### Writing Style
- **Product docs:** User-focused, business language, outcomes
- **Architecture docs:** Design-focused, trade-offs, diagrams
- **Technical docs:** Implementation-focused, code examples, how-to

#### Maintenance
- **Add changelog** at bottom of each document
- **Update version/date** when making changes
- **Move outdated docs** to archive/ directory
- **Keep archive/** for historical reference (never delete)

#### Navigation
- **docs/README.md** is the entry point
- Organize by **topic** (Installation, API, CLI, Database)
- Organize by **role** (End User, Developer, Architect)
- Provide **use case-based paths** ("I want to...")

### Code Comments

In addition to documentation files, write clear code comments:

- **Explain WHY**, not what (code shows what)
- **Document complex logic**
- **Add docstrings** to all functions
- **Keep comments updated** when code changes

```python
# ✅ GOOD - Explains reasoning
def calculate_dew_point(temp_f: float, humidity: float) -> float:
    """
    Calculate dew point using Magnus formula.

    Uses the simplified Magnus formula which is accurate for
    typical weather conditions (temp: -40°F to 122°F, RH: 1-100%).

    Args:
        temp_f: Temperature in Fahrenheit
        humidity: Relative humidity as percentage (0-100)

    Returns:
        Dew point temperature in Fahrenheit
    """
    # Convert F to C for formula
    temp_c = (temp_f - 32) * 5/9

    # Magnus formula constants
    a = 17.27
    b = 237.7

    # Calculate dew point in Celsius
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(humidity / 100.0)
    dew_point_c = (b * alpha) / (a - alpha)

    # Convert back to Fahrenheit
    return (dew_point_c * 9/5) + 32

# ❌ BAD - Just restates code
def calc(t, h):
    # Convert to celsius
    tc = (t - 32) * 5/9
    # Do calculation
    result = some_formula(tc, h)
    # Return result
    return result
```

### Documentation Workflow

#### When Adding New Features
1. **Update requirements.md** if feature changes business goals
2. **Create ADR** if making architectural decision
3. **Update architecture/overview.md** if changing system design
4. **Update technical guides** (API, CLI, database) with new functionality
5. **Add examples** showing how to use the new feature

#### When Making Breaking Changes
1. **Create ADR** documenting the change and rationale
2. **Update all affected docs** (architecture, technical guides)
3. **Add migration guide** if users need to take action
4. **Archive old versions** to archive/ directory

#### When Deprecating Features
1. **Update docs** with deprecation notices
2. **Document migration path** to replacement
3. **Set timeline** for removal
4. **Keep docs** until feature is fully removed

---

## 🚀 Performance Tips

### Backend
- **Use async where beneficial** (database I/O, API calls)
- **Add indexes** to frequently queried database columns
- **Cache expensive queries** if data doesn't change often
- **Paginate large result sets**

### Frontend
- **Lazy load components** that aren't immediately visible
- **Memoize expensive calculations** with useMemo
- **Debounce API calls** triggered by user input
- **Use React.memo** for components that rarely change

```jsx
// ✅ GOOD - Debounced search
import { useState, useEffect } from 'react';
import { debounce } from 'lodash';

function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const debouncedSearch = debounce(() => {
      if (query.length >= 3) {
        onSearch(query);
      }
    }, 500); // Wait 500ms after user stops typing

    debouncedSearch();
    return () => debouncedSearch.cancel();
  }, [query, onSearch]);

  return (
    <input
      type="text"
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="Search..."
    />
  );
}
```

---

## 📦 Dependencies & Package Management

### Python (Backend)
```bash
# Install dependencies
pip install fastapi uvicorn python-dotenv sqlite3

# Keep requirements.txt updated
pip freeze > requirements.txt

# Use virtual environment
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate on Windows
```

### TypeScript (Frontend)
```bash
# Create React app with Vite
npm create vite@latest frontend -- --template react

# Install dependencies
npm install recharts tailwindcss axios

# Keep package.json clean
npm install --save <package>  # Production dependency
npm install --save-dev <package>  # Development dependency
```

---

## 🐛 Debugging Tips

### Backend Debugging
- Use **FastAPI's /docs** endpoint to test APIs
- Add **logging** to track request flow
- Use **print statements** liberally during development
- Check **database with SQLite browser** to verify data

### Frontend Debugging
- Use **React DevTools** browser extension
- Check **browser console** for errors
- Use **Network tab** to inspect API calls
- Add **console.log** to track state changes

---

## ✅ Git Best Practices

### Commit Messages
```bash
# ✅ GOOD - Clear, descriptive
git commit -m "Add temperature chart component with Recharts"
git commit -m "Fix: Handle empty database in API endpoint"
git commit -m "Update: Improve error messages in weather service"

# ❌ BAD - Vague, unhelpful
git commit -m "updates"
git commit -m "fix bug"
git commit -m "changes"
```

### Branching Strategy
Use descriptive branch names with prefixes:

```bash
# ✅ GOOD - Clear prefix and description
git checkout -b feature/cli-interface
git checkout -b feature/env-file-support
git checkout -b bugfix/emoji-encoding-windows
git checkout -b bugfix/api-rate-limit-handling

# ❌ BAD - No prefix, unclear
git checkout -b cli
git checkout -b env-support
git checkout -b fix
```

**Branch Prefixes:**
- **feature/** - New features or enhancements
- **bugfix/** - Bug fixes
- **refactor/** - Code refactoring without changing functionality
- **docs/** - Documentation updates only
- **test/** - Adding or updating tests

**Branch Names:**
- Use lowercase with hyphens
- Be descriptive but concise
- Include what, not how (e.g., `feature/csv-export` not `feature/add-csv-library`)

---

## 🎯 Development Workflow

### Phase 1: CLI & Data Collection (Completed ✅)
1. ✅ Create project structure and configuration
2. ✅ Implement CLI interface with Click framework
3. ✅ Build API client for Ambient Weather API
4. ✅ Build database operations with context managers
5. ✅ Implement fetch command for latest data
6. ✅ Implement backfill command for historical data
7. ✅ Add CSV export functionality
8. ✅ Set up .env file support with python-dotenv
9. ✅ Create package with setup.py for easy installation

### Phase 2: Frontend Prototype
1. ✅ Set up React + Vite project
2. ✅ Create basic layout and navigation
3. ✅ Build API service layer
4. ✅ Create weather data components
5. ✅ Add basic charts with Recharts
6. ✅ Style with Tailwind CSS

### Phase 3: Polish & Features
1. Add more chart types
2. Implement date range filtering
3. Add export functionality (CSV, PDF)
4. Improve error handling and loading states
5. Add dark mode support
6. Make responsive for mobile

### Phase 4: Automation & Deployment (Future)
1. Set up automated data collection
2. Add authentication (if needed)
3. Deploy to cloud (Render, Vercel, etc.)
4. Set up CI/CD pipeline

---

## 💡 Key Reminders for Claude Code

When building features:
1. **Ask clarifying questions** if requirements are unclear
2. **Show code diffs** for review before applying
3. **Explain your approach** before implementing
4. **Test immediately** after creating code
5. **Follow these guidelines** unless user requests otherwise
6. **Prioritize working code** over perfect code initially
7. **Iterate and improve** based on feedback

---

## 📚 Learning Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Recharts**: https://recharts.org/
- **SQLite Tutorial**: https://www.sqlitetutorial.net/

---

**Last Updated:** January 2, 2026
**Project Status:** Phase 2 Complete - FastAPI backend, React+TypeScript frontend, DuckDB migration, Docker deployment
