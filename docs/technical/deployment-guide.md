# Deployment Guide

**Target Platforms:** Windows, macOS, Linux, Raspberry Pi
**Deployment Methods:** Docker Compose (recommended), Native Python

---

## Prerequisites

### Docker Deployment (Recommended)
- **Docker:** 20.10+ with Docker Compose
- **Disk Space:** 2GB for images + 5GB for data
- **RAM:** 2GB minimum, 4GB recommended
- **Network:** Internet access for pulling images and API calls

### Native Python Deployment
- **Python:** 3.13 or higher
- **Node.js:** 20 or higher (for frontend)
- **pip:** Latest version
- **npm:** Latest version
- **Disk Space:** 1GB for dependencies + 5GB for data
- **RAM:** 4GB minimum, 8GB recommended

---

## Quick Start (Docker Compose)

### 1. Clone Repository

```bash
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your API keys
nano .env  # or: vim .env, code .env, notepad .env
```

**Required values in .env:**
```bash
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APPLICATION_KEY=your_application_key_here
STATION_MAC_ADDRESS=00:11:22:33:44:55
```

Get your keys from: https://ambientweather.net/account

### 3. Start Application

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Initialize Database

```bash
# Create database schema
docker-compose exec backend weather-app init-db
```

### 5. Backfill Historical Data (Optional)

```bash
# Backfill last year
docker-compose exec backend weather-app backfill \
  --start 2024-01-01 \
  --end 2024-12-31
```

### 6. Access Dashboard

Open browser: http://localhost:8000

---

## Native Python Deployment

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install package in editable mode
pip install -e .

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Initialize database
weather-app init-db

# Start backend server
python -m uvicorn weather_app.api.main:app --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup (Separate Terminal)

```bash
cd web

# Install dependencies
npm install

# Build production bundle
npm run build

# Serve production build
npm run preview
```

### 3. Access Application

- **Backend API:** http://localhost:8000/api
- **Frontend Dashboard:** http://localhost:3000

---

## Configuration

### Environment Variables

**Required:**
```bash
AMBIENT_API_KEY=your_api_key_here
AMBIENT_APPLICATION_KEY=your_application_key_here
STATION_MAC_ADDRESS=00:11:22:33:44:55
```

**Optional:**
```bash
DATABASE_PATH=./data/weather.db  # Database file location
LOG_LEVEL=INFO                    # Logging level (DEBUG, INFO, WARNING, ERROR)
API_TIMEOUT=30                    # API request timeout (seconds)
RETRY_MAX_ATTEMPTS=5              # Max retry attempts for API calls
```

### Docker Compose Configuration

**docker-compose.yml customization:**
```yaml
version: '3.8'
services:
  backend:
    ports:
      - "8000:8000"  # Change left side to use different port
    volumes:
      - ./data:/app/data  # Database persistence
      - ./.env:/app/.env  # Environment variables
    environment:
      - DATABASE_PATH=/app/data/weather.db

  frontend:
    ports:
      - "3000:80"  # Change left side to use different port
```

---

## Automated Data Collection

### Built-in Scheduler (Recommended)

**APScheduler is integrated into the FastAPI application** and automatically fetches weather data when the server is running.

**Configuration** (via .env):
```bash
SCHEDULER_ENABLED=true                  # Enable/disable scheduler (default: true)
SCHEDULER_FETCH_INTERVAL_MINUTES=5      # Fetch interval (default: 5 minutes)
```

**How it works:**
- Scheduler starts automatically when FastAPI application starts
- Fetches latest data at configured interval (default: every 5 minutes)
- Handles errors gracefully without crashing the server
- Logs all fetch attempts and results to application logs
- Stops gracefully when server shuts down

**Monitor scheduler status:**
```bash
# Check if scheduler is running and next fetch time
curl http://localhost:8000/api/scheduler/status | jq
```

**When to use:**
- ✅ Running via Docker Compose
- ✅ Running via `uvicorn` or `main.py` continuously
- ✅ Want automatic data collection without external setup

**When NOT to use:**
- ❌ Running server only for manual queries (set `SCHEDULER_ENABLED=false`)
- ❌ Already using cron/systemd for scheduled fetching (avoid duplicate fetches)

---

### Option 2: cron (Linux/macOS)

**Use case:** Manual control over scheduling, or when not running FastAPI server continuously.

```bash
# Edit crontab
crontab -e

# Add entry (fetch every 5 minutes)
*/5 * * * * cd /path/to/Weather-App && docker-compose exec -T backend weather-app fetch >> /var/log/weather-fetch.log 2>&1
```

### Option 2: systemd Timer (Linux)

**Service:** `/etc/systemd/system/weather-fetch.service`
```ini
[Unit]
Description=Weather App Data Fetch
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/path/to/Weather-App
ExecStart=/usr/bin/docker-compose exec -T backend weather-app fetch
StandardOutput=journal
StandardError=journal
```

**Timer:** `/etc/systemd/system/weather-fetch.timer`
```ini
[Unit]
Description=Weather App Fetch Timer

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-fetch.timer
sudo systemctl start weather-fetch.timer
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task → "Weather App Fetch"
3. Trigger: Daily, Repeat every 5 minutes
4. Action: Start a program
   - Program: `C:\Program Files\Docker\Docker\resources\bin\docker-compose.exe`
   - Arguments: `exec -T backend weather-app fetch`
   - Start in: `C:\Weather-App`

---

## Backup and Restore

### Backup Database

```bash
# Stop containers (optional, for consistency)
docker-compose down

# Copy database file
cp ./data/weather.db ./backups/weather_$(date +%Y%m%d).db

# Compress (optional)
gzip ./backups/weather_$(date +%Y%m%d).db

# Restart
docker-compose up -d
```

### Automated Backup Script

```bash
#!/bin/bash
# backup_weather.sh
BACKUP_DIR=~/weather-backups
mkdir -p $BACKUP_DIR

# Copy database
cp ./data/weather.db $BACKUP_DIR/weather_$(date +%Y%m%d_%H%M%S).db

# Delete backups older than 30 days
find $BACKUP_DIR -name "weather_*.db" -mtime +30 -delete

echo "Backup complete: $BACKUP_DIR"
```

**Schedule with cron:**
```bash
# Daily at 2am
0 2 * * * /path/to/backup_weather.sh >> /var/log/weather-backup.log 2>&1
```

### Restore Database

```bash
# Stop containers
docker-compose down

# Restore from backup
cp ./backups/weather_20241231.db ./data/weather.db

# Restart
docker-compose up -d
```

---

## Updates

### Docker Deployment

```bash
# Pull latest code
cd /path/to/Weather-App
git pull

# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Verify
docker-compose logs -f
```

### Native Python Deployment

```bash
# Pull latest code
cd /path/to/Weather-App
git pull

# Update backend
source venv/bin/activate
pip install -r requirements.txt --upgrade
pip install -e .

# Update frontend
cd web
npm install
npm run build
```

---

## Monitoring

### Health Check

```bash
# Check API health
curl http://localhost:8000/api/health

# Expected response:
# {"status":"ok","database":"connected","total_records":125432,...}
```

### View Logs

**Docker:**
```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

**Native Python:**
```bash
# Backend logs (stdout)
# Frontend logs (browser console)
```

### Database Statistics

```bash
# Docker
docker-compose exec backend weather-app info

# Native
weather-app info
```

---

## Troubleshooting

### Containers Not Starting

```bash
# Check Docker status
docker ps -a

# View logs
docker-compose logs backend
docker-compose logs frontend

# Restart containers
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Database Connection Errors

```bash
# Check database file exists
ls -lh ./data/weather.db

# Check file permissions
chmod 644 ./data/weather.db

# Reinitialize database
docker-compose exec backend weather-app init-db
```

### API Authentication Errors

```bash
# Verify .env file
cat .env | grep AMBIENT

# Check API keys at https://ambientweather.net/account

# Test API manually
curl -H "Content-Type: application/json" \
  "https://api.ambientweather.net/v1/devices?applicationKey=YOUR_APP_KEY&apiKey=YOUR_API_KEY"
```

### Port Conflicts

```bash
# Error: port 8000 already in use

# Option 1: Stop conflicting process
lsof -i :8000  # Find process using port
kill <PID>

# Option 2: Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use port 8080 instead
```

---

## Platform-Specific Notes

### Raspberry Pi (ARM64)

**Recommended Hardware:**
- Raspberry Pi 4, 4GB RAM minimum
- SSD or USB drive (SD cards wear out quickly)
- Heatsink or fan (optional but recommended)

**Setup:**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker run hello-world

# Deploy Weather App (same as x86)
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App
cp .env.example .env
nano .env
docker-compose up -d
```

### Windows

**Docker Desktop:**
- Enable WSL2 backend (faster than Hyper-V)
- Increase Docker memory limit to 4GB (Settings → Resources → Advanced)

**File Paths:**
- Use forward slashes in docker-compose.yml: `./data:/app/data`
- Use PowerShell or Git Bash for commands

### macOS

**Docker Desktop:**
- Increase memory limit to 4GB (Preferences → Resources → Advanced)

**File Paths:**
- Same as Linux (forward slashes)

---

## Security Considerations

### Credential Security

**Protecting Your API Keys:**

Your `.env` file contains sensitive API credentials that must never be shared or committed to version control.

**Best Practices:**
- ✅ Never commit `.env` file to git (already in `.gitignore`)
- ✅ Set restrictive file permissions: `chmod 600 .env` (Linux/macOS)
- ✅ Use `.env.example` for documentation (safe to commit)
- ✅ Rotate credentials before making your repository public
- ❌ Never share API keys in screenshots, logs, or documentation
- ❌ Never commit credentials to version control

**Git Pre-Commit Hook:**

A pre-commit hook has been installed at `.git/hooks/pre-commit` to prevent accidentally committing `.env` files. This provides an additional safety layer beyond `.gitignore`.

### Credential Rotation

**When to Rotate API Credentials:**
- Before making your repository public
- If credentials may have been exposed (screenshots, logs, shared files)
- Periodically as a security best practice (e.g., every 6-12 months)
- After revoking access for collaborators
- If you suspect unauthorized API usage

**How to Rotate Ambient Weather API Credentials:**

1. **Generate New Credentials:**
   - Visit https://ambientweather.net/account
   - Navigate to **Dashboard → Account → API Keys**
   - Click **"Regenerate API Key"** - This creates a new API key
   - Click **"Regenerate Application Key"** - This creates a new Application key
   - Copy both new keys immediately

2. **Update Your .env File:**
   ```bash
   # Edit your .env file
   nano .env  # or: vim .env, code .env, notepad .env

   # Replace with new credentials
   AMBIENT_API_KEY=your_new_api_key_here
   AMBIENT_APP_KEY=your_new_application_key_here
   ```

3. **Restart Services:**

   **Docker Deployment:**
   ```bash
   docker-compose restart backend
   ```

   **Native Python Deployment:**
   ```bash
   # Stop the running server (Ctrl+C)
   # Restart it:
   python -m uvicorn weather_app.web.app:create_app --factory --reload
   ```

4. **Verify New Credentials Work:**
   ```bash
   # Test API connection
   weather-app fetch --limit 1

   # Or check API health
   curl http://localhost:8000/api/health
   ```

5. **Revoke Old Credentials (Optional but Recommended):**
   - Old API keys remain valid until explicitly revoked
   - On Ambient Weather dashboard, you can view and revoke old keys
   - This ensures old credentials cannot be misused

**Important Notes:**
- Ambient Weather allows multiple active API keys per account
- Rotating creates new keys but doesn't automatically revoke old ones
- For maximum security, revoke old keys after rotation is complete
- Update any other applications or scripts using the old credentials

### File Permissions

**Linux/macOS:**
```bash
# Restrict .env file to owner only
chmod 600 .env

# Verify permissions
ls -l .env
# Should show: -rw------- (owner read/write only)
```

**Windows:**
```powershell
# Restrict .env file to current user only
icacls .env /inheritance:r /grant:r "$($env:USERNAME):F"
```

### Network Access

**Local-Only (Default):**
- Backend: `http://localhost:8000` (not accessible from network)
- Frontend: `http://localhost:3000` (not accessible from network)

**Network Access (Optional):**

Edit `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "0.0.0.0:8000:8000"  # Accessible from network
```

**HTTPS (Recommended for Network Access):**

Use reverse proxy (nginx, Caddy, Traefik):
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name weather.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
    }
}
```

---

## Performance Tuning

### Database Optimization

```bash
# DuckDB is fast by default, but can optimize:
# 1. Ensure SSD (not SD card)
# 2. Use CHECKPOINT command periodically (automatic)
# 3. Increase DuckDB memory limit (future config)
```

### Docker Resource Limits

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

---

## Uninstall

### Docker Deployment

```bash
# Stop and remove containers
docker-compose down

# Remove database and data
rm -rf ./data

# Remove Docker images (optional)
docker rmi $(docker images | grep weather-app | awk '{print $3}')
```

### Native Python Deployment

```bash
# Deactivate virtual environment
deactivate

# Remove files
cd ..
rm -rf Weather-App
```

---

## References

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [systemd Timer Documentation](https://www.freedesktop.org/software/systemd/man/systemd.timer.html)
- [nginx Reverse Proxy Guide](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)

---

## Document Changelog

- **2026-01-06:** Consolidated DOCKER_SETUP.md content into this guide
- **2026-01-02:** Initial deployment guide extracted from specifications.md
