# Configuration Reference: TradingView to Kraken Webhook Service

This document provides a comprehensive reference for all configuration options available in the TradingView to Kraken webhook service.

## Table of Contents

- [Environment Variables](#environment-variables)
- [Configuration File](#configuration-file)
- [Secret Management](#secret-management)
- [Logging Configuration](#logging-configuration)
- [Docker Configuration](#docker-configuration)
- [Google Cloud Run Configuration](#google-cloud-run-configuration)
- [Advanced Configuration](#advanced-configuration)

## Environment Variables

The service is primarily configured through environment variables. These can be set directly in the environment or through a `.env` file.

### Required Environment Variables

These variables are required in production environments:

| Variable | Description | Example |
|----------|-------------|---------|
| `KRAKEN_API_KEY` | Kraken API key | `abcdef123456` |
| `KRAKEN_API_SECRET` | Kraken API secret | `ABCDEFGhijklmnopqrstuvwxyz0123456789+/=` |
| `WEBHOOK_SECRET` | Secret for webhook signature validation | `your_webhook_secret_here` |

### Optional Environment Variables

These variables have default values but can be customized:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ENVIRONMENT` | Deployment environment | `development` | `production` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `PORT` | Port to run the service on | `8080` | `3000` |
| `GCP_PROJECT_ID` | Google Cloud project ID for Secret Manager | `None` | `your-project-id` |

### Environment-Specific Settings

#### Development Environment

```
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

In development mode:
- Detailed error messages are returned in responses
- Console-formatted logs are used
- Webhook signature validation is optional

#### Production Environment

```
ENVIRONMENT=production
LOG_LEVEL=INFO
```

In production mode:
- Generic error messages are returned in responses
- JSON-formatted logs are used
- Webhook signature validation is required

## Configuration File

The service uses a configuration module at `config/config.py` that loads environment variables and provides access to configuration values.

### Configuration Class

```python
class Config:
    def __init__(self):
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
```

### Configuration Validation

The configuration module validates required settings based on the environment:

```python
def _validate_config(self):
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
```

## Secret Management

The service supports two methods for managing secrets:

### Environment Variables

Secrets can be provided directly as environment variables:

```
KRAKEN_API_KEY=your_api_key_here
KRAKEN_API_SECRET=your_api_secret_here
WEBHOOK_SECRET=your_webhook_secret_here
```

### Google Cloud Secret Manager

For production deployments, Google Cloud Secret Manager is recommended:

1. Set the `GCP_PROJECT_ID` environment variable:
   ```
   GCP_PROJECT_ID=your-project-id
   ```

2. Create secrets in Google Cloud Secret Manager:
   ```bash
   echo -n "your-api-key" | gcloud secrets create KRAKEN_API_KEY --data-file=-
   echo -n "your-api-secret" | gcloud secrets create KRAKEN_API_SECRET --data-file=-
   echo -n "your-webhook-secret" | gcloud secrets create WEBHOOK_SECRET --data-file=-
   ```

3. Grant the service account access to the secrets:
   ```bash
   gcloud secrets add-iam-policy-binding KRAKEN_API_KEY \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/secretmanager.secretAccessor"
   ```

The service will automatically retrieve secrets from Secret Manager if available, falling back to environment variables if not found.

## Logging Configuration

The service uses structured logging with `structlog`.

### Log Levels

Available log levels (in increasing order of severity):

| Level | Description |
|-------|-------------|
| `DEBUG` | Detailed information for debugging |
| `INFO` | General operational information |
| `WARNING` | Warning events that might require attention |
| `ERROR` | Error events that might still allow the application to continue |
| `CRITICAL` | Critical events that may cause the application to terminate |

### Log Formats

The logging format depends on the environment:

- **Development**: Human-readable console format
- **Production**: JSON format for machine parsing

### Log Context

Logs include contextual information:

- Request ID for tracing requests
- Environment information
- Component information
- Additional context specific to each log entry

Example log entry (JSON format):
```json
{
  "timestamp": "2023-04-15T12:34:56.789Z",
  "level": "info",
  "event": "Trade executed successfully",
  "request_id": "1234-5678-90ab-cdef",
  "order_id": "OQCLML-BW3P3-BUCMWZ",
  "symbol": "XBTUSD",
  "side": "buy"
}
```

### Configuring Logging

Logging is configured in `src/utils/logging.py`:

```python
def configure_logging():
    """Configure structured logging."""
    log_level = config.get_log_level()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            format_processor,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

## Docker Configuration

The service includes a Dockerfile for containerized deployment.

### Environment Variables in Docker

When running with Docker, environment variables can be passed using the `--env-file` flag:

```bash
docker run -p 8080:8080 --env-file .env tradingview-kraken-webhook
```

### Docker Compose Example

```yaml
version: '3'
services:
  webhook:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      - GCP_PROJECT_ID=your-project-id
    volumes:
      - /path/to/service-account-key.json:/app/service-account-key.json
    restart: unless-stopped
```

## Google Cloud Run Configuration

The service is designed for deployment to Google Cloud Run.

### Environment Variables in Cloud Run

Set environment variables during deployment:

```bash
gcloud run deploy tradingview-kraken-webhook \
  --image gcr.io/PROJECT_ID/tradingview-kraken-webhook \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,GCP_PROJECT_ID=PROJECT_ID"
```

### Cloud Run Service Configuration

| Setting | Recommended Value | Description |
|---------|------------------|-------------|
| Memory | 256Mi | Minimum memory allocation |
| CPU | 1 | CPU allocation |
| Concurrency | 80 | Maximum concurrent requests |
| Timeout | 300s | Request timeout |
| Min instances | 0 | Minimum number of instances |
| Max instances | 10 | Maximum number of instances |

### Cloud Build Configuration

The service includes a `cloudbuild.yaml` file for CI/CD with Google Cloud Build:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/tradingview-kraken-webhook:$COMMIT_SHA', '.']

  # Push the container image to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/tradingview-kraken-webhook:$COMMIT_SHA']

  # Deploy container image to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'tradingview-kraken-webhook'
      - '--image'
      - 'gcr.io/$PROJECT_ID/tradingview-kraken-webhook:$COMMIT_SHA'
      - '--region'
      - '${_REGION}'
      - '--platform'
      - 'managed'
      - '--allow-unauthenticated'
      - '--set-env-vars'
      - 'ENVIRONMENT=production,LOG_LEVEL=INFO,GCP_PROJECT_ID=$PROJECT_ID'
```

## Advanced Configuration

### Custom Middleware

The service uses several middleware components that can be customized:

#### Request ID Middleware

Adds a unique request ID to each request for tracing:

```python
class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add a request ID to each request."""
    
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
```

#### CORS Middleware

Controls Cross-Origin Resource Sharing:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Customize for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Customizing Trade Execution

The trade executor can be customized by modifying `src/executor/kraken_executor.py`:

#### Initialization Cooldown

Controls how often the service attempts to initialize the Kraken API:

```python
self._init_cooldown = 60  # seconds to wait between initialization attempts
```

#### Custom Order Parameters

Additional order parameters can be added to the `TradeRequest` model in `src/utils/models.py`.

### Webhook Payload Customization

To support custom fields in the webhook payload:

1. Add fields to the `TradingViewAlert` model in `src/utils/models.py`
2. Update the `from_tradingview_alert` method in the `TradeRequest` model
3. Add validation logic as needed

Example custom field:
```python
class TradingViewAlert(BaseModel):
    # Existing fields...
    
    # Custom fields
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom fields for extended functionality")