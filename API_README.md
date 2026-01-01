# Weather API Documentation

FastAPI backend for the Weather Application that provides REST API endpoints for querying weather data from the SQLite database.

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the API

Start the FastAPI server:

```bash
python main.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Endpoints

### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

**Example:**
```bash
curl http://localhost:8000/
```

### 2. Get Weather Data
```
GET /weather
```
Query weather data with optional filters and pagination.

**Query Parameters:**
- `limit` (optional): Maximum number of records (1-1000, default: 100)
- `offset` (optional): Number of records to skip (default: 0)
- `start_date` (optional): Filter by start date (YYYY-MM-DD format)
- `end_date` (optional): Filter by end date (YYYY-MM-DD format)
- `order` (optional): Sort order - 'asc' or 'desc' (default: desc)

**Examples:**
```bash
# Get last 100 records (default)
curl http://localhost:8000/weather

# Get last 50 records
curl http://localhost:8000/weather?limit=50

# Get records from a specific date range
curl "http://localhost:8000/weather?start_date=2024-12-01&end_date=2024-12-31"

# Get records with pagination
curl http://localhost:8000/weather?limit=100&offset=100

# Get oldest records first
curl http://localhost:8000/weather?order=asc&limit=10
```

### 3. Get Latest Weather Data
```
GET /weather/latest
```
Returns the most recent weather reading from the database.

**Example:**
```bash
curl http://localhost:8000/weather/latest
```

**Response:**
```json
{
  "id": 1234,
  "dateutc": 1704067200000,
  "date": "2024-12-31T12:00:00",
  "tempf": 72.5,
  "feelsLike": 71.2,
  "humidity": 65,
  "windspeedmph": 5.2,
  "dailyrainin": 0.0,
  ...
}
```

### 4. Get Database Statistics
```
GET /weather/stats
```
Returns statistics about the weather database.

**Example:**
```bash
curl http://localhost:8000/weather/stats
```

**Response:**
```json
{
  "total_records": 15234,
  "min_date": "2024-03-01T00:00:00",
  "max_date": "2024-12-31T23:59:59",
  "date_range_days": 305
}
```

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## CORS Configuration

CORS is enabled for all origins to allow the React frontend to connect.

**For production**, update the CORS settings in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid query parameters (e.g., bad date format)
- **404 Not Found**: No data found
- **500 Internal Server Error**: Database or server errors

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

## Database Schema

The API queries the `weather_data` table with the following structure:

- **Temperature**: `tempf`, `feelsLike`, `dewPoint`, `tempinf`
- **Humidity**: `humidity`, `humidityin`
- **Pressure**: `baromrelin`, `baromabsin`
- **Wind**: `windspeedmph`, `windgustmph`, `winddir`, `maxdailygust`
- **Rain**: `hourlyrainin`, `dailyrainin`, `weeklyrainin`, `monthlyrainin`, `totalrainin`
- **Solar**: `solarradiation`, `uv`
- **Battery**: `battout`, `battin`
- **Raw Data**: `raw_json` (complete API response)

## Example: Using with React Frontend

```javascript
// Fetch latest weather data
const response = await fetch('http://localhost:8000/weather/latest');
const latestWeather = await response.json();

// Fetch last 24 hours of data
const today = new Date();
const yesterday = new Date(today);
yesterday.setDate(yesterday.getDate() - 1);

const response = await fetch(
  `http://localhost:8000/weather?start_date=${yesterday.toISOString().split('T')[0]}&limit=288`
);
const weatherData = await response.json();
```

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

## Testing

Test the API endpoints using curl or any HTTP client:

```bash
# Test root endpoint
curl http://localhost:8000/

# Test latest weather
curl http://localhost:8000/weather/latest

# Test stats
curl http://localhost:8000/weather/stats
```
