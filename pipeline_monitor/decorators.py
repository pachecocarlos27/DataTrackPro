import time
import functools
import logging
import traceback
from typing import Callable, Any, Optional, TypeVar
import psutil
import json
from .dashboard.app import emit_metric
from .prometheus_metrics import (
    start_pipeline_timing, stop_pipeline_timing,
    record_pipeline_run, update_memory_usage,
    update_active_pipelines
)

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def track_performance(alert_threshold: Optional[float] = None) -> Callable[[F], F]:
    """
    Decorator to track function performance metrics including execution time and memory usage.

    Args:
        alert_threshold: Maximum execution time in seconds before triggering alert
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Initialize metrics
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss
            start_pipeline_timing()

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Record success metrics
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss
                execution_time = end_time - start_time
                memory_used = end_memory - start_memory

                # Log metrics
                metrics = {
                    'function_name': func.__name__,
                    'execution_time': execution_time,
                    'memory_usage_mb': memory_used / 1024 / 1024,
                    'success': True,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                logger.info(json.dumps(metrics))

                # Update Prometheus metrics
                stop_pipeline_timing(func.__name__)
                record_pipeline_run(func.__name__, True)
                update_memory_usage(func.__name__, end_memory)
                update_active_pipelines(1)

                # Emit metrics to dashboard
                emit_metric('performance', {
                    'active_pipelines': 1,
                    'execution_time': execution_time
                })
                emit_metric('memory', {
                    'rss_mb': end_memory / 1024 / 1024,
                    'memory_used_mb': memory_used / 1024 / 1024
                })

                # Check alert threshold
                if alert_threshold and execution_time > alert_threshold:
                    alert_msg = (
                        f"Function {func.__name__} exceeded time threshold: "
                        f"{execution_time:.2f}s > {alert_threshold}s"
                    )
                    logger.warning(alert_msg)
                    emit_metric('alert', {'message': alert_msg})

                return result

            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                stop_pipeline_timing(func.__name__)
                record_pipeline_run(func.__name__, False)
                emit_metric('alert', {
                    'message': f"Error in {func.__name__}: {str(e)}"
                })
                raise

        return wrapper
    return decorator