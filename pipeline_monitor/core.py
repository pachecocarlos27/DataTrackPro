"""Core functionality for Pipeline Monitor."""

from .context import ResourceMonitor
from .decorators import track_performance
from .alerts import setup_alerts, log_alert_handler
from .config import Configuration

class PipelineMonitor:
    def __init__(self, config=None):
        self.active = True
        self.config = config or Configuration()
        self.alert_hook = setup_alerts(log_alert_handler)
        
    def resource_monitor(self, name):
        """Create a resource monitoring context."""
        return ResourceMonitor(name)
        
    def track(self, func):
        """Decorator to track function performance."""
        return track_performance(func)
        
    def alert(self, message, data=None):
        """Send an alert."""
        if self.active:
            self.alert_hook.alert(message, data)
        
    def stop(self):
        """Stop the monitor."""
        self.active = False 