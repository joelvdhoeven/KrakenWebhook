#!/usr/bin/env python
"""
Test script for sending webhook requests to the TradingView to Kraken webhook service.
This script simulates TradingView alerts for local testing.
"""
import argparse
import json
import hmac
import hashlib
import requests
from typing import Dict, Any, Optional


def load_payload(file_path: str) -> Dict[str, Any]:
    """
    Load a JSON payload from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The loaded JSON payload
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def sign_payload(payload: Dict[str, Any], secret: str) -> str:
    """
    Sign a payload using HMAC-SHA256.
    
    Args:
        payload: The payload to sign
        secret: The secret key
        
    Returns:
        The signature as a hexadecimal string
    """
    payload_bytes = json.dumps(payload).encode('utf-8')
    return hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()


def send_webhook(
    url: str,
    payload: Dict[str, Any],
    secret: Optional[str] = None,
    validate_only: bool = False
) -> requests.Response:
    """
    Send a webhook request.
    
    Args:
        url: The webhook URL
        payload: The payload to send
        secret: The secret key for signing the payload
        validate_only: Whether to use the validation endpoint
        
    Returns:
        The response from the server
    """
    # Prepare headers
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Add signature if secret is provided
    if secret:
        signature = sign_payload(payload, secret)
        headers['X-Signature'] = signature
    
    # Determine the endpoint
    if validate_only:
        if not url.endswith('/validate'):
            url = f"{url}/validate"
    
    # Send the request
    return requests.post(url, json=payload, headers=headers)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test the TradingView to Kraken webhook service')
    parser.add_argument('--url', type=str, default='http://localhost:8080/webhook/tradingview',
                        help='The webhook URL')
    parser.add_argument('--payload', type=str, default='../examples/tradingview_alert.json',
                        help='Path to the JSON payload file')
    parser.add_argument('--secret', type=str, help='The webhook secret for signing the payload')
    parser.add_argument('--validate', action='store_true', help='Use the validation endpoint')
    
    args = parser.parse_args()
    
    # Load the payload
    try:
        payload = load_payload(args.payload)
    except Exception as e:
        print(f"Error loading payload: {e}")
        return
    
    # Send the webhook
    try:
        response = send_webhook(args.url, payload, args.secret, args.validate)
        
        # Print the response
        print(f"Status code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
        
    except Exception as e:
        print(f"Error sending webhook: {e}")


if __name__ == '__main__':
    main()