# OpenAPI TypeScript Code Generation

This project uses **openapi-typescript-codegen** to automatically generate type-safe TypeScript clients from the FastAPI backend's OpenAPI schema.

## What is This?

The backend (FastAPI) automatically generates an OpenAPI 3.0 schema at `http://localhost:8000/openapi.json`. This schema describes all API endpoints, request parameters, and response types.

We use `openapi-typescript-codegen` to convert that schema into:
- **TypeScript types** (`src/api/models/*.ts`) - Exact types matching backend Pydantic models
- **API service classes** (`src/api/services/*.ts`) - Type-safe functions to call each endpoint
- **Core utilities** (`src/api/core/*.ts`) - HTTP client, error handling, etc.

## Benefits

✅ **End-to-end type safety** - TypeScript knows exact shape of API responses
✅ **Zero manual typing** - Types automatically sync with backend changes
✅ **Compile-time errors** - Breaking API changes caught before runtime
✅ **IDE autocomplete** - Full IntelliSense for all API calls
✅ **Contract-driven development** - Backend changes force frontend updates

## Usage

### Using the Generated API Client

```typescript
import { DefaultService, type WeatherData } from './api';
import { initializeApiClient } from './lib/api-config';

// Initialize once (done in App.tsx)
initializeApiClient();

// Use the generated service
const weather: WeatherData = await DefaultService.getLatestWeatherWeatherLatestGet();

// TypeScript knows all fields!
console.log(weather.tempf); // ✅ Autocomplete works
console.log(weather.temp);  // ❌ Compile error - field doesn't exist
```

### Regenerating Types (When Backend Changes)

Run this whenever you update the FastAPI backend:

```bash
npm run codegen
```

**What this does:**
1. Downloads OpenAPI schema from `http://localhost:8000/openapi.json`
2. Generates TypeScript types in `src/api/`
3. Overwrites old generated files
4. Cleans up temporary files

**Important:** Make sure the FastAPI backend is running before running codegen!

```bash
# Terminal 1: Start backend
cd ..
source venv/bin/activate
uvicorn weather_app.api.main:app --reload

# Terminal 2: Regenerate types
cd web
npm run codegen
```

## When to Regenerate

Regenerate the client whenever you:
- ✅ Add new API endpoints
- ✅ Modify API response models (Pydantic)
- ✅ Change request parameters
- ✅ Update endpoint paths or HTTP methods

You do **NOT** need to regenerate for:
- ❌ Backend logic changes (if API contract unchanged)
- ❌ Database changes (if API responses unchanged)
- ❌ Frontend-only changes

## Generated File Structure

```
src/api/
├── core/                   # HTTP client utilities
│   ├── OpenAPI.ts         # Configuration (BASE_URL, etc.)
│   ├── request.ts         # Fetch wrapper
│   └── ...
├── models/                # TypeScript types
│   ├── WeatherData.ts     # Maps to backend WeatherData Pydantic model
│   ├── DatabaseStats.ts   # Maps to backend DatabaseStats model
│   └── ...
├── services/              # API service classes
│   └── DefaultService.ts  # All API endpoints as static methods
└── index.ts              # Exports everything
```

**⚠️ DO NOT EDIT GENERATED FILES**

Files in `src/api/` are auto-generated and will be overwritten on next codegen run.

If you need custom API logic, create wrapper functions in `src/lib/` or `src/services/`.

## Configuration

### API Base URL

Set via environment variable in `.env`:

```bash
VITE_API_URL=http://localhost:8000
```

This is configured in `src/lib/api-config.ts`.

### Codegen Options

Codegen settings are in `package.json`:

```json
{
  "scripts": {
    "codegen": "curl -s http://localhost:8000/openapi.json -o openapi.json && openapi-typescript-codegen --input ./openapi.json --output ./src/api --client fetch && rm openapi.json"
  }
}
```

**Options used:**
- `--input ./openapi.json` - Path to OpenAPI schema
- `--output ./src/api` - Output directory
- `--client fetch` - Use native Fetch API (not axios)

## Troubleshooting

### "Unable to resolve $ref pointer"

**Problem:** Backend isn't running or schema is invalid

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/openapi.json

# If not running, start it:
cd .. && uvicorn weather_app.api.main:app --reload
```

### "Module not found" errors

**Problem:** Types not generated or wrong path

**Solution:**
```bash
# Regenerate types
npm run codegen

# Check files exist
ls -la src/api/
```

### TypeScript errors after backend changes

**Problem:** API contract changed but types not regenerated

**Solution:**
```bash
# Regenerate types to match new backend
npm run codegen

# Fix any TypeScript errors in your components
# (These errors are GOOD - they caught a breaking change!)
```

## CI/CD Integration (Future)

Add to GitHub Actions workflow:

```yaml
# .github/workflows/frontend.yml
- name: Start backend for codegen
  run: |
    uvicorn weather_app.api.main:app &
    sleep 5  # Wait for server to start

- name: Generate API client
  run: |
    cd web
    npm run codegen

- name: Build frontend
  run: |
    cd web
    npm run build
```

## References

- [openapi-typescript-codegen](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [FastAPI OpenAPI docs](https://fastapi.tiangolo.com/advanced/extending-openapi/)
- [OpenAPI 3.0 Specification](https://swagger.io/specification/)

---

**Last Updated:** 2026-01-02
