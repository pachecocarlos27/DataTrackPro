import time
import psutil
import logging
from typing import Optional, Any
import json
from contextlib import ContextDecorator
from .dashboard.app import emit_metric

logger = logging.getLogger(__name__)

class ResourceMonitor(ContextDecorator):
    """
    Context manager for monitoring resource usage during execution.
    """

    def __init__(self, name: str, alert_threshold_mb: Optional[float] = None):
        """
        Initialize the resource monitor.

        Args:
            name: Name of the monitored block
            alert_threshold_mb: Memory threshold in MB to trigger alerts
        """
        self.name = name
        self.alert_threshold_mb = alert_threshold_mb
        self.start_time: float = 0.0
        self.start_memory: float = 0.0
        self.process = psutil.Process()

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

        except Exception as e:
            logger.error(f"Error in monitoring exit: {str(e)}")