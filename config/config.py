"""
Configuration management for the TradingView to Kraken webhook service.
Loads configuration from environment variables and provides access to configuration values.
"""
import os
from typing import Dict, Any, Optional
from enum import Enum
import logging

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Environment(str, Enum):
    """Enum for environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Config:
    """Configuration class for the application."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Environment
        self.environment = Environment(os.getenv("ENVIRONMENT", "development").lower())
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # API Keys
        self.kraken_api_key = os.getenv("KRAKEN_API_KEY")
        self.kraken_api_secret = os.getenv("KRAKEN_API_SECRET")
        
        # Webhook
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")
        
        # Google Cloud
        self.gcp_project_id = os.getenv("GCP_PROJECT_ID")
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate that required configuration is present."""
        if self.environment == Environment.PRODUCTION:
            missing_vars = []
            
            if not self.kraken_api_key:
                missing_vars.append("KRAKEN_API_KEY")
            if not self.kraken_api_secret:
                missing_vars.append("KRAKEN_API_SECRET")
            if not self.webhook_secret:
                missing_vars.append("WEBHOOK_SECRET")
                
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @property
    def is_production(self) -> bool:
        """Check if the environment is production."""
        return self.environment == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        """Check if the environment is development."""
        return self.environment == Environment.DEVELOPMENT
    
    def get_log_level(self) -> int:
        """Get the log level as a logging constant."""
        return getattr(logging, self.log_level, logging.INFO)
    
    def as_dict(self) -> Dict[str, Any]:
        """Return configuration as a dictionary (with sensitive values masked)."""
        config_dict = {
            "environment": self.environment,
            "log_level": self.log_level,
            "kraken_api_key": "***" if self.kraken_api_key else None,
            "kraken_api_secret": "***" if self.kraken_api_secret else None,
            "webhook_secret": "***" if self.webhook_secret else None,
            "gcp_project_id": self.gcp_project_id,
        }
        return config_dict


# Create a singleton instance
config = Config()