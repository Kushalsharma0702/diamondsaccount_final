"""
Production-ready CORS middleware for FastAPI
Handles all CORS requests including OPTIONS preflight
Configured to work in both development and production
"""
import logging
from typing import List, Optional
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class ProductionCORSMiddleware(BaseHTTPMiddleware):
    """
    Production-ready CORS middleware that handles ALL CORS requests
    This middleware runs before any route handlers and intercepts OPTIONS requests
    """
    
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: Optional[List[str]] = None,
        allow_methods: Optional[List[str]] = None,
        allow_headers: Optional[List[str]] = None,
        allow_credentials: bool = True,
        max_age: int = 3600,
        is_development: bool = False,
    ):
        super().__init__(app)
        self.allow_origins = allow_origins or []
        self.allow_methods = allow_methods or ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
        self.allow_headers = allow_headers or ["content-type", "authorization", "x-requested-with", "accept"]
        self.allow_credentials = allow_credentials
        self.max_age = max_age
        self.is_development = is_development
        
        # In development, allow localhost and 127.0.0.1 on any port
        if self.is_development:
            self._add_development_origins()
        
        logger.info(f"✅ CORS Middleware initialized")
        logger.info(f"   Development mode: {self.is_development}")
        logger.info(f"   Allowed origins: {len(self.allow_origins)} configured")
        logger.info(f"   Allowed methods: {', '.join(self.allow_methods)}")
        logger.info(f"   Allowed headers: {', '.join(self.allow_headers)}")
    
    def _add_development_origins(self):
        """Add common development origins"""
        dev_origins = [
            "http://localhost:8080",
            "http://127.0.0.1:8080",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
        
        for origin in dev_origins:
            if origin not in self.allow_origins:
                self.allow_origins.append(origin)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if origin is allowed"""
        if not origin:
            return False
        
        # In development, allow any localhost or 127.0.0.1
        if self.is_development:
            if "localhost" in origin.lower() or "127.0.0.1" in origin:
                return True
        
        # Check against configured origins
        return origin in self.allow_origins
    
    def _build_cors_headers(self, origin: Optional[str] = None) -> dict:
        """Build CORS headers for response"""
        headers = {
            "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
            "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
            "Access-Control-Max-Age": str(self.max_age),
        }
        
        if self.allow_credentials:
            headers["Access-Control-Allow-Credentials"] = "true"
        
        if origin:
            headers["Access-Control-Allow-Origin"] = origin
        elif self.is_development:
            # In development, allow any origin
            headers["Access-Control-Allow-Origin"] = "*"
        else:
            # In production, only allow configured origins
            if self.allow_origins:
                headers["Access-Control-Allow-Origin"] = self.allow_origins[0]
        
        headers["Vary"] = "Origin"
        
        return headers
    
    async def dispatch(self, request: Request, call_next):
        """Handle CORS for all requests"""
        origin = request.headers.get("origin", "")
        
        # Handle OPTIONS preflight requests IMMEDIATELY
        if request.method == "OPTIONS":
            # Check if origin is allowed
            is_allowed = self._is_origin_allowed(origin) if origin else self.is_development
            
            if is_allowed or self.is_development:
                # Get requested headers and methods from preflight
                requested_methods = request.headers.get("access-control-request-method", "POST")
                requested_headers = request.headers.get("access-control-request-headers", "")
                
                # Build CORS headers
                cors_headers = self._build_cors_headers(origin if origin else None)
                
                # Override with requested headers if provided
                if requested_headers:
                    cors_headers["Access-Control-Allow-Headers"] = requested_headers
                
                logger.debug(f"✅ OPTIONS preflight allowed: {request.url.path} from {origin}")
                
                # Return 200 OK immediately - don't route
                return Response(
                    status_code=200,
                    headers=cors_headers,
                )
            else:
                logger.warning(f"❌ OPTIONS preflight rejected: {origin}")
                return Response(
                    status_code=403,
                    content="CORS policy: Origin not allowed",
                    headers=self._build_cors_headers(),
                )
        
        # Process normal requests (GET, POST, PUT, DELETE, etc.)
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            # Even on error, add CORS headers
            error_response = Response(
                status_code=500,
                content=str(e),
                headers=self._build_cors_headers(origin if origin else None),
            )
            return error_response
        
        # Add CORS headers to ALL responses
        if origin:
            is_allowed = self._is_origin_allowed(origin)
            if is_allowed or self.is_development:
                cors_headers = self._build_cors_headers(origin)
                # Merge CORS headers into response
                for key, value in cors_headers.items():
                    response.headers[key] = value
        elif self.is_development:
            # In development, add CORS headers even without origin
            cors_headers = self._build_cors_headers()
            for key, value in cors_headers.items():
                response.headers[key] = value
        
        return response

