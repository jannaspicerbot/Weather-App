# Testing Standards & Strategies

**Purpose:** Comprehensive testing guidelines for backend and frontend
**Reference:** Load this doc when writing tests
**Last Updated:** January 2026

---

## When to Use This Document

**Load before:**
- Writing unit tests
- Writing integration tests
- Setting up test fixtures
- Debugging test failures
- Adding test coverage

**Referenced from:** CLAUDE.md → "Working on tests"

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Backend Testing (pytest)](#backend-testing-pytest)
3. [Frontend Testing (Vitest)](#frontend-testing-vitest)
4. [Integration Testing](#integration-testing)
5. [Test Fixtures](#test-fixtures)
6. [Mocking Strategies](#mocking-strategies)
7. [Coverage Requirements](#coverage-requirements)

---

## Testing Philosophy

### Testing Pyramid

```
      /\
     /E2E\         (Few) - End-to-end tests
    /------\
   /Integration\   (Some) - API + Database tests
  /------------\
 /   Unit Tests  \ (Many) - Functions, components
/----------------\
```

**Priorities:**
1. **Unit tests** - Fast, isolated, many
2. **Integration tests** - API + database, moderate
3. **E2E tests** - Full system, few (not implemented yet)

### Test-Driven Development (TDD)

For complex features:
1. Write test first (it fails)
2. Write minimum code to pass
3. Refactor while keeping tests green
4. Repeat

For simple features:
- Write tests after implementation
- Verify behavior with edge cases

---

## Backend Testing (pytest)

### Test Structure

```python
# tests/test_weather_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

def test_get_latest_weather_success(client, test_db_with_data):
    """Test successful retrieval of latest weather data."""
    # Arrange - Setup done in fixtures

    # Act
    response = client.get("/api/weather/latest")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "temperature_f" in data
    assert data["temperature_f"] > -100  # Reasonable range

def test_get_latest_weather_no_data(client, empty_db):
    """Test 404 when no data exists."""
    response = client.get("/api/weather/latest")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_get_latest_weather_database_error(client, broken_db):
    """Test 500 error handling for database failures."""
    response = client.get("/api/weather/latest")
    assert response.status_code == 500
```

### Parametrized Tests

```python
@pytest.mark.parametrize("start,end,expected_count", [
    ("2026-01-01", "2026-01-31", 744),  # 31 days * 24 hours
    ("2026-01-13", "2026-01-13", 24),   # Single day
    ("2026-01-01", "2026-01-02", 48),   # Two days
])
def test_weather_range_counts(client, test_db, start, end, expected_count):
    """Test weather range query returns correct number of records."""
    response = client.get(
        "/api/weather/range",
        params={"start_date": start, "end_date": end}
    )
    assert response.status_code == 200
    assert len(response.json()) == expected_count

@pytest.mark.parametrize("invalid_input,expected_error", [
    ({"start_date": "invalid"}, "validation"),
    ({"start_date": "2026-01-31", "end_date": "2026-01-01"}, "end_date must be after"),
    ({"start_date": "2030-01-01", "end_date": "2030-01-02"}, "future"),
])
def test_weather_range_validation(client, invalid_input, expected_error):
    """Test input validation."""
    response = client.get("/api/weather/range", params=invalid_input)
    assert response.status_code in [400, 422]
    assert expected_error.lower() in str(response.json()).lower()
```

### Database Tests

```python
from weather_app.database import WeatherDB
from datetime import datetime

def test_insert_weather_reading(test_db):
    """Test inserting weather reading."""
    db = WeatherDB(test_db)

    reading = {
        "timestamp": datetime.now(),
        "station_id": "TEST001",
        "temperature_f": 72.5,
        "humidity": 45
    }

    # Insert
    result_id = db.insert_reading(reading)
    assert result_id > 0

    # Verify
    retrieved = db.get_by_id(result_id)
    assert retrieved["temperature_f"] == 72.5
    assert retrieved["station_id"] == "TEST001"

def test_query_date_range(test_db_with_data):
    """Test date range query."""
    db = WeatherDB(test_db_with_data)

    start = datetime(2026, 1, 1)
    end = datetime(2026, 1, 31)

    results = db.query_range(start, end)

    assert len(results) > 0
    assert all(start <= r["timestamp"] <= end for r in results)
    assert results[0]["timestamp"] >= results[-1]["timestamp"]  # Descending order

def test_batch_insert(test_db):
    """Test batch insert performance."""
    db = WeatherDB(test_db)

    # Create 1000 readings
    readings = [
        {
            "timestamp": datetime.now() + timedelta(minutes=i),
            "station_id": "TEST001",
            "temperature_f": 70.0 + (i % 10),
            "humidity": 40 + (i % 20)
        }
        for i in range(1000)
    ]

    # Insert in batch
    count = db.batch_insert(readings)
    assert count == 1000

    # Verify count
    total = db.count()
    assert total == 1000
```

### API Client Tests

```python
import responses
from weather_app.services.ambient_client import AmbientWeatherClient

@responses.activate
def test_fetch_devices_success():
    """Test successful device fetch."""
    # Mock API response
    responses.add(
        responses.GET,
        "https://api.ambientweather.net/v1/devices",
        json=[
            {
                "macAddress": "00:11:22:33:44:55",
                "lastData": {
                    "tempf": 72.5,
                    "humidity": 45
                }
            }
        ],
        status=200
    )

    client = AmbientWeatherClient(api_key="test", app_key="test")
    devices = client.get_devices()

    assert len(devices) == 1
    assert devices[0]["macAddress"] == "00:11:22:33:44:55"

@responses.activate
def test_fetch_devices_rate_limit():
    """Test rate limit handling."""
    responses.add(
        responses.GET,
        "https://api.ambientweather.net/v1/devices",
        status=429,
        headers={"Retry-After": "60"}
    )

    client = AmbientWeatherClient(api_key="test", app_key="test")

    with pytest.raises(RateLimitError) as exc_info:
        client.get_devices()

    assert exc_info.value.retry_after == 60
```

---

## Frontend Testing (Vitest)

### Component Tests

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { WeatherChart } from './WeatherChart';

describe('WeatherChart', () => {
  const mockData = [
    { timestamp: '2026-01-13T12:00:00Z', temperature_f: 72 },
    { timestamp: '2026-01-13T13:00:00Z', temperature_f: 74 }
  ];

  it('renders chart with data', () => {
    render(<WeatherChart data={mockData} />);

    // Chart should have role="img" with aria-label
    const chart = screen.getByRole('img', { name: /temperature chart/i });
    expect(chart).toBeInTheDocument();
  });

  it('shows loading state', () => {
    render(<WeatherChart data={[]} isLoading={true} />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('shows error state', () => {
    const error = 'Failed to fetch data';
    render(<WeatherChart data={[]} error={error} />);

    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(error);
  });

  it('handles empty data gracefully', () => {
    render(<WeatherChart data={[]} />);

    expect(screen.getByText(/no data available/i)).toBeInTheDocument();
  });

  it('calls onRangeChange when date picker updates', async () => {
    const handleRangeChange = vi.fn();

    render(
      <WeatherChart
        data={mockData}
        onRangeChange={handleRangeChange}
      />
    );

    // Find and click date range button
    const rangeButton = screen.getByRole('button', { name: /change date range/i });
    fireEvent.click(rangeButton);

    // Wait for callback
    await waitFor(() => {
      expect(handleRangeChange).toHaveBeenCalledTimes(1);
    });
  });
});
```

### Hook Tests

```typescript
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { useWeatherData } from './useWeatherData';

describe('useWeatherData', () => {
  beforeEach(() => {
    // Setup fetch mock
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches weather data successfully', async () => {
    const mockData = [
      { timestamp: '2026-01-13T12:00:00Z', temperature_f: 72 }
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockData
    });

    const { result } = renderHook(() =>
      useWeatherData({ stationId: 'STATION001' })
    );

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBe(null);

    // Wait for data
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBe(null);
  });

  it('handles fetch errors', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() =>
      useWeatherData({ stationId: 'STATION001' })
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeTruthy();
    expect(result.current.error.message).toBe('Network error');
    expect(result.current.data).toBe(null);
  });

  it('refetches when dependencies change', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => []
    });

    const { result, rerender } = renderHook(
      ({ stationId }) => useWeatherData({ stationId }),
      { initialProps: { stationId: 'STATION001' } }
    );

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(global.fetch).toHaveBeenCalledTimes(1);

    // Change station ID
    rerender({ stationId: 'STATION002' });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
```

### User Interaction Tests

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('WeatherForm', () => {
  it('submits form with user input', async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(<WeatherForm onSubmit={handleSubmit} />);

    // Fill in form
    const stationInput = screen.getByLabelText(/station id/i);
    await user.type(stationInput, 'STATION001');

    const dateInput = screen.getByLabelText(/date/i);
    await user.type(dateInput, '2026-01-13');

    // Submit
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    // Verify callback
    await waitFor(() => {
      expect(handleSubmit).toHaveBeenCalledWith({
        stationId: 'STATION001',
        date: '2026-01-13'
      });
    });
  });

  it('shows validation errors', async () => {
    const user = userEvent.setup();
    render(<WeatherForm onSubmit={vi.fn()} />);

    // Submit without filling form
    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    // Check for error messages
    expect(screen.getByText(/station id is required/i)).toBeInTheDocument();
  });
});
```

---

## Integration Testing

### API + Database Integration

```python
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from weather_app.api.main import app
from weather_app.database import WeatherDB

@pytest.fixture
def integration_client(tmp_path):
    """Client with real database."""
    db_path = tmp_path / "test.db"

    # Initialize database
    db = WeatherDB(str(db_path))
    db.initialize()

    # Seed data
    db.insert_reading({
        "timestamp": datetime.now(),
        "station_id": "INT001",
        "temperature_f": 72.5,
        "humidity": 45
    })

    # Override app database
    app.state.db = db

    client = TestClient(app)
    yield client

    # Cleanup
    db_path.unlink(missing_ok=True)

def test_full_api_flow(integration_client):
    """Test complete API workflow."""
    client = integration_client

    # 1. Get latest weather
    response = client.get("/api/weather/latest")
    assert response.status_code == 200
    latest = response.json()
    assert latest["station_id"] == "INT001"

    # 2. Query by date range
    response = client.get(
        "/api/weather/range",
        params={
            "start_date": "2026-01-01",
            "end_date": "2026-12-31"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

    # 3. Get statistics
    response = client.get("/api/weather/stats/daily")
    assert response.status_code == 200
```

---

## Test Fixtures

### Conftest.py (pytest)

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import duckdb

from weather_app.api.main import app
from weather_app.database import WeatherDB

@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)

@pytest.fixture
def test_db(tmp_path):
    """Temporary test database."""
    db_path = tmp_path / "test.db"
    conn = duckdb.connect(str(db_path))

    # Create schema
    conn.execute("""
        CREATE TABLE weather_data (
            id INTEGER PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            station_id VARCHAR NOT NULL,
            temperature_f DOUBLE,
            humidity INTEGER
        )
    """)

    yield str(db_path)

    conn.close()
    db_path.unlink(missing_ok=True)

@pytest.fixture
def test_db_with_data(test_db):
    """Database with sample data."""
    conn = duckdb.connect(test_db)

    # Insert test data
    base_time = datetime(2026, 1, 13, 12, 0, 0)
    for i in range(24):  # 24 hours of data
        conn.execute("""
            INSERT INTO weather_data VALUES (?, ?, ?, ?, ?)
        """, [
            i + 1,
            base_time + timedelta(hours=i),
            "STATION001",
            70.0 + (i % 10),  # Temperature varies
            40 + (i % 20)     # Humidity varies
        ])

    conn.close()
    return test_db

@pytest.fixture
def empty_db(test_db):
    """Empty database for testing edge cases."""
    return test_db

@pytest.fixture
def sample_weather_reading():
    """Sample weather reading dict."""
    return {
        "timestamp": datetime.now(),
        "station_id": "TEST001",
        "temperature_f": 72.5,
        "humidity": 45,
        "wind_speed_mph": 5.2,
        "pressure_inhg": 30.12
    }
```

### Setup Files (Vitest)

```typescript
// vitest.setup.ts
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});
```

---

## Mocking Strategies

### API Mocking

```typescript
import { vi } from 'vitest';

// Mock fetch globally
global.fetch = vi.fn();

beforeEach(() => {
  global.fetch.mockClear();
});

// Mock successful response
global.fetch.mockResolvedValueOnce({
  ok: true,
  status: 200,
  json: async () => ({ data: 'test' })
});

// Mock error response
global.fetch.mockResolvedValueOnce({
  ok: false,
  status: 404,
  json: async () => ({ detail: 'Not found' })
});

// Mock network error
global.fetch.mockRejectedValueOnce(new Error('Network error'));
```

### Time Mocking

```python
from unittest.mock import patch
from datetime import datetime

@patch('weather_app.utils.get_current_time')
def test_with_mocked_time(mock_time):
    """Test with fixed time."""
    mock_time.return_value = datetime(2026, 1, 13, 12, 0, 0)

    # Your test here
    result = function_that_uses_current_time()
    assert result.timestamp == mock_time.return_value
```

---

## Coverage Requirements

### Minimum Coverage

- **Unit tests:** 80% code coverage
- **Integration tests:** All critical paths
- **E2E tests:** Happy path + major error scenarios

### Running Coverage

```bash
# Python
pytest --cov=weather_app --cov-report=html tests/

# TypeScript
npm run test:coverage
```

### Excluding from Coverage

```python
def debug_function():  # pragma: no cover
    """Development only - excluded from coverage."""
    print("Debug info")
```

---

## CI/CD Integration

Tests run automatically on every push:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd web && npm ci
      - run: cd web && npm test -- --run
```

---

## Checklist for New Tests

- [ ] Test follows AAA pattern (Arrange, Act, Assert)
- [ ] Test name clearly describes what is tested
- [ ] Uses appropriate fixtures
- [ ] Mocks external dependencies
- [ ] Tests both success and failure cases
- [ ] Tests edge cases (empty, null, invalid input)
- [ ] Runs in isolation (no dependencies on other tests)
- [ ] Runs quickly (< 1 second per test ideally)
- [ ] Cleanup performed in fixtures
- [ ] Assertions are specific (not just `assert result`)

---

**See also:**
- docs/standards/API-STANDARDS.md - API testing patterns
- docs/standards/REACT-STANDARDS.md - Component testing
- docs/examples/ - Real test examples from project

**Questions?** Refer to CLAUDE.md or ask before implementing.
