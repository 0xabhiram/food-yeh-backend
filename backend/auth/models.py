"""
Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class TokenRequest(BaseModel):
    """Request model for token generation."""
    username: str = Field(..., min_length=1, max_length=50, description="Username")
    password: str = Field(..., min_length=6, description="Password")

class TokenResponse(BaseModel):
    """Response model for token generation."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: str = Field(..., description="User role")

class UserCreate(BaseModel):
    """Model for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="Password")
    role: str = Field(default="user", description="User role")
    permissions: List[str] = Field(default=[], description="User permissions")

class UserResponse(BaseModel):
    """Response model for user data."""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    permissions: List[str] = Field(..., description="User permissions")
    is_active: bool = Field(..., description="User active status")

class PasswordChange(BaseModel):
    """Model for password change request."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

class UserUpdate(BaseModel):
    """Model for updating user information."""
    email: Optional[EmailStr] = Field(None, description="User email")
    role: Optional[str] = Field(None, description="User role")
    permissions: Optional[List[str]] = Field(None, description="User permissions")
    is_active: Optional[bool] = Field(None, description="User active status") 