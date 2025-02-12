"""
Pipeline Monitor - A library for monitoring data pipelines with automatic metrics collection and logging.
"""

from .decorators import track_performance
from .context import ResourceMonitor
from .logging_utils import setup_logging
from .alerts import setup_alerts, AlertHook
from .config import Configuration

__version__ = "0.1.0"
__all__ = ['track_performance', 'ResourceMonitor', 'setup_logging', 'setup_alerts', 'AlertHook', 'Configuration']
