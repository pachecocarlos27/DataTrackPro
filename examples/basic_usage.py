from pipeline_monitor import track_performance, ResourceMonitor
from pipeline_monitor.config import Configuration

# Load configuration
config = Configuration.from_file("examples/config.json")

# Using the decorator
@track_performance(
    alert_threshold=30,  # 30 seconds
    memory_threshold=500,  # 500MB
    config_path="examples/config.json"  # Use thresholds from config file
)
def process_data():
    # Your processing code here
    pass

# Using the context manager
with ResourceMonitor("data_processing", alert_threshold_mb=1000):
    # Your processing code here
    pass

# Using configuration file
@track_performance(config_path="examples/config.json")
def pipeline_step():
    # Will use thresholds from config file
    pass

if __name__ == "__main__":
    # Example pipeline
    process_data()
    pipeline_step()
