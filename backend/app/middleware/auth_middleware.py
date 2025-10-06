"""
Global authentication middleware for Foodyeh API.
Applies JWT authentication to all endpoints except public auth endpoints.
"""

import re
from typing import List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db
from app.models import User
from app.utils.security import log_security_event

# Public endpoints that don't require authentication
PUBLIC_PATHS = [
    r'^/$',  # Root endpoint
    r'^/health$',
    r'^/auth/signup$',
    r'^/auth/login$',
    r'^/auth/token$',  # Add token endpoint
    r'^/auth/refresh$',
    r'^/docs$',
    r'^/openapi\.json$',
    r'^/redoc$',
    r'^/static/.*$',  # Static files
    r'^/uploads/.*$'  # Upload files
]

# Compile regex patterns for efficient matching
PUBLIC_PATTERNS = [re.compile(pattern) for pattern in PUBLIC_PATHS]

def is_public_path(path: str) -> bool:
    """Check if a path is public (no authentication required)."""
    return any(pattern.match(path) for pattern in PUBLIC_PATTERNS)

async def auth_middleware(request: Request, call_next):
    """
    Global authentication middleware.
    
    - Skips authentication for public paths
    - Applies JWT authentication to all other endpoints
    - Logs security events for unauthorized access
    """
    path = request.url.path
    method = request.method
    
    # Skip authentication for public paths
    if is_public_path(path):
        response = await call_next(request)
        return response
    
    # Skip authentication for OPTIONS requests (CORS preflight)
    if method == "OPTIONS":
        response = await call_next(request)
        return response
    
    # Apply JWT authentication to all other endpoints
    try:
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            client_ip = request.client.host if request.client else "unknown"
            log_security_event("missing_auth_header", ip_address=client_ip, details={
                "path": path,
                "method": method
            })
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header required"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        if not auth_header.startswith("Bearer "):
            client_ip = request.client.host if request.client else "unknown"
            log_security_event("invalid_auth_format", ip_address=client_ip, details={
                "path": path,
                "method": method
            })
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Extract token
        token = auth_header.split(" ")[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(
                token, 
                settings.jwt_secret, 
                algorithms=[settings.jwt_algorithm]
            )
            email: str = payload.get("sub")
            user_id: int = payload.get("user_id")
            
            if email is None or user_id is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token payload"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Get user from database
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if user is None:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            if not user.is_active:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User account is disabled"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Add user to request state
            request.state.user = user
            
            # Continue with the request
            response = await call_next(request)
            return response
            
        except JWTError as e:
            client_ip = request.client.host if request.client else "unknown"
            log_security_event("jwt_decode_error", ip_address=client_ip, details={
                "path": path,
                "method": method,
                "error": str(e)
            })
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
    except Exception as e:
        # Log unexpected authentication errors
        client_ip = request.client.host if request.client else "unknown"
        log_security_event("auth_error", ip_address=client_ip, details={
            "path": path,
            "method": method,
            "error": str(e)
        })
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication failed"},
            headers={"WWW-Authenticate": "Bearer"}
        )
