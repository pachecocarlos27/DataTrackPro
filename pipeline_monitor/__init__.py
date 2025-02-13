"""
Pipeline Monitor - A library for monitoring data pipelines with automatic metrics collection and logging.
"""

from .decorators import track_performance
from .context import ResourceMonitor
from .logging_utils import setup_logging
from .alerts import setup_alerts, log_alert_handler
from .config import Configuration
from .dashboard import start_dashboard

# Create aliases for better readability
monitor = track_performance
MonitoringBlock = ResourceMonitor

__version__ = "0.1.0"
__all__ = [
    'track_performance',
    'ResourceMonitor',
    'Configuration',
    'setup_alerts',
    'log_alert_handler',
    'setup_logging',
    'start_dashboard'
]