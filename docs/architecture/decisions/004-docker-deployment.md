# ADR-004: Docker Compose for Deployment

**Status:** ✅ Accepted (Phase 2)
**Date:** 2026-01-01
**Deciders:** Janna Spicer, Principal Software Architect (peer review)

---

## Context

The Weather App targets hobbyist users who may not be Python developers. The application has multiple components that must work together:
- Python backend (FastAPI + Uvicorn)
- TypeScript frontend (React + Vite)
- DuckDB database (single file)
- Environment configuration (.env file)

**User Experience Goals:**
- Installation should be **one command**
- Works on Windows, macOS, Linux
- No manual dependency management (Python, Node.js, npm)
- Updates should be easy (`docker-compose pull`)
- Data persistence across container restarts

---

## Decision

We will use **Docker Compose** as the recommended deployment method for end users.

---

## Rationale

### User Experience: One-Command Deployment

**Without Docker:**
```bash
# Backend setup (10 steps)
git clone https://github.com/jannaspicerbot/Weather-App
cd Weather-App
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with API keys
weather-app init-db
uvicorn weather_app.api.main:app --port 8000 &

# Frontend setup (5 steps)
cd web
npm install
npm run build
npm run preview &

# User must manage 2 processes, 2 terminal windows
```

**With Docker Compose:**
```bash
# One-command deployment (3 steps)
git clone https://github.com/jannaspicerbot/Weather-App
cd Weather-App
cp .env.example .env
# Edit .env with API keys
docker-compose up -d

# Done! Access dashboard at http://localhost:8000
```

### Benefits

1. **Consistent Environment**
   - Python 3.11, Node.js 20, npm versions locked in Dockerfiles
   - No "works on my machine" issues
   - Same environment in development and production

2. **Cross-Platform Support**
   - Works on Windows, macOS, Linux
   - Works on Raspberry Pi (ARM64)
   - Works on cloud VMs (AWS, GCP, Azure)

3. **Easy Updates**
   ```bash
   # Pull latest version
   docker-compose pull

   # Restart with new version
   docker-compose up -d

   # Data persists in ./data volume
   ```

4. **Isolated Dependencies**
   - No conflicts with system Python/Node.js
   - No need to manage virtual environments
   - Clean uninstall: `docker-compose down && rm -rf .`

5. **Data Persistence**
   ```yaml
   volumes:
     - ./data:/app/data        # DuckDB file persists
     - ./.env:/app/.env        # Configuration persists
   ```

### Alignment with Peer Review

From peer-review.md:

> "Docker + GitHub Releases: One-Command Setup"
> "User Experience: docker-compose up -d"
> "Works on Raspberry Pi, Mac, Windows"
> "Easy updates (docker-compose pull)"

Peer review priority: **HIGH**

---

## Consequences

### Positive

- ✅ One-command deployment (`docker-compose up -d`)
- ✅ Cross-platform (Windows, macOS, Linux, Raspberry Pi)
- ✅ Consistent environment (no dependency version conflicts)
- ✅ Easy updates (`docker-compose pull`)
- ✅ Data persistence (volumes for database and config)
- ✅ Isolated dependencies (no conflicts with system packages)
- ✅ Production-ready (same environment in dev and prod)

### Negative

- ⚠️ Requires Docker installed (but Docker Desktop is simple to install)
- ⚠️ Larger disk usage (~500MB for images vs ~100MB native)
- ⚠️ Slight performance overhead (negligible for I/O-bound workload)
- ⚠️ Debugging is harder (need to exec into containers)

### Neutral

- Docker Compose is now built into Docker CLI (`docker compose` vs `docker-compose`)
- Native development still supported (venv + npm) for contributors

---

## Implementation

### docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: weather-app-backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data            # DuckDB file persistence
      - ./.env:/app/.env            # API keys
    environment:
      - DATABASE_PATH=/app/data/weather.db
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./web
      dockerfile: ../Dockerfile.frontend
    container_name: weather-app-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    restart: unless-stopped
```

### Dockerfile.backend

```dockerfile
# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY weather_app/ ./weather_app/
COPY setup.py .
COPY pyproject.toml .

# Install package in editable mode
RUN pip install -e .

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "weather_app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.frontend

```dockerfile
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build production bundle
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf (Frontend Proxy)

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Serve React app
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### .env.example

```bash
# Ambient Weather API credentials
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APPLICATION_KEY=your_application_key_here
STATION_MAC_ADDRESS=00:11:22:33:44:55

# Optional settings
DATABASE_PATH=./data/weather.db
LOG_LEVEL=INFO
API_TIMEOUT=30
RETRY_MAX_ATTEMPTS=5
```

---

## User Workflows

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App

# 2. Configure API keys
cp .env.example .env
nano .env  # Edit with your API keys

# 3. Start application
docker-compose up -d

# 4. Initialize database (first time only)
docker-compose exec backend weather-app init-db

# 5. Backfill historical data
docker-compose exec backend weather-app backfill --start 2024-01-01 --end 2024-12-31

# 6. Access dashboard
open http://localhost:8000
```

### Daily Operations

```bash
# Fetch latest data
docker-compose exec backend weather-app fetch

# View logs
docker-compose logs -f backend

# Check database stats
docker-compose exec backend weather-app info

# Export data
docker-compose exec backend weather-app export --start 2024-01-01 --end 2024-12-31 --output /app/data/export.csv
```

### Updates

```bash
# Pull latest version
git pull
docker-compose pull

# Restart containers
docker-compose down
docker-compose up -d

# Database and configuration persist in ./data and ./.env
```

### Scheduling Automated Fetches

**Option 1: cron (Linux/macOS)**
```bash
# Add to crontab
crontab -e

# Fetch every 5 minutes
*/5 * * * * cd /path/to/Weather-App && docker-compose exec -T backend weather-app fetch >> /var/log/weather-fetch.log 2>&1
```

**Option 2: Task Scheduler (Windows)**
- Create scheduled task to run:
  ```powershell
  cd C:\Weather-App
  docker-compose exec -T backend weather-app fetch
  ```

**Option 3: Docker restart policy (simple but less flexible)**
```yaml
# In docker-compose.yml
services:
  scheduler:
    image: weather-app-backend
    command: bash -c "while true; do weather-app fetch && sleep 300; done"
    restart: unless-stopped
```

---

## Alternatives Considered

### 1. Manual Installation (pip + npm)
- **Pros:** No Docker dependency, smaller disk footprint
- **Cons:** Requires Python 3.11+, Node.js 20+, manual dependency management, platform-specific issues
- **Verdict:** Too many steps for hobbyist users, "works on my machine" problems

### 2. Single Docker Container (Backend + Frontend)
- **Pros:** Simpler docker-compose.yml, fewer moving parts
- **Cons:** Harder to scale independently, mixed Python/Node.js dependencies, larger image
- **Verdict:** Violates separation of concerns, harder to debug

### 3. Kubernetes (K8s)
- **Pros:** Production-grade orchestration, auto-scaling, high availability
- **Cons:** Massive overkill for single-user local app, steep learning curve, complex setup
- **Verdict:** Over-engineered for hobbyist use case

### 4. Snap/Flatpak/AppImage (Linux)
- **Pros:** Native Linux packaging, sandboxed
- **Cons:** Linux-only, doesn't solve Windows/macOS, still requires multiple packages
- **Verdict:** Doesn't meet cross-platform requirement

### 5. GitHub Container Registry + Pre-built Images
- **Pros:** No build step for users, faster deployment
- **Cons:** Requires CI/CD setup, image versioning, larger downloads
- **Verdict:** Planned for Phase 3 (users can still build locally for now)

---

## Validation

### Success Criteria
- [x] `docker-compose up -d` starts both containers
- [x] Backend accessible at http://localhost:8000
- [x] Frontend accessible at http://localhost:3000
- [x] DuckDB data persists in ./data volume
- [x] .env configuration works correctly
- [x] CLI commands work via `docker-compose exec backend`
- [x] Health check endpoint returns 200 OK
- [x] Logs viewable via `docker-compose logs`

### Testing Results (Phase 2 Completion)
```bash
# Build and start
✅ PASS: docker-compose build (builds both images)
✅ PASS: docker-compose up -d (starts containers)

# Container health
✅ PASS: docker-compose ps (both containers running)
✅ PASS: curl http://localhost:8000/api/health (backend responds)
✅ PASS: curl http://localhost:3000 (frontend serves React app)

# Data persistence
✅ PASS: ./data/weather.db created
✅ PASS: Data persists after container restart

# CLI commands
✅ PASS: docker-compose exec backend weather-app --help
✅ PASS: docker-compose exec backend weather-app info
```

---

## Future Enhancements

### Phase 3: Pre-built Images (GitHub Container Registry)

```yaml
# Future docker-compose.yml
services:
  backend:
    image: ghcr.io/jannaspicerbot/weather-app:latest
    # No build step needed

  frontend:
    image: ghcr.io/jannaspicerbot/weather-app-frontend:latest
    # No build step needed
```

**User workflow becomes:**
```bash
# Download docker-compose.yml only (no git clone)
curl -O https://raw.githubusercontent.com/jannaspicerbot/Weather-App/main/docker-compose.yml
cp .env.example .env
nano .env
docker-compose up -d
```

### Multi-Architecture Support

```dockerfile
# Build for multiple architectures (AMD64, ARM64)
# Enables Raspberry Pi support
FROM --platform=$BUILDPLATFORM python:3.11-slim
```

---

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Multi-Stage Builds](https://docs.docker.com/develop/develop-images/multistage-build/)
- [Nginx Reverse Proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
- [Peer Review: Deployment & Distribution](../peer-review.md)

---

## Document Changelog

- **2026-01-01:** Decision made during Phase 2 deployment planning
- **2026-01-02:** Formalized as ADR-004 during documentation reorganization
