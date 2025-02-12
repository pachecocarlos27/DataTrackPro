import time
import functools
import logging
import traceback
from typing import Callable, Any, Optional, TypeVar, cast
import psutil
import json
from .dashboard.app import emit_metric

logger = logging.getLogger(__name__)

T = TypeVar('T')

def track_performance(alert_threshold: Optional[float] = None) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator to track function performance metrics including execution time and memory usage.

    Args:
        alert_threshold: Maximum execution time in seconds before triggering alert
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

            success = True
            error_info = {}
            result = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_info = {
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'stacktrace': traceback.format_exc()
                }
                raise
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB

                execution_time = end_time - start_time
                memory_used = end_memory - start_memory

                metrics = {
                    'function_name': func.__name__,
                    'execution_time': execution_time,
                    'memory_usage_mb': memory_used,
                    'success': success,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                if not success:
                    metrics['error_details'] = error_info

                logger.info(json.dumps(metrics))

                # Emit metrics to dashboard
                emit_metric('performance', {
                    'active_pipelines': 1,  # This will be enhanced later
                    'execution_time': execution_time
                })

                emit_metric('memory', {
                    'rss_mb': end_memory,
                    'memory_used_mb': memory_used
                })

                if alert_threshold and execution_time > alert_threshold:
                    alert_msg = (
                        f"Function {func.__name__} exceeded time threshold: "
                        f"{execution_time:.2f}s > {alert_threshold}s"
                    )
                    logger.warning(alert_msg)
                    emit_metric('alert', {'message': alert_msg})

            return cast(T, result)
        return wrapper
    return decorator