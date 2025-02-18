"""
Prometheus metrics integration for pipeline monitoring.
"""
from prometheus_client import Counter, Gauge, Histogram, CollectorRegistry
from typing import Dict, Any
import threading
import time

# Create a custom registry for our metrics
REGISTRY = CollectorRegistry()

# Define metrics
PIPELINE_RUNS = Counter(
    'pipeline_runs_total',
    'Total number of pipeline executions',
    ['pipeline_name', 'status'],
    registry=REGISTRY
)

PIPELINE_DURATION = Histogram(
    'pipeline_duration_seconds',
    'Pipeline execution duration in seconds',
    ['pipeline_name'],
    registry=REGISTRY
)

MEMORY_USAGE = Gauge(
    'pipeline_memory_usage_bytes',
    'Current memory usage in bytes',
    ['pipeline_name'],
    registry=REGISTRY
)

ACTIVE_PIPELINES = Gauge(
    'active_pipelines',
    'Number of currently active pipelines',
    registry=REGISTRY
)

# Thread-local storage for timing
_local = threading.local()

def start_pipeline_timing() -> None:
    """Start timing a pipeline execution."""
    _local.start_time = time.time()

def stop_pipeline_timing(pipeline_name: str) -> None:
    """Stop timing a pipeline execution and record the duration."""
    if hasattr(_local, 'start_time'):
        duration = time.time() - _local.start_time
        PIPELINE_DURATION.labels(pipeline_name=pipeline_name).observe(duration)
        del _local.start_time

def record_pipeline_run(pipeline_name: str, success: bool) -> None:
    """Record a pipeline execution."""
    PIPELINE_RUNS.labels(
        pipeline_name=pipeline_name, 
        status='success' if success else 'failure'
    ).inc()

def update_memory_usage(pipeline_name: str, memory_bytes: float) -> None:
    """Update memory usage metrics."""
    MEMORY_USAGE.labels(pipeline_name=pipeline_name).set(memory_bytes)

    # Send SMS alert if memory usage exceeds threshold
    from .alerts import sms_alert_handler
    from .config import Configuration

    config = Configuration.from_file("examples/config.json")
    sms_cfg = config.get('alerts', {}).get('sms', {})
    if sms_cfg:
        handler = sms_alert_handler(
            provider_url=sms_cfg['provider_url'],
            api_key=sms_cfg['api_key'],
            sender_number=sms_cfg['sender_number'],
            recipient_numbers=sms_cfg['recipient_numbers']
        )
        alert_msg = (
            f"Memory usage ({memory_bytes / 1024 / 1024:.2f}MB) "
            f"exceeded threshold"
        )
        handler(alert_msg, {
            'memory_usage_bytes': memory_bytes
        })

def update_active_pipelines(count: int) -> None:
    """Update the number of active pipelines."""
    ACTIVE_PIPELINES.set(count)
