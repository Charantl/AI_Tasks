from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
import time
import json
import redis
import os
from typing import Dict, Optional
from datetime import datetime
import jwt
from app.core.logging_config import get_logger

logger = get_logger("gateway_advanced")

# Redis connection for rate limiting
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Security
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Rate limiting configuration
RATE_LIMIT_WINDOW = 3600
RATE_LIMIT_MAX_REQUESTS = 1000

# Service routing configuration
MAIN_SERVICE_URL = "http://localhost:8000"

SERVICES = {
    "auth": {"prefix": "/auth", "rate_limit": 100, "requires_auth": False},
    "user": {"prefix": "/user", "rate_limit": 500, "requires_auth": True},
    "subscription": {"prefix": "/subscription", "rate_limit": 200, "requires_auth": True},
    "artist": {"prefix": "/artist", "rate_limit": 300, "requires_auth": True},
    "album": {"prefix": "/album", "rate_limit": 400, "requires_auth": False},
    "song": {"prefix": "/song", "rate_limit": 600, "requires_auth": False},
    "search": {"prefix": "/search", "rate_limit": 800, "requires_auth": False},
    "recommendations": {"prefix": "/recommendations", "rate_limit": 300, "requires_auth": True},
    "liked_song": {"prefix": "/liked-song", "rate_limit": 400, "requires_auth": True},
    "play_history": {"prefix": "/play-history", "rate_limit": 400, "requires_auth": True},
    "comment": {"prefix": "/comment", "rate_limit": 300, "requires_auth": True},
    "share": {"prefix": "/share", "rate_limit": 200, "requires_auth": True},
    "analytics": {"prefix": "/analytics", "rate_limit": 200, "requires_auth": True},
    "ws": {"prefix": "/ws", "rate_limit": 1000, "requires_auth": True}
}

class AdvancedAPIGateway:
    def __init__(self):
        self.app = FastAPI(
            title="Spotify-like Music Platform API Gateway",
            description="Advanced API Gateway for music streaming platform",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
    
    def setup_middleware(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        @self.app.middleware("http")
        async def gateway_middleware(request: Request, call_next):
            return await self.process_request(request, call_next)
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "gateway": True, "version": "advanced"}
        
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def gateway_route(request: Request, path: str):
            return await self.route_request(request, path)
    
    async def process_request(self, request: Request, call_next):
        start_time = time.time()
        user_id = await self.get_user_id_from_token(request)
        service = self.identify_service(request.url.path)
        
        if service and not await self.check_rate_limit(user_id, service):
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        
        await self.log_request(request, user_id, service)
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        await self.log_response(request, response, process_time, user_id, service)
        
        return response
    
    async def route_request(self, request: Request, path: str):
        service = self.identify_service(path)
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        if service["requires_auth"]:
            user_id = await self.get_user_id_from_token(request)
            if not user_id:
                raise HTTPException(status_code=401, detail="Authentication required")
        
        return await self.forward_request(request, service)
    
    def identify_service(self, path: str) -> Optional[Dict]:
        for service_name, service_config in SERVICES.items():
            if path.startswith(service_config["prefix"]):
                return service_config
        return None
    
    async def get_user_id_from_token(self, request: Request) -> Optional[str]:
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
        if not user_id:
            user_id = "anonymous"
        
        key = f"rate_limit:{user_id}:{service['prefix']}"
        
        try:
            count = redis_client.get(key)
            if count is None:
                redis_client.setex(key, RATE_LIMIT_WINDOW, 1)
                return True
            
            count = int(count)
            if count >= service.get("rate_limit", RATE_LIMIT_MAX_REQUESTS):
                return False
            
            redis_client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return True
    
    async def log_request(self, request: Request, user_id: Optional[str], service: Dict):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "user_id": user_id,
            "service": service.get("prefix", "unknown") if service else "unknown",
            "ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "type": "request"
        }
        logger.info(f"Gateway Request: {json.dumps(log_data)}")
    
    async def log_response(self, request: Request, response, process_time: float, user_id: Optional[str], service: Dict):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "process_time_ms": round(process_time, 2),
            "user_id": user_id,
            "service": service.get("prefix", "unknown") if service else "unknown",
            "type": "response"
        }
        logger.info(f"Gateway Response: {json.dumps(log_data)}")
    
    async def forward_request(self, request: Request, service: Dict):
        try:
            target_url = f"{MAIN_SERVICE_URL}{request.url.path}"
            if request.url.query:
                target_url += f"?{request.url.query}"
            
            headers = dict(request.headers)
            headers.pop("host", None)
            
            body = None
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    timeout=30.0
                )
                
                return JSONResponse(
                    status_code=response.status_code,
                    content=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                    headers=dict(response.headers)
                )
                
        except httpx.RequestError as e:
            logger.error(f"Error forwarding request: {e}")
            raise HTTPException(status_code=502, detail="Service temporarily unavailable")
        except Exception as e:
            logger.error(f"Unexpected error in gateway: {e}")
            raise HTTPException(status_code=500, detail="Internal gateway error")

gateway = AdvancedAPIGateway()
app = gateway.app 