from pipeline_monitor import track_performance, ResourceMonitor, setup_logging
from pipeline_monitor.dashboard import start_dashboard
from pipeline_monitor.alerts import setup_alerts, log_alert_handler
import time
import threading

# Setup logging
setup_logging(log_file='pipeline.log', json_format=True)

# Setup alerts
alert_hook = setup_alerts(log_alert_handler)

# Example function with performance tracking
@track_performance(alert_threshold=5.0)
def process_data(size: int) -> list:
    result = []
    for i in range(size):
        time.sleep(0.01)  # Simulate processing
        result.append(i * i)
    return result

def run_demo():
    while True:
        # Process some data
        with ResourceMonitor("data_processing", alert_threshold_mb=100):
            data = process_data(100)
            time.sleep(1)
            
            # Trigger an alert
            alert_hook.alert(
                "Processing complete",
                context={'data_size': len(data)}
            )

if __name__ == '__main__':
    # Start the dashboard in a separate thread
    dashboard_thread = threading.Thread(
        target=start_dashboard,
        kwargs={'port': 5000},
        daemon=True
    )
    dashboard_thread.start()
    
    # Run the demo process
    run_demo()
