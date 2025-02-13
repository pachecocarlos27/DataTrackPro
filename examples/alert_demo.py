from pipeline_monitor import track_performance, ResourceMonitor, Configuration
import time

# Load configuration with alert settings
config = Configuration.from_file("config.json")

@track_performance(
    alert_threshold=1.0,  # Alert if function takes more than 1 second
    memory_threshold=100,  # Alert if memory usage exceeds 100MB
    config_path="config.json"  # Use alert channels from config
)
def slow_function():
    """Function that will trigger alerts."""
    # Simulate memory-intensive work
    big_list = list(range(1000000))
    time.sleep(2)  # Trigger time threshold
    return len(big_list)

def main():
    # Monitor a block that will trigger memory alert
    with ResourceMonitor("memory_intensive", alert_threshold_mb=50):
        result = slow_function()
        print(f"Processed {result} items")

if __name__ == "__main__":
    main() 