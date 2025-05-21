# Trading Examples: TradingView to Kraken Webhook Service

This document provides examples of different trading scenarios and the corresponding JSON payloads to send to the webhook service.

## Table of Contents

- [Basic Order Types](#basic-order-types)
  - [Market Buy Order](#market-buy-order)
  - [Market Sell Order](#market-sell-order)
  - [Limit Buy Order](#limit-buy-order)
  - [Limit Sell Order](#limit-sell-order)
- [Advanced Order Types](#advanced-order-types)
  - [Stop Loss Order](#stop-loss-order)
  - [Take Profit Order](#take-profit-order)
  - [Stop Loss Limit Order](#stop-loss-limit-order)
  - [Take Profit Limit Order](#take-profit-limit-order)
- [Trading Strategies](#trading-strategies)
  - [Moving Average Crossover](#moving-average-crossover)
  - [RSI Overbought/Oversold](#rsi-overboughtoversold)
  - [Bollinger Band Breakout](#bollinger-band-breakout)
  - [MACD Crossover](#macd-crossover)
- [Risk Management](#risk-management)
  - [Position Sizing](#position-sizing)
  - [Leveraged Trading](#leveraged-trading)
  - [Scaling In/Out](#scaling-inout)
- [Multi-Pair Trading](#multi-pair-trading)
  - [Bitcoin and Ethereum](#bitcoin-and-ethereum)
  - [Altcoin Trading](#altcoin-trading)

## Basic Order Types

### Market Buy Order

A market buy order executes immediately at the current market price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Simple Market Buy",
  "alert_message": "BTC/USD buy signal triggered"
}
```

**Use Case:** When you want to enter a position immediately without waiting for a specific price.

### Market Sell Order

A market sell order executes immediately at the current market price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Simple Market Sell",
  "alert_message": "BTC/USD sell signal triggered"
}
```

**Use Case:** When you want to exit a position immediately without waiting for a specific price.

### Limit Buy Order

A limit buy order will only execute at or below the specified price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "limit",
  "volume": 0.001,
  "price": 45000,
  "strategy_name": "Limit Buy at Support",
  "alert_message": "BTC/USD reached support level"
}
```

**Use Case:** When you want to buy at a specific price or better, typically at support levels or during pullbacks.

### Limit Sell Order

A limit sell order will only execute at or above the specified price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "limit",
  "volume": 0.001,
  "price": 55000,
  "strategy_name": "Limit Sell at Resistance",
  "alert_message": "BTC/USD reached resistance level"
}
```

**Use Case:** When you want to sell at a specific price or better, typically at resistance levels or price targets.

## Advanced Order Types

### Stop Loss Order

A stop loss order triggers a market sell order when the price falls to or below the stop price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "stop-loss",
  "volume": 0.001,
  "stop_price": 42000,
  "strategy_name": "Stop Loss Protection",
  "alert_message": "BTC/USD broke support level"
}
```

**Use Case:** To limit losses if the market moves against your position.

### Take Profit Order

A take profit order triggers a market sell order when the price rises to or above the stop price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "take-profit",
  "volume": 0.001,
  "stop_price": 55000,
  "strategy_name": "Take Profit Target",
  "alert_message": "BTC/USD reached profit target"
}
```

**Use Case:** To secure profits when a price target is reached.

### Stop Loss Limit Order

A stop loss limit order triggers a limit sell order when the price falls to or below the stop price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "stop-loss-limit",
  "volume": 0.001,
  "price": 41900,
  "stop_price": 42000,
  "strategy_name": "Stop Loss Limit Protection",
  "alert_message": "BTC/USD broke support level"
}
```

**Use Case:** To limit losses with more control over the execution price than a regular stop loss.

### Take Profit Limit Order

A take profit limit order triggers a limit sell order when the price rises to or above the stop price.

**TradingView Alert Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "take-profit-limit",
  "volume": 0.001,
  "price": 55100,
  "stop_price": 55000,
  "strategy_name": "Take Profit Limit Target",
  "alert_message": "BTC/USD reached profit target"
}
```

**Use Case:** To secure profits with more control over the execution price than a regular take profit order.

## Trading Strategies

### Moving Average Crossover

A strategy that generates buy signals when a shorter-term moving average crosses above a longer-term moving average, and sell signals when it crosses below.

**Buy Signal Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Moving Average Crossover",
  "alert_message": "Golden Cross: 50 EMA crossed above 200 EMA",
  "custom_fields": {
    "timeframe": "1d",
    "fast_ma": "50 EMA",
    "slow_ma": "200 EMA",
    "signal_type": "golden_cross"
  }
}
```

**Sell Signal Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Moving Average Crossover",
  "alert_message": "Death Cross: 50 EMA crossed below 200 EMA",
  "custom_fields": {
    "timeframe": "1d",
    "fast_ma": "50 EMA",
    "slow_ma": "200 EMA",
    "signal_type": "death_cross"
  }
}
```

**Use Case:** Trend-following strategy for medium to long-term trading.

### RSI Overbought/Oversold

A strategy that generates buy signals when the Relative Strength Index (RSI) is oversold and sell signals when it's overbought.

**Buy Signal Payload:**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.01,
  "strategy_name": "RSI Strategy",
  "alert_message": "ETH/USD RSI below 30 (oversold)",
  "custom_fields": {
    "timeframe": "4h",
    "indicator": "RSI",
    "rsi_value": 28.5,
    "signal_type": "oversold"
  }
}
```

**Sell Signal Payload:**

```json
{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.01,
  "strategy_name": "RSI Strategy",
  "alert_message": "ETH/USD RSI above 70 (overbought)",
  "custom_fields": {
    "timeframe": "4h",
    "indicator": "RSI",
    "rsi_value": 72.5,
    "signal_type": "overbought"
  }
}
```

**Use Case:** Mean-reversion strategy for short to medium-term trading.

### Bollinger Band Breakout

A strategy that generates buy signals when the price breaks above the upper Bollinger Band and sell signals when it breaks below the lower Bollinger Band.

**Buy Signal Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Bollinger Band Breakout",
  "alert_message": "BTC/USD broke above upper Bollinger Band",
  "custom_fields": {
    "timeframe": "1h",
    "indicator": "Bollinger Bands",
    "band": "upper",
    "std_dev": 2,
    "signal_type": "breakout"
  }
}
```

**Sell Signal Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Bollinger Band Breakout",
  "alert_message": "BTC/USD broke below lower Bollinger Band",
  "custom_fields": {
    "timeframe": "1h",
    "indicator": "Bollinger Bands",
    "band": "lower",
    "std_dev": 2,
    "signal_type": "breakdown"
  }
}
```

**Use Case:** Volatility breakout strategy for short-term trading.

### MACD Crossover

A strategy that generates buy signals when the MACD line crosses above the signal line and sell signals when it crosses below.

**Buy Signal Payload:**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.01,
  "strategy_name": "MACD Crossover",
  "alert_message": "ETH/USD MACD crossed above signal line",
  "custom_fields": {
    "timeframe": "4h",
    "indicator": "MACD",
    "fast_length": 12,
    "slow_length": 26,
    "signal_length": 9,
    "signal_type": "bullish_crossover"
  }
}
```

**Sell Signal Payload:**

```json
{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.01,
  "strategy_name": "MACD Crossover",
  "alert_message": "ETH/USD MACD crossed below signal line",
  "custom_fields": {
    "timeframe": "4h",
    "indicator": "MACD",
    "fast_length": 12,
    "slow_length": 26,
    "signal_length": 9,
    "signal_type": "bearish_crossover"
  }
}
```

**Use Case:** Trend-following strategy for medium-term trading.

## Risk Management

### Position Sizing

Using a percentage of your account balance to determine position size.

**Fixed Percentage Position Sizing:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.002,
  "strategy_name": "Fixed Percentage Position",
  "alert_message": "BTC/USD buy signal with 2% account risk",
  "custom_fields": {
    "risk_percentage": 2,
    "account_balance": 10000,
    "risk_reward_ratio": 2.5
  }
}
```

**Use Case:** Consistent risk management across different trades.

### Leveraged Trading

Using leverage to increase exposure while managing risk.

**Leveraged Trading Payload:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.01,
  "leverage": 3,
  "strategy_name": "Leveraged Breakout",
  "alert_message": "BTC/USD breakout with 3x leverage",
  "custom_fields": {
    "timeframe": "4h",
    "stop_loss_percentage": 2,
    "take_profit_percentage": 6
  }
}
```

**Use Case:** Increasing potential returns while managing risk with appropriate stop losses.

### Scaling In/Out

Entering or exiting a position in multiple parts.

**Scaling In Payload (First Entry):**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.03,
  "strategy_name": "Scaling In Strategy",
  "alert_message": "ETH/USD initial entry (30%)",
  "custom_fields": {
    "entry_type": "initial",
    "position_percentage": 30,
    "total_planned_entries": 3
  }
}
```

**Scaling In Payload (Second Entry):**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.04,
  "strategy_name": "Scaling In Strategy",
  "alert_message": "ETH/USD second entry (40%)",
  "custom_fields": {
    "entry_type": "second",
    "position_percentage": 40,
    "total_planned_entries": 3
  }
}
```

**Scaling Out Payload (Partial Exit):**

```json
{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "market",
  "volume": 0.05,
  "strategy_name": "Scaling Out Strategy",
  "alert_message": "ETH/USD first take profit (50%)",
  "custom_fields": {
    "exit_type": "partial",
    "position_percentage": 50,
    "total_planned_exits": 2
  }
}
```

**Use Case:** Reducing risk and improving average entry/exit prices.

## Multi-Pair Trading

### Bitcoin and Ethereum

Trading the two largest cryptocurrencies with correlated strategies.

**Bitcoin Buy Signal:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Major Crypto Trend Following",
  "alert_message": "BTC/USD bullish trend confirmation",
  "custom_fields": {
    "timeframe": "1d",
    "market_cap_rank": 1,
    "correlation_group": "major_crypto"
  }
}
```

**Ethereum Buy Signal:**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.01,
  "strategy_name": "Major Crypto Trend Following",
  "alert_message": "ETH/USD bullish trend confirmation",
  "custom_fields": {
    "timeframe": "1d",
    "market_cap_rank": 2,
    "correlation_group": "major_crypto"
  }
}
```

**Use Case:** Diversifying across major cryptocurrencies while following the same overall market trend.

### Altcoin Trading

Trading smaller market cap cryptocurrencies.

**Altcoin Buy Signal:**

```json
{
  "symbol": "DOTUSD",
  "side": "buy",
  "order_type": "limit",
  "volume": 5,
  "price": 12.50,
  "strategy_name": "Altcoin Accumulation",
  "alert_message": "DOT/USD reached accumulation zone",
  "custom_fields": {
    "timeframe": "4h",
    "market_cap_rank": 12,
    "category": "layer1",
    "bitcoin_dominance": 42.5
  }
}
```

**Altcoin Sell Signal:**

```json
{
  "symbol": "DOTUSD",
  "side": "sell",
  "order_type": "limit",
  "volume": 5,
  "price": 18.75,
  "strategy_name": "Altcoin Take Profit",
  "alert_message": "DOT/USD reached profit target",
  "custom_fields": {
    "timeframe": "4h",
    "market_cap_rank": 12,
    "category": "layer1",
    "profit_percentage": 50
  }
}
```

**Use Case:** Trading altcoins during appropriate market cycles for potentially higher returns.

## Additional Examples

### Dollar-Cost Averaging (DCA)

Regularly buying a fixed amount regardless of price.

**DCA Buy Signal:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Bitcoin DCA",
  "alert_message": "Weekly BTC purchase",
  "custom_fields": {
    "dca_frequency": "weekly",
    "dca_day": "monday",
    "investment_amount_usd": 50
  }
}
```

**Use Case:** Long-term accumulation strategy that reduces the impact of volatility.

### Grid Trading

Placing multiple buy and sell orders at different price levels.

**Grid Trading Buy Level:**

```json
{
  "symbol": "ETHUSD",
  "side": "buy",
  "order_type": "limit",
  "volume": 0.02,
  "price": 2800,
  "strategy_name": "ETH Grid Trading",
  "alert_message": "ETH/USD reached grid buy level",
  "custom_fields": {
    "grid_level": 3,
    "total_grid_levels": 7,
    "grid_range_low": 2600,
    "grid_range_high": 3200
  }
}
```

**Grid Trading Sell Level:**

```json
{
  "symbol": "ETHUSD",
  "side": "sell",
  "order_type": "limit",
  "volume": 0.02,
  "price": 3000,
  "strategy_name": "ETH Grid Trading",
  "alert_message": "ETH/USD reached grid sell level",
  "custom_fields": {
    "grid_level": 5,
    "total_grid_levels": 7,
    "grid_range_low": 2600,
    "grid_range_high": 3200
  }
}
```

**Use Case:** Profiting from price oscillations within a range.

### Ichimoku Cloud Strategy

Trading based on the Ichimoku Cloud indicator.

**Ichimoku Cloud Buy Signal:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "Ichimoku Cloud Strategy",
  "alert_message": "BTC/USD price crossed above cloud",
  "custom_fields": {
    "timeframe": "1d",
    "tenkan_sen": 48250,
    "kijun_sen": 46800,
    "senkou_span_a": 45200,
    "senkou_span_b": 44100,
    "cloud_color": "green"
  }
}
```

**Use Case:** Comprehensive trend-following strategy that considers multiple factors.

### Divergence Trading

Trading based on divergence between price and an indicator.

**Bullish Divergence Buy Signal:**

```json
{
  "symbol": "XBTUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.001,
  "strategy_name": "RSI Divergence",
  "alert_message": "BTC/USD bullish RSI divergence",
  "custom_fields": {
    "timeframe": "4h",
    "indicator": "RSI",
    "divergence_type": "bullish",
    "price_low_1": 42500,
    "price_low_2": 41800,
    "rsi_low_1": 32,
    "rsi_low_2": 36
  }
}
```

**Use Case:** Identifying potential reversals based on momentum divergences.