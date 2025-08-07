"""
Authentication routes for Foodyeh API.
Provides JWT token generation and user management endpoints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from .jwt_handler import jwt_handler, get_current_user, get_current_admin_user
from .models import TokenRequest, TokenResponse, UserCreate, UserResponse, PasswordChange, UserUpdate
from database import get_db
from logging_config import log_authentication_attempt

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory user storage for demo (replace with database in production)
DEMO_USERS = {
    "admin": {
        "user_id": "admin-001",
        "username": "admin",
        "email": "admin@foodyeh.io",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8J5Hh2e",  # admin123
        "role": "admin",
        "permissions": ["read", "write", "admin"],
        "is_active": True
    },
    "user": {
        "user_id": "user-001", 
        "username": "user",
        "email": "user@foodyeh.io",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8J5Hh2e",  # admin123
        "role": "user",
        "permissions": ["read"],
        "is_active": True
    }
}

def get_user_by_username(username: str) -> Dict[str, Any]:
    """Get user by username from demo storage."""
    return DEMO_USERS.get(username)

def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user with username and password.
    
    Args:
        username: Username
        password: Plain text password
        
    Returns:
        User data if authentication successful
        
    Raises:
        HTTPException: If authentication fails
    """
    user = get_user_by_username(username)
    if not user:
        return None
    
    if not jwt_handler.verify_password(password, user["hashed_password"]):
        return None
    
    if not user["is_active"]:
        return None
    
    return user

@router.post("/token", response_model=TokenResponse)
async def create_access_token(
    token_request: TokenRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """
    Create JWT access token for authenticated user.
    
    Args:
        token_request: Username and password
        db: Database session
        
    Returns:
        JWT token response
        
    Raises:
        HTTPException: If authentication fails
    """
    # Authenticate user
    user = authenticate_user(token_request.username, token_request.password)
    
    if not user:
        # Log failed authentication attempt
        log_authentication_attempt(
            ip="127.0.0.1",  # In production, get from request
            username=token_request.username,
            success=False,
            path="/auth/token"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful authentication
    log_authentication_attempt(
        ip="127.0.0.1",  # In production, get from request
        username=token_request.username,
        success=True,
        path="/auth/token"
    )
    
    # Create token data
    token_data = {
        "sub": user["user_id"],
        "username": user["username"],
        "role": user["role"],
        "permissions": user["permissions"]
    }
    
    # Generate access token
    access_token = jwt_handler.create_access_token(data=token_data)
    
    # Calculate expiration time
    expires_in = jwt_handler.access_token_expire_days * 24 * 60 * 60  # Convert days to seconds
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user_id=user["user_id"],
        username=user["username"],
        role=user["role"]
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    user = get_user_by_username(current_user["username"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse(
        user_id=user["user_id"],
        username=user["username"],
        email=user["email"],
        role=user["role"],
        permissions=user["permissions"],
        is_active=user["is_active"]
    )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Change user password.
    
    Args:
        password_change: Current and new password
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    user = get_user_by_username(current_user["username"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if not jwt_handler.verify_password(password_change.current_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = jwt_handler.hash_password(password_change.new_password)
    
    # Update password (in production, save to database)
    user["hashed_password"] = new_hashed_password
    
    return {"message": "Password changed successfully"}

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> List[UserResponse]:
    """
    Get all users (admin only).
    
    Args:
        current_user: Current admin user
        
    Returns:
        List of all users
    """
    users = []
    for user_data in DEMO_USERS.values():
        users.append(UserResponse(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data["email"],
            role=user_data["role"],
            permissions=user_data["permissions"],
            is_active=user_data["is_active"]
        ))
    
    return users

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_create: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_admin_user)
) -> UserResponse:
    """
    Create a new user (admin only).
    
    Args:
        user_create: User creation data
        current_user: Current admin user
        
    Returns:
        Created user information
    """
    # Check if username already exists
    if get_user_by_username(user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    hashed_password = jwt_handler.hash_password(user_create.password)
    
    new_user = {
        "user_id": user_id,
        "username": user_create.username,
        "email": user_create.email,
        "hashed_password": hashed_password,
        "role": user_create.role,
        "permissions": user_create.permissions,
        "is_active": True
    }
    
    # Add to demo storage (in production, save to database)
    DEMO_USERS[user_create.username] = new_user
    
    return UserResponse(
        user_id=new_user["user_id"],
        username=new_user["username"],
        email=new_user["email"],
        role=new_user["role"],
        permissions=new_user["permissions"],
        is_active=new_user["is_active"]
    )

@router.get("/verify")
async def verify_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify JWT token validity.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Token verification result
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"],
        "permissions": current_user["permissions"]
    } 