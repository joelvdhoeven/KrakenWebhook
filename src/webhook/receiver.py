"""
Webhook receiver for TradingView alerts.
Handles incoming HTTP requests from TradingView and forwards them to the payload processor.
"""
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from src.utils.logging import get_logger
from src.processor.payload_processor import payload_processor
from src.executor.kraken_executor import kraken_executor
from src.utils.models import TradeResponse

logger = get_logger(__name__)

# Create a router for webhook endpoints
router = APIRouter(tags=["webhook"])


@router.post("/webhook/tradingview", response_model=Dict[str, Any])
async def tradingview_webhook(request: Request) -> Dict[str, Any]:
    """
    Handle incoming webhook requests from TradingView.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        A JSON response with the result of the trade execution
    """
    try:
        # Process the webhook payload
        alert, trade_request = await payload_processor.process_request(request)
        
        # Execute the trade
        trade_response = kraken_executor.execute_trade(trade_request)
        
        # Prepare the response
        response_data = {
            "success": trade_response.success,
            "message": f"Order {'executed' if trade_response.success else 'failed'}",
            "order_id": trade_response.order_id,
            "error": trade_response.error,
            "trade_details": {
                "symbol": alert.symbol,
                "side": alert.side,
                "order_type": alert.order_type,
                "volume": alert.volume,
                "price": alert.price,
            }
        }
        
        # Log the result
        if trade_response.success:
            logger.info(
                "Trade executed successfully",
                order_id=trade_response.order_id,
                symbol=alert.symbol,
                side=alert.side
            )
        else:
            logger.error(
                "Trade execution failed",
                error=trade_response.error,
                symbol=alert.symbol,
                side=alert.side
            )
        
        # Return success or error response
        status_code = status.HTTP_200_OK if trade_response.success else status.HTTP_400_BAD_REQUEST
        return JSONResponse(content=response_data, status_code=status_code)
        
    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions
        raise
    
    except Exception as e:
        # Log and return a 500 error for unexpected exceptions
        logger.error("Unexpected error processing webhook", error=str(e))
        return JSONResponse(
            content={
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/webhook/tradingview/validate", response_model=Dict[str, Any])
async def validate_tradingview_webhook(request: Request) -> Dict[str, Any]:
    """
    Validate a webhook request without executing a trade.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        A JSON response with the validation result
    """
    try:
        # Process the webhook payload
        alert, trade_request = await payload_processor.process_request(request)
        
        # Validate the trade request
        trade_response = kraken_executor.validate_trade(trade_request)
        
        # Prepare the response
        response_data = {
            "success": trade_response.success,
            "message": f"Validation {'successful' if trade_response.success else 'failed'}",
            "error": trade_response.error,
            "trade_details": {
                "symbol": alert.symbol,
                "side": alert.side,
                "order_type": alert.order_type,
                "volume": alert.volume,
                "price": alert.price,
            }
        }
        
        # Log the result
        if trade_response.success:
            logger.info(
                "Trade validation successful",
                symbol=alert.symbol,
                side=alert.side
            )
        else:
            logger.error(
                "Trade validation failed",
                error=trade_response.error,
                symbol=alert.symbol,
                side=alert.side
            )
        
        # Return success or error response
        status_code = status.HTTP_200_OK if trade_response.success else status.HTTP_400_BAD_REQUEST
        return JSONResponse(content=response_data, status_code=status_code)
        
    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions
        raise
    
    except Exception as e:
        # Log and return a 500 error for unexpected exceptions
        logger.error("Unexpected error validating webhook", error=str(e))
        return JSONResponse(
            content={
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/webhook/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        A JSON response with the service status
    """
    return {
        "status": "ok",
        "service": "tradingview-kraken-webhook"
    }