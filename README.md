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