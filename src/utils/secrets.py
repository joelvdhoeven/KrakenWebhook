"""
Secret management utilities for the TradingView to Kraken webhook service.
Provides access to secrets from environment variables or Google Cloud Secret Manager.
"""
import os
from typing import Optional

from config.config import config
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Flag to track if we've attempted to import google-cloud-secret-manager
_tried_import = False
_secret_manager_available = False

# Only try to import if GCP project ID is set
if config.gcp_project_id:
    try:
        from google.cloud import secretmanager
        _secret_manager_available = True
    except ImportError:
        logger.warning("google-cloud-secret-manager not installed, falling back to environment variables")
        _tried_import = True


class SecretManager:
    """Secret manager for accessing sensitive configuration."""
    
    def __init__(self):
        """Initialize the secret manager."""
        self._client = None
        if _secret_manager_available and config.gcp_project_id:
            try:
                self._client = secretmanager.SecretManagerServiceClient()
                logger.info("Initialized Google Cloud Secret Manager")
            except Exception as e:
                logger.error("Failed to initialize Google Cloud Secret Manager", error=str(e))
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value by name.
        
        Args:
            secret_name: The name of the secret
            default: Default value if secret is not found
            
        Returns:
            The secret value or default if not found
        """
        # First try environment variables
        env_value = os.getenv(secret_name)
        if env_value:
            logger.debug(f"Retrieved secret {secret_name} from environment")
            return env_value
        
        # Then try Google Cloud Secret Manager if available
        if self._client and config.gcp_project_id:
            try:
                secret_path = f"projects/{config.gcp_project_id}/secrets/{secret_name}/versions/latest"
                response = self._client.access_secret_version(name=secret_path)
                secret_value = response.payload.data.decode("UTF-8")
                logger.debug(f"Retrieved secret {secret_name} from Secret Manager")
                return secret_value
            except Exception as e:
                logger.warning(f"Failed to retrieve secret {secret_name} from Secret Manager", error=str(e))
        
        # Return default if secret not found
        logger.debug(f"Secret {secret_name} not found, using default")
        return default
    
    def get_kraken_credentials(self) -> tuple[Optional[str], Optional[str]]:
        """
        Get Kraken API credentials.
        
        Returns:
            Tuple of (api_key, api_secret)
        """
        api_key = self.get_secret("KRAKEN_API_KEY")
        api_secret = self.get_secret("KRAKEN_API_SECRET")
        
        if not api_key or not api_secret:
            logger.warning("Kraken API credentials not found")
            
        return api_key, api_secret
    
    def get_webhook_secret(self) -> Optional[str]:
        """
        Get the webhook secret for validating incoming requests.
        
        Returns:
            The webhook secret or None if not found
        """
        return self.get_secret("WEBHOOK_SECRET")


# Create a singleton instance
secret_manager = SecretManager()