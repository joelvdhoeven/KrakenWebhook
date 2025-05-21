# Security Guide: TradingView to Kraken Webhook Service

This guide covers security considerations, best practices, and implementation details for the TradingView to Kraken webhook service.

## Table of Contents

- [Security Overview](#security-overview)
- [Authentication and Authorization](#authentication-and-authorization)
- [Data Protection](#data-protection)
- [API Security](#api-security)
- [Infrastructure Security](#infrastructure-security)
- [Monitoring and Incident Response](#monitoring-and-incident-response)
- [Security Checklist](#security-checklist)

## Security Overview

The TradingView to Kraken webhook service handles sensitive financial data and has access to trading capabilities, making security a critical concern. Key security considerations include:

1. **Authentication**: Ensuring only authorized TradingView alerts can trigger trades
2. **Credential Protection**: Securely storing and managing API keys
3. **Data Validation**: Preventing malicious or malformed inputs
4. **Secure Communication**: Encrypting data in transit
5. **Monitoring**: Detecting and responding to suspicious activities

## Authentication and Authorization

### Webhook Authentication

The service uses HMAC-SHA256 signatures to authenticate incoming webhook requests:

1. **How it works**:
   - A shared secret is established between TradingView and the webhook service
   - TradingView includes a signature in the `X-Signature` header
   - The service verifies this signature against the request body

2. **Implementation details**:
   ```python
   # In payload_processor.py
   expected_signature = hmac.new(
       webhook_secret.encode(),
       body,
       hashlib.sha256
   ).hexdigest()
   
   # Compare signatures using constant-time comparison
   if not hmac.compare_digest(signature, expected_signature):
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Invalid signature"
       )
   ```

3. **Best practices**:
   - Use a strong, random webhook secret (at least 32 bytes)
   - Rotate the webhook secret regularly
   - Use constant-time comparison to prevent timing attacks

### API Key Management

The service securely manages Kraken API keys:

1. **Storage options**:
   - Environment variables (development)
   - Google Cloud Secret Manager (production)

2. **Implementation details**:
   ```python
   # In secrets.py
   def get_kraken_credentials(self) -> tuple[Optional[str], Optional[str]]:
       api_key = self.get_secret("KRAKEN_API_KEY")
       api_secret = self.get_secret("KRAKEN_API_SECRET")
       return api_key, api_secret
   ```

3. **Best practices**:
   - Use read-only API keys when possible
   - Limit API key permissions to only what's needed
   - Never log or expose API keys
   - Rotate API keys regularly

## Data Protection

### Sensitive Data Handling

The service implements several measures to protect sensitive data:

1. **Masking in logs**:
   ```python
   # In payload_processor.py
   def _log_payload(self, payload: Dict[str, Any]) -> None:
       masked_payload = payload.copy()
       sensitive_fields = ["api_key", "api_secret", "key", "secret", "password", "token"]
       for field in sensitive_fields:
           if field in masked_payload:
               masked_payload[field] = "***"
       logger.debug("Received webhook payload", payload=masked_payload)
   ```

2. **Secure configuration display**:
   ```python
   # In config.py
   def as_dict(self) -> Dict[str, Any]:
       config_dict = {
           "environment": self.environment,
           "log_level": self.log_level,
           "kraken_api_key": "***" if self.kraken_api_key else None,
           "kraken_api_secret": "***" if self.kraken_api_secret else None,
           "webhook_secret": "***" if self.webhook_secret else None,
           "gcp_project_id": self.gcp_project_id,
       }
       return config_dict
   ```

3. **Best practices**:
   - Never log sensitive data
   - Mask sensitive fields in error messages
   - Don't include sensitive data in HTTP responses
   - Clear sensitive data from memory when no longer needed

### Input Validation

The service uses Pydantic for robust input validation:

1. **Model validation**:
   ```python
   # In models.py
   class TradingViewAlert(BaseModel):
       symbol: str = Field(..., description="Trading pair symbol (e.g., 'XBTUSD')")
       side: OrderSide = Field(..., description="Order side: 'buy' or 'sell'")
       # Additional fields...
       
       @validator('symbol')
       def validate_symbol(cls, v):
           # Validation logic...
           return v
   ```

2. **Best practices**:
   - Validate all input data
   - Use strict type checking
   - Implement custom validators for business rules
   - Reject unexpected or malformed inputs

## API Security

### Kraken API Security

When interacting with the Kraken API:

1. **Request signing**:
   - The Kraken API requires signed requests
   - The krakenex library handles this securely

2. **Rate limiting**:
   - The service implements cooldown periods to respect Kraken's rate limits
   - Failed initialization attempts are throttled

3. **Best practices**:
   - Handle API errors gracefully
   - Implement exponential backoff for retries
   - Monitor API usage to stay within limits

### Webhook API Security

For the webhook API:

1. **Input sanitization**:
   - All JSON input is validated against Pydantic models
   - Unexpected fields are ignored

2. **Error handling**:
   - Detailed errors are only shown in development mode
   - Generic error messages in production

3. **Best practices**:
   - Use HTTPS for all endpoints
   - Implement rate limiting
   - Consider IP whitelisting for production

## Infrastructure Security

### Deployment Security

Secure deployment considerations:

1. **Docker security**:
   - Use official base images
   - Run as non-root user
   - Scan images for vulnerabilities

2. **Cloud Run security**:
   - Use the principle of least privilege for service accounts
   - Enable Cloud Run security features
   - Configure appropriate concurrency and scaling

3. **Best practices**:
   - Keep dependencies updated
   - Use vulnerability scanning in CI/CD
   - Implement infrastructure as code

### Network Security

Protecting network communications:

1. **HTTPS enforcement**:
   - All webhook endpoints should use HTTPS
   - Cloud Run automatically provides HTTPS

2. **CORS configuration**:
   ```python
   # In main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # Restrict in production
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

3. **Best practices**:
   - Restrict CORS in production
   - Use TLS 1.2+ for all communications
   - Consider using a Web Application Firewall (WAF)

## Monitoring and Incident Response

### Security Monitoring

Implement comprehensive monitoring:

1. **Log analysis**:
   - Monitor for authentication failures
   - Track unusual trading patterns
   - Alert on high error rates

2. **Audit logging**:
   - Log all trade executions
   - Record authentication attempts
   - Track configuration changes

3. **Best practices**:
   - Centralize logs
   - Implement log retention policies
   - Set up automated alerts

### Incident Response

Prepare for security incidents:

1. **Response plan**:
   - Define roles and responsibilities
   - Document response procedures
   - Establish communication channels

2. **Recovery procedures**:
   - API key rotation
   - Service redeployment
   - Forensic analysis

3. **Best practices**:
   - Practice incident response
   - Document lessons learned
   - Update security measures based on incidents

## Security Checklist

Use this checklist to ensure your deployment is secure:

### Authentication and Authorization

- [ ] Strong webhook secret configured (32+ random bytes)
- [ ] Webhook signature validation enabled
- [ ] Kraken API keys have minimal necessary permissions
- [ ] API keys and secrets stored securely (not in code)
- [ ] Regular rotation schedule for all secrets

### Data Protection

- [ ] Sensitive data masked in logs
- [ ] Input validation for all webhook payloads
- [ ] No sensitive data in error responses
- [ ] Secure handling of trade information

### API Security

- [ ] HTTPS enforced for all endpoints
- [ ] Rate limiting implemented
- [ ] Appropriate error handling
- [ ] Kraken API rate limits respected

### Infrastructure Security

- [ ] Dependencies up to date
- [ ] Docker image scanned for vulnerabilities
- [ ] Service accounts follow least privilege principle
- [ ] Network security controls in place

### Monitoring and Incident Response

- [ ] Logging configured for security events
- [ ] Alerts set up for suspicious activities
- [ ] Incident response plan documented
- [ ] Regular security reviews scheduled

## Additional Security Measures

Consider these additional security enhancements:

1. **IP Whitelisting**:
   - Restrict webhook access to TradingView IP ranges
   - Implement in Cloud Run or a proxy

2. **Request Throttling**:
   - Limit the number of requests per minute
   - Prevent denial of service attacks

3. **Two-Factor Authentication**:
   - Require 2FA for Kraken account
   - Use 2FA for cloud service access

4. **Penetration Testing**:
   - Conduct regular security assessments
   - Test for common vulnerabilities

5. **Security Headers**:
   - Implement security headers in FastAPI
   - Protect against common web vulnerabilities