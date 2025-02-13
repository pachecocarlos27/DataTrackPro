from pipeline_monitor import track_performance, ResourceMonitor, Configuration, setup_logging
from prometheus_client import start_http_server, Counter, Gauge
import time
import random
import logging

# Load configuration
config = Configuration.from_file("examples/config.json")
setup_logging(**config.get('logging', {}))
logger = logging.getLogger(__name__)

# Custom Prometheus metrics
ITEMS_PROCESSED = Counter('pipeline_items_processed_total', 'Number of items processed')
BATCH_SIZE = Gauge('pipeline_batch_size_current', 'Current batch size')
PROCESSING_TIME = Gauge('pipeline_processing_time_seconds', 'Processing time per batch')

def start_prometheus():
    """Start Prometheus metrics server."""
    prometheus_config = config.get('prometheus', {})
    port = prometheus_config.get('port', 9090)
    start_http_server(port)
    logger.info(f"Prometheus metrics available at http://localhost:{port}")

@track_performance(memory_threshold=50, config_path="examples/config.json")
def process_batch(size: int):
    """Process a batch of data with variable timing."""
    start = time.time()
    BATCH_SIZE.set(size)
    
    # Simulate variable processing time
    time.sleep(random.uniform(0.1, 0.5))
    result = [i * i for i in range(size)]
    
    # Update metrics
    ITEMS_PROCESSED.inc(size)
    PROCESSING_TIME.set(time.time() - start)
    
    return result

def run_pipeline():
    """Run a demo pipeline with multiple monitored components."""
    batch_sizes = [100, 200, 300, 400, 500]
    
    for size in batch_sizes:
        with ResourceMonitor(f"batch_processing_{size}", config_path="examples/config.json"):
            try:
                result = process_batch(size)
                logger.info(f"Processed batch of {size}: got {len(result)} results")
                time.sleep(0.5)  # Pause between batches
            except Exception as e:
                logger.error(f"Error processing batch {size}: {e}")

def main():
    start_prometheus()
    logger.info("Starting demo pipeline...")
    
    try:
        while True:
            run_pipeline()
    except KeyboardInterrupt:
        logger.info("Stopping demo...")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")

if __name__ == "__main__":
    main()
