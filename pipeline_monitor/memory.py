import psutil
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dict containing memory usage metrics in MB and bytes
    """
    process = psutil.Process()
    memory_info = process.memory_info()

    metrics = {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'rss_bytes': memory_info.rss,  # Add raw bytes for Prometheus
        'vms_bytes': memory_info.vms   # Add raw bytes for Prometheus
    }

    return metrics

def log_memory_usage(threshold_mb: Optional[float] = None, pipeline_name: Optional[str] = None) -> None:
    """
    Log current memory usage and optionally check against threshold.
    Updates Prometheus metrics if pipeline name is provided.

    Args:
        threshold_mb: Optional threshold in MB to trigger warning
        pipeline_name: Optional name of the pipeline for metrics tracking
    """
    metrics = get_memory_usage()
    logger.info(f"Memory usage metrics: {metrics}")

    # Update Prometheus metrics if pipeline name is provided
    if pipeline_name is not None:
        from .prometheus_metrics import update_memory_usage
        update_memory_usage(pipeline_name, metrics['rss_bytes'])

    if threshold_mb is not None and metrics['rss_mb'] > threshold_mb:
        logger.warning(
            f"Memory usage ({metrics['rss_mb']:.2f}MB) "
            f"exceeded threshold ({threshold_mb}MB)"
        )

    # Send SMS alert if memory usage exceeds threshold
    if threshold_mb is not None and metrics['rss_mb'] > threshold_mb:
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
                f"Memory usage ({metrics['rss_mb']:.2f}MB) "
                f"exceeded threshold ({threshold_mb}MB)"
            )
            handler(alert_msg, {
                'memory_usage_mb': metrics['rss_mb'],
                'threshold_mb': threshold_mb
            })
