# Weather App Backend Dockerfile
# Multi-stage build for optimized production image

FROM python:3.14-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY weather_app/ weather_app/
COPY setup.py .

# Install the package
RUN pip install -e .

# Create data directory for database
RUN mkdir -p /data

# Expose FastAPI port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/data/ambient_weather.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Default command: Run FastAPI server
CMD ["uvicorn", "weather_app.web.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
