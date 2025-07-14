import os
from typing import Dict, List

# Gateway Configuration
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", 8001))

# Backend Service Configuration
MAIN_SERVICE_URL = os.getenv("MAIN_SERVICE_URL", "http://localhost:8000")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Rate Limiting Configuration
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", 3600))  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", 1000))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
CORS_ALLOW_METHODS = os.getenv("CORS_ALLOW_METHODS", "*").split(",")
CORS_ALLOW_HEADERS = os.getenv("CORS_ALLOW_HEADERS", "*").split(",")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Service-specific rate limits
SERVICE_RATE_LIMITS = {
    "auth": int(os.getenv("AUTH_RATE_LIMIT", 100)),
    "user": int(os.getenv("USER_RATE_LIMIT", 500)),
    "subscription": int(os.getenv("SUBSCRIPTION_RATE_LIMIT", 200)),
    "artist": int(os.getenv("ARTIST_RATE_LIMIT", 300)),
    "album": int(os.getenv("ALBUM_RATE_LIMIT", 400)),
    "song": int(os.getenv("SONG_RATE_LIMIT", 600)),
    "search": int(os.getenv("SEARCH_RATE_LIMIT", 800)),
    "recommendations": int(os.getenv("RECOMMENDATIONS_RATE_LIMIT", 300)),
    "liked_song": int(os.getenv("LIKED_SONG_RATE_LIMIT", 400)),
    "play_history": int(os.getenv("PLAY_HISTORY_RATE_LIMIT", 400)),
    "comment": int(os.getenv("COMMENT_RATE_LIMIT", 300)),
    "share": int(os.getenv("SHARE_RATE_LIMIT", 200)),
    "analytics": int(os.getenv("ANALYTICS_RATE_LIMIT", 200)),
    "ws": int(os.getenv("WS_RATE_LIMIT", 1000))
}

# Service authentication requirements
SERVICE_AUTH_REQUIREMENTS = {
    "auth": False,
    "user": True,
    "subscription": True,
    "artist": True,
    "album": False,
    "song": False,
    "search": False,
    "recommendations": True,
    "liked_song": True,
    "play_history": True,
    "comment": True,
    "share": True,
    "analytics": True,
    "ws": True
}

# Health check configuration
HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", 30))  # seconds

# Request timeout configuration
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))  # seconds

# Circuit breaker configuration
CIRCUIT_BREAKER_ENABLED = os.getenv("CIRCUIT_BREAKER_ENABLED", "true").lower() == "true"
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", 5))
CIRCUIT_BREAKER_RECOVERY_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_RECOVERY_TIMEOUT", 60))  # seconds

# Metrics configuration
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "true").lower() == "true"
METRICS_PORT = int(os.getenv("METRICS_PORT", 8002))

# Load balancing configuration (for future microservices)
LOAD_BALANCER_ENABLED = os.getenv("LOAD_BALANCER_ENABLED", "false").lower() == "true"
LOAD_BALANCER_STRATEGY = os.getenv("LOAD_BALANCER_STRATEGY", "round_robin")  # round_robin, least_connections, etc.

# Cache configuration
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", 300))  # seconds

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}

# API Documentation
API_DOCS_ENABLED = os.getenv("API_DOCS_ENABLED", "true").lower() == "true"
API_DOCS_URL = os.getenv("API_DOCS_URL", "/docs")
API_REDOC_URL = os.getenv("API_REDOC_URL", "/redoc")

# Monitoring and alerting
ALERTING_ENABLED = os.getenv("ALERTING_ENABLED", "false").lower() == "true"
ALERT_WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL", "")
ALERT_RATE_LIMIT_THRESHOLD = int(os.getenv("ALERT_RATE_LIMIT_THRESHOLD", 80))  # percentage

# Development mode
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true" 