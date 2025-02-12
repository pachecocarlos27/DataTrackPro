import time
import psutil
import logging
from typing import Optional, Any
import json
from contextlib import ContextDecorator

logger = logging.getLogger(__name__)

class ResourceMonitor(ContextDecorator):
    """
    Context manager for monitoring resource usage during execution.
    """

    def __init__(self, name: str, alert_threshold_mb: Optional[float] = None):
        self.name = name
        self.alert_threshold_mb = alert_threshold_mb
        self.start_time: float = 0.0
        self.start_memory: float = 0.0
        self.process = psutil.Process()

    def __enter__(self) -> 'ResourceMonitor':
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        logger.info(f"Starting monitoring block: {self.name}")
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Any) -> bool:
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

        if self.alert_threshold_mb and memory_used > self.alert_threshold_mb:
            logger.warning(
                f"Block {self.name} exceeded memory threshold: "
                f"{memory_used:.2f}MB > {self.alert_threshold_mb}MB"
            )

        return False  # Don't suppress exceptions