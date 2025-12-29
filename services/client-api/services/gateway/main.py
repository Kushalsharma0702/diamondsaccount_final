"""
API Gateway for TaxEase - Routes requests to microservices
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import httpx
import os
from datetime import datetime
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="TaxEase API Gateway",
    description="API Gateway for TaxEase Microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure for production
)

# Service URLs
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://localhost:8001"),
    "tax": os.getenv("TAX_SERVICE_URL", "http://localhost:8002"),
    "file": os.getenv("FILE_SERVICE_URL", "http://localhost:8003"),
    "report": os.getenv("REPORT_SERVICE_URL", "http://localhost:8004"),
}

@app.get("/")
@limiter.limit("10/minute")
async def root(request: Request):
    """Root endpoint"""
    return {
        "service": "TaxEase API Gateway",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Health check endpoint"""
    
    # Check all services
    service_status = {}
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                service_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
    
    return {
        "gateway": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": service_status
    }

async def proxy_request(service_name: str, path: str, request: Request):
    """Proxy request to microservice"""
    
    service_url = SERVICES.get(service_name)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    # Build target URL
    target_url = f"{service_url}{path}"
    
    # Get request body
    body = await request.body()
    
    # Forward headers (excluding host)
    headers = dict(request.headers)
    headers.pop("host", None)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                params=request.query_params,
                content=body,
                timeout=30.0
            )
            
            # Return response
            return response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            
        except httpx.RequestError as e:
            logger.error(f"Error proxying request to {service_name}: {e}")
            raise HTTPException(status_code=502, detail=f"Service {service_name} unavailable")

# Auth service routes
@app.api_route("/api/v1/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("20/minute")
async def auth_proxy(path: str, request: Request):
    """Proxy requests to auth service"""
    return await proxy_request("auth", f"/api/v1/auth/{path}", request)

# Tax service routes
@app.api_route("/api/v1/tax/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("15/minute")
async def tax_proxy(path: str, request: Request):
    """Proxy requests to tax service"""
    return await proxy_request("tax", f"/api/v1/tax/{path}", request)

# File service routes
@app.api_route("/api/v1/files/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("10/minute")
async def file_proxy(path: str, request: Request):
    """Proxy requests to file service"""
    return await proxy_request("file", f"/api/v1/files/{path}", request)

# Report service routes
@app.api_route("/api/v1/reports/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
@limiter.limit("5/minute")
async def report_proxy(path: str, request: Request):
    """Proxy requests to report service"""
    return await proxy_request("report", f"/api/v1/reports/{path}", request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
