import psutil
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def get_memory_usage() -> Dict[str, float]:
    """
    Get current memory usage statistics.

    Returns:
        Dict containing memory usage metrics in MB
    """
    process = psutil.Process()
    memory_info = process.memory_info()

    metrics = {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent()
    }

    return metrics

def log_memory_usage(threshold_mb: Optional[float] = None) -> None:
    """
    Log current memory usage and optionally check against threshold.

    Args:
        threshold_mb: Optional threshold in MB to trigger warning
    """
    metrics = get_memory_usage()
    logger.info(f"Memory usage metrics: {metrics}")

    if threshold_mb is not None and metrics['rss_mb'] > threshold_mb:
        logger.warning(
            f"Memory usage ({metrics['rss_mb']:.2f}MB) "
            f"exceeded threshold ({threshold_mb}MB)"
        )