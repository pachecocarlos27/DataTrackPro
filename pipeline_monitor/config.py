from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class Configuration:
    """
    Configuration management for pipeline monitoring.
    """

    def __init__(self, config_dict: Optional[Dict[str, Any]] = None):
        self.config: Dict[str, Any] = config_dict if config_dict is not None else {}

        # Set defaults
        self.config.setdefault('logging', {
            'level': 'INFO',
            'json_format': True,
            'log_file': None
        })

        self.config.setdefault('alerts', {
            'enabled': True,
            'time_threshold': 300,  # 5 minutes
            'memory_threshold': 1000,  # 1GB
            'slack_webhook': None,  # Optional Slack webhook URL
            'email': {  # Optional email configuration
                'smtp_host': None,
                'smtp_port': 587,
                'sender': None,
                'password': None,
                'recipients': []
            }
        })

    @classmethod
    def from_file(cls, file_path: str) -> 'Configuration':
        """
        Load configuration from JSON file.

        Args:
            file_path: Path to JSON configuration file

        Returns:
            Configuration instance
        """
        try:
            with open(file_path, 'r') as f:
                config_dict = json.load(f)
            return cls(config_dict)
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {str(e)}")
            return cls()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value