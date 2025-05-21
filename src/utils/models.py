"""
Data models for the TradingView to Kraken webhook service.
Defines the structure of incoming webhook payloads and outgoing trade requests.
"""
from enum import Enum
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field, validator


class OrderType(str, Enum):
    """Enum for order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop-loss"
    TAKE_PROFIT = "take-profit"
    STOP_LOSS_LIMIT = "stop-loss-limit"
    TAKE_PROFIT_LIMIT = "take-profit-limit"


class OrderSide(str, Enum):
    """Enum for order sides."""
    BUY = "buy"
    SELL = "sell"


class TradingViewAlert(BaseModel):
    """Model for incoming TradingView alert webhook payload."""
    
    # Required fields
    symbol: str = Field(..., description="Trading pair symbol (e.g., 'XBTUSD')")
    side: OrderSide = Field(..., description="Order side: 'buy' or 'sell'")
    
    # Optional fields with defaults
    order_type: OrderType = Field(default=OrderType.MARKET, description="Order type")
    volume: Optional[float] = Field(default=None, description="Order volume/quantity")
    price: Optional[float] = Field(default=None, description="Limit price (required for limit orders)")
    leverage: Optional[int] = Field(default=None, description="Leverage for margin trading")
    stop_price: Optional[float] = Field(default=None, description="Stop price for stop orders")
    
    # Additional fields
    strategy_name: Optional[str] = Field(default=None, description="Name of the trading strategy")
    alert_message: Optional[str] = Field(default=None, description="Alert message from TradingView")
    
    # Custom fields for additional functionality
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields for extended functionality")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate and normalize the trading pair symbol."""
        # Convert to uppercase
        v = v.upper()
        
        # Add common mappings for popular pairs if they don't include the proper format
        symbol_mappings = {
            "BTCUSD": "XBTUSD",
            "BTC/USD": "XBTUSD",
            "ETHUSD": "ETHUSD",
            "ETH/USD": "ETHUSD",
        }
        
        return symbol_mappings.get(v, v)
    
    @validator('price', 'stop_price')
    def validate_prices(cls, v, values, **kwargs):
        """Validate price fields based on order type."""
        if v is None:
            field_name = kwargs.get('field', '')
            order_type = values.get('order_type')
            
            # Check if price is required for this order type
            price_required_for = [
                OrderType.LIMIT, 
                OrderType.STOP_LOSS_LIMIT, 
                OrderType.TAKE_PROFIT_LIMIT
            ]
            
            stop_price_required_for = [
                OrderType.STOP_LOSS,
                OrderType.STOP_LOSS_LIMIT,
                OrderType.TAKE_PROFIT,
                OrderType.TAKE_PROFIT_LIMIT
            ]
            
            if (field_name == 'price' and order_type in price_required_for) or \
               (field_name == 'stop_price' and order_type in stop_price_required_for):
                raise ValueError(f"{field_name} is required for {order_type} orders")
        
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        """Validate that volume is positive."""
        if v is not None and v <= 0:
            raise ValueError("Volume must be positive")
        return v


class TradeRequest(BaseModel):
    """Model for trade execution requests to Kraken API."""
    
    # Required fields
    pair: str = Field(..., description="Trading pair in Kraken format")
    type: OrderSide = Field(..., description="Order type: 'buy' or 'sell'")
    ordertype: str = Field(..., description="Order type in Kraken format")
    
    # Conditional required fields
    volume: Optional[str] = Field(default=None, description="Order volume/quantity")
    price: Optional[str] = Field(default=None, description="Price for limit orders")
    price2: Optional[str] = Field(default=None, description="Secondary price for stop-loss-limit orders")
    leverage: Optional[str] = Field(default=None, description="Leverage amount for margin trading")
    
    # Optional fields
    starttm: Optional[str] = Field(default=None, description="Scheduled start time")
    expiretm: Optional[str] = Field(default=None, description="Expiration time")
    validate: Optional[bool] = Field(default=None, description="Validate inputs only, don't submit order")
    
    # Additional Kraken-specific fields
    oflags: Optional[str] = Field(default=None, description="Order flags")
    userref: Optional[str] = Field(default=None, description="User reference ID")
    
    @classmethod
    def from_tradingview_alert(cls, alert: TradingViewAlert) -> 'TradeRequest':
        """
        Convert a TradingView alert to a Kraken trade request.
        
        Args:
            alert: The TradingView alert
            
        Returns:
            A TradeRequest object ready to be sent to Kraken
        """
        # Map TradingView order types to Kraken order types
        ordertype_mapping = {
            OrderType.MARKET: "market",
            OrderType.LIMIT: "limit",
            OrderType.STOP_LOSS: "stop-loss",
            OrderType.TAKE_PROFIT: "take-profit",
            OrderType.STOP_LOSS_LIMIT: "stop-loss-limit",
            OrderType.TAKE_PROFIT_LIMIT: "take-profit-limit",
        }
        
        # Create the base request
        request = {
            "pair": alert.symbol,
            "type": alert.side.value,
            "ordertype": ordertype_mapping[alert.order_type],
        }
        
        # Add volume if provided
        if alert.volume is not None:
            request["volume"] = str(alert.volume)
        
        # Add price for limit orders
        if alert.price is not None:
            request["price"] = str(alert.price)
        
        # Add stop price for stop orders
        if alert.stop_price is not None:
            if alert.order_type in [OrderType.STOP_LOSS_LIMIT, OrderType.TAKE_PROFIT_LIMIT]:
                request["price2"] = str(alert.stop_price)
            else:
                request["price"] = str(alert.stop_price)
        
        # Add leverage if provided
        if alert.leverage is not None:
            request["leverage"] = str(alert.leverage)
        
        return cls(**request)


class TradeResponse(BaseModel):
    """Model for trade execution responses."""
    
    success: bool = Field(..., description="Whether the trade was successful")
    order_id: Optional[str] = Field(default=None, description="Order ID if successful")
    error: Optional[str] = Field(default=None, description="Error message if unsuccessful")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional details")
    
    @classmethod
    def success_response(cls, order_id: str, details: Optional[Dict[str, Any]] = None) -> 'TradeResponse':
        """
        Create a success response.
        
        Args:
            order_id: The order ID
            details: Additional details
            
        Returns:
            A TradeResponse object
        """
        return cls(
            success=True,
            order_id=order_id,
            details=details
        )
    
    @classmethod
    def error_response(cls, error: str, details: Optional[Dict[str, Any]] = None) -> 'TradeResponse':
        """
        Create an error response.
        
        Args:
            error: The error message
            details: Additional details
            
        Returns:
            A TradeResponse object
        """
        return cls(
            success=False,
            error=error,
            details=details
        )