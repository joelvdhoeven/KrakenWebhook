"""
Tests for the TradingView to Kraken webhook service.
"""
import json
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/webhook/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "TradingView to Kraken Webhook Service"


def test_webhook_validation_missing_fields(client):
    """Test webhook validation with missing required fields."""
    # Missing required fields
    payload = {
        "side": "buy"
        # Missing symbol
    }
    
    response = client.post(
        "/webhook/tradingview/validate",
        json=payload
    )
    
    assert response.status_code == 400
    assert "Invalid payload format" in response.json().get("detail", "")


def test_webhook_validation_invalid_values(client):
    """Test webhook validation with invalid values."""
    # Invalid side value
    payload = {
        "symbol": "XBTUSD",
        "side": "invalid_side"  # Should be 'buy' or 'sell'
    }
    
    response = client.post(
        "/webhook/tradingview/validate",
        json=payload
    )
    
    assert response.status_code == 400
    assert "Invalid payload format" in response.json().get("detail", "")


def test_webhook_validation_valid_payload(client, monkeypatch):
    """Test webhook validation with a valid payload."""
    # Mock the validate_trade method to avoid actual API calls
    from src.executor.kraken_executor import kraken_executor
    from src.utils.models import TradeResponse
    
    def mock_validate_trade(*args, **kwargs):
        return TradeResponse.success_response("MOCK_ORDER_ID")
    
    monkeypatch.setattr(kraken_executor, "validate_trade", mock_validate_trade)
    
    # Valid payload
    payload = {
        "symbol": "XBTUSD",
        "side": "buy",
        "order_type": "market",
        "volume": 0.001
    }
    
    response = client.post(
        "/webhook/tradingview/validate",
        json=payload
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Validation successful" in response.json()["message"]
    assert response.json()["trade_details"]["symbol"] == "XBTUSD"
    assert response.json()["trade_details"]["side"] == "buy"