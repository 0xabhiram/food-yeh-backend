"""
JWT Authentication Handler for Foodyeh API.
Implements secure JWT token generation and verification using python-jose.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class JWTHandler:
    """JWT token handler with secure configuration."""
    
    def __init__(self):
        # Get secret key from environment or generate a secure one
        self.secret_key = self._get_secret_key()
        self.algorithm = "HS512"  # Using HS512 as requested
        self.access_token_expire_days = 180  # 6 months as requested
        
    def _get_secret_key(self) -> str:
        """Get or generate a secure 512-bit secret key."""
        secret_key = os.getenv("JWT_SECRET_KEY")
        
        if not secret_key:
            # Generate a secure 512-bit (64 bytes) key
            secret_key = secrets.token_urlsafe(64)
            print(f"WARNING: JWT_SECRET_KEY not found in environment. Generated temporary key: {secret_key[:20]}...")
            print("Please set JWT_SECRET_KEY environment variable for production use.")
        
        # Ensure minimum length for security
        if len(secret_key) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")
            
        return secret_key
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        # Set expiration time (6 months from now)
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.access_token_expire_days)
        
        # Add required JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
        })
        
        # Ensure 'sub' claim is present
        if "sub" not in to_encode:
            raise ValueError("JWT payload must include 'sub' claim")
        
        # Encode JWT with HS512 algorithm
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            # Decode and verify the token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Validate required claims
            if "sub" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing 'sub' claim"
                )
            
            if "exp" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing 'exp' claim"
                )
            
            if "iat" not in payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing 'iat' claim"
                )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

# Global JWT handler instance
jwt_handler = JWTHandler()

async def get_current_user(credentials: HTTPAuthorizationCredentials = security) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        User data from token payload
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    payload = jwt_handler.verify_token(token)
    
    # Extract user information from token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    return {
        "user_id": user_id,
        "username": payload.get("username"),
        "role": payload.get("role", "user"),
        "permissions": payload.get("permissions", []),
        "token_data": payload
    }

async def get_current_admin_user(current_user: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Dependency to get the current admin user.
    Requires the user to have admin role.
    
    Args:
        current_user: Current user from get_current_user dependency
        
    Returns:
        Admin user data
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user is None:
        current_user = await get_current_user()
    
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    return current_user 