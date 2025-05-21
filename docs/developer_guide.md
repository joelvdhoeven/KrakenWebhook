# Developer Guide: TradingView to Kraken Webhook Service

This guide provides detailed information about the codebase structure, components, and how to extend the TradingView to Kraken webhook service.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Codebase Structure](#codebase-structure)
- [Key Components](#key-components)
- [Data Flow](#data-flow)
- [Extending the Service](#extending-the-service)
- [Testing](#testing)
- [Deployment](#deployment)
- [Best Practices](#best-practices)

## Architecture Overview

The TradingView to Kraken webhook service follows a modular architecture with clear separation of concerns:

1. **Webhook Receiver**: Handles HTTP requests and responses
2. **Payload Processor**: Validates and transforms incoming data
3. **Trade Executor**: Interacts with the Kraken API
4. **Secret Manager**: Manages sensitive credentials
5. **Logging**: Provides structured logging throughout the application

This architecture allows for:
- Independent testing of components
- Easy extension of functionality
- Clear separation of business logic from infrastructure concerns

## Codebase Structure

```
KrakenWebhook/
├── config/                 # Configuration management
│   └── config.py           # Configuration loading and validation
├── docs/                   # Documentation
├── examples/               # Example payloads and configurations
│   └── tradingview_alert.json  # Example TradingView alert payload
├── scripts/                # Utility scripts
│   └── test_webhook.py     # Script for testing the webhook
├── src/                    # Source code
│   ├── __init__.py
│   ├── main.py             # Application entry point
│   ├── executor/           # Trade execution
│   │   ├── __init__.py
│   │   └── kraken_executor.py  # Kraken API integration
│   ├── processor/          # Payload processing
│   │   ├── __init__.py
│   │   └── payload_processor.py  # Webhook payload validation
│   ├── utils/              # Utility modules
│   │   ├── __init__.py
│   │   ├── logging.py      # Logging configuration
│   │   ├── models.py       # Data models
│   │   └── secrets.py      # Secret management
│   └── webhook/            # Webhook handling
│       ├── __init__.py
│       └── receiver.py     # FastAPI routes
├── tests/                  # Test suite
│   └── test_webhook.py     # Webhook tests
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── Dockerfile              # Docker configuration
├── pytest.ini              # Pytest configuration
├── README.md               # Project overview
└── requirements.txt        # Python dependencies
```

## Key Components

### FastAPI Application (`src/main.py`)

The main application module initializes the FastAPI application, configures middleware, exception handlers, and includes the webhook router.

Key features:
- CORS middleware configuration
- Global exception handling
- Request ID middleware for tracing
- Startup and shutdown event handlers

### Webhook Receiver (`src/webhook/receiver.py`)

Handles incoming HTTP requests from TradingView and forwards them to the payload processor.

Endpoints:
- `POST /webhook/tradingview`: Executes trades based on TradingView alerts
- `POST /webhook/tradingview/validate`: Validates trade requests without executing them
- `GET /webhook/health`: Health check endpoint

### Payload Processor (`src/processor/payload_processor.py`)

Validates and processes incoming webhook payloads from TradingView.

Key responsibilities:
- JSON payload parsing
- Signature validation using HMAC-SHA256
- Conversion to internal data models
- Input validation using Pydantic

### Trade Executor (`src/executor/kraken_executor.py`)

Handles the execution of trades on the Kraken exchange using the krakenex library.

Key features:
- Kraken API initialization and connection management
- Trade execution with error handling
- Order validation
- Account balance and open orders retrieval

### Data Models (`src/utils/models.py`)

Defines the structure of incoming webhook payloads and outgoing trade requests using Pydantic.

Key models:
- `TradingViewAlert`: Represents incoming TradingView alert data
- `TradeRequest`: Represents a trade request to Kraken
- `TradeResponse`: Represents the result of a trade execution

### Secret Management (`src/utils/secrets.py`)

Manages sensitive credentials from environment variables or Google Cloud Secret Manager.

Features:
- Fallback mechanism (Secret Manager → environment variables)
- Credential caching
- Secure logging (masking sensitive values)

### Logging (`src/utils/logging.py`)

Configures structured logging using structlog.

Features:
- JSON formatting for production
- Console formatting for development
- Request ID tracking
- Context-aware logging

### Configuration (`config/config.py`)

Manages application configuration from environment variables.

Features:
- Environment-specific settings
- Configuration validation
- Secure configuration display (masking sensitive values)

## Data Flow

1. TradingView sends a webhook alert to the `/webhook/tradingview` endpoint
2. The webhook receiver passes the request to the payload processor
3. The payload processor:
   - Validates the signature (if configured)
   - Parses the JSON payload
   - Validates the payload structure
   - Converts it to a `TradingViewAlert` model
   - Converts the alert to a `TradeRequest` model
4. The webhook receiver passes the trade request to the trade executor
5. The trade executor:
   - Initializes the Kraken API (if not already initialized)
   - Executes the trade on Kraken
   - Returns a `TradeResponse` with the result
6. The webhook receiver returns a JSON response to the client

## Extending the Service

### Adding New Order Types

To add support for new order types:

1. Update the `OrderType` enum in `src/utils/models.py`
2. Add validation logic in the `TradingViewAlert` model
3. Update the `from_tradingview_alert` method in the `TradeRequest` model
4. Add tests for the new order type

### Supporting Additional Exchanges

To add support for a new exchange:

1. Create a new executor module (e.g., `src/executor/binance_executor.py`)
2. Implement the same interface as `KrakenExecutor`
3. Add configuration for the new exchange in `config/config.py`
4. Create a factory in `src/main.py` to select the appropriate executor
5. Add new routes in `src/webhook/receiver.py` for the new exchange

### Adding Custom Validation Rules

To add custom validation rules:

1. Add validators to the `TradingViewAlert` model in `src/utils/models.py`
2. Update the `process_request` method in `src/processor/payload_processor.py`

### Implementing Advanced Authentication

To implement more advanced authentication:

1. Create a new middleware in `src/utils/auth.py`
2. Add the middleware to the FastAPI application in `src/main.py`
3. Update the configuration in `config/config.py`

## Testing

### Unit Tests

The project uses pytest for unit testing. Run the tests with:

```bash
pytest
```

Key test files:
- `tests/test_webhook.py`: Tests for the webhook receiver
- Add more test files for each component

### Integration Tests

For integration testing:

1. Use the `scripts/test_webhook.py` script to send test requests
2. Create a test environment with a Kraken sandbox account
3. Use environment variables to configure the test environment

### Mocking External Services

For testing without calling external services:

1. Use the `unittest.mock` library to mock the Kraken API
2. Create fixture data in `tests/fixtures/`
3. Use dependency injection in FastAPI to replace real services with mocks

## Deployment

### Docker

The service can be deployed using Docker:

```bash
docker build -t tradingview-kraken-webhook .
docker run -p 8080:8080 --env-file .env tradingview-kraken-webhook
```

### Google Cloud Run

For deployment to Google Cloud Run:

1. Build and push the container:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/tradingview-kraken-webhook
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy tradingview-kraken-webhook \
     --image gcr.io/PROJECT_ID/tradingview-kraken-webhook \
     --platform managed \
     --region REGION \
     --allow-unauthenticated
   ```

3. Set environment variables:
   ```bash
   gcloud run services update tradingview-kraken-webhook \
     --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO"
   ```

### Kubernetes

For Kubernetes deployment:

1. Create Kubernetes manifests in a `k8s/` directory
2. Use Kubernetes secrets for sensitive information
3. Configure health checks using the `/webhook/health` endpoint

## Best Practices

### Error Handling

- Use structured error responses
- Log errors with context
- Return appropriate HTTP status codes
- Provide clear error messages to clients

### Logging

- Use structured logging with context
- Include request IDs for tracing
- Mask sensitive information
- Use appropriate log levels

### Security

- Validate webhook signatures
- Use HTTPS for all endpoints
- Store secrets securely
- Implement rate limiting
- Validate all input

### Performance

- Use connection pooling for Kraken API
- Implement caching where appropriate
- Monitor response times
- Use async/await for I/O-bound operations

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all public functions and classes
- Use meaningful variable and function names