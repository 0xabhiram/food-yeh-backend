from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import time
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routers import auth, dishes, orders, admin
from app.services.mqtt_client import mqtt_client
from app.utils.security import rate_limiter, log_security_event
from app.middleware.auth_middleware import auth_middleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Foodyeh API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Connect to MQTT broker
    try:
        mqtt_client.connect()
        logger.info("MQTT client connected")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Foodyeh API...")
    try:
        mqtt_client.disconnect()
        logger.info("MQTT client disconnected")
    except Exception as e:
        logger.error(f"Error disconnecting MQTT client: {e}")


app = FastAPI(
    title="Foodyeh API",
    description="Smart Vending Machine Management System API",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# ✅ Secure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["Content-Length"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# ✅ Global authentication middleware
app.middleware("http")(auth_middleware)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """✅ Rate limiting middleware"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limit by IP
    if rate_limiter.is_rate_limited(client_ip, limit=60, window=60):
        log_security_event("rate_limit_exceeded", ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Try again later."
        )
    
    response = await call_next(request)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """✅ Enhanced request logging with security events"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request (sanitized)
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
    
    response = await call_next(request)
    
    # Log security events for certain status codes
    if response.status_code in [401, 403, 429, 500]:
        log_security_event(
            "request_error",
            ip_address=client_ip,
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code
            }
        )
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """✅ Secure global exception handler with sanitized error messages"""
    # Log the actual error for debugging
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # ✅ Sanitized error messages - never expose internal details in production
    if settings.debug:
        detail = str(exc)
    else:
        detail = "Internal server error"
    
    # ✅ Log security event for monitoring
    client_ip = request.client.host if request.client else "unknown"
    logger.warning("Application error", extra={
        "event_type": "application_error",
        "ip_address": client_ip,
        "path": request.url.path,
        "method": request.method,
        "error_type": type(exc).__name__
    })
    
    return JSONResponse(
        status_code=500,
        content={"detail": detail}
    )


# Include routers
app.include_router(auth.router)
app.include_router(dishes.router)
app.include_router(orders.router)
app.include_router(admin.router)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Foodyeh API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
