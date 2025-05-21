"""
Main application module for the TradingView to Kraken webhook service.
Sets up the FastAPI application and configures routes, middleware, and logging.
"""
import os
import sys
from typing import Dict, Any

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config.config import config
from src.utils.logging import configure_logging, get_logger, RequestIdMiddleware
from src.webhook.receiver import router as webhook_router

# Configure logging
configure_logging()
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        The configured FastAPI application
    """
    # Create the FastAPI app
    app = FastAPI(
        title="TradingView to Kraken Webhook Service",
        description="A service that receives TradingView alerts and executes trades on Kraken",
        version="1.0.0",
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add request ID middleware
    app.add_middleware(RequestIdMiddleware)
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all unhandled exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "Internal server error",
                "error": str(exc) if config.is_development else "An unexpected error occurred"
            }
        )
    
    # Add routers
    app.include_router(webhook_router)
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        """Handle application startup."""
        logger.info(
            "Starting TradingView to Kraken webhook service",
            environment=config.environment,
            config=config.as_dict()
        )
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Handle application shutdown."""
        logger.info("Shutting down TradingView to Kraken webhook service")
    
    # Add root endpoint
    @app.get("/", tags=["root"])
    async def root() -> Dict[str, Any]:
        """Root endpoint."""
        return {
            "service": "TradingView to Kraken Webhook Service",
            "version": "1.0.0",
            "status": "running",
            "environment": config.environment
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    """Run the application when executed directly."""
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8080"))
    
    # Run with uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=config.is_development
    )