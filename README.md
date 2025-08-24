# DataTrackPro

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/pachecocarlos27/DataTrackPro)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Python-based data tracking and analytics platform designed for real-time monitoring, analysis, and visualization of business metrics and KPIs.

## 🌟 Features

- **📊 Real-Time Analytics**: Live data tracking with minimal latency
- **📈 Interactive Dashboards**: Customizable visualization dashboards
- **🔔 Smart Alerts**: Configurable alerts for anomaly detection
- **📁 Multiple Data Sources**: Support for databases, APIs, and file systems
- **🔄 Automated Reports**: Schedule and generate reports automatically
- **🔐 Role-Based Access**: Secure multi-user environment with permissions
- **📱 Responsive Design**: Mobile-friendly web interface
- **🚀 High Performance**: Optimized for handling large datasets

## 🖼️ Screenshots

<div align="center">
  <img src="docs/images/dashboard.png" alt="Dashboard Screenshot" width="600"/>
  <p><em>Main Analytics Dashboard</em></p>
</div>

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Architecture](#-architecture)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/pachecocarlos27/DataTrackPro.git
cd DataTrackPro

# Build and run with Docker Compose
docker-compose up -d
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/pachecocarlos27/DataTrackPro.git
cd DataTrackPro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up the database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run the server
python manage.py runserver
```

## 🏃 Quick Start

```python
from datatrackpro import DataTracker
from datatrackpro.sources import PostgreSQLSource
from datatrackpro.metrics import Metric, AggregationType

# Initialize DataTrackPro
tracker = DataTracker()

# Add a data source
postgres_source = PostgreSQLSource(
    host="localhost",
    database="analytics",
    user="user",
    password="password"
)
tracker.add_source("main_db", postgres_source)

# Define a metric
sales_metric = Metric(
    name="daily_sales",
    source="main_db",
    query="SELECT date, SUM(amount) as total FROM sales GROUP BY date",
    aggregation=AggregationType.SUM,
    refresh_interval=300  # 5 minutes
)

# Add metric to tracker
tracker.add_metric(sales_metric)

# Start tracking
tracker.start()
```

## 🏗️ Architecture

```
DataTrackPro/
├── core/                 # Core tracking engine
│   ├── tracker.py       # Main tracker class
│   ├── metrics.py       # Metric definitions
│   └── scheduler.py     # Job scheduling
├── sources/             # Data source connectors
│   ├── base.py         # Base source class
│   ├── postgresql.py   # PostgreSQL connector
│   └── api.py          # REST API connector
├── visualizations/      # Dashboard components
│   ├── charts.py       # Chart generators
│   └── dashboards.py   # Dashboard builder
├── api/                # REST API
│   ├── views.py       # API endpoints
│   └── serializers.py # Data serializers
└── web/               # Web interface
    ├── static/        # CSS, JS, images
    └── templates/     # HTML templates
```

## 📚 Usage

### Creating Custom Metrics

```python
from datatrackpro.metrics import Metric, MetricType

# Time series metric
revenue_metric = Metric(
    name="monthly_revenue",
    metric_type=MetricType.TIME_SERIES,
    source="financial_db",
    query="""
        SELECT 
            DATE_TRUNC('month', created_at) as month,
            SUM(amount) as revenue
        FROM transactions
        WHERE status = 'completed'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """,
    visualization="line_chart"
)

# Gauge metric
active_users = Metric(
    name="active_users",
    metric_type=MetricType.GAUGE,
    source="app_db",
    query="SELECT COUNT(DISTINCT user_id) FROM sessions WHERE last_seen > NOW() - INTERVAL '5 minutes'",
    visualization="gauge",
    thresholds={
        "critical": 100,
        "warning": 500,
        "normal": 1000
    }
)
```

### Building Dashboards

```python
from datatrackpro.dashboards import Dashboard, Layout

# Create a dashboard
sales_dashboard = Dashboard(
    name="Sales Overview",
    layout=Layout.GRID,
    refresh_rate=60  # seconds
)

# Add widgets
sales_dashboard.add_widget(
    metric="daily_sales",
    position=(0, 0),
    size=(6, 4),
    title="Daily Sales Trend"
)

sales_dashboard.add_widget(
    metric="conversion_rate",
    position=(6, 0),
    size=(6, 4),
    title="Conversion Rate"
)

# Save dashboard
sales_dashboard.save()
```

### Setting Up Alerts

```python
from datatrackpro.alerts import Alert, AlertCondition

# Create alert
low_stock_alert = Alert(
    name="Low Stock Alert",
    metric="inventory_count",
    condition=AlertCondition.LESS_THAN,
    threshold=100,
    recipients=["inventory@company.com"],
    message="Stock level for {product_name} is below threshold: {current_value}"
)

# Add to tracker
tracker.add_alert(low_stock_alert)
```

## 📖 API Documentation

### REST API Endpoints

#### Metrics
- `GET /api/metrics/` - List all metrics
- `POST /api/metrics/` - Create new metric
- `GET /api/metrics/{id}/` - Get metric details
- `GET /api/metrics/{id}/data/` - Get metric data
- `PUT /api/metrics/{id}/` - Update metric
- `DELETE /api/metrics/{id}/` - Delete metric

#### Dashboards
- `GET /api/dashboards/` - List all dashboards
- `POST /api/dashboards/` - Create new dashboard
- `GET /api/dashboards/{id}/` - Get dashboard
- `PUT /api/dashboards/{id}/` - Update dashboard

#### Example Request

```bash
# Get metric data
curl -X GET https://your-domain.com/api/metrics/daily_sales/data/ \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json"
```

## ⚙️ Configuration

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/datatrackpro

# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for alerts)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-password

# API
API_RATE_LIMIT=1000
API_RATE_PERIOD=3600
```

### Advanced Configuration

```python
# config.py
DATATRACKPRO_CONFIG = {
    'CACHE_TTL': 300,  # 5 minutes
    'MAX_WORKERS': 10,
    'BATCH_SIZE': 1000,
    'LOG_LEVEL': 'INFO',
    'TIMEZONE': 'UTC',
    'DATE_FORMAT': '%Y-%m-%d',
    'DECIMAL_PLACES': 2,
}
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=datatrackpro tests/

# Run specific test file
pytest tests/test_metrics.py

# Run integration tests
pytest tests/integration/
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Django and Django REST Framework
- Charts powered by Chart.js and D3.js
- Real-time updates using WebSockets
- Deployed on AWS/Docker

## 📞 Support

- 📧 Email: support@datatrackpro.com
- 📖 Documentation: [docs.datatrackpro.com](https://docs.datatrackpro.com)
- 💬 Community: [Discord Server](https://discord.gg/datatrackpro)
- 🐛 Issues: [GitHub Issues](https://github.com/pachecocarlos27/DataTrackPro/issues)

---

<div align="center">
  <strong>DataTrackPro</strong> - Transform your data into insights
  <br>
  Made with ❤️ by <a href="https://github.com/pachecocarlos27">Carlos Pacheco</a>
</div>
