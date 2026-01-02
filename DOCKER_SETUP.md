# Docker Setup Guide

This guide explains how to run the Weather App using Docker Compose for easy deployment and development.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed
- [Docker Compose](https://docs.docker.com/compose/install/) installed
- `.env` file with Ambient Weather API credentials (see below)

## Quick Start

### 1. Create Environment File

Create a `.env` file in the project root with your Ambient Weather API credentials:

```bash
# Ambient Weather API Credentials
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APP_KEY=your_app_key_here

# Optional: Use DuckDB instead of SQLite (10-100x faster for analytics)
USE_DUCKDB=true

# Optional: Database path (defaults to /data/ambient_weather.db in container)
# DB_PATH=/data/ambient_weather.db
```

### 2. Start the Application

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access the Application

- **Frontend**: http://localhost (or http://localhost:80)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 4. Initialize Database and Fetch Data

```bash
# Access the backend container
docker-compose exec backend bash

# Inside the container, run CLI commands:
weather-app init-db
weather-app fetch --limit 100
weather-app backfill --start 2024-01-01 --end 2024-12-31

# Exit the container
exit
```

## Architecture

The Docker Compose setup includes:

### Services

1. **Backend** (`weather-app-backend`)
   - FastAPI application
   - Python 3.11-slim base image
   - Exposes port 8000
   - Database stored in Docker volume

2. **Frontend** (`weather-app-frontend`)
   - React + TypeScript + Vite
   - Nginx for serving static files
   - Exposes port 80
   - Proxies `/api/*` requests to backend

### Volumes

- `weather-data`: Persistent storage for database files

### Networks

- `weather-network`: Bridge network for inter-service communication

## Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
# Stop all services
docker-compose stop

# Stop and remove containers, networks
docker-compose down

# Stop and remove everything including volumes (WARNING: deletes database)
docker-compose down -v
```

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Access Container Shell

```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh
```

### Database Operations

```bash
# Run CLI commands
docker-compose exec backend weather-app --help
docker-compose exec backend weather-app fetch --limit 10
docker-compose exec backend weather-app info

# Backup database
docker cp weather-app-backend:/data/ambient_weather.db ./backup.db

# Restore database
docker cp ./backup.db weather-app-backend:/data/ambient_weather.db
```

### Migrate from SQLite to DuckDB

```bash
# Access backend container
docker-compose exec backend bash

# Run migration
weather-app migrate --backup

# Update .env to use DuckDB
echo "USE_DUCKDB=true" >> .env

# Restart backend
exit
docker-compose restart backend
```

## Development Mode

For development with hot-reload:

### Backend Development

```bash
# Stop the Docker backend
docker-compose stop backend

# Run backend locally with hot-reload
cd weather-app
uvicorn weather_app.web.app:create_app --factory --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Stop the Docker frontend
docker-compose stop frontend

# Run frontend locally with hot-reload
cd frontend
npm install
npm run dev
```

Frontend will be available at http://localhost:5173

## Production Deployment

For production deployment:

1. Update nginx.conf to use production API URL
2. Set appropriate CORS_ORIGINS in weather_app/config.py
3. Use environment-specific .env files
4. Consider using Docker secrets for API keys
5. Set up proper logging and monitoring
6. Use a reverse proxy (Caddy/Traefik) for HTTPS

Example production docker-compose override:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    restart: always
    environment:
      - LOG_LEVEL=INFO

  frontend:
    restart: always
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Backend won't start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Missing .env file → Create .env with API keys
# - Permission issues → Check volume permissions
```

### Frontend shows API errors

```bash
# Check backend is running
docker-compose ps

# Check backend health
curl http://localhost:8000/api/health

# Check nginx proxy configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Database issues

```bash
# Check volume exists
docker volume ls | grep weather

# Check database file
docker-compose exec backend ls -lah /data

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend weather-app init-db
```

### Port conflicts

If ports 80 or 8000 are already in use:

```bash
# Edit docker-compose.yml to use different ports
# For example, change "80:80" to "8080:80"
# Then restart
docker-compose up -d
```

## Performance Tuning

### Use DuckDB for Better Analytics Performance

Set in `.env`:
```
USE_DUCKDB=true
```

DuckDB provides 10-100x faster performance for analytical queries.

### Resource Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          memory: 512M
```

## Monitoring

### Health Checks

```bash
# Check service health
docker-compose ps

# Manual health check
curl http://localhost:8000/api/health
curl http://localhost/
```

### Resource Usage

```bash
# Monitor resource usage
docker stats

# Service-specific
docker stats weather-app-backend weather-app-frontend
```

## Backup and Restore

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=./backups
mkdir -p $BACKUP_DIR

DATE=$(date +%Y%m%d_%H%M%S)
docker cp weather-app-backend:/data/ambient_weather.db $BACKUP_DIR/backup_$DATE.db

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.db" -mtime +7 -delete
```

Run with cron:
```bash
# Daily backup at 2 AM
0 2 * * * /path/to/backup.sh
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/Weather-App/issues
- Documentation: See docs/ directory

---

**Last Updated**: January 2, 2026
