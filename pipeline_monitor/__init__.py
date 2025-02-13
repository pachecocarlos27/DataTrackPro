"""
Pipeline Monitor - A library for monitoring data pipelines with automatic metrics collection and logging.
"""

from .decorators import track_performance  # Provides a decorator to track function performance
from .context import ResourceMonitor  # Context manager for monitoring resource usage
from .logging_utils import setup_logging  # Utility to set up logging configuration
from .alerts import setup_alerts, log_alert_handler  # Functions to set up alerts and log alert handler
from .config import Configuration  # Configuration management for pipeline monitoring
from .dashboard import start_dashboard  # Function to start the monitoring dashboard

# Create aliases for better readability
monitor = track_performance
MonitoringBlock = ResourceMonitor

__version__ = "0.2.0"
__all__ = [
    'track_performance',
    'ResourceMonitor',
    'Configuration',
    'setup_alerts',
    'log_alert_handler',
    'setup_logging',
    'start_dashboard'
]
