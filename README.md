# Weather App - Ambient Weather Data Dashboard

![Main CI](https://github.com/jannaspicerbot/Weather-App/workflows/Main%20CI/badge.svg)
![Accessibility CI](https://github.com/jannaspicerbot/Weather-App/workflows/Accessibility%20CI/badge.svg)
![Documentation CI](https://github.com/jannaspicerbot/Weather-App/workflows/Documentation%20CI/badge.svg)
[![codecov](https://codecov.io/gh/jannaspicerbot/Weather-App/branch/main/graph/badge.svg)](https://codecov.io/gh/jannaspicerbot/Weather-App)

A modern, full-stack web application for collecting, storing, and visualizing data from your Ambient Weather Network device with automated scheduling and interactive dashboards.

## 🌟 Features

- **🌡️ Real-Time Monitoring** - Live weather data from your Ambient Weather station
- **📊 Interactive Charts** - Beautiful, accessible visualizations with Victory Charts
- **📅 50-Year Retention** - Store decades of full-resolution data with DuckDB
- **⚙️ Automated Collection** - Built-in scheduler (APScheduler) for hands-free data collection
- **🖥️ Web Dashboard** - Modern React + TypeScript interface
- **🐳 Easy Deployment** - Docker Compose for one-command setup
- **💻 Desktop Installers** - Standalone executables for Windows and macOS
- **🔌 REST API** - Comprehensive API for integrations and custom dashboards
- **📱 Responsive Design** - Works on desktop and tablets
- **♿ Accessible** - WCAG 2.2 Level AA compliance

## 📋 What You Need

1. An Ambient Weather account with a weather station
2. API credentials from Ambient Weather ([Get them here](https://ambientweather.net/account))
3. Docker + Docker Compose (recommended) OR Python 3.10+ and Node.js 18+

## ⚠️ Important: API Credentials Security

**NEVER commit your `.env` file to Git!** This file contains your personal API credentials.

- ✅ The `.env` file is already in `.gitignore` to protect your credentials
- ✅ Use `.env.example` as a template (safe to commit)
- ✅ Get your API keys from: https://ambientweather.net/account
- ❌ **Never share** your API keys publicly or commit them to version control

**Before making this repository public**, rotate (regenerate) your API credentials to ensure old keys cannot be misused. See [docs/technical/deployment-guide.md](docs/technical/deployment-guide.md#credential-security) for credential rotation instructions.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App

# 2. Create .env file with your API credentials
cp .env.example .env
# Edit .env and add your AMBIENT_API_KEY and AMBIENT_APP_KEY

# 3. Start everything with Docker
docker-compose up -d

# 4. Initialize the database
docker-compose exec backend weather-app init-db

# 5. Fetch your weather data
docker-compose exec backend weather-app fetch --limit 288

# 6. Open the dashboard
# Visit http://localhost:5173 in your browser
```

**That's it!** The web dashboard is now running and displaying your weather data.

### Option 2: Native Installation

For development or if you prefer not to use Docker:

```bash
# 1. Clone the repository
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App

# 2. Set up Python backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .

# 3. Create .env file with your API credentials
cp .env.example .env
# Edit .env and add your AMBIENT_API_KEY and AMBIENT_APP_KEY

# 4. Initialize database and fetch data
weather-app init-db
weather-app fetch --limit 288

# 5. Start the backend API
uvicorn weather_app.web.app:create_app --factory --reload

# 6. In a new terminal, set up the frontend
cd web
npm install
npm run dev

# 7. Open http://localhost:5173 in your browser
```

### Option 3: Desktop Installer

Download standalone installers for Windows or macOS:

- **Windows**: [WeatherAppSetup.exe](../../releases) (no Python required)
- **macOS**: [WeatherApp.app](../../releases) (drag-and-drop installation)

See [installer/README.md](installer/README.md) for build instructions.

## 📖 Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

### Getting Started
- **[Deployment Guide](docs/technical/deployment-guide.md)** - Installation, configuration, and setup
- **[CLI Reference](docs/technical/cli-reference.md)** - Command-line tool usage
- **[API Reference](docs/technical/api-reference.md)** - REST API endpoints and examples

### Architecture & Design
- **[Architecture Overview](docs/architecture/overview.md)** - System design and components
- **[Architecture Decision Records](docs/architecture/decisions/)** - Technology choices and rationale
- **[Design System](docs/design/design-tokens.md)** - Color palette and accessibility standards

### Navigation
- **[Documentation Index](docs/README.md)** - Complete documentation navigation guide

## 🏗️ Architecture

The Weather App is built with modern, production-ready technologies:

**Backend:**
- **FastAPI** - High-performance Python web framework with automatic OpenAPI docs
- **DuckDB** - Analytics database (10-100x faster than SQLite)
- **APScheduler** - Automated data collection scheduling
- **Click** - Command-line interface framework

**Frontend:**
- **React** - Modern UI framework with hooks
- **TypeScript** - Type-safe JavaScript
- **Victory Charts** - Accessible, theme-aware data visualization
- **React Aria** - WCAG 2.2 AA accessible components
- **TailwindCSS** - Utility-first styling
- **Vite** - Fast build tool and dev server

**Deployment:**
- **Docker Compose** - Multi-container orchestration
- **PyInstaller** - Standalone desktop executables

See [docs/architecture/overview.md](docs/architecture/overview.md) for detailed architecture documentation.

## 🖥️ CLI Usage

The Weather App includes a powerful command-line interface:

```bash
# Initialize the database
weather-app init-db

# Fetch latest weather data
weather-app fetch --limit 288

# Backfill historical data
weather-app backfill --start 2024-01-01 --end 2024-12-31

# Show database info
weather-app info

# Export data to CSV
weather-app export --output weather_data.csv --start 2024-01-01
```

See [docs/technical/cli-reference.md](docs/technical/cli-reference.md) for complete CLI documentation.

## 🌐 REST API

The FastAPI backend provides a comprehensive REST API:

```bash
# Get latest weather reading
GET /api/weather/latest

# Get weather history
GET /api/weather/history?start_date=2024-01-01&end_date=2024-12-31

# Get weather statistics
GET /api/weather/stats?start_date=2024-01-01&end_date=2024-12-31

# Health check
GET /health
```

**Interactive API docs** (Swagger UI): http://localhost:8000/docs

See [docs/technical/api-reference.md](docs/technical/api-reference.md) for complete API documentation with code examples in JavaScript, Python, and curl.

## ⚙️ Automated Data Collection

Set up automated data collection to keep your database up to date:

**With Docker Compose:**
```bash
# Edit docker-compose.yml and uncomment the scheduler service
# The scheduler runs fetch every 5 minutes automatically
docker-compose up -d
```

**Native Installation:**

See [docs/technical/deployment-guide.md](docs/technical/deployment-guide.md) for instructions on setting up:
- **Linux/macOS**: systemd or cron
- **Windows**: Task Scheduler
- **All platforms**: APScheduler built-in scheduler

## 📊 Dashboard Features

The web dashboard provides:

- **📈 Temperature Analysis** - Indoor/outdoor temps with trends
- **💨 Wind Monitoring** - Speed, gusts, and direction
- **🌧️ Precipitation Tracking** - Rainfall amounts and rates
- **🔘 Barometric Pressure** - Pressure trends and weather patterns
- **💧 Humidity Levels** - Indoor and outdoor humidity
- **☀️ Solar Data** - Solar radiation and UV index
- **📅 Time Range Selector** - View 24h, week, month, year, or custom ranges
- **🎨 Theme Support** - Light and dark modes (respects system preference)
- **📱 Responsive Design** - Works on desktop and tablets

## 🛠️ Development

Contributions are welcome! To set up a development environment:

```bash
# Clone and install dependencies
git clone https://github.com/jannaspicerbot/Weather-App.git
cd Weather-App
pip install -r requirements.txt
pip install -e .
cd web && npm install

# Run code quality checks
black weather_app/                    # Format Python code
ruff check --fix weather_app/         # Lint Python code
mypy weather_app/                     # Type check Python code
cd web && npm run lint                # Lint TypeScript code

# Run tests
pytest                                # Backend tests
pytest -m unit                        # Fast unit tests only
cd web && npm test                    # Frontend tests
```

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for contribution guidelines.

## 🔒 Security & Privacy

- **Local-First** - All data stored locally in your DuckDB database
- **No Cloud** - Your weather data never leaves your system
- **API Keys** - Secure credential storage in `.env` file
- **CORS** - Properly configured for security
- **Input Validation** - Pydantic models validate all API inputs

## 🗂️ Project Structure

```
Weather-App/
├── weather_app/              # Python backend
│   ├── cli/                  # CLI commands
│   ├── fetch/                # Ambient Weather API client
│   ├── database/             # DuckDB repository layer
│   └── web/                  # FastAPI application
├── web/                      # React + TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   └── types/            # TypeScript types
│   └── dist/                 # Built frontend (generated)
├── docs/                     # Documentation
│   ├── architecture/         # System design & ADRs
│   ├── design/               # UI/UX & accessibility
│   ├── product/              # Requirements & specs
│   └── technical/            # API, CLI, deployment guides
├── installer/                # Desktop app installers
│   ├── windows/              # Windows .exe installer
│   └── macos/                # macOS .app installer
├── tests/                    # Test suite
├── docker-compose.yml        # Docker orchestration
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Python project config
└── .env                      # API credentials (create from .env.example)
```

## 🐛 Troubleshooting

**"No devices found"**
- Verify your API credentials are correct in `.env`
- Ensure your weather station is online at ambientweather.net

**"Database error"**
- Run `weather-app init-db` to initialize the database
- Check that the database file has write permissions

**"API rate limit exceeded"**
- Ambient Weather API allows 1 request/second
- Reduce fetch frequency or use smaller `--limit` values

**Docker issues**
- Ensure Docker Desktop is running
- Try `docker-compose down && docker-compose up -d` to restart

See [docs/technical/deployment-guide.md](docs/technical/deployment-guide.md) for more troubleshooting tips.

## 📄 License

This project is open source and available for personal use. See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. **Read** [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines
2. **Fork** the repository
3. **Create** a feature branch: `git checkout -b feature/my-feature`
4. **Commit** your changes: `git commit -m "Add my feature"`
5. **Push** to the branch: `git push origin feature/my-feature`
6. **Open** a Pull Request

## 🙏 Acknowledgments

- **Ambient Weather** - For providing the API and excellent weather stations
- **FastAPI** - For making Python web APIs a joy to build
- **DuckDB** - For blazing-fast analytics queries
- **Victory Charts** - For accessible, beautiful data visualizations
- **React Aria** - For accessible component patterns

## 📧 Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/jannaspicerbot/Weather-App/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jannaspicerbot/Weather-App/discussions)

## 🗺️ Roadmap

See [docs/product/requirements.md](docs/product/requirements.md) for the complete roadmap.

**Phase 3 (In Progress):**
- ✅ APScheduler integration for automated data collection
- ✅ Desktop installers (Windows/macOS)
- 🔄 React + TypeScript frontend (in development)
- 🔄 Victory Charts integration
- 🔄 Multi-station support

**Future Phases:**
- User authentication for multi-user deployments
- Real-time WebSocket updates
- Mobile app (React Native)
- Weather alerts and notifications
- Machine learning for weather prediction

---

**Built with ❤️ for weather enthusiasts**

[Documentation](docs/README.md) • [API Reference](docs/technical/api-reference.md) • [Contributing](docs/CONTRIBUTING.md)
