# API Gateway Documentation

## Overview

The API Gateway provides a centralized entry point for all client requests to the Spotify-like music platform. It implements essential features for production-ready applications including authentication, rate limiting, request/response logging, and CORS configuration.

## Features

### ✅ Route Requests to Different Services
- Routes requests based on URL prefixes to appropriate services
- Supports all HTTP methods (GET, POST, PUT, DELETE, PATCH)
- Configurable service mapping

### ✅ Authentication Middleware
- JWT token validation
- Automatic user ID extraction from tokens
- Service-specific authentication requirements
- Anonymous user support for public endpoints

### ✅ Rate Limiting Per User
- Redis-based rate limiting
- Configurable limits per service
- User-specific rate limiting
- Anonymous user rate limiting
- Graceful degradation when Redis is unavailable

### ✅ Request/Response Logging
- Structured JSON logging
- Request metadata capture (method, path, user, IP, user-agent)
- Response metadata capture (status code, processing time)
- Service identification in logs

### ✅ CORS Configuration
- Configurable CORS origins
- Support for credentials
- All HTTP methods and headers allowed
- Production-ready CORS setup

## Architecture

```
Client Request → API Gateway → Backend Services
                ↓
            - Authentication
            - Rate Limiting
            - Request Logging
            - CORS Handling
            - Request Forwarding
```

## Configuration

### Environment Variables

```bash
# Gateway Configuration
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8001

# Backend Service
MAIN_SERVICE_URL=http://localhost:8000

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Rate Limiting
RATE_LIMIT_WINDOW=3600
RATE_LIMIT_MAX_REQUESTS=1000

# CORS
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=true

# Logging
LOG_LEVEL=INFO
DEBUG_MODE=false
```

### Service-Specific Rate Limits

| Service | Rate Limit | Requires Auth |
|---------|------------|---------------|
| auth | 100/hour | No |
| user | 500/hour | Yes |
| subscription | 200/hour | Yes |
| artist | 300/hour | Yes |
| album | 400/hour | No |
| song | 600/hour | No |
| search | 800/hour | No |
| recommendations | 300/hour | Yes |
| liked_song | 400/hour | Yes |
| play_history | 400/hour | Yes |
| comment | 300/hour | Yes |
| share | 200/hour | Yes |
| analytics | 200/hour | Yes |
| ws | 1000/hour | Yes |

## Usage

### Starting the Gateway

```bash
# Using the startup script
python run_gateway.py

# Or directly with uvicorn
uvicorn app.gateway_advanced:app --host 0.0.0.0 --port 8001
```

### Health Check

```bash
curl http://localhost:8001/health
```

Response:
```json
{
  "status": "healthy",
  "gateway": true,
  "version": "advanced"
}
```

### Example Requests

#### Public Endpoint (No Auth Required)
```bash
curl http://localhost:8001/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

#### Protected Endpoint (Auth Required)
```bash
curl http://localhost:8001/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Monitoring

### Logs

The gateway logs all requests and responses in structured JSON format:

```json
{
  "timestamp": "2024-01-01T12:00:00.000Z",
  "method": "GET",
  "path": "/user/profile",
  "user_id": "123",
  "service": "/user",
  "ip": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "type": "request"
}
```

### Rate Limiting

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

### Error Responses

#### Rate Limit Exceeded (429)
```json
{
  "detail": "Rate limit exceeded"
}
```

#### Authentication Required (401)
```json
{
  "detail": "Authentication required"
}
```

#### Service Not Found (404)
```json
{
  "detail": "Service not found"
}
```

## Security Features

### JWT Token Validation
- Automatic token extraction from Authorization header
- Token validation using configured secret key
- User ID extraction for rate limiting and logging

### Security Headers
The gateway adds security headers to all responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

### CORS Protection
- Configurable allowed origins
- Support for credentials
- Proper preflight request handling

## Performance

### Rate Limiting Performance
- Redis-based rate limiting for high performance
- In-memory fallback when Redis is unavailable
- Configurable rate limit windows and thresholds

### Request Forwarding
- Async HTTP client for efficient request forwarding
- Configurable timeouts
- Error handling with appropriate HTTP status codes

### Logging Performance
- Structured logging for easy parsing
- Minimal performance impact
- Configurable log levels

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "run_gateway.py"]
```

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required for rate limiting)
redis-server

# Start the main backend service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start the API Gateway
python run_gateway.py
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Ensure Redis is running
   - Check Redis host and port configuration
   - Gateway will continue to work without Redis (no rate limiting)

2. **Backend Service Unavailable**
   - Check if main backend service is running on port 8000
   - Verify MAIN_SERVICE_URL configuration
   - Check network connectivity

3. **Rate Limiting Not Working**
   - Verify Redis connection
   - Check rate limit configuration
   - Monitor Redis logs for errors

4. **Authentication Issues**
   - Verify SECRET_KEY configuration
   - Check JWT token format
   - Ensure tokens are not expired

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG_MODE=true
python run_gateway.py
```

## Future Enhancements

- [ ] Circuit breaker pattern for service resilience
- [ ] Load balancing for multiple backend instances
- [ ] Request/response caching
- [ ] Advanced metrics and monitoring
- [ ] API key authentication
- [ ] Request transformation and validation
- [ ] WebSocket support for real-time features 