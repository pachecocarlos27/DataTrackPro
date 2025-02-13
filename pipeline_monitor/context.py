import time
import psutil
import logging
from typing import Optional, Any
import json
from contextlib import ContextDecorator
from .dashboard.app import emit_metric
from .alerts import setup_alerts, log_alert_handler, sms_alert_handler
from .config import Configuration

logger = logging.getLogger(__name__)

class ResourceMonitor(ContextDecorator):
    """
    Context manager for monitoring resource usage during execution.
    """

    def __init__(self, name: str, alert_threshold_mb: Optional[float] = None, config_path: Optional[str] = None):
        """
        Initialize the resource monitor.

        Args:
            name: Name of the monitored block
            alert_threshold_mb: Memory threshold in MB to trigger alerts
            config_path: Optional path to configuration file
        """
        self.name = name
        self.config = Configuration.from_file(config_path) if config_path else Configuration()
        self.alert_threshold_mb = alert_threshold_mb or self.config.get('alerts', {}).get('memory_threshold')
        self.start_time: float = 0.0
        self.start_memory: float = 0.0
        self.process = psutil.Process()
        
        # Setup alert handler based on configuration
        alert_config = self.config.get('alerts', {})
        if alert_config.get('slack_webhook'):
            from .alerts import slack_alert_handler
            handler = slack_alert_handler(alert_config['slack_webhook'])
        elif alert_config.get('email'):
            from .alerts import email_alert_handler
            email_cfg = alert_config['email']
            handler = email_alert_handler(
                smtp_host=email_cfg['smtp_host'],
                smtp_port=email_cfg['smtp_port'],
                sender=email_cfg['sender'],
                password=email_cfg['password'],
                recipients=email_cfg['recipients']
            )
        elif alert_config.get('sms'):
            sms_cfg = alert_config['sms']
            handler = sms_alert_handler(
                provider_url=sms_cfg['provider_url'],
                api_key=sms_cfg['api_key'],
                sender_number=sms_cfg['sender_number'],
                recipient_numbers=sms_cfg['recipient_numbers']
            )
        else:
            handler = log_alert_handler
            
        self.alert_hook = setup_alerts(handler)

    def __enter__(self) -> 'ResourceMonitor':
        """Start monitoring the block."""
        try:
            self.start_time = time.time()
            self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
            logger.info(f"Starting monitoring block: {self.name}")
        except Exception as e:
            logger.error(f"Error starting monitoring block: {str(e)}")
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any) -> None:
        """
        Stop monitoring and record metrics.

        Args:
            exc_type: Type of exception if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        try:
            end_time = time.time()
            end_memory = self.process.memory_info().rss / 1024 / 1024  # MB

            execution_time = end_time - self.start_time
            memory_used = end_memory - self.start_memory

            metrics = {
                'block_name': self.name,
                'execution_time': execution_time,
                'memory_usage_mb': memory_used,
                'success': exc_type is None,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            if exc_type is not None:
                metrics['error_type'] = exc_type.__name__
                metrics['error_message'] = str(exc_val)

            logger.info(json.dumps(metrics))

            # Emit metrics to dashboard
            emit_metric('performance', {
                'active_pipelines': 1,
                'execution_time': execution_time
            })

            emit_metric('memory', {
                'rss_mb': end_memory,
                'memory_used_mb': memory_used
            })

            if self.alert_threshold_mb and memory_used > self.alert_threshold_mb:
                alert_msg = (
                    f"Block {self.name} exceeded memory threshold: "
                    f"{memory_used:.2f}MB > {self.alert_threshold_mb}MB"
                )
                logger.warning(alert_msg)
                emit_metric('alert', {'message': alert_msg})
                
                # Send alert through configured handler
                self.alert_hook.alert(alert_msg, {
                    'block_name': self.name,
                    'memory_used_mb': memory_used,
                    'threshold_mb': self.alert_threshold_mb,
                    'metrics': metrics
                })

        except Exception as e:
            logger.error(f"Error in monitoring exit: {str(e)}")
