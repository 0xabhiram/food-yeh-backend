"""
Authentication service for JWT token handling and user validation.
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
from config import settings
from fastapi import Request

logger = structlog.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()


class AuthService:
    """Authentication service for JWT token handling."""
    
    def __init__(self):
        """Initialize authentication service."""
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Token payload data
            expires_delta: Optional expiration delta
        
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info("Access token created", user_id=data.get("sub"))
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload
        
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user ID"
                )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            logger.debug("Token verified successfully", user_id=user_id)
            return payload
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed"
            )
    
    def get_current_user(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """
        Get current user from JWT token.
        
        Args:
            credentials: HTTP authorization credentials
        
        Returns:
            User information from token
        
        Raises:
            HTTPException: If token is invalid
        """
        token = credentials.credentials
        
        # Additional security checks
        if not token or len(token) < 10:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
        
        # Check for suspicious patterns in token
        if any(pattern in token.lower() for pattern in ["script", "javascript", "vbscript"]):
            logger.warning("Suspicious token pattern detected", token_preview=token[:10])
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        payload = self.verify_token(token)
        return payload
    
    def get_current_admin_user(
        self, 
        current_user: Dict[str, Any] = Depends(lambda: None)
    ) -> Dict[str, Any]:
        """
        Get current admin user with elevated privileges.
        
        Args:
            current_user: Current user from token
        
        Returns:
            Admin user information
        
        Raises:
            HTTPException: If user is not admin
        """
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # Check if user has admin role
        user_role = current_user.get("role", "user")
        if user_role != "admin":
            logger.warning("Non-admin user attempted admin access", 
                          user_id=current_user.get("sub"), role=user_role)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return current_user
    
    def validate_ip_whitelist(self, client_ip: str) -> bool:
        """
        Validate if client IP is in admin whitelist.
        
        Args:
            client_ip: Client IP address
        
        Returns:
            True if IP is whitelisted, False otherwise
        """
        if not settings.admin_whitelist_ips:
            logger.warning("No admin IP whitelist configured")
            return False
        
        # Check exact IP match
        if client_ip in settings.admin_whitelist_ips:
            return True
        
        # Check for CIDR notation (basic implementation)
        for whitelisted_ip in settings.admin_whitelist_ips:
            if "/" in whitelisted_ip:
                # Basic CIDR check (in production, use ipaddress module)
                network_part = whitelisted_ip.split("/")[0]
                if client_ip.startswith(network_part):
                    return True
        
        logger.warning("IP not in admin whitelist", ip=client_ip)
        return False
    
    def create_user_token(self, user_id: str, role: str = "user") -> str:
        """
        Create access token for user.
        
        Args:
            user_id: User identifier
            role: User role (default: "user")
        
        Returns:
            JWT access token
        """
        data = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "iat": datetime.utcnow().timestamp()
        }
        
        return self.create_access_token(data)
    
    def refresh_token(self, token: str) -> str:
        """
        Refresh an existing token.
        
        Args:
            token: Current JWT token
        
        Returns:
            New JWT access token
        """
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            role = payload.get("role", "user")
            
            # Create new token with same user info
            return self.create_user_token(user_id, role)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token (add to blacklist).
        
        Args:
            token: JWT token to revoke
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # In a production system, you would add the token to a blacklist
            # For now, we'll just log the revocation
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            logger.info("Token revoked", user_id=user_id)
            return True
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False


# Global auth service instance
auth_service = AuthService()


# Dependency functions for FastAPI
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """FastAPI dependency for getting current user."""
    return auth_service.get_current_user(credentials)


def get_current_admin_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """FastAPI dependency for getting current admin user."""
    return auth_service.get_current_admin_user(current_user)


def require_admin_ip(request: Request) -> bool:
    """FastAPI dependency for requiring admin IP whitelist."""
    client_ip = request.client.host if request.client else "unknown"
    
    if not auth_service.validate_ip_whitelist(client_ip):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: IP not in admin whitelist"
        )
    
    return True 