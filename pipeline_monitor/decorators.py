import time
import functools
import logging
import traceback
from typing import Callable, Any, Optional, TypeVar, Union, Dict, NamedTuple
import psutil
import json
from .dashboard.app import emit_metric
from .prometheus_metrics import (
    start_pipeline_timing, stop_pipeline_timing,
    record_pipeline_run, update_memory_usage,
    update_active_pipelines
)
from .alerts import setup_alerts, log_alert_handler, slack_alert_handler, email_alert_handler, sms_alert_handler
from .config import Configuration
from .logging_utils import JSONFormatter

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

class Metrics(NamedTuple):
    """Container for performance metrics."""
    function_name: str
    execution_time: float
    memory_used: float
    end_memory: int
    success: bool = True
    timestamp: str = time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return self._asdict()

class AlertConfig(NamedTuple):
    """Container for alert configuration."""
    time_threshold: Optional[float]
    mem_threshold: Optional[float]
    alert_hook: Any

def get_alert_handler(alert_config: Dict[str, Any]) -> Callable:
    """Get appropriate alert handler based on configuration."""
    if not alert_config:
        return log_alert_handler

    if webhook := alert_config.get('slack_webhook'):
        return slack_alert_handler(webhook)
    
    if email_cfg := alert_config.get('email'):
        return email_alert_handler(
            smtp_host=email_cfg['smtp_host'],
            smtp_port=email_cfg['smtp_port'],
            sender=email_cfg['sender'],
            password=email_cfg['password'],
            recipients=email_cfg['recipients']
        )
    
    if sms_cfg := alert_config.get('sms'):
        return sms_alert_handler(
            provider_url=sms_cfg['provider_url'],
            api_key=sms_cfg['api_key'],
            sender_number=sms_cfg['sender_number'],
            recipient_numbers=sms_cfg['recipient_numbers']
        )
    
    return log_alert_handler

def track_performance(
    alert_threshold: Optional[float] = None,
    memory_threshold: Optional[float] = None,
    config_path: Optional[str] = None
) -> Callable[[F], F]:
    """Decorator to track function performance metrics."""
    # Load configuration once when decorator is applied
    config = Configuration.from_file(config_path) if config_path else Configuration()
    alert_config = config.get('alerts', {})
    
    # Create alert configuration
    alert_cfg = AlertConfig(
        time_threshold=alert_threshold or alert_config.get('time_threshold'),
        mem_threshold=memory_threshold or alert_config.get('memory_threshold'),
        alert_hook=setup_alerts(get_alert_handler(alert_config))
    )

    def decorator(func: F) -> F:
        # Cache the process object
        process = psutil.Process()
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            start_memory = process.memory_info().rss
            start_pipeline_timing()

            try:
                result = func(*args, **kwargs)
                memory_info = process.memory_info()
                
                # Calculate metrics
                metrics = Metrics(
                    function_name=func.__name__,
                    execution_time=time.time() - start_time,
                    memory_used=(memory_info.rss - start_memory) / 1024 / 1024,
                    end_memory=memory_info.rss
                )

                # Update monitoring and check thresholds
                update_monitoring_systems(metrics)
                check_thresholds(metrics, alert_cfg)

                return result

            except Exception as e:
                handle_error(func.__name__, e, alert_cfg.alert_hook)
                raise

        return wrapper
    return decorator

def update_monitoring_systems(metrics: Metrics) -> None:
    """Update all monitoring systems with current metrics."""
    metrics_dict = metrics.to_dict()
    logger.info(json.dumps(metrics_dict))

    # Update Prometheus metrics
    stop_pipeline_timing(metrics.function_name)
    record_pipeline_run(metrics.function_name, True)
    update_memory_usage(metrics.function_name, metrics.end_memory)
    update_active_pipelines(1)

    # Emit metrics to dashboard
    emit_metric('performance', {
        'active_pipelines': 1,
        'execution_time': metrics.execution_time
    })
    emit_metric('memory', {
        'rss_mb': metrics.end_memory / 1024 / 1024,
        'memory_used_mb': metrics.memory_used
    })

def check_thresholds(metrics: Metrics, alert_cfg: AlertConfig) -> None:
    """Check time and memory thresholds and send alerts if exceeded."""
    if alert_cfg.time_threshold and metrics.execution_time > alert_cfg.time_threshold:
        alert_msg = (
            f"Function {metrics.function_name} exceeded time threshold: "
            f"{metrics.execution_time:.2f}s > {alert_cfg.time_threshold}s"
        )
        send_alert(alert_msg, {
            'function_name': metrics.function_name,
            'execution_time': metrics.execution_time,
            'threshold': alert_cfg.time_threshold,
            'metrics': metrics.to_dict()
        }, alert_cfg.alert_hook)

    if alert_cfg.mem_threshold and metrics.memory_used > alert_cfg.mem_threshold:
        alert_msg = (
            f"Function {metrics.function_name} exceeded memory threshold: "
            f"{metrics.memory_used:.2f}MB > {alert_cfg.mem_threshold}MB"
        )
        send_alert(alert_msg, {
            'function_name': metrics.function_name,
            'memory_used_mb': metrics.memory_used,
            'threshold_mb': alert_cfg.mem_threshold,
            'metrics': metrics.to_dict()
        }, alert_cfg.alert_hook)

def send_alert(message: str, context: Dict[str, Any], alert_hook: Any) -> None:
    """Send alert through configured handler."""
    logger.warning(message)
    emit_metric('alert', {'message': message})
    alert_hook.alert(message, context)

def handle_error(func_name: str, error: Exception, alert_hook: Any) -> None:
    """Handle and report function errors."""
    error_msg = f"Error in {func_name}: {str(error)}"
    logger.error(error_msg)
    stop_pipeline_timing(func_name)
    record_pipeline_run(func_name, False)
    
    alert_hook.alert(error_msg, {
        'function_name': func_name,
        'error': str(error),
        'traceback': traceback.format_exc(),
        'type': 'error'
    })

def track_performance(func):
    """Decorator to track function performance."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        print(f"Function {func.__name__} took {duration:.2f} seconds")
        return result
    return wrapper
