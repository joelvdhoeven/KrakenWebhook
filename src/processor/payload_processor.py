"""
Payload processor for TradingView webhook alerts.
Validates and processes incoming webhook payloads from TradingView.
"""
import json
import hmac
import hashlib
from typing import Dict, Any, Optional, Tuple, Union

from fastapi import Request, HTTPException, status
from pydantic import ValidationError

from src.utils.logging import get_logger
from src.utils.models import TradingViewAlert, TradeRequest
from src.utils.secrets import secret_manager

logger = get_logger(__name__)


class PayloadProcessor:
    """Processor for TradingView webhook payloads."""
    
    def __init__(self):
        """Initialize the payload processor."""
        self._webhook_secret = None
    
    async def process_request(self, request: Request) -> Tuple[TradingViewAlert, TradeRequest]:
        """
        Process an incoming webhook request.
        
        Args:
            request: The FastAPI request object
            
        Returns:
            A tuple of (TradingViewAlert, TradeRequest)
            
        Raises:
            HTTPException: If the request is invalid
        """
        # Validate the request signature if a webhook secret is configured
        await self._validate_signature(request)
        
        # Parse the request body
        try:
            body = await request.json()
        except json.JSONDecodeError as e:
            logger.error("Failed to parse request body as JSON", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Log the incoming payload (masked for security)
        self._log_payload(body)
        
        # Validate and convert to TradingViewAlert model
        try:
            alert = TradingViewAlert(**body)
        except ValidationError as e:
            logger.error("Invalid TradingView alert payload", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid payload format: {str(e)}"
            )
        
        # Convert to TradeRequest
        trade_request = TradeRequest.from_tradingview_alert(alert)
        
        logger.info(
            "Processed TradingView alert",
            symbol=alert.symbol,
            side=alert.side,
            order_type=alert.order_type
        )
        
        return alert, trade_request
    
    async def _validate_signature(self, request: Request) -> None:
        """
        Validate the request signature using HMAC.
        
        Args:
            request: The FastAPI request object
            
        Raises:
            HTTPException: If the signature is invalid
        """
        # Get the webhook secret
        webhook_secret = self._get_webhook_secret()
        
        # Skip validation if no webhook secret is configured
        if not webhook_secret:
            logger.warning("Webhook signature validation skipped: no webhook secret configured")
            return
        
        # Get the signature from the header
        signature = request.headers.get("X-Signature")
        if not signature:
            logger.warning("No signature header found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing signature header"
            )
        
        # Get the raw request body
        body = await request.body()
        
        # Compute the expected signature
        expected_signature = hmac.new(
            webhook_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid signature"
            )
        
        logger.debug("Webhook signature validated successfully")
    
    def _get_webhook_secret(self) -> Optional[str]:
        """
        Get the webhook secret.
        
        Returns:
            The webhook secret or None if not configured
        """
        if self._webhook_secret is None:
            self._webhook_secret = secret_manager.get_webhook_secret()
        
        return self._webhook_secret
    
    def _log_payload(self, payload: Dict[str, Any]) -> None:
        """
        Log the incoming payload with sensitive information masked.
        
        Args:
            payload: The payload to log
        """
        # Create a copy of the payload
        masked_payload = payload.copy()
        
        # Mask sensitive fields
        sensitive_fields = ["api_key", "api_secret", "key", "secret", "password", "token"]
        for field in sensitive_fields:
            if field in masked_payload:
                masked_payload[field] = "***"
        
        logger.debug("Received webhook payload", payload=masked_payload)


# Create a singleton instance
payload_processor = PayloadProcessor()