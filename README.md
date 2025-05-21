# TradingView to Kraken Webhook Service

A webhook service that receives TradingView alerts and executes trades on the Kraken cryptocurrency exchange. Built with Python and FastAPI, designed for deployment to Google Cloud Run.

## Features

- **Webhook Receiver**: Accepts and validates incoming TradingView alerts
- **Payload Processor**: Parses and validates JSON structure
- **Trade Executor**: Interacts with Kraken API to execute trades
- **Secure Credential Management**: Supports environment variables and Google Cloud Secret Manager
- **Error Handling & Logging**: Comprehensive error handling and structured logging
- **Cloud-Ready**: Designed for deployment to Google Cloud Run

## Architecture

The service consists of the following components:

1. **Webhook Receiver**: FastAPI endpoints that accept incoming webhook requests
2. **Payload Processor**: Validates and processes the webhook payload
3. **Trade Executor**: Executes trades on Kraken using the krakenex library
4. **Secret Manager**: Securely manages API credentials
5. **Logging**: Structured logging with context for monitoring and debugging

## Setup

### Prerequisites

- Python 3.8+
- Kraken API key and secret
- TradingView Pro account (for sending webhook alerts)

### Local Development

1. Clone the repository:
   ```
   git clone <repository-url>
   cd KrakenWebhook
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```
   cp .env.example .env
   # Edit .env with your Kraken API credentials and other settings
   ```

4. Run the application:
   ```
   python -m src.main
   ```

5. The service will be available at http://localhost:8080

### Docker

Build and run the Docker container:

```
docker build -t tradingview-kraken-webhook .
docker run -p 8080:8080 --env-file .env tradingview-kraken-webhook
```

## Deployment to Google Cloud Run

### Using Google Cloud Build

1. Build the container image:
   ```
   gcloud builds submit --tag gcr.io/PROJECT_ID/tradingview-kraken-webhook
   ```

2. Deploy to Cloud Run:
   ```
   gcloud run deploy tradingview-kraken-webhook \
     --image gcr.io/PROJECT_ID/tradingview-kraken-webhook \
     --platform managed \
     --region REGION \
     --allow-unauthenticated
   ```

3. Set environment variables:
   ```
   gcloud run services update tradingview-kraken-webhook \
     --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO"
   ```

### Using Secret Manager for API Keys

1. Create secrets in Google Cloud Secret Manager:
   ```
   echo -n "your-api-key" | gcloud secrets create KRAKEN_API_KEY --data-file=-
   echo -n "your-api-secret" | gcloud secrets create KRAKEN_API_SECRET --data-file=-
   echo -n "your-webhook-secret" | gcloud secrets create WEBHOOK_SECRET --data-file=-
   ```

2. Grant the Cloud Run service account access to the secrets:
   ```
   gcloud secrets add-iam-policy-binding KRAKEN_API_KEY \
     --member="serviceAccount:SERVICE_ACCOUNT_EMAIL" \
     --role="roles/secretmanager.secretAccessor"
   
   # Repeat for other secrets
   ```

3. Set the GCP_PROJECT_ID environment variable:
   ```
   gcloud run services update tradingview-kraken-webhook \
     --set-env-vars="GCP_PROJECT_ID=YOUR_PROJECT_ID"
   ```

## TradingView Setup

1. Create a TradingView alert with webhook action
2. Set the webhook URL to your deployed service: `https://your-service-url/webhook/tradingview`
3. Format the alert message as JSON with the required fields:
   ```json
   {
     "symbol": "XBTUSD",
     "side": "buy",
     "order_type": "market",
     "volume": 0.001
   }
   ```

4. For added security, set the `X-Signature` header in TradingView using HMAC-SHA256 with your webhook secret

## API Documentation

Once the service is running, you can access the OpenAPI documentation at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## License

[MIT License](LICENSE)