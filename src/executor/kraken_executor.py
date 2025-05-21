"""
Trade executor for the Kraken exchange.
Handles the execution of trades on the Kraken exchange using the krakenex library.
"""
import time
from typing import Dict, Any, Optional, Tuple, List

import krakenex
from pykrakenapi import KrakenAPI

from src.utils.logging import get_logger
from src.utils.models import TradeRequest, TradeResponse
from src.utils.secrets import secret_manager

logger = get_logger(__name__)


class KrakenExecutor:
    """Trade executor for the Kraken exchange."""
    
    def __init__(self):
        """Initialize the Kraken executor."""
        self._api = None
        self._k = None
        self._initialized = False
        self._last_init_attempt = 0
        self._init_cooldown = 60  # seconds to wait between initialization attempts
    
    def _initialize(self) -> bool:
        """
        Initialize the Kraken API client.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        # Check if we've tried to initialize recently
        current_time = time.time()
        if current_time - self._last_init_attempt < self._init_cooldown and not self._initialized:
            logger.debug("Skipping initialization due to cooldown")
            return False
        
        self._last_init_attempt = current_time
        
        # Get API credentials
        api_key, api_secret = secret_manager.get_kraken_credentials()
        
        if not api_key or not api_secret:
            logger.error("Missing Kraken API credentials")
            return False
        
        try:
            # Initialize krakenex
            self._k = krakenex.API(key=api_key, secret=api_secret)
            
            # Initialize pykrakenapi
            self._api = KrakenAPI(self._k)
            
            # Test the connection
            server_time = self._k.query_public('Time')
            if 'error' in server_time and server_time['error']:
                logger.error("Failed to connect to Kraken API", error=server_time['error'])
                return False
            
            logger.info("Successfully initialized Kraken API")
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error("Failed to initialize Kraken API", error=str(e))
            self._initialized = False
            return False
    
    def execute_trade(self, trade_request: TradeRequest) -> TradeResponse:
        """
        Execute a trade on the Kraken exchange.
        
        Args:
            trade_request: The trade request to execute
            
        Returns:
            A TradeResponse object with the result of the trade
        """
        # Initialize the API if needed
        if not self._initialized and not self._initialize():
            return TradeResponse.error_response(
                "Failed to initialize Kraken API",
                {"retry_after": self._init_cooldown}
            )
        
        # Prepare the request parameters
        params = trade_request.dict(exclude_none=True)
        
        try:
            # Execute the trade
            logger.info("Executing trade", trade_request=params)
            result = self._k.query_private('AddOrder', params)
            
            # Check for errors
            if 'error' in result and result['error']:
                logger.error("Trade execution failed", error=result['error'])
                return TradeResponse.error_response(
                    f"Kraken API error: {', '.join(result['error'])}",
                    {"kraken_response": result}
                )
            
            # Extract the order ID
            if 'result' in result and 'txid' in result['result']:
                order_ids = result['result']['txid']
                if order_ids:
                    order_id = order_ids[0]
                    logger.info("Trade executed successfully", order_id=order_id)
                    return TradeResponse.success_response(
                        order_id,
                        {"kraken_response": result['result']}
                    )
            
            # If we get here, something unexpected happened
            logger.warning("Unexpected response from Kraken API", response=result)
            return TradeResponse.error_response(
                "Unexpected response from Kraken API",
                {"kraken_response": result}
            )
            
        except Exception as e:
            logger.error("Exception during trade execution", error=str(e))
            return TradeResponse.error_response(
                f"Exception during trade execution: {str(e)}"
            )
    
    def validate_trade(self, trade_request: TradeRequest) -> TradeResponse:
        """
        Validate a trade request without executing it.
        
        Args:
            trade_request: The trade request to validate
            
        Returns:
            A TradeResponse object with the validation result
        """
        # Create a copy of the request with validate=True
        validation_request = TradeRequest(**trade_request.dict())
        validation_request.validate = True
        
        return self.execute_trade(validation_request)
    
    def get_account_balance(self) -> Dict[str, float]:
        """
        Get the account balance.
        
        Returns:
            A dictionary mapping asset names to balances
        """
        # Initialize the API if needed
        if not self._initialized and not self._initialize():
            logger.error("Failed to get account balance due to initialization failure")
            return {}
        
        try:
            # Query the balance
            result = self._k.query_private('Balance')
            
            # Check for errors
            if 'error' in result and result['error']:
                logger.error("Failed to get account balance", error=result['error'])
                return {}
            
            # Parse the result
            if 'result' in result:
                # Convert string values to float
                balance = {k: float(v) for k, v in result['result'].items()}
                return balance
            
            return {}
            
        except Exception as e:
            logger.error("Exception while getting account balance", error=str(e))
            return {}
    
    def get_open_orders(self) -> List[Dict[str, Any]]:
        """
        Get open orders.
        
        Returns:
            A list of open orders
        """
        # Initialize the API if needed
        if not self._initialized and not self._initialize():
            logger.error("Failed to get open orders due to initialization failure")
            return []
        
        try:
            # Query open orders
            result = self._k.query_private('OpenOrders')
            
            # Check for errors
            if 'error' in result and result['error']:
                logger.error("Failed to get open orders", error=result['error'])
                return []
            
            # Parse the result
            if 'result' in result and 'open' in result['result']:
                orders = []
                for order_id, order_data in result['result']['open'].items():
                    order = order_data.copy()
                    order['order_id'] = order_id
                    orders.append(order)
                return orders
            
            return []
            
        except Exception as e:
            logger.error("Exception while getting open orders", error=str(e))
            return []


# Create a singleton instance
kraken_executor = KrakenExecutor()