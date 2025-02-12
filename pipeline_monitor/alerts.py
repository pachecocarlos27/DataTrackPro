from typing import Callable, Optional, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class AlertHook:
    """
    Hook for handling alerts and notifications.
    """
    
    def __init__(self, handler: Callable[[str, Dict[str, Any]], None]):
        """
        Initialize alert hook with custom handler.
        
        Args:
            handler: Callable that processes alerts
        """
        self.handler = handler
    
    def alert(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Trigger an alert with given message and context.
        
        Args:
            message: Alert message
            context: Optional context dictionary
        """
        if context is None:
            context = {}
        
        try:
            self.handler(message, context)
        except Exception as e:
            logger.error(f"Failed to send alert: {str(e)}")

def setup_alerts(handler: Callable[[str, Dict[str, Any]], None]) -> AlertHook:
    """
    Setup alert system with custom handler.
    
    Args:
        handler: Callable that processes alerts
    
    Returns:
        Configured AlertHook instance
    """
    return AlertHook(handler)

# Example alert handlers
def log_alert_handler(message: str, context: Dict[str, Any]) -> None:
    """
    Simple handler that logs alerts to the logging system.
    """
    logger.warning(f"ALERT: {message}\nContext: {json.dumps(context)}")
