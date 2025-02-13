from typing import Callable, Optional, Dict, Any, Union
import logging
import json
import smtplib
from email.message import EmailMessage
import requests
from functools import wraps

logger = logging.getLogger(__name__)

def validate_handler(func: Callable) -> Callable:
    """Decorator to validate alert handler signature."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        handler = args[1] if len(args) > 1 else kwargs.get('handler')
        if not callable(handler):
            raise ValueError("Handler must be callable")
        # Validate handler signature
        try:
            from inspect import signature
            sig = signature(handler)
            if len(sig.parameters) != 2:
                raise ValueError("Handler must accept exactly 2 parameters (message, context)")
        except Exception as e:
            raise ValueError(f"Invalid handler signature: {str(e)}")
        return func(*args, **kwargs)
    return wrapper

class AlertHook:
    """
    Hook for handling alerts and notifications.
    """
    
    @validate_handler
    def __init__(self, handler: Callable[[str, Dict[str, Any]], None]):
        """
        Initialize alert hook with custom handler.
        
        Args:
            handler: Callable that processes alerts
        """
        self.handler = handler
    
    @validate_handler
    def update_handler(self, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Update the alert handler.
        
        Args:
            handler: New handler callable
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

def email_alert_handler(
    smtp_host: str,
    smtp_port: int,
    sender: str,
    password: str,
    recipients: Union[str, list]
) -> Callable:
    """
    Create an email alert handler.
    
    Args:
        smtp_host: SMTP server host
        smtp_port: SMTP server port
        sender: Sender email address
        password: Sender email password
        recipients: Single recipient or list of recipients
    """
    if isinstance(recipients, str):
        recipients = [recipients]

    def handler(message: str, context: Dict[str, Any]) -> None:
        msg = EmailMessage()
        msg.set_content(f"{message}\n\nContext:\n{json.dumps(context, indent=2)}")
        msg['Subject'] = 'Pipeline Monitor Alert'
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")

    return handler

def slack_alert_handler(webhook_url: str) -> Callable:
    """
    Create a Slack alert handler.
    
    Args:
        webhook_url: Slack webhook URL
    """
    def handler(message: str, context: Dict[str, Any]) -> None:
        payload = {
            "text": f"*Alert*: {message}\n```{json.dumps(context, indent=2)}```"
        }
        try:
            response = requests.post(webhook_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {str(e)}")

    return handler

def sms_alert_handler(
    provider_url: str,
    api_key: str,
    sender_number: str,
    recipient_numbers: Union[str, list]
) -> Callable:
    """
    Create an SMS alert handler.
    
    Args:
        provider_url: SMS provider API URL
        api_key: API key for authentication
        sender_number: Sender phone number
        recipient_numbers: Single recipient or list of recipient phone numbers
    """
    if isinstance(recipient_numbers, str):
        recipient_numbers = [recipient_numbers]

    def handler(message: str, context: Dict[str, Any]) -> None:
        payload = {
            "api_key": api_key,
            "sender": sender_number,
            "recipients": recipient_numbers,
            "message": message
        }
        try:
            response = requests.post(provider_url, json=payload)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send SMS alert: {str(e)}")

    return handler
