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

## Running the Tools

After installation, you can use the following commands:

1. Start the monitoring dashboard:
```bash
pipeline-dashboard
```

2. Run the demo pipeline:
```bash
pipeline-demo
```

3. Run with Prometheus metrics:
```bash
pipeline-prometheus