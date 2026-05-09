# CS3S2 - Knowledge Hub Hybrid Cloud Monitoring System

> **Case Study 3 - LO3: Automation** | Hybrid Cloud Infrastructure Monitoring

A comprehensive monitoring solution for managing on-premises infrastructure (GNS3), Azure PaaS services, and containerized applications through a unified web interface.

## 📋 Project Overview

The Knowledge Hub is transitioning from pure on-premises setup into a **hybrid cloud environment**. This project implements a modern monitoring system with:

- **Web Frontend**: Modern Flask application with interactive dashboards
- **Backend API**: RESTful API for metrics collection and storage
- **Monitoring Client**: Data collectors from on-premises infrastructure
- **Cloud Integration**: Azure SQL Database and Entra ID authentication
- **Container Support**: Docker containerization for all components

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Web Browser / Client                         │
│                   (Bootstrap UI, Responsive)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Monitoring Web Frontend (Flask)                     │
│  ├─ Dashboard (Overview, Metrics, Host Details)                 │
│  ├─ AJAX API Endpoints                                          │
│  ├─ Bootstrap UI with Charts (Chart.js)                         │
│  └─ API Client Service                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Monitoring Backend API (Flask)                      │
│  ├─ /api/v1/metrics (GET/POST)                                  │
│  ├─ /api/v1/health (GET/POST)                                   │
│  └─ API Key Authentication                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
        ┌──────────────────┐  ┌──────────────┐
        │  Azure SQL DB    │  │  Monitoring  │
        │                  │  │  Client      │
        └──────────────────┘  └──────┬───────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌──────────────────────┐      ┌──────────────────────┐
        │  On-Prem (GNS3)      │      │  Azure (PaaS)        │
        │  - Domain Controller │      │  - App Services      │
        │  - File Servers      │      │  - Azure SQL DB      │
        │  - pfSense (VPN)     │      │  - Container Apps    │
        └──────────────────────┘      └──────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd cs3s2

# Create .env file
cp monitoring-web/.env.example .env

# Edit .env with your settings
# Important: Set API_KEY, API_BASE_URL, and DB_CONNECTION_STRING

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f monitoring-web
docker-compose logs -f monitoring-api
```

Access the application:
- **Frontend**: http://localhost:5001
- **Backend API**: http://localhost:5000/api/v1

### Option 2: Local Development

```bash
# 1. Start Backend API
cd monitoring-api
python -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
flask run

# 2. Start Frontend (in new terminal)
cd monitoring-web
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run --port 5001
```

## 📁 Project Structure

```
cs3s2/
├── monitoring-api/              # Backend API (Flask)
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── config.py           # Configuration
│   │   ├── models.py           # Data models
│   │   ├── database.py         # DB operations
│   │   ├── auth.py             # Authentication
│   │   └── routes/             # API endpoints
│   ├── requirements.txt
│   ├── wsgi.py
│   ├── Dockerfile
│   └── README.md
│
├── monitoring-web/              # Frontend Application (Flask) ⭐ NEW
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── config.py           # Configuration
│   │   ├── routes/
│   │   │   ├── main.py        # Main routes
│   │   │   ├── dashboard.py   # Dashboard views
│   │   │   └── api.py         # AJAX endpoints
│   │   ├── services/
│   │   │   ├── api_client.py  # Backend API client
│   │   │   └── data_processor.py # Data processing
│   │   ├── templates/          # Jinja2 templates
│   │   │   ├── base.html
│   │   │   ├── index.html
│   │   │   ├── about.html
│   │   │   └── dashboard/      # Dashboard templates
│   │   └── static/             # CSS, JS files
│   ├── tests/
│   ├── requirements.txt
│   ├── wsgi.py
│   ├── Dockerfile
│   ├── .env.example
│   └── README.md
│
├── monitoring-client/           # Data Collection Client
│   ├── monitor.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── docker-compose.yml          # Compose configuration (updated)
├── README.md                   # This file
└── [Bicep files, PowerShell scripts, design docs]
```

## 🔧 Configuration

### Environment Variables

Create `.env` file based on `monitoring-web/.env.example`:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secure-key

# Backend API
API_BASE_URL=http://localhost:5000/api/v1
API_KEY=your-api-key
API_TIMEOUT=10

# Refresh Intervals
METRICS_REFRESH_INTERVAL=30
HEALTH_REFRESH_INTERVAL=60

# Authentication
AUTH_ENABLED=false
# (Entra ID settings for future use)
```

## 🎯 Key Features

### Frontend (monitoring-web) ⭐ NEW
- ✅ **Real-time Dashboards**: Live monitoring with auto-refresh
- ✅ **Multi-host Support**: Monitor multiple infrastructure components
- ✅ **Interactive Charts**: Visual representation of metrics (Chart.js)
- ✅ **Responsive Design**: Works on desktop, tablet, mobile
- ✅ **Filtering & Drill-down**: Filter metrics by host, metric type
- ✅ **Status Indicators**: Color-coded alerts (OK, WARNING, CRITICAL)
- ✅ **Modern UI**: Bootstrap 5 based design

### Backend API (monitoring-api)
- ✅ **RESTful Endpoints**: `/api/v1/metrics`, `/api/v1/health`
- ✅ **API Key Auth**: Secure endpoint protection
- ✅ **Azure SQL Integration**: Persistent data storage
- ✅ **Scalable Design**: Blueprint-based architecture
- ✅ **Error Handling**: Comprehensive error responses

### Data Collection
- ✅ **Metrics Collection**: From on-premises and cloud hosts
- ✅ **Health Checks**: Service availability monitoring
- ✅ **Configurable Intervals**: Adjustable collection frequency

## 📊 Usage

### Dashboard Pages

1. **Home** (`/`)
   - System status overview
   - Quick access to monitoring tools

2. **Dashboard Overview** (`/dashboard/`)
   - Total metrics count
   - Monitored hosts overview
   - Status summary (OK, WARNING, CRITICAL)
   - Recent metrics table

3. **Metrics View** (`/dashboard/metrics`)
   - Detailed metrics list
   - Filter by host or metric type
   - Pagination support

4. **Host Details** (`/dashboard/host/<host>`)
   - Host-specific metrics
   - Metric statistics (avg, min, max)
   - Time-series charts

## 🐳 Docker Deployment

### Build Images
```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build monitoring-web
```

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d monitoring-web

# View logs
docker-compose logs -f monitoring-web

# Stop services
docker-compose down
```

### Health Checks
```bash
# Check frontend
curl http://localhost:5001/health

# Check backend API
curl http://localhost:5000/api/v1/health/status

# Docker health status
docker ps --filter "name=monitoring"
```

## 🧪 Testing

### Run Tests
```bash
cd monitoring-web
pytest

# With coverage
pytest --cov=app tests/

# Verbose output
pytest -v tests/test_main.py
```

### Test Coverage
```bash
pytest --cov=app --cov-report=html tests/
# Open htmlcov/index.html in browser
```

## 🔒 Security Features

- [x] API Key authentication
- [x] HTTPS/TLS ready
- [x] CSRF protection setup
- [x] Secure session cookies
- [x] Input validation
- [ ] Entra ID OAuth2/OIDC (planned)
- [ ] Rate limiting (planned)
- [ ] Audit logging (planned)

## 📈 Performance

- Configurable cache strategies
- Efficient API calls with timeout handling
- Client-side rendering with Chart.js
- Responsive design optimization
- Connection pooling for database

## 🐛 Troubleshooting

### Backend Connection Failed
```bash
# Check if backend is running
curl http://localhost:5000/api/v1/health/status

# Check environment variables
echo $API_BASE_URL
echo $API_KEY

# Verify network connectivity
docker network inspect cs3s2_monitoring
```

### No Data Showing
- Verify API_KEY matches in both frontend and backend
- Check if monitoring client is collecting data
- Inspect browser console for errors (F12)
- Check Docker logs: `docker-compose logs monitoring-api`

### Port Already in Use
```bash
# Change ports in docker-compose.yml or use:
docker-compose -p myproject up -d
```

## 📚 Documentation

- [Frontend README](./monitoring-web/README.md)
- [Backend README](./monitoring-api/README.md)
- [Client README](./monitoring-client/README.md)
- [Project Plan](./CS3S2_PlanningOverview-Summary_FernandoRodriguez.md)

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Commit: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Create Pull Request

## 📝 License

© 2024 The Knowledge Hub - All rights reserved

## 📞 Support

For issues or questions:
1. Check existing documentation
2. Review troubleshooting section
3. Contact development team

## 🗺️ Roadmap

- [ ] Week 1: Analysis, Design, Foundation ✓ (In Progress)
  - [x] Project Planning & Requirements Analysis
  - [x] Web Frontend Development (Task 2) ⭐ NEW
  - [x] Research & Architecture Design
- [ ] Week 2: Containerization, CI/CD Setup
  - [ ] Secure Authentication (Entra ID)
  - [ ] Application Containerization
  - [ ] CI/CD Pipeline - GitHub Actions
  - [ ] DNS Security Analysis
- [ ] Week 3: Deployment, Security, Monitoring
  - [ ] CI/CD Pipeline - Deployment
  - [ ] Container Platform Monitoring
  - [ ] Cloud Security Hardening (ZTA)
  - [ ] Network Enhancements
  - [ ] Service Resilience & Backup
- [ ] Week 4: Testing, Documentation, Presentation
  - [ ] Final Integration & Testing
  - [ ] Documentation Set
  - [ ] Presentation & Reflection

See [Project Plan](./CS3S2_PlanningOverview-Summary_FernandoRodriguez.md) for detailed timeline.

## ✨ What's New (v2.0)

This version includes the improved **monitoring-web** frontend application featuring:

- Modern Flask application factory pattern
- RESTful AJAX API endpoints for real-time data
- Bootstrap 5 responsive UI with professional styling
- Interactive dashboards with Chart.js visualizations
- Modular service architecture (API client, data processor)
- Comprehensive error handling and logging
- Full test coverage with pytest
- Docker containerization ready
- Environment-based configuration
- Production-ready deployment setup

The web frontend connects to the existing backend API and provides a user-friendly interface for monitoring the hybrid infrastructure without requiring CLI or direct server access (REQ-S2P3-001).
