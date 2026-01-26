# Weather App Full-Stack Dockerfile
# Multi-stage build for optimized production image with frontend + backend

# =============================================================================
# STAGE 1: Build Frontend (React + Vite)
# =============================================================================
FROM node:25-slim AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY web/package*.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY web/ ./

# Build production frontend
RUN npm run build

# =============================================================================
# STAGE 2: Build Backend (Python + FastAPI)
# =============================================================================
FROM python:3.14-slim AS backend-builder

WORKDIR /app

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY weather_app/ weather_app/
COPY setup.py .

# Install the package
RUN pip install -e .

# =============================================================================
# STAGE 3: Final Production Image
# =============================================================================
FROM python:3.14-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend application
COPY --from=backend-builder /app/weather_app /app/weather_app
COPY --from=backend-builder /app/setup.py /app/setup.py

# Copy built frontend into backend's static directory
COPY --from=frontend-builder /frontend/dist /app/web/dist

# Create data directory for database
RUN mkdir -p /data

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/data/ambient_weather.duckdb
ENV STATIC_FILES_DIR=/app/web/dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command: Run FastAPI server
# The FastAPI app will serve both API endpoints and static frontend files
CMD ["uvicorn", "weather_app.web.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
