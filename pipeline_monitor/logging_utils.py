"""Logging utilities for Pipeline Monitor."""

import logging
import json
import sys
from typing import Optional

class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    """
    
    def format(self, record):
        """
        Format the log record as a JSON string.
        
        Args:
            record: Log record to format
        
        Returns:
            JSON string representation of the log record
        """
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger_name': record.name
        }
        
        if hasattr(record, 'props'):
            log_data.update(record.props)
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging(level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('pipeline_monitor')

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    json_format: bool = True
) -> None:
    """
    Setup logging configuration with optional JSON formatting and file output.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path for log output
        json_format: Whether to use JSON formatting (default: True)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
