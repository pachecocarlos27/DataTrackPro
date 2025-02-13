from pipeline_monitor import (
    track_performance, ResourceMonitor, Configuration, 
    start_dashboard, setup_logging
)
import threading
import time
import random
import logging
import math

# Load configuration
config = Configuration.from_file("examples/config.json")
setup_logging(**config.get('logging', {}))
logger = logging.getLogger(__name__)

class MLPipeline:
    """Demo ML pipeline with monitoring."""
    
    def __init__(self):
        self.dashboard_thread = None
        self.dashboard_config = config.get('dashboard', {})
    
    def start_dashboard(self):
        """Start the monitoring dashboard."""
        self.dashboard_thread = threading.Thread(
            target=start_dashboard,
            kwargs=self.dashboard_config,
            daemon=True
        )
        self.dashboard_thread.start()
        logger.info(f"Dashboard started at http://{self.dashboard_config.get('host', '0.0.0.0')}:"
                   f"{self.dashboard_config.get('port', 5000)}")
        time.sleep(1)  # Wait for dashboard

    @track_performance(alert_threshold=2.0, config_path="examples/config.json")
    def train_model(self, epochs: int):
        """Simulate ML model training."""
        losses = []
        for epoch in range(epochs):
            time.sleep(0.2)
            loss = 1 / (epoch + 1) + random.uniform(0, 0.1)
            losses.append(loss)
            logger.info(f"Epoch {epoch + 1}/{epochs}, Loss: {loss:.4f}")
        return min(losses)

    @track_performance(memory_threshold=200, config_path="examples/config.json")
    def preprocess_data(self, size: int):
        """Simulate data preprocessing."""
        data = [random.random() for _ in range(size)]
        time.sleep(0.1)
        return sum(data) / len(data)

    def run_pipeline(self):
        """Run the complete training pipeline."""
        with ResourceMonitor("training_pipeline"):
            try:
                logger.info("Starting data preprocessing...")
                avg = self.preprocess_data(10000)
                logger.info(f"Data average: {avg:.2f}")
                
                logger.info("Starting model training...")
                best_loss = self.train_model(10)
                logger.info(f"Training complete. Best loss: {best_loss:.4f}")
                
                return best_loss
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                return None

def main():
    pipeline = MLPipeline()
    pipeline.start_dashboard()
    
    try:
        while True:
            pipeline.run_pipeline()
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Stopping pipeline...")

if __name__ == "__main__":
    main()
