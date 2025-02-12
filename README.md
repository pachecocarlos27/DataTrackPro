# Pipeline Monitor

A Python library for advanced data pipeline monitoring with comprehensive observability and visualization capabilities.

## Features

- Automatic performance tracking using decorators and context managers
- Real-time interactive web dashboard with live metrics and WebSocket updates
- JSON-structured logging with detailed execution insights
- Integrated monitoring for ETL and machine learning pipelines
- Built-in alerting and performance tracking
- Extensible design supporting multiple observability integrations

## Installation

```bash
pip install pipeline-monitor
```

## Quick Start

```python
from pipeline_monitor import monitor, MonitoringBlock

# Decorate functions for automatic monitoring
@monitor
def process_data():
    # Your data processing code here
    pass

# Use context manager for block monitoring
with MonitoringBlock("data_processing"):
    process_data()
```

## Documentation

For detailed documentation and examples, visit our [documentation](https://github.com/replit/pipeline-monitor/docs).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
