# Claude Code Best Practices & Guidelines

**Project:** Weather Dashboard Application  
**Stack:** FastAPI + React + SQLite  
**Developer Level:** Learning modern app development  
**Goals:** Fast prototype → Iterate for polish → Learn best practices

---

## 🎯 Core Principles

1. **Write clean, readable code** - Prioritize clarity over cleverness
2. **Comment complex logic** - Explain WHY, not just WHAT
3. **Follow language conventions** - PEP 8 for Python, ESLint standards for JavaScript
4. **Test as you build** - Verify functionality immediately
5. **Keep it simple first** - Optimize later if needed

---

## 📁 Project Structure

### Backend (FastAPI)
```
Weather-App/
├── backend/
│   ├── main.py              # FastAPI app, routes
│   ├── database.py          # Database connection, queries
│   ├── models.py            # Pydantic models for validation
│   ├── config.py            # Configuration, environment variables
│   └── requirements.txt     # Python dependencies
├── ambient_weather.db       # SQLite database (existing)
└── .env                     # Environment variables (existing)
```

### Frontend (React + Vite)
```
Weather-App/
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main application component
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API calls
│   │   └── utils/           # Helper functions
│   ├── public/              # Static assets
│   ├── package.json         # npm dependencies
│   └── vite.config.js       # Vite configuration
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

## ⚛️ React/JavaScript Best Practices

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

```javascript
// ✅ GOOD - Centralized, error handling, clear
// src/services/api.js
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

## 📝 Documentation

### Code Comments
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

### JavaScript (Frontend)
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

### Branching
- **main** - working production code
- **dev** - development branch
- **feature/** - new features
- **bugfix/** - bug fixes

---

## 🎯 Development Workflow

### Phase 1: Backend Setup (Current)
1. ✅ Create FastAPI application structure
2. ✅ Build database query functions
3. ✅ Create API endpoints for weather data
4. ✅ Test endpoints with FastAPI /docs
5. ✅ Add CORS for frontend access

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

**Last Updated:** January 1, 2026  
**Project Status:** Phase 1 (Backend Setup)
