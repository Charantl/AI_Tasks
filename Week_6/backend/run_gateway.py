#!/usr/bin/env python3
"""
API Gateway startup script for the Spotify-like music platform.
This gateway provides:
- Route requests to different services
- Authentication middleware
- Rate limiting per user
- Request/response logging
- CORS configuration
"""

import uvicorn
import os
from app.gateway_advanced import app
from app.gateway_config import GATEWAY_HOST, GATEWAY_PORT, DEBUG_MODE

if __name__ == "__main__":
    print("🚀 Starting API Gateway...")
    print(f"📍 Gateway will run on {GATEWAY_HOST}:{GATEWAY_PORT}")
    print(f"🔗 Backend service URL: {os.getenv('MAIN_SERVICE_URL', 'http://localhost:8000')}")
    print(f"📊 Debug mode: {DEBUG_MODE}")
    print("=" * 50)
    
    uvicorn.run(
        "app.gateway_advanced:app",
        host=GATEWAY_HOST,
        port=GATEWAY_PORT,
        reload=DEBUG_MODE,
        log_level="info"
    ) 