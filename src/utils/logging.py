"""
Logging configuration for the TradingView to Kraken webhook service.
Sets up structured logging with appropriate formatters and handlers.
"""
import logging
import sys
import time
from typing import Dict, Any, Optional

import structlog
from structlog.types import Processor

from config.config import config


def configure_logging() -> None:
    """Configure logging for the application."""
    # Set up standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=config.get_log_level(),
    )

    # Configure structlog
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if config.is_development:
        # Development: pretty console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer()
        ]
    else:
        # Production: JSON for cloud logging
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: The name of the logger, typically __name__
        
    Returns:
        A configured structlog logger
    """
    return structlog.get_logger(name)


class RequestIdMiddleware:
    """Middleware to add request ID to the logging context."""
    
    def __init__(self, app):
        """Initialize the middleware."""
        self.app = app
    
    async def __call__(self, scope, receive, send):
        """Add request ID to the logging context."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Generate a request ID
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Add request ID to the logging context
        with structlog.contextvars.bound_contextvars(request_id=request_id):
            return await self.app(scope, receive, send)