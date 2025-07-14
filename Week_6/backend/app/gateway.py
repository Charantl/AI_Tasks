from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import json
import redis
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import jwt
from app.core.logging_config import get_logger

logger = get_logger("gateway")

# Redis connection for rate limiting
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Security
security = HTTPBearer()
SECRET_KEY = "your-secret-key"  # Should be in env vars
ALGORITHM = "HS256"

# Rate limiting configuration
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
RATE_LIMIT_MAX_REQUESTS = 1000  # Max requests per window per user

# Service routing configuration
SERVICES = {
    "auth": {
        "base_url": "http://localhost:8000",
        "prefix": "/auth",
        "rate_limit": 100,  # More lenient for auth
        "requires_auth": False
    },
    "user": {
        "base_url": "http://localhost:8000",
        "prefix": "/user",
        "rate_limit": 500,
        "requires_auth": True
    },
    "subscription": {
        "base_url": "http://localhost:8000",
        "prefix": "/subscription",
        "rate_limit": 200,
        "requires_auth": True
    },
    "artist": {
        "base_url": "http://localhost:8000",
        "prefix": "/artist",
        "rate_limit": 300,
        "requires_auth": True
    },
    "album": {
        "base_url": "http://localhost:8000",
        "prefix": "/album",
        "rate_limit": 400,
        "requires_auth": False
    },
    "song": {
        "base_url": "http://localhost:8000",
        "prefix": "/song",
        "rate_limit": 600,
        "requires_auth": False
    },
    "search": {
        "base_url": "http://localhost:8000",
        "prefix": "/search",
        "rate_limit": 800,
        "requires_auth": False
    },
    "recommendations": {
        "base_url": "http://localhost:8000",
        "prefix": "/recommendations",
        "rate_limit": 300,
        "requires_auth": True
    },
    "playlist": {
        "base_url": "http://localhost:8000",
        "prefix": "/playlist",
        "rate_limit": 400,
        "requires_auth": True
    },
    "analytics": {
        "base_url": "http://localhost:8000",
        "prefix": "/analytics",
        "rate_limit": 200,
        "requires_auth": True
    },
    "ws": {
        "base_url": "http://localhost:8000",
        "prefix": "/ws",
        "rate_limit": 1000,
        "requires_auth": True
    }
}

class APIGateway:
    def __init__(self):
        self.app = FastAPI(
            title="Spotify-like Music Platform API Gateway",
            description="API Gateway for music streaming platform",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup gateway routes"""
        @self.app.middleware("http")
        async def gateway_middleware(request: Request, call_next):
            return await self.process_request(request, call_next)
        
        # Health check
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "gateway": True}
        
        # Route all requests through gateway
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def gateway_route(request: Request, path: str):
            return await self.route_request(request, path)
    
    async def process_request(self, request: Request, call_next):
        """Process incoming requests with logging and rate limiting"""
        start_time = time.time()
        
        # Extract user info for rate limiting
        user_id = await self.get_user_id_from_token(request)
        service = self.identify_service(request.url.path)
        
        # Rate limiting check
        if not await self.check_rate_limit(user_id, service):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Log request
        await self.log_request(request, user_id, service)
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = (time.time() - start_time) * 1000
        await self.log_response(request, response, process_time, user_id, service)
        
        return response
    
    async def route_request(self, request: Request, path: str):
        """Route request to appropriate service"""
        service = self.identify_service(path)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check authentication if required
        if service["requires_auth"]:
            user_id = await self.get_user_id_from_token(request)
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        # Forward request to service
        return await self.forward_request(request, service)
    
    def identify_service(self, path: str) -> Optional[Dict]:
        """Identify which service the request should be routed to"""
        for service_name, service_config in SERVICES.items():
            if path.startswith(service_config["prefix"]):
                return service_config
        return None
    
    async def get_user_id_from_token(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return None
    
    async def check_rate_limit(self, user_id: Optional[str], service: Dict) -> bool:
        """Check if request is within rate limits"""
        if not user_id:
            user_id = "anonymous"
        
        key = f"rate_limit:{user_id}:{service['prefix']}"
        current_time = int(time.time())
        
        try:
            # Get current count
            count = redis_client.get(key)
            if count is None:
                # First request in window
                redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
                return True
            
            count = int(count)
            if count >= service.get("rate_limit", RATE_LIMIT_MAX_REQUESTS):
                return False
            
            # Increment count
            redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True  # Allow request if Redis is down
    
    async def log_request(self, request: Request, user_id: Optional[str], service: Dict):
        """Log incoming request"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "user_id": user_id,
            "service": service.get("prefix", "unknown"),
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "type": "request"
        }
        logger.info(f"Gateway Request: {json.dumps(log_data)}")
    
    async def log_response(self, request: Request, response, process_time: float, user_id: Optional[str], service: Dict):
        """Log response"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "user_id": user_id,
            "service": service.get("prefix", "unknown"),
            "type": "response"
        }
        logger.info(f"Gateway Response: {json.dumps(log_data)}")
    
    async def forward_request(self, request: Request, service: Dict):
        """Forward request to appropriate service"""
        # In a real implementation, this would make HTTP requests to microservices
        # For now, we'll return a placeholder response
        return JSONResponse(
            content={
                "message": f"Request routed to {service['prefix']} service",
                "service": service['prefix'],
                "method": request.method,
                "path": str(request.url.path)
            }
        )

# Create gateway instance
gateway = APIGateway()
app = gateway.app 