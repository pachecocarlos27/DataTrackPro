from pipeline_monitor import track_performance, ResourceMonitor, Configuration, setup_logging
import time
import os
import psutil
import logging
import numpy as np
from typing import List, Tuple

# Load configuration
config = Configuration.from_file("config.json")
setup_logging(**config.get('logging', {}))
logger = logging.getLogger(__name__)

class MemoryMonitor:
    """Memory usage monitoring and optimization demo."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> float:
        """Get current process memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def log_memory_usage(self, label: str):
        """Log current memory usage with label."""
        current = self.get_memory_usage()
        delta = current - self.initial_memory
        logger.info(f"{label}: {current:.1f}MB (Δ{delta:+.1f}MB)")

    @track_performance(memory_threshold=100)
    def memory_intensive_task(self, size: int) -> Tuple[int, float]:
        """Perform a memory-intensive operation."""
        start_mem = self.get_memory_usage()
        
        # Create large arrays
        data = np.arange(size, dtype=np.float64)
        result = np.sum(data ** 2)
        
        peak_mem = self.get_memory_usage()
        return result, peak_mem - start_mem

    @track_performance(memory_threshold=50)
    def process_in_batches(self, total_size: int, batch_size: int) -> List[float]:
        """Process data in batches to manage memory."""
        results = []
        
        for i in range(0, total_size, batch_size):
            with ResourceMonitor(f"batch_{i}", alert_threshold_mb=20):
                end = min(i + batch_size, total_size)
                batch = np.arange(i, end, dtype=np.float64)
                result = np.sum(batch ** 2)
                results.append(result)
                
                self.log_memory_usage(f"Batch {i}")
                
        return results

    def demonstrate_memory_leak(self, iterations: int):
        """Demonstrate memory leak detection."""
        logger.info("Demonstrating memory leak detection...")
        cached_data = []
        
        for i in range(iterations):
            with ResourceMonitor(f"leak_demo_{i}", alert_threshold_mb=50):
                # Simulate memory leak by accumulating data
                data = np.random.random(1000000)
                cached_data.append(data)
                
                self.log_memory_usage(f"Iteration {i + 1}")
                time.sleep(0.1)

    def run_demos(self):
        """Run all memory monitoring demos."""
        logger.info("Starting memory monitoring demos...")
        self.log_memory_usage("Initial")

        # Demo 1: Memory-intensive task
        logger.info("\nRunning memory-intensive task...")
        result, memory_used = self.memory_intensive_task(1000000)
        logger.info(f"Task completed: result={result}, memory_used={memory_used:.1f}MB")

        # Demo 2: Batch processing
        logger.info("\nProcessing in batches...")
        results = self.process_in_batches(1000000, 100000)
        logger.info(f"Batch processing completed: {len(results)} batches")

        # Demo 3: Memory leak detection
        try:
            self.demonstrate_memory_leak(5)
        except Exception as e:
            logger.error(f"Memory leak demo error: {e}")

        self.log_memory_usage("Final")

def main():
    monitor = MemoryMonitor()
    
    try:
        monitor.run_demos()
    except KeyboardInterrupt:
        logger.info("Stopping memory demos...")
    except Exception as e:
        logger.error(f"Error in memory demos: {e}")

if __name__ == "__main__":
    main() 