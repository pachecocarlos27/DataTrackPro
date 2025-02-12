from pipeline_monitor import track_performance, ResourceMonitor, setup_logging
from pipeline_monitor.dashboard import start_dashboard
from pipeline_monitor.alerts import setup_alerts, log_alert_handler
import time
import threading
import logging

# Setup logging
setup_logging(log_file='pipeline.log', json_format=True)

logger = logging.getLogger(__name__)

# Setup alerts
alert_hook = setup_alerts(log_alert_handler)

# Example function with performance tracking
@track_performance(alert_threshold=5.0)
def process_data(size: int) -> list:
    """Example pipeline that processes data and generates metrics."""
    result = []
    for i in range(size):
        time.sleep(0.01)  # Simulate processing
        result.append(i * i)
    return result

def run_demo():
    """Run continuous demo processing."""
    while True:
        # Process some data with resource monitoring
        with ResourceMonitor("data_processing", alert_threshold_mb=100):
            try:
                data = process_data(100)
                time.sleep(1)

                # Trigger an alert
                alert_hook.alert(
                    "Processing complete",
                    context={'data_size': len(data)}
                )
            except Exception as e:
                logger.error(f"Error in demo processing: {str(e)}")

if __name__ == '__main__':
    try:
        # Start the dashboard in a separate thread
        dashboard_thread = threading.Thread(
            target=start_dashboard,
            kwargs={'port': 5001, 'debug': False},  # Use a different port
            daemon=True
        )
        dashboard_thread.start()
        logger.info("Dashboard thread started")

        print("Dashboard started on http://0.0.0.0:5001")
        print("Prometheus metrics available at http://0.0.0.0:5001/metrics")

        # Run the demo process
        run_demo()
    except Exception as e:
        logger.error(f"Error in main thread: {str(e)}")
        raise