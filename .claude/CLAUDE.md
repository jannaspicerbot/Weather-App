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

## 🚨 CRITICAL: Git Workflow & Best Practices

### Always Use Feature Branches - NO EXCEPTIONS

**NEVER work directly on `main`. ALWAYS create a feature branch first.**

```bash
# ✅ CORRECT WORKFLOW
git branch --show-current           # Check current branch
git checkout -b feature/my-feature  # Create feature branch
# ... make changes ...
git add .
git commit -m "Descriptive message"
git push -u origin feature/my-feature
# Create PR on GitHub for review

# ❌ WRONG - Never do this!
git branch --show-current  # Output: main
# ... make changes on main ... ← STOP! Create branch first!
```

**Before making ANY code changes:**
1. **Check current branch**: `git branch --show-current`
2. **If on main**: IMMEDIATELY create a feature branch: `git checkout -b feature/descriptive-name`
3. **Make all changes**: Only after you're on a feature branch
4. **Commit and push**: To the feature branch
5. **Create PR**: For review before merging to main

**No exceptions. Even for "small" changes, documentation updates, or typo fixes.**

---

### Branch Naming Conventions

Use descriptive branch names with prefixes:

```bash
# ✅ GOOD - Clear prefix and description
git checkout -b feature/apscheduler-integration
git checkout -b feature/env-file-support
git checkout -b bugfix/emoji-encoding-windows
git checkout -b bugfix/api-rate-limit-handling
git checkout -b refactor/database-layer
git checkout -b docs/update-api-reference
git checkout -b chore/rename-claude-guidelines

# ❌ BAD - No prefix, unclear
git checkout -b cli
git checkout -b env-support
git checkout -b fix
```

**Branch Prefixes:**
- `feature/` - New features or enhancements
- `bugfix/` - Bug fixes
- `refactor/` - Code refactoring without changing functionality
- `docs/` - Documentation updates only
- `chore/` - Maintenance tasks (dependencies, config, cleanup)
- `test/` - Adding or updating tests

**Branch Names:**
- Use lowercase with hyphens
- Be descriptive but concise
- Include what, not how (e.g., `feature/csv-export` not `feature/add-csv-library`)

---

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

**Commit Message Guidelines:**
- Start with a verb (Add, Fix, Update, Remove, Refactor)
- Be specific about what changed
- Keep under 72 characters for the first line
- Add body for complex changes (optional)

---

### Why This Matters

- **Protects main branch** from incomplete or broken code
- **Enables code review** via pull requests
- **Allows easy rollback** if something breaks
- **Follows industry best practices** for professional development
- **Maintains clean history** for future developers

---

## 📁 Project Structure

High-level organization:

```
Weather-App/
├── weather_app/          # Python backend (FastAPI + CLI)
├── web/                  # React + TypeScript frontend
├── docs/                 # Documentation (see docs/README.md)
├── tests/                # Test scripts
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── ambient_weather.duckdb  # DuckDB database
```

**Detailed structure:** See [docs/architecture/overview.md](../docs/architecture/overview.md) for complete file-by-file breakdown.

---

## 🐍 Python/FastAPI Best Practices

### Code Formatting & Linting

This project uses automated tools to ensure code quality and consistency:

**Tools:**
- **Black** (line length: 88) - Opinionated code formatter
- **Ruff** - Fast linter (replaces flake8, isort)
- **isort** - Import sorting (Black-compatible profile)
- **mypy** - Static type checking

**Key rules from [pyproject.toml](../pyproject.toml):**
- Line length: 88 characters (Black default)
- Python versions: 3.10, 3.11, 3.12
- Import sorting: Black-compatible profile with trailing commas
- Type hints: Encouraged but not strictly required for all functions

**Run before committing:**
```bash
# Format code with Black
black weather_app/

# Check and auto-fix linting issues
ruff check --fix weather_app/

# Type check with mypy
mypy weather_app/

# Or run all checks together
black weather_app/ && ruff check --fix weather_app/ && mypy weather_app/
```

**Important:** CI will run these checks automatically. Fix any issues before pushing.

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

## 🎨 Styling with CSS Custom Properties (Design Tokens)

This project uses a **semantic design token system** with CSS custom properties instead of utility CSS frameworks. See [docs/design/design-tokens.md](../docs/design/design-tokens.md) for the full specification.

### Best Practices
- Use **semantic CSS classes** (e.g., `.weather-card`, `.stat-value`)
- Reference **design tokens** via CSS custom properties (`var(--color-water)`)
- Keep styles in **component-specific CSS files** or the global `index.css`
- Use **CSS Grid and Flexbox** for layouts
- Support **dark mode** via `@media (prefers-color-scheme: dark)`

```jsx
// ✅ GOOD - Semantic classes with design tokens
<div className="dashboard-container">
  <h1 className="dashboard-title">
    Weather Dashboard
  </h1>

  <div className="card-grid">
    {/* Cards here */}
  </div>
</div>

// ✅ GOOD - Using design tokens in CSS
// In index.css or component CSS:
.dashboard-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-4);
  background: var(--color-bg-primary);
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-6);
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-4);
}

// ❌ BAD - Inline styles with hardcoded values
<div style={{width: '800px', background: '#fff', padding: '20px'}}>
  <h1 style={{fontSize: '32px', fontWeight: 'bold'}}>Weather</h1>
</div>
```

### Design Token Reference
- **Colors:** `--color-water`, `--color-growth`, `--color-text-primary`, `--color-bg-secondary`
- **Spacing:** `--spacing-1` (4px) through `--spacing-12` (48px)
- **Charts:** `--chart-line-water`, `--chart-grid`, `--chart-axis`

See `web/src/index.css` for the complete token definitions.

---

## 🧪 Testing & Validation

### Testing Framework
This project uses **pytest** for automated testing with the following structure:

### Test Organization
```bash
tests/
├── test_*.py          # Automated test files
├── experiment_*.py    # Diagnostic/research scripts
└── conftest.py        # Shared fixtures and configuration

docs/testing/          # Testing documentation
└── refactoring-test-plan.md  # Feature-specific test plans
```

### Test Markers (pytest.ini)
Use pytest markers to categorize tests:
- `@pytest.mark.unit` - Fast unit tests (no external dependencies)
- `@pytest.mark.integration` - Integration tests (database, API)
- `@pytest.mark.requires_api_key` - Tests needing Ambient Weather API + App keys

### Running Tests
```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run without API key tests
pytest -m "not requires_api_key"

# Run specific test file
pytest tests/test_database.py

# Verbose output with detailed assertions
pytest -v

# Show print statements during test run
pytest -s
```

### Writing Tests

**Unit Tests:**
```python
import pytest
from weather_app.database import WeatherRepository

@pytest.mark.unit
def test_temperature_conversion():
    """Test Fahrenheit to Celsius conversion."""
    result = convert_temp(32.0)
    assert result == 0.0

@pytest.mark.unit
def test_validate_date_format():
    """Test date string validation."""
    assert validate_date("2024-01-01") is True
    assert validate_date("01/01/2024") is False
```

**Integration Tests:**
```python
@pytest.mark.integration
def test_database_insert(test_db):
    """Test inserting weather data into database."""
    repo = WeatherRepository(test_db)
    data = {"tempf": 72.5, "humidity": 45, "date": "2024-01-01T12:00:00"}

    result = repo.insert(data)
    assert result.success is True
    assert result.inserted_count == 1
```

**API Tests (requires both API key and App key):**
```python
@pytest.mark.requires_api_key
@pytest.mark.integration
def test_fetch_weather_data():
    """Test fetching from Ambient Weather API.

    Requires environment variables:
    - AMBIENT_API_KEY
    - AMBIENT_APP_KEY
    """
    api = AmbientWeatherAPI(api_key, app_key)
    data = api.get_device_data(mac_address, limit=1)

    assert len(data) == 1
    assert "tempf" in data[0]
    assert "humidity" in data[0]
```

### Test Fixtures (conftest.py)
Create `tests/conftest.py` for shared fixtures:

```python
import pytest
import tempfile
from pathlib import Path
from weather_app.database import WeatherDatabase

@pytest.fixture
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".duckdb", delete=False) as f:
        db_path = f.name

    db = WeatherDatabase(db_path)
    db.initialize()
    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)

@pytest.fixture
def sample_weather_data():
    """Provide sample weather data for tests."""
    return {
        "tempf": 72.5,
        "humidity": 45,
        "windspeedmph": 5.2,
        "baromrelin": 30.12,
        "date": "2024-01-01T12:00:00"
    }

@pytest.fixture
def api_credentials():
    """Load API credentials from environment.

    Both API key and App key are required for Ambient Weather API.
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    return {
        "api_key": os.getenv("AMBIENT_API_KEY"),
        "app_key": os.getenv("AMBIENT_APP_KEY")
    }
```

### What to Test

**Backend:**
- ✅ Database operations (insert, query, update)
- ✅ API client methods (with mock responses)
- ✅ Data validation (Pydantic models)
- ✅ Error handling (invalid input, missing data)
- ✅ Date range logic
- ✅ Statistics calculations
- ✅ CLI commands (using Click's testing utilities)

**Frontend:**
- ✅ Component rendering (React Testing Library)
- ✅ API integration (mock responses)
- ✅ User interactions (button clicks, form inputs)
- ✅ Chart data formatting
- ✅ Error state handling

### Manual Testing

**Backend - Test endpoints with Swagger UI:**
```bash
# Start the FastAPI server
uvicorn weather_app.web.app:create_app --factory --reload

# Visit: http://localhost:8000/docs
# Try each endpoint in the interactive Swagger UI
```

**Frontend - Test in browser:**
```bash
# Start the Vite dev server
cd web && npm run dev

# Visit: http://localhost:5174
# Check browser console for errors
# Test with real API and with mock data
```

### Test-Driven Development (TDD)
When adding new features:
1. **Write test first** - Define expected behavior
2. **Run test (should fail)** - Confirms test works
3. **Write minimal code** - Make test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - For each new requirement

### CI/CD Testing
Tests run automatically on every push via GitHub Actions.
See [docs/technical/ci-cd.md](../docs/technical/ci-cd.md) for CI configuration details.

### Feature-Specific Test Plans
For major features or refactoring, create detailed test plans in `docs/testing/`:
- Example: [docs/testing/refactoring-test-plan.md](../docs/testing/refactoring-test-plan.md)

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

## 📝 Documentation & Contributing

For complete documentation standards, writing guidelines, ADR templates, and contribution workflows, see:

**[docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)**

Key documentation locations:
- **Product docs**: `docs/product/` - Requirements, goals, user personas
- **Architecture docs**: `docs/architecture/` - System design, ADRs, decisions
- **Technical docs**: `docs/technical/` - API reference, CLI guide, deployment
- **Navigation**: `docs/README.md` - Documentation index

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

# Install dependencies (see package.json for current list)
npm install victory axios @react-aria/button

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

## 💡 Key Reminders for Claude Code

When building features:

1. **ALWAYS create a feature branch first** - See [Git Workflow](#-critical-git-workflow--best-practices) ⚠️
2. **Ask clarifying questions** if requirements are unclear
3. **Explain your approach** before implementing
4. **Test immediately** after creating code
5. **Follow these guidelines** unless user requests otherwise
6. **Prioritize working code** over perfect code initially
7. **Iterate and improve** based on feedback

**Project Roadmap**: See `docs/product/requirements.md` for development phases and timeline.

**External Resources**: See `docs/README.md` for links to framework documentation and tutorials.

---

**Last Updated:** January 3, 2026
**Project Status:** Phase 3 In Progress - APScheduler integration complete
