# 🚀 Quick Start Guide - Monitoring Web Frontend

## What Was Created

A **modern Flask web application** for monitoring your hybrid cloud infrastructure with:

- 🎨 **Beautiful Dashboard** - Real-time metrics visualization
- 📊 **Interactive Charts** - Trend analysis with Chart.js
- 🔐 **Secure API** - Integration with monitoring backend
- 📱 **Responsive Design** - Works on desktop, tablet, mobile
- 🐳 **Docker Ready** - Easy containerization and deployment

## File Structure

```
monitoring-web/
├── app/
│   ├── __init__.py              ← Application factory
│   ├── config.py                ← Environment configuration
│   ├── routes/
│   │   ├── main.py             ← Home, about pages
│   │   ├── dashboard.py        ← Dashboard views
│   │   └── api.py              ← AJAX endpoints
│   ├── services/
│   │   ├── api_client.py       ← Backend API client
│   │   └── data_processor.py   ← Data processing
│   ├── templates/              ← HTML templates (Jinja2 + Bootstrap 5)
│   └── static/                 ← CSS & JavaScript
├── tests/                       ← Unit tests (pytest)
├── wsgi.py                      ← Entry point for Gunicorn
├── requirements.txt             ← Python dependencies
├── .env.example                 ← Configuration template
├── Dockerfile                   ← Container image
└── README.md                    ← Full documentation
```

## 📋 Quick Start (Local Development)

### 1. Prerequisites
```bash
# Ensure you have Python 3.9+
python --version

# Ensure the backend API is running
curl http://localhost:5000/api/v1/health/status
```

### 2. Create Virtual Environment
```bash
cd monitoring-web

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env to match your backend
nano .env
# Edit these lines:
# API_BASE_URL=http://localhost:5000/api/v1
# API_KEY=your-api-key-here
```

### 5. Run Development Server
```bash
flask run --port 5001
```

✅ **Now open:** http://localhost:5001

## 🐳 Quick Start (Docker)

### Option 1: Using Docker Compose (Recommended)
```bash
# From the root project directory
docker-compose up -d

# View logs
docker-compose logs -f monitoring-web
```

Access at: http://localhost:5001

### Option 2: Manual Docker
```bash
# Build image
docker build -t monitoring-web:latest .

# Run container
docker run -d \
  -p 5001:5001 \
  -e API_BASE_URL=http://host.docker.internal:5000/api/v1 \
  -e API_KEY=your-api-key \
  --name monitoring-web \
  monitoring-web:latest

# View logs
docker logs -f monitoring-web
```

## 📊 Dashboard Pages

### 🏠 Home Page (`/`)
- System overview
- Quick stats cards
- Features list
- System status check

### 📈 Dashboard Overview (`/dashboard/`)
- Total metrics count
- Monitored hosts
- Status summary (OK / WARNING / CRITICAL)
- Recent metrics table
- Auto-refresh (30 seconds)

### 📋 Metrics View (`/dashboard/metrics`)
- Detailed metrics list
- Filter by host
- Filter by metric type
- Sortable table
- Pagination

### 🖥️ Host Details (`/dashboard/host/<hostname>`)
- Host-specific metrics
- Metric statistics (avg, min, max)
- Interactive charts (Chart.js)
- Metric history
- Grouped by metric type

## 🔧 Configuration Options

### Environment Variables (`.env`)

```env
# Flask Settings
FLASK_ENV=development              # development, production, testing
FLASK_DEBUG=true                  # Enable debug mode (false in prod)
SECRET_KEY=your-secret-key        # Session encryption key

# Backend API
API_BASE_URL=http://localhost:5000/api/v1
API_KEY=your-api-key-here
API_TIMEOUT=10                    # Request timeout (seconds)

# Auto-Refresh
METRICS_REFRESH_INTERVAL=30       # Dashboard refresh (seconds)
HEALTH_REFRESH_INTERVAL=60        # Health check (seconds)

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Authentication (for future use)
AUTH_ENABLED=false
ENTRA_ID_CLIENT_ID=
ENTRA_ID_CLIENT_SECRET=
ENTRA_ID_TENANT_ID=
```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage
pytest --cov=app tests/

# Generate HTML coverage report
pytest --cov=app --cov-report=html tests/
# Open: htmlcov/index.html
```

## 🔍 Troubleshooting

### Backend Connection Failed
```bash
# Check if backend is running
curl http://localhost:5000/api/v1/health/status

# Check environment variables
echo $API_BASE_URL
echo $API_KEY

# Check logs
docker-compose logs monitoring-api
```

### No Metrics Showing
- Ensure backend API has data in database
- Check API_KEY matches in both frontend and backend
- Look at browser console (F12 → Console tab)
- Check application logs: `docker-compose logs monitoring-web`

### Port Already in Use
```bash
# Find process using port 5001
lsof -i :5001  # Linux/Mac
netstat -ano | findstr :5001  # Windows

# Kill process or change port in .env
FLASK_PORT=5002
```

### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## 📚 Key Features Explained

### Real-time Dashboards
- Auto-refreshes every 30 seconds
- Shows latest metrics from backend
- Click "Refresh" button for immediate update

### Multi-host Monitoring
- Monitors multiple on-premises and cloud hosts
- Color-coded status: 🟢 OK, 🟡 WARNING, 🔴 CRITICAL
- Click host name to see detailed metrics

### Data Filtering
- Filter metrics by host in dropdown
- Filter by metric type (CPU, Memory, etc.)
- Click "Apply Filters" to search

### Interactive Charts
- Visualize metric trends over time
- Shows last 20 data points
- Automatically calculates min/max/average

### Secure API Communication
- Uses API key authentication
- Timeout handling for failed requests
- Error messages for troubleshooting

## 🚀 Deployment

### Production Checklist
- [ ] Change `FLASK_DEBUG=false`
- [ ] Set strong `SECRET_KEY`
- [ ] Configure HTTPS/TLS
- [ ] Set `SESSION_COOKIE_SECURE=true`
- [ ] Update `API_BASE_URL` to production
- [ ] Implement Entra ID authentication
- [ ] Add rate limiting
- [ ] Enable logging to file

### Using Gunicorn
```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app

# Run in background with logging
gunicorn -w 4 -b 0.0.0.0:5001 \
  --access-logfile access.log \
  --error-logfile error.log \
  --daemon \
  wsgi:app
```

### Using Nginx Reverse Proxy
```nginx
upstream monitoring_web {
    server 127.0.0.1:5001;
}

server {
    listen 80;
    server_name monitoring.example.com;
    
    location / {
        proxy_pass http://monitoring_web;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📖 Full Documentation

- **Frontend README**: `monitoring-web/README.md`
- **Backend README**: `monitoring-api/README.md`
- **Project Plan**: `CS3S2_PlanningOverview-Summary_FernandoRodriguez.md`

## 🆘 Getting Help

1. **Check logs**: `docker-compose logs monitoring-web`
2. **Browser console**: Press F12 in web browser
3. **API status**: Visit `/api/status`
4. **Health check**: Visit `/health`
5. **About page**: Visit `/about` for architecture info

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review full README in `monitoring-web/`
3. Check project documentation
4. Contact development team

---

**Happy Monitoring! 🎉**

For more information, see the [Full README](./README.md)
