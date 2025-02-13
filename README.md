# Pipeline Monitor

A comprehensive monitoring solution for Python data pipelines.

## Features

- Performance tracking with decorators and context managers
- Memory usage monitoring
- Automatic alerting (Slack, Email, Logs)
- Real-time dashboard
- Prometheus metrics integration
- JSON logging

## Installation

```bash
pip install pipeline-monitor
```

## Quick Start

```python
from pipeline_monitor import track_performance, ResourceMonitor

# Monitor function performance
@track_performance(alert_threshold=30, memory_threshold=500)
def process_data():
    pass

# Monitor code blocks
with ResourceMonitor("data_processing", alert_threshold_mb=1000):
    pass
```

## Configuration

Create a `config.json` file:

```json
{
    "alerts": {
        "time_threshold": 300,
        "memory_threshold": 1000,
        "slack_webhook": "https://hooks.slack.com/...",
        "email": {
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "sender": "alerts@company.com",
            "password": "secret",
            "recipients": ["team@company.com"]
        }
    }
}
```

## Tools

```bash
# Start monitoring dashboard
pipeline-dashboard

# Run demo pipeline
pipeline-demo

# Start Prometheus metrics
pipeline-prometheus

# Test alerts configuration
pipeline-test-alerts config.json
```

## Tutorials and Examples

Check out our interactive tutorials in the `examples/notebooks` directory:

1. `01_basic_usage.ipynb` - Getting started with performance tracking
2. `02_dashboard_monitoring.ipynb` - Real-time dashboard monitoring

To run the tutorials:

1. Install Jupyter:
```bash
pip install jupyter
```

2. Start Jupyter:
```bash
jupyter notebook examples/notebooks/