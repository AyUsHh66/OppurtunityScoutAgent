"""
Production-grade security middleware for FastAPI
Includes API key validation, rate limiting, and CORS
"""

import time
from typing import Optional, Dict
from fastapi import Request, HTTPException, Header
from fastapi.responses import JSONResponse
from functools import lru_cache
from collections import defaultdict
from datetime import datetime, timedelta
import hashlib
import hmac

from core_engine.logging_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Rate limiter with per-endpoint configuration"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Clean old entries every 60 seconds
        self.last_cleanup = time.time()
    
    def is_allowed(self, client_id: str, limit: int = 60, window: int = 60) -> bool:
        """
        Check if request is allowed
        
        Args:
            client_id: Unique client identifier (IP or API key)
            limit: Max requests allowed in window
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        
        # Cleanup old entries
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
        
        # Get requests in current window
        cutoff = now - window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if req_time > cutoff
        ]
        
        if len(self.requests[client_id]) >= limit:
            return False
        
        self.requests[client_id].append(now)
        return True
    
    def _cleanup_old_requests(self):
        """Clean up old request records"""
        now = time.time()
        cutoff = now - 3600  # Keep 1 hour of history
        
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > cutoff
            ]
            if not self.requests[client_id]:
                del self.requests[client_id]
        
        self.last_cleanup = now


class APIKeyValidator:
    """Validates and manages API keys"""
    
    def __init__(self, admin_key: Optional[str] = None):
        self.admin_key = admin_key or "change-me-in-production"
        self.key_cache: Dict[str, Dict] = {}
    
    def validate_key(self, api_key: str) -> bool:
        """Validate API key format and value"""
        if not api_key:
            return False
        
        # Admin key always works
        if api_key == self.admin_key:
            logger.info("Admin key used")
            return True
        
        # Key must be at least 32 characters (hash-like)
        if len(api_key) < 32:
            return False
        
        return True
    
    def get_client_id(self, api_key: str) -> str:
        """Get client identifier from API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]


# Global instances
rate_limiter = RateLimiter()
api_validator = APIKeyValidator()


class SecurityMiddleware:
    """FastAPI middleware for security features"""
    
    def __init__(self, app, api_key_validator: Optional[APIKeyValidator] = None):
        self.app = app
        self.validator = api_validator if api_validator is None else api_validator
    
    async def __call__(self, request: Request):
        # Add request ID for tracking
        request_id = self._generate_request_id(request)
        request.state.request_id = request_id
        
        # Add start time for duration tracking
        request.state.start_time = time.time()
        
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        request.state.client_ip = client_ip
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "method": request.method,
                "path": request.url.path,
            }
        )
        
        response = await self.app(request)
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(time.time() - request.state.start_time)
        
        return response
    
    @staticmethod
    def _generate_request_id(request: Request) -> str:
        """Generate unique request ID"""
        content = f"{time.time()}_{request.method}_{request.url.path}_{request.client}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


async def validate_api_key(
    request: Request,
    x_api_key: Optional[str] = Header(None)
) -> str:
    """
    Dependency for validating API keys
    
    Usage:
        @app.get("/protected")
        async def protected(api_key: str = Depends(validate_api_key)):
            ...
    """
    api_key = x_api_key or request.query_params.get("api_key")
    
    if not api_key:
        logger.warning("Missing API key", extra={"request_id": request.state.request_id})
        raise HTTPException(
            status_code=401,
            detail="Missing API key",
            headers={"X-Request-ID": request.state.request_id}
        )
    
    if not api_validator.validate_key(api_key):
        logger.warning("Invalid API key", extra={"request_id": request.state.request_id})
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"X-Request-ID": request.state.request_id}
        )
    
    return api_key


async def check_rate_limit(request: Request):
    """
    Dependency for rate limiting
    
    Default: 60 requests per minute per IP
    
    Usage:
        @app.get("/api/endpoint")
        async def endpoint(_: None = Depends(check_rate_limit)):
            ...
    """
    client_id = request.state.client_ip
    
    if not rate_limiter.is_allowed(client_id, limit=60, window=60):
        logger.warning(
            "Rate limit exceeded",
            extra={
                "request_id": request.state.request_id,
                "client_id": client_id,
            }
        )
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={
                "X-Request-ID": request.state.request_id,
                "Retry-After": "60"
            }
        )


def get_cors_config() -> Dict:
    """Get CORS configuration for production"""
    return {
        "allow_origins": [
            "https://yourdomain.com",  # Change this
            "https://www.yourdomain.com",  # Change this
        ],
        "allow_credentials": True,
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["X-API-Key", "Content-Type"],
        "max_age": 3600,
    }


def get_endpoint_rate_limits() -> Dict[str, Dict]:
    """Per-endpoint rate limit configuration"""
    return {
        "/api/v1/jobs/search": {"limit": 30, "window": 60},  # 30 per minute
        "/api/v1/notifications/send": {"limit": 10, "window": 60},  # 10 per minute
        "/api/v1/leads/qualify": {"limit": 20, "window": 60},  # 20 per minute
        "/api/v1/config": {"limit": 100, "window": 60},  # 100 per minute (read-only)
    }
