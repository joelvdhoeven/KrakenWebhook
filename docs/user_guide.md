# User Guide: TradingView to Kraken Webhook Service

This guide explains how to set up and use the TradingView to Kraken webhook service to execute automated trades on the Kraken exchange based on TradingView alerts.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setting Up TradingView Alerts](#setting-up-tradingview-alerts)
- [Alert Payload Format](#alert-payload-format)
- [Order Types](#order-types)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Prerequisites

Before you begin, ensure you have:

1. A TradingView Pro account (Pro, Pro+ or Premium) that supports webhook alerts
2. A Kraken account with API access enabled
3. The TradingView to Kraken webhook service deployed and running

## Setting Up TradingView Alerts

### Creating an Alert in TradingView

1. Open TradingView and navigate to your chart
2. Click on the "Alerts" button in the right sidebar
3. Click "Create Alert"
4. Configure your alert conditions (e.g., price crossing above a moving average)
5. In the "Alert actions" section:
   - Enable "Webhook URL"
   - Enter your webhook URL: `https://your-service-url/webhook/tradingview`
   - Set the alert message to the JSON payload (see format below)

### Configuring the Alert Message

The alert message must be a valid JSON object with the required fields. Here's a basic example:

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001
}
```

### Adding Security Headers (Recommended)

For enhanced security, add a custom header with a signature:

1. In TradingView's alert setup, click "More Options" under the webhook section
2. Add a custom header:
   - Name: `X-Signature`
   - Value: Generate an HMAC-SHA256 signature of your JSON payload using your webhook secret

Note: Since TradingView doesn't natively support generating signatures, you may need to use a third-party service or custom solution to generate and update these signatures.

## Alert Payload Format

### Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| `symbol` | Trading pair symbol | `"XBTUSD"` |
| `side` | Order side: `buy` or `sell` | `"buy"` |

### Optional Fields

| Field | Description | Default | Example |
|-------|-------------|---------|---------|
| `order_type` | Order type | `"market"` | `"limit"` |
| `volume` | Order volume/quantity | - | `0.001` |
| `price` | Limit price (required for limit orders) | - | `50000` |
| `leverage` | Leverage for margin trading | - | `5` |
| `stop_price` | Stop price for stop orders | - | `49000` |
| `strategy_name` | Name of the trading strategy | - | `"Golden Cross"` |
| `alert_message` | Alert message from TradingView | - | `"Price crossed above MA"` |
| `custom_fields` | Custom fields for extended functionality | `{}` | `{"timeframe": "1h"}` |

### Symbol Format

The service supports various symbol formats and will attempt to normalize them:

- `BTCUSD` → `XBTUSD`
- `BTC/USD` → `XBTUSD`
- `ETHUSD` → `ETHUSD`

For other pairs, use the exact symbol format as required by Kraken.

## Order Types

The service supports the following order types:

### Market Orders

Executes immediately at the current market price:

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001
}
```

### Limit Orders

Executes only when the market reaches your specified price:

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "limit",
  "volume": 0.001,
  "price": 45000
}
```

### Stop Loss Orders

Triggers a market order when price reaches or goes below the stop price:

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "stop-loss",
  "volume": 0.001,
  "stop_price": 42000
}
```

### Take Profit Orders

Triggers a market order when price reaches or goes above the stop price:

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "take-profit",
  "volume": 0.001,
  "stop_price": 55000
}
```

### Stop Loss Limit Orders

Triggers a limit order when price reaches the stop price:

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "stop-loss-limit",
  "volume": 0.001,
  "price": 41900,
  "stop_price": 42000
}
```

### Take Profit Limit Orders

Triggers a limit order when price reaches the stop price:

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "take-profit-limit",
  "volume": 0.001,
  "price": 55100,
  "stop_price": 55000
}
```

## Security

### Webhook Signature Validation

For enhanced security, the service can validate webhook requests using HMAC-SHA256 signatures:

1. Set a strong, random `WEBHOOK_SECRET` in your service configuration
2. When sending requests, include an `X-Signature` header with the HMAC-SHA256 signature of the request body

### Testing Signature Validation

You can test signature validation using the included test script:

```bash
python scripts/test_webhook.py --url http://localhost:8080/webhook/tradingview --payload examples/tradingview_alert.json --secret your_webhook_secret
```

## Troubleshooting

### Common Issues

1. **Invalid JSON payload**: Ensure your TradingView alert message is valid JSON
2. **Missing required fields**: Check that your payload includes at least `symbol` and `side`
3. **Invalid signature**: Verify that your webhook secret matches between the service and your signature generation
4. **Order validation failures**: Use the validation endpoint to test orders without executing them

### Validation Endpoint

To validate a trade request without executing it:

```bash
python scripts/test_webhook.py --url http://localhost:8080/webhook/tradingview --payload examples/tradingview_alert.json --secret your_webhook_secret --validate
```

### Checking Logs

If you're running the service locally or have access to the logs, check for error messages:

```bash
# Set LOG_LEVEL=DEBUG for more detailed logs
LOG_LEVEL=DEBUG python -m src.main
```

## Examples

### Simple Market Buy

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001
}
```

### Limit Sell with Strategy Information

```json
{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "limit",
  "volume": 0.1,
  "price": 3500,
  "strategy_name": "RSI Overbought",
  "alert_message": "ETH/USD RSI above 70",
  "custom_fields": {
    "timeframe": "4h",
    "signal_strength": "strong",
    "rsi_value": 78.5
  }
}
```

### Stop Loss with Leverage

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "stop-loss",
  "volume": 0.005,
  "stop_price": 42000,
  "leverage": 3,
  "strategy_name": "Trend Following",
  "alert_message": "BTC/USD broke support level"
}