# ADR-001: FastAPI Backend Framework

**Status:** ✅ Accepted (Phase 1)
**Date:** 2025-12-15
**Deciders:** Janna Spicer, Architecture Review

---

## Context

The Weather App needs a Python web framework to expose weather data via REST API. The API must support:
- Type-safe request/response validation
- Auto-generated API documentation
- Async I/O for efficient handling of concurrent requests
- Easy integration with Pydantic models
- OpenAPI 3.0 schema generation for TypeScript client codegen

---

## Decision

We will use **FastAPI** as the web framework for the backend API.

---

## Rationale

### Comparison with Alternatives

| Feature | FastAPI | Flask | Django REST |
|---------|---------|-------|-------------|
| **Type Safety** | ✅ Native (Pydantic) | ❌ Manual | ⚠️ DRF serializers |
| **OpenAPI Docs** | ✅ Auto-generated | ❌ Manual (flask-swagger) | ⚠️ Manual (drf-spectacular) |
| **Async Support** | ✅ Native (async/await) | ⚠️ Added in 2.0 | ❌ Limited |
| **Performance** | ✅ High (Starlette) | ⚠️ Medium | ❌ Lower (ORM overhead) |
| **Learning Curve** | ✅ Low (Flask-like) | ✅ Very low | ❌ High |
| **Boilerplate** | ✅ Minimal | ✅ Minimal | ❌ Heavy |

### Key Benefits

1. **Auto-generated OpenAPI Schema**
   ```python
   # FastAPI automatically generates OpenAPI 3.0 schema
   # Available at http://localhost:8000/docs (Swagger UI)
   # Available at http://localhost:8000/openapi.json (JSON schema)

   @app.get("/api/weather/latest", response_model=WeatherReading)
   async def get_latest():
       return db.get_latest()
   ```

2. **Type Safety with Pydantic**
   ```python
   class WeatherReading(BaseModel):
       timestamp: datetime
       temperature: float
       humidity: float | None

   # FastAPI validates request/response automatically
   # Invalid data returns 422 Unprocessable Entity
   ```

3. **TypeScript Code Generation**
   ```bash
   # OpenAPI schema enables TypeScript client generation
   npx openapi-typescript-codegen --input http://localhost:8000/openapi.json --output ./src/api

   # Frontend gets full type safety
   import { WeatherService } from './api';
   const data = await WeatherService.getWeatherLatest(); // TypeScript knows exact shape!
   ```

4. **Performance**
   - Built on Starlette (async framework)
   - Comparable to Node.js/Go for I/O-bound workloads
   - Async database queries don't block other requests

5. **Developer Experience**
   - Flask-like simplicity with modern Python type hints
   - Automatic interactive docs at `/docs`
   - Hot reload during development

### Alignment with Peer Review

From peer-review.md:

> "FastAPI: High-performance async framework with automatic OpenAPI schema"
> "OpenAPI → TypeScript codegen for end-to-end type safety"

---

## Consequences

### Positive

- ✅ End-to-end type safety (Python → OpenAPI → TypeScript)
- ✅ No manual API documentation needed
- ✅ Frontend can generate type-safe client from OpenAPI schema
- ✅ Fast enough for 1000s of concurrent dashboard users
- ✅ Easy to test (pytest + TestClient)

### Negative

- ⚠️ Newer than Flask/Django (less Stack Overflow answers)
- ⚠️ Async patterns require understanding of async/await
- ⚠️ Some third-party libraries may not support async

### Neutral

- FastAPI requires Python 3.7+ (we're using 3.11+, so no issue)
- Uvicorn required as ASGI server (simple: `uvicorn main:app`)

---

## Implementation

### Project Structure
```
weather_app/
├── api/
│   ├── main.py          # FastAPI app instance
│   ├── routes.py        # API endpoints
│   └── models.py        # Pydantic models
```

### Sample Code
```python
# weather_app/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Weather App API",
    version="1.0.0",
    description="Local-first weather data collection and visualization"
)

# CORS for frontend (Vite dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
from weather_app.api import routes
app.include_router(routes.router, prefix="/api")
```

---

## Alternatives Considered

### 1. Flask + flask-restx
- **Pros:** Mature, large community, familiar to Python developers
- **Cons:** No native type safety, manual OpenAPI schema, no async by default
- **Verdict:** Too much manual work for type safety and docs

### 2. Django REST Framework
- **Pros:** Batteries included, admin panel, ORM
- **Cons:** Heavy for simple API, ORM not needed (DuckDB direct SQL), steep learning curve
- **Verdict:** Over-engineered for this use case

### 3. Node.js + Express
- **Pros:** JavaScript everywhere (same language as frontend)
- **Cons:** No type safety without TypeScript, lose Python data science ecosystem
- **Verdict:** Doesn't leverage Python strengths for data processing

---

## Validation

### Success Criteria
- [x] API endpoints return JSON responses
- [x] OpenAPI schema auto-generated at `/docs`
- [x] Pydantic models validate request/response data
- [x] TypeScript client can be generated from OpenAPI schema
- [x] Tests pass using FastAPI TestClient

### Metrics (Phase 2 completion)
- **OpenAPI schema:** ✅ Auto-generated at http://localhost:8000/docs
- **Type safety:** ✅ Pydantic models prevent invalid data
- **Performance:** ✅ Handles 1000s of concurrent requests
- **Developer experience:** ✅ Interactive docs, hot reload

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [OpenAPI TypeScript Codegen](https://github.com/ferdikoomen/openapi-typescript-codegen)
- [Peer Review: Technology Stack Recommendations](../peer-review.md)

---

## Document Changelog

- **2025-12-15:** Decision made during Phase 1 architecture planning
- **2026-01-02:** Formalized as ADR-001 during documentation reorganization
