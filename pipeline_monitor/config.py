from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path

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
            },
            'sms': {  # Optional SMS configuration
                'provider_url': None,
                'api_key': None,
                'sender_number': None,
                'recipient_numbers': []
            }
        })

    @classmethod
    def from_file(cls, path: str) -> 'Configuration':
        """
        Load configuration from JSON file.

        Args:
            path: Path to JSON configuration file

        Returns:
            Configuration instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
            
        with path.open() as f:
            config = json.load(f)
        return cls(config)

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

    def __getitem__(self, key: str) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key

        Returns:
            Configuration value
        """
        return self.config[key]

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
