"""
Main FastAPI application for Foodyeh vending machine backend.
Production-ready with comprehensive security features.
"""

import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn

from config import settings
from routers import order, status, admin
from auth.routes import router as auth_router
from services.mqtt_client import get_mqtt_service
from auth.jwt_handler import get_current_user
from utils.rate_limiter import rate_limit_middleware
from logging_config import (
    get_app_logger, 
    get_security_logger, 
    log_security_event,
    log_authentication_attempt,
    log_https_violation
)

# Get configured loggers
logger = get_app_logger(__name__)
security_logger = get_security_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Foodyeh API server", version=settings.app_version)
    
    # Initialize MQTT connection
    try:
        mqtt_service = get_mqtt_service()
        if mqtt_service.connect():
            logger.info("MQTT connection established successfully")
        else:
            logger.warning("Failed to establish MQTT connection")
    except Exception as e:
        logger.error(f"Error initializing MQTT service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Foodyeh API server")
    
    # Disconnect MQTT
    try:
        mqtt_service = get_mqtt_service()
        mqtt_service.disconnect()
        logger.info("MQTT connection closed")
    except Exception as e:
        logger.error(f"Error disconnecting MQTT service: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-ready FastAPI backend for Foodyeh smart vending machine",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.foodyeh.io", "localhost", "127.0.0.1"]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=settings.allowed_methods,
    allow_headers=settings.allowed_headers,
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)


# HTTPS enforcement middleware
@app.middleware("http")
async def enforce_https(request: Request, call_next):
    """Enforce HTTPS in production."""
    if settings.enforce_https and not settings.debug:
        # Check if request is coming through HTTPS
        forwarded_proto = request.headers.get("X-Forwarded-Proto")
        if forwarded_proto != "https":
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Log HTTPS violation for Fail2Ban
            log_https_violation(
                ip=client_ip,
                path=request.url.path,
                user_agent=user_agent
            )
            
            return JSONResponse(
                status_code=400,
                content={"detail": "HTTPS required"}
            )
    
    response = await call_next(request)
    return response


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Remove server information
    response.headers["Server"] = "Foodyeh-API"
    
    return response


# Request logging middleware with security focus
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with security considerations."""
    start_time = time.time()
    
    # Log request (without sensitive data)
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    
    # Don't log sensitive headers or body
    headers_to_log = {
        k: v for k, v in request.headers.items() 
        if k.lower() not in ["authorization", "cookie", "x-api-key"]
    }
    
    logger.info("Request started",
                method=method,
                url=url,
                client_ip=client_ip,
                user_agent=request.headers.get("user-agent", "unknown"))
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log security events for Fail2Ban
        if response.status_code in [401, 403, 429]:
            log_security_event(
                event="unauthorized_access",
                ip=client_ip,
                path=request.url.path,
                status_code=response.status_code,
                method=method,
                user_agent=request.headers.get("user-agent", "unknown")
            )
        
        logger.info("Request completed",
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    process_time=process_time,
                    client_ip=client_ip)
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error("Request failed",
                    method=method,
                    url=url,
                    error=str(e),
                    process_time=process_time,
                    client_ip=client_ip)
        raise


# Global exception handler to prevent information leakage
@app.exception_handler(Exception)
async def safe_error_handler(request: Request, exc: Exception):
    """Global exception handler to prevent information leakage."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log the actual error for debugging (but don't expose it)
    logger.error("Unhandled exception",
                path=request.url.path,
                error=str(exc),
                error_type=type(exc).__name__,
                client_ip=client_ip,
                user_agent=user_agent)
    
    # Log security event for Fail2Ban
    log_security_event(
        event="application_error",
        ip=client_ip,
        path=request.url.path,
        user_agent=user_agent,
        details={"error_type": type(exc).__name__}
    )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    client_ip = request.client.host if request.client else "unknown"
    
    logger.warning("Validation error",
                  path=request.url.path,
                  errors=exc.errors(),
                  client_ip=client_ip)
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    client_ip = request.client.host if request.client else "unknown"
    
    # Log security events for authentication/authorization failures
    if exc.status_code in [401, 403]:
        log_security_event(
            event="auth_failure",
            ip=client_ip,
            path=request.url.path,
            status_code=exc.status_code,
            user_agent=request.headers.get("user-agent", "unknown"),
            details={"detail": exc.detail}
        )
    
    logger.warning("HTTP exception",
                  path=request.url.path,
                  status_code=exc.status_code,
                  detail=exc.detail,
                  client_ip=client_ip)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(order.router, prefix="/api/v1")
app.include_router(status.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Root endpoint with basic information."""
    # Rate limiting check
    rate_limit_middleware(request)
    
    return {
        "message": "Foodyeh API",
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs" if settings.debug else "disabled"
    }


# Health check endpoint (requires authentication)
@app.get("/health")
async def health_check(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Basic health check endpoint."""
    # Rate limiting check
    rate_limit_middleware(request)
    
    try:
        mqtt_service = get_mqtt_service()
        mqtt_healthy = mqtt_service.is_healthy()
        
        return {
            "status": "healthy" if mqtt_healthy else "degraded",
            "timestamp": time.time(),
            "mqtt": "connected" if mqtt_service.is_connected else "disconnected",
            "version": settings.app_version
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": time.time(),
            "error": "Health check failed",
            "version": settings.app_version
        }


# API information endpoint
@app.get("/api/info")
async def api_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Get API information."""
    # Rate limiting check
    rate_limit_middleware(request)
    
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Production-ready FastAPI backend for Foodyeh smart vending machine",
        "features": [
            "JWT Authentication",
            "Rate Limiting",
            "MQTT Integration",
            "Admin Controls",
            "Security Headers",
            "CORS Protection",
            "IP Whitelisting"
        ],
        "endpoints": {
            "orders": "/api/v1/order",
            "status": "/api/v1/status",
            "admin": "/api/v1/admin",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    # Production server configuration
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    ) 