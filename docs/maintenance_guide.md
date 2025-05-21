# Maintenance Guide: TradingView to Kraken Webhook Service

This guide covers common maintenance operations, monitoring, and troubleshooting for the TradingView to Kraken webhook service.

## Table of Contents

- [Routine Maintenance](#routine-maintenance)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Scaling](#scaling)
- [Backup and Recovery](#backup-and-recovery)
- [Security Maintenance](#security-maintenance)
- [Upgrading](#upgrading)

## Routine Maintenance

### Dependency Updates

Regularly update dependencies to ensure security and stability:

1. Check for outdated packages:
   ```bash
   pip list --outdated
   ```

2. Update requirements.txt with new versions:
   ```bash
   pip freeze > requirements.txt
   ```

3. Test thoroughly after updating dependencies

### Log Rotation

If running outside of a managed environment like Cloud Run:

1. Configure log rotation for application logs:
   ```bash
   # Example logrotate configuration
   /var/log/tradingview-kraken-webhook/*.log {
       daily
       missingok
       rotate 14
       compress
       delaycompress
       notifempty
       create 0640 www-data www-data
   }
   ```

### API Key Rotation

Regularly rotate Kraken API keys for security:

1. Generate new API keys in the Kraken account dashboard
2. Update the keys in your environment or Secret Manager:
   ```bash
   # If using environment variables
   export KRAKEN_API_KEY=your_new_key
   export KRAKEN_API_SECRET=your_new_secret
   
   # If using Google Cloud Secret Manager
   echo -n "your_new_key" | gcloud secrets versions add KRAKEN_API_KEY --data-file=-
   echo -n "your_new_secret" | gcloud secrets versions add KRAKEN_API_SECRET --data-file=-
   ```

3. Restart the service to apply the new keys

### Health Checks

Regularly verify the service is operational:

1. Use the health check endpoint:
   ```bash
   curl https://your-service-url/webhook/health
   ```

2. Expected response:
   ```json
   {
     "status": "ok",
     "service": "tradingview-kraken-webhook"
   }
   ```

## Monitoring

### Logging

Monitor application logs for errors and important events:

1. In Google Cloud Run:
   - View logs in the Google Cloud Console
   - Set up log-based alerts for error conditions

2. In a custom environment:
   - Configure log aggregation (e.g., ELK stack, Graylog)
   - Set up alerts for error patterns

### Key Metrics to Monitor

1. **Request Rate**: Number of webhook requests per minute
2. **Error Rate**: Percentage of requests resulting in errors
3. **Response Time**: Time to process webhook requests
4. **Trade Success Rate**: Percentage of trades successfully executed
5. **Memory Usage**: Application memory consumption
6. **CPU Usage**: Application CPU utilization

### Setting Up Alerts

Configure alerts for critical conditions:

1. High error rate (e.g., >5% of requests)
2. Sustained high response times (e.g., >500ms)
3. Failed health checks
4. Unusual trading patterns (e.g., sudden spike in trade volume)

### Monitoring Kraken API Usage

Monitor Kraken API rate limits and usage:

1. Track API calls in application logs
2. Set up alerts for approaching rate limits
3. Monitor for API errors indicating rate limiting

## Troubleshooting

### Common Issues and Solutions

#### Service Not Starting

**Symptoms**: Service fails to start, startup logs show errors

**Possible Causes and Solutions**:

1. **Missing environment variables**:
   - Check that all required environment variables are set
   - Verify `.env` file is properly loaded

2. **Port conflicts**:
   - Ensure port 8080 is not in use by another service
   - Change the port using the `PORT` environment variable

3. **Dependency issues**:
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check for compatibility issues between packages

#### Webhook Authentication Failures

**Symptoms**: 401 Unauthorized responses, signature validation errors

**Possible Causes and Solutions**:

1. **Mismatched webhook secret**:
   - Verify the `WEBHOOK_SECRET` matches between service and TradingView
   - Check that the signature is being correctly generated

2. **Incorrect signature format**:
   - Ensure the signature is a valid HMAC-SHA256 hexadecimal string
   - Verify the signature is being sent in the `X-Signature` header

#### Trade Execution Failures

**Symptoms**: 400 Bad Request responses, trade execution errors

**Possible Causes and Solutions**:

1. **Invalid Kraken API credentials**:
   - Verify API key and secret are correct
   - Check API key permissions on Kraken

2. **Insufficient funds**:
   - Check account balance on Kraken
   - Verify trade volume is within available balance

3. **Invalid order parameters**:
   - Validate order parameters against Kraken requirements
   - Check for minimum order size restrictions

4. **Market conditions**:
   - Verify the market is open and trading
   - Check for unusual market conditions or halts

### Diagnostic Commands

#### Checking Service Status

```bash
# If running in Docker
docker ps | grep tradingview-kraken-webhook

# If running in Google Cloud Run
gcloud run services describe tradingview-kraken-webhook
```

#### Viewing Logs

```bash
# If running locally
tail -f logs/app.log

# If running in Docker
docker logs -f tradingview-kraken-webhook

# If running in Google Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=tradingview-kraken-webhook" --limit=50
```

#### Testing the Webhook

```bash
# Test with validation only
python scripts/test_webhook.py --url https://your-service-url/webhook/tradingview/validate --payload examples/tradingview_alert.json --secret your_webhook_secret

# Test with actual execution
python scripts/test_webhook.py --url https://your-service-url/webhook/tradingview --payload examples/tradingview_alert.json --secret your_webhook_secret
```

### Debugging Techniques

1. **Enable debug logging**:
   ```bash
   export LOG_LEVEL=DEBUG
   ```

2. **Inspect request and response details**:
   - Use the test script with verbose output
   - Check application logs for request details

3. **Validate Kraken API connectivity**:
   - Test API credentials directly with Kraken API
   - Check for network connectivity issues

4. **Inspect payload processing**:
   - Verify JSON payload structure
   - Check for validation errors in logs

## Scaling

### Vertical Scaling

Increase resources for the service:

1. In Docker:
   ```bash
   docker run -p 8080:8080 --env-file .env --memory=512m --cpus=1 tradingview-kraken-webhook
   ```

2. In Google Cloud Run:
   ```bash
   gcloud run services update tradingview-kraken-webhook \
     --memory=512Mi \
     --cpu=1
   ```

### Horizontal Scaling

For high-volume scenarios, scale horizontally:

1. In Google Cloud Run:
   ```bash
   gcloud run services update tradingview-kraken-webhook \
     --min-instances=2 \
     --max-instances=10
   ```

2. Configure autoscaling based on request volume:
   ```bash
   gcloud run services update tradingview-kraken-webhook \
     --concurrency=50
   ```

### Rate Limiting

Implement rate limiting to prevent abuse:

1. Add a rate limiting middleware to the FastAPI application
2. Configure rate limits based on client IP or API key
3. Monitor and adjust rate limits based on usage patterns

## Backup and Recovery

### Configuration Backup

Regularly backup configuration:

1. Export environment variables:
   ```bash
   env | grep 'KRAKEN\|WEBHOOK' > config_backup.env
   ```

2. Backup Google Cloud Secret Manager secrets:
   ```bash
   gcloud secrets versions access latest --secret=KRAKEN_API_KEY > kraken_api_key.backup
   gcloud secrets versions access latest --secret=KRAKEN_API_SECRET > kraken_api_secret.backup
   gcloud secrets versions access latest --secret=WEBHOOK_SECRET > webhook_secret.backup
   ```

### Disaster Recovery

In case of service failure:

1. Restore from backup:
   ```bash
   # Restore environment variables
   source config_backup.env
   
   # Restore secrets
   cat kraken_api_key.backup | gcloud secrets versions add KRAKEN_API_KEY --data-file=-
   cat kraken_api_secret.backup | gcloud secrets versions add KRAKEN_API_SECRET --data-file=-
   cat webhook_secret.backup | gcloud secrets versions add WEBHOOK_SECRET --data-file=-
   ```

2. Redeploy the service:
   ```bash
   # In Google Cloud Run
   gcloud run deploy tradingview-kraken-webhook \
     --image gcr.io/PROJECT_ID/tradingview-kraken-webhook:latest
   ```

## Security Maintenance

### Security Audits

Regularly audit the service for security issues:

1. Scan dependencies for vulnerabilities:
   ```bash
   pip-audit
   ```

2. Review access controls:
   - Check API key permissions on Kraken
   - Review Cloud Run service account permissions

3. Audit webhook access:
   - Review webhook access logs
   - Check for unauthorized access attempts

### Updating Security Configurations

1. Update webhook secret:
   ```bash
   # Generate a new secret
   NEW_SECRET=$(openssl rand -hex 32)
   
   # Update in environment or Secret Manager
   echo -n "$NEW_SECRET" | gcloud secrets versions add WEBHOOK_SECRET --data-file=-
   ```

2. Update TradingView alert configurations with the new secret

### Security Incident Response

In case of a security incident:

1. Revoke compromised API keys immediately
2. Rotate all secrets and API keys
3. Review logs for unauthorized access
4. Deploy updated service with security patches

## Upgrading

### Minor Updates

For minor updates and patches:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Restart the service:
   ```bash
   # If running locally
   python -m src.main
   
   # If running in Docker
   docker-compose restart
   ```

### Major Updates

For major version upgrades:

1. Review the changelog for breaking changes
2. Test in a staging environment first
3. Backup all configuration and data
4. Deploy the new version with a rollback plan
5. Monitor closely after upgrade

### Rollback Procedure

If an upgrade causes issues:

1. Revert to the previous version:
   ```bash
   # In Google Cloud Run
   gcloud run services update tradingview-kraken-webhook \
     --image gcr.io/PROJECT_ID/tradingview-kraken-webhook:previous-version
   ```

2. Restore configuration from backup if needed
3. Investigate the issue before attempting the upgrade again