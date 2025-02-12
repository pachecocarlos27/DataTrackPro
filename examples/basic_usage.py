from pipeline_monitor import track_performance, ResourceMonitor, setup_logging
from pipeline_monitor.alerts import setup_alerts, log_alert_handler
import time

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

# Example using context manager
def main():
    # Track a block of code
    with ResourceMonitor("data_processing", alert_threshold_mb=100):
        # Process some data
        data = process_data(100)
        
        # Simulate more work
        time.sleep(1)
        
        # Trigger an alert
        alert_hook.alert(
            "Processing complete",
            context={'data_size': len(data)}
        )

if __name__ == '__main__':
    main()
