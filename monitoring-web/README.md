# Monitoring Web Frontend

A modern Flask-based web application for monitoring hybrid cloud infrastructure across on-premises servers (GNS3), Azure PaaS services, and containerized applications.

## Features

- **Real-time Dashboards**: Interactive monitoring dashboards with live metrics
- **Multi-host Monitoring**: Monitor metrics from multiple on-premises and cloud hosts
- **Secure API Communication**: API key-based authentication with the backend
- **Historical Data & Trends**: Track metrics over time with visual charts
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Entra ID Ready**: Prepared for Azure Entra ID integration
- **RESTful API**: Backend connection via REST API

## Architecture

```
┌─────────────────────┐
│  Web Browser        │
│  (Bootstrap UI)     │
└──────────┬──────────┘
           │ HTTP/HTTPS
           ▼
┌─────────────────────────────────┐
│  Flask Web Frontend              │
│  - Dashboard                    │
│  - Metrics View                 │
│  - Host Details                 │
└──────────┬──────────────────────┘
           │ REST API (HTTP)
           ▼
┌─────────────────────────────────┐
│  Monitoring Backend API         │
│  - Metrics Endpoint             │
│  - Health Endpoint              │
└──────────┬──────────────────────┘
           │
           ▼
      ┌──────────────┐
      │  Azure SQL   │
      │  Database    │
      └──────────────┘
```

## Prerequisites

- Python 3.9+
- pip or conda
- Backend API running (see backend documentation)
- `.env` file configured with API credentials

## Installation

### 1. Clone the repository
```bash
cd monitoring-web
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
# Important: Set API_BASE_URL and API_KEY to match your backend
```

### 5. Run development server
```bash
flask run
```

The application will be available at `http://localhost:5001`

## Configuration

### Environment Variables

```env
# Flask
FLASK_ENV=development                    # development, production, or testing
FLASK_DEBUG=true                        # Enable debug mode
SECRET_KEY=your-secret-key              # Session key

# Backend API
API_BASE_URL=http://localhost:5000/api/v1
API_KEY=your-api-key-here
API_TIMEOUT=10                          # Request timeout in seconds

# Refresh intervals
METRICS_REFRESH_INTERVAL=30              # Dashboard auto-refresh
HEALTH_REFRESH_INTERVAL=60

# Server
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Authentication (future)
AUTH_ENABLED=false
ENTRA_ID_CLIENT_ID=
ENTRA_ID_CLIENT_SECRET=
ENTRA_ID_TENANT_ID=
```

## Project Structure

```
monitoring-web/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration management
│   ├── routes/                  # Flask blueprints
│   │   ├── main.py             # Home, about, health routes
│   │   ├── dashboard.py        # Dashboard views
│   │   └── api.py              # AJAX API endpoints
│   ├── services/               # Business logic
│   │   ├── api_client.py       # Backend API client
│   │   └── data_processor.py   # Data aggregation/processing
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html          # Base template
│   │   ├── index.html         # Home page
│   │   ├── about.html         # About page
│   │   └── dashboard/         # Dashboard templates
│   │       ├── overview.html
│   │       ├── metrics.html
│   │       └── host_details.html
│   └── static/                # Static files
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
├── tests/                      # Test files
├── wsgi.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Running with Docker

### Build image
```bash
docker build -t monitoring-web:latest .
```

### Run container
```bash
docker run -d \
  -p 5001:5001 \
  -e API_BASE_URL=http://monitoring-api:5000/api/v1 \
  -e API_KEY=your-api-key \
  --name monitoring-web \
  monitoring-web:latest
```

## Docker Compose

See `docker-compose.yml` in the root directory to run both frontend and backend together.

## Usage

### Home Page
- Overview of the monitoring system
- Quick access to dashboard
- System status indicator

### Dashboard
- **Overview**: High-level metrics summary, host status
- **Metrics**: Detailed metrics view with filtering
- **Host Details**: Detailed information for a specific host with charts

### Features

- **Real-time Updates**: Dashboard auto-refreshes every 30 seconds
- **Filtering**: Filter metrics by host or metric type
- **Host Drill-down**: Click on any host to see detailed metrics
- **Chart Visualization**: Visual representation of metric trends
- **Status Indicators**: Color-coded status (OK, WARNING, CRITICAL)

## Testing

### Run tests
```bash
pytest

# With coverage
pytest --cov=app tests/
```

### Run specific test
```bash
pytest tests/test_main.py::test_index_page -v
```

## Development

### Hot Reload
Development server automatically reloads on code changes.

### Debugging
Use VS Code debugger or add breakpoints:
```python
import pdb; pdb.set_trace()
```

### Adding New Routes
1. Create blueprint in `app/routes/`
2. Register in `app/__init__.py`
3. Create templates in `app/templates/`

### Adding New API Client Methods
Extend `APIClient` class in `app/services/api_client.py`

## Production Deployment

### Using Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app
```

### Using Docker
```bash
docker run -d -p 5001:5001 --env-file .env monitoring-web:latest
```

### Security Considerations
- [ ] Set `FLASK_DEBUG=false` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Enable `SESSION_COOKIE_SECURE=true` (HTTPS only)
- [ ] Implement Entra ID authentication
- [ ] Use HTTPS/TLS
- [ ] Restrict API access with firewalls
- [ ] Implement rate limiting
- [ ] Add CSRF protection

## Troubleshooting

### Backend Connection Failed
- Verify `API_BASE_URL` is correct
- Check `API_KEY` matches backend configuration
- Ensure backend API is running and accessible
- Check firewall rules

### Templates Not Found
- Ensure `app/templates/` directory exists
- Clear Flask cache: `rm -rf __pycache__ .flask_cache`

### Static Files Not Loading
- Run `flask collect-static` (if using static file collection)
- Check `app/static/` permissions
- Verify paths in templates

## Security Features

- [x] API Key authentication with backend
- [x] CSRF protection via Flask-WTF (optional)
- [x] Secure session cookies (HTTPONLY, SECURE)
- [x] SQL injection protection (ORM-safe)
- [ ] Entra ID authentication (planned)
- [ ] Rate limiting (planned)
- [ ] Input validation (in progress)

## Performance

- Configurable cache strategies
- Lightweight API calls
- Efficient database queries (via backend)
- Client-side rendering with Chart.js
- Responsive design optimization

## Future Enhancements

- [ ] Entra ID/OIDC authentication
- [ ] Real-time WebSocket updates
- [ ] Alert management UI
- [ ] Custom dashboard widgets
- [ ] Dark mode theme
- [ ] Mobile app
- [ ] Advanced analytics
- [ ] Scheduled reports

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/my-feature`
4. Create Pull Request

## License

© 2024 The Knowledge Hub - All rights reserved

## Support

For issues or questions, contact the development team.

## Changelog

### Version 2.0
- Modern Flask application factory pattern
- RESTful API design
- Bootstrap-based responsive UI
- Chart.js data visualization
- Modular service architecture
- Comprehensive error handling
- Test coverage

### Version 1.0
- Initial release
- Basic dashboard
- Metrics display
