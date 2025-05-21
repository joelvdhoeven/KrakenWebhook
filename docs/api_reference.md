# API Reference: TradingView to Kraken Webhook Service

This document provides detailed information about the API endpoints available in the TradingView to Kraken webhook service.

## Table of Contents

- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Root Endpoint](#root-endpoint)
  - [Health Check](#health-check)
  - [TradingView Webhook](#tradingview-webhook)
  - [Validate TradingView Webhook](#validate-tradingview-webhook)
- [Request and Response Formats](#request-and-response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Base URL

When running locally, the base URL is:
```
http://localhost:8080
```

When deployed to Google Cloud Run, the base URL will be:
```
https://tradingview-kraken-webhook-[hash].run.app
```

Or your custom domain if configured.

## Authentication

The webhook endpoints use HMAC-SHA256 signature validation for authentication:

1. Generate a signature by creating an HMAC-SHA256 hash of the request body using your webhook secret
2. Include this signature in the `X-Signature` header of your request

Example signature generation in Python:
```python
import hmac
import hashlib
import json

def generate_signature(payload, secret):
    payload_bytes = json.dumps(payload).encode('utf-8')
    return hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()

# Usage
payload = {"symbol": "XBTUSD", "side": "buy", "order_type": "market", "volume": 0.001}
signature = generate_signature(payload, "your_webhook_secret")
```

## Endpoints

### Root Endpoint

Returns basic information about the service.

- **URL**: `/`
- **Method**: `GET`
- **Authentication**: None

#### Response

```json
{
  "service": "TradingView to Kraken Webhook Service",
  "version": "1.0.0",
  "status": "running",
  "environment": "development"
}
```

#### Status Codes

- `200 OK`: Service is running

### Health Check

Simple health check endpoint to verify the service is operational.

- **URL**: `/webhook/health`
- **Method**: `GET`
- **Authentication**: None

#### Response

```json
{
  "status": "ok",
  "service": "tradingview-kraken-webhook"
}
```

#### Status Codes

- `200 OK`: Service is healthy

### TradingView Webhook

Receives TradingView alerts and executes trades on Kraken.

- **URL**: `/webhook/tradingview`
- **Method**: `POST`
- **Authentication**: HMAC-SHA256 signature in `X-Signature` header (if `WEBHOOK_SECRET` is configured)

#### Request Body

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "price": null,
  "leverage": null,
  "stop_price": null,
  "strategy_name": "Golden Cross Strategy",
  "alert_message": "BTC/USD crossed above the 50-day moving average",
  "custom_fields": {
    "timeframe": "1h",
    "signal_strength": "strong"
  }
}
```

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair symbol (e.g., "XBTUSD") |
| `side` | string | Order side: "buy" or "sell" |

#### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `order_type` | string | Order type: "market", "limit", "stop-loss", "take-profit", "stop-loss-limit", "take-profit-limit" |
| `volume` | number | Order volume/quantity |
| `price` | number | Limit price (required for limit orders) |
| `leverage` | integer | Leverage for margin trading |
| `stop_price` | number | Stop price for stop orders |
| `strategy_name` | string | Name of the trading strategy |
| `alert_message` | string | Alert message from TradingView |
| `custom_fields` | object | Custom fields for extended functionality |

#### Response

```json
{
  "success": true,
  "message": "Order executed",
  "order_id": "OQCLML-BW3P3-BUCMWZ",
  "error": null,
  "trade_details": {
    "symbol": "XBTUSD",
    "side": "buy",
    "order_type": "market",
    "volume": 0.001,
    "price": null
  }
}
```

#### Status Codes

- `200 OK`: Trade executed successfully
- `400 Bad Request`: Invalid request or trade execution failed
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Server error

### Validate TradingView Webhook

Validates a TradingView alert without executing a trade.

- **URL**: `/webhook/tradingview/validate`
- **Method**: `POST`
- **Authentication**: HMAC-SHA256 signature in `X-Signature` header (if `WEBHOOK_SECRET` is configured)

#### Request Body

Same as the TradingView webhook endpoint.

#### Response

```json
{
  "success": true,
  "message": "Validation successful",
  "error": null,
  "trade_details": {
    "symbol": "XBTUSD",
    "side": "buy",
    "order_type": "market",
    "volume": 0.001,
    "price": null
  }
}
```

#### Status Codes

- `200 OK`: Validation successful
- `400 Bad Request`: Invalid request or validation failed
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Server error

## Request and Response Formats

### Content Type

All requests and responses use JSON format with content type `application/json`.

### Date Format

Dates and times are represented in ISO 8601 format: `YYYY-MM-DDTHH:MM:SSZ`.

### Numeric Values

- `volume` is represented as a decimal number with up to 8 decimal places
- `price` is represented as a decimal number with precision appropriate for the trading pair

## Error Handling

### Error Response Format

```json
{
  "success": false,
  "message": "Error message",
  "error": "Detailed error description",
  "trade_details": {
    "symbol": "XBTUSD",
    "side": "buy",
    "order_type": "market",
    "volume": 0.001,
    "price": null
  }
}
```

### Common Error Codes

| Status Code | Description | Possible Causes |
|-------------|-------------|----------------|
| 400 | Bad Request | Invalid JSON, missing required fields, invalid order parameters |
| 401 | Unauthorized | Missing or invalid signature |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error, Kraken API issues |

## Rate Limiting

The service implements basic rate limiting to prevent abuse:

- Maximum of 60 requests per minute per IP address
- Cooldown period after failed initialization attempts

When rate limits are exceeded, the service returns a `429 Too Many Requests` response.

## Examples

### Example 1: Market Buy Order

#### Request

```http
POST /webhook/tradingview HTTP/1.1
Host: your-service-url
Content-Type: application/json
X-Signature: 5a1e02b1f7d9c9370e9d33f121aa4f26e8e7a9b3c80e111e3f3d7e4f2f6a1b2c

{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Golden Cross Strategy",
  "alert_message": "BTC/USD crossed above the 50-day moving average"
}
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Order executed",
  "order_id": "OQCLML-BW3P3-BUCMWZ",
  "error": null,
  "trade_details": {
    "symbol": "XBTUSD",
    "side": "buy",
    "order_type": "market",
    "volume": 0.001,
    "price": null
  }
}
```

### Example 2: Limit Sell Order

#### Request

```http
POST /webhook/tradingview HTTP/1.1
Host: your-service-url
Content-Type: application/json
X-Signature: 7c2e4d8a9f1b3c5e7a9b3c5e7a9b3c5e7a9b3c5e7a9b3c5e7a9b3c5e7a9b3c5e

{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "limit",
  "volume": 0.1,
  "price": 3500,
  "strategy_name": "RSI Overbought",
  "alert_message": "ETH/USD RSI above 70"
}
```

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Order executed",
  "order_id": "OQCLML-BW3P3-BUCMWZ",
  "error": null,
  "trade_details": {
    "symbol": "ETHUSD",
    "side": "sell",
    "order_type": "limit",
    "volume": 0.1,
    "price": 3500
  }
}
```

### Example 3: Validation Error

#### Request

```http
POST /webhook/tradingview HTTP/1.1
Host: your-service-url
Content-Type: application/json
X-Signature: 9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b

{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "limit",
  "volume": 0.001
}
```

#### Response

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "success": false,
  "message": "Order failed",
  "error": "price is required for limit orders",
  "trade_details": {
    "symbol": "XBTUSD",
    "side": "buy",
    "order_type": "limit",
    "volume": 0.001,
    "price": null
  }
}
```

### Example 4: Authentication Error

#### Request

```http
POST /webhook/tradingview HTTP/1.1
Host: your-service-url
Content-Type: application/json
X-Signature: invalid-signature

{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001
}
```

#### Response

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "success": false,
  "message": "Unauthorized",
  "error": "Invalid signature",
  "trade_details": null
}