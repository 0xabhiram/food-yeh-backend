from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RefreshToken, UserRole
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, get_current_user, revoke_refresh_token
)
from app.utils.security import rate_limiter, SecurityUtils, log_security_event
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """✅ Secure user registration with input validation (PUBLIC ENDPOINT)"""
    client_ip = request.client.host if request.client else "unknown"
    
    # ✅ Rate limiting for signup: 3 attempts per 10 minutes
    rate_key = f"auth_signup:{client_ip}"
    if rate_limiter.is_rate_limited(rate_key, limit=3, window=600):
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "signup"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # ✅ Input validation and sanitization
    try:
        sanitized_email = SecurityUtils.validate_email(user_data.email)
        sanitized_password = SecurityUtils.validate_password_strength(user_data.password)
        sanitized_first_name = SecurityUtils.sanitize_input(user_data.first_name, max_length=50)
        sanitized_last_name = SecurityUtils.sanitize_input(user_data.last_name, max_length=50)
        sanitized_phone = SecurityUtils.sanitize_input(user_data.phone, max_length=20) if user_data.phone else None
    except HTTPException:
        log_security_event("invalid_input", ip_address=client_ip, details={"endpoint": "signup"})
        raise
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == sanitized_email).first()
    if existing_user:
        log_security_event("duplicate_registration", ip_address=client_ip, details={"email": sanitized_email})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # ✅ Create new user with sanitized data
    hashed_password = get_password_hash(sanitized_password)
    db_user = User(
        email=sanitized_email,
        password_hash=hashed_password,
        first_name=sanitized_first_name,
        last_name=sanitized_last_name,
        phone=sanitized_phone,
        role=UserRole.USER
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # ✅ Log successful registration
    log_security_event("user_registered", user_id=str(db_user.id), ip_address=client_ip)
    
    return db_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """✅ Login user and return access token (PUBLIC ENDPOINT)"""
    # ✅ Enhanced rate limiting for public auth endpoints
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"auth_login:{client_ip}"
    
    # Stricter rate limit for login: 5 attempts per 10 minutes
    if rate_limiter.is_rate_limited(rate_key, limit=5, window=600):
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "login"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Check if account is locked
    if rate_limiter.is_account_locked(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to too many failed attempts"
        )
    
    # ✅ Verify user credentials with sanitized error messages
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        remaining_attempts = rate_limiter.record_failed_login(user_data.email)
        log_security_event("failed_login", ip_address=client_ip, details={"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"  # Generic message for security
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Clear failed login attempts on successful login
    rate_limiter.clear_failed_logins(user_data.email)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=timedelta(days=settings.refresh_token_expire_days)
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """✅ Refresh access token using refresh token (PUBLIC ENDPOINT)"""
    # ✅ Rate limiting for refresh: 10 attempts per 10 minutes
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"auth_refresh:{client_ip}"
    if rate_limiter.is_rate_limited(rate_key, limit=10, window=600):
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "refresh"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many refresh attempts. Please try again later."
        )
    
    try:
        # Get refresh token from request body or header
        body = request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Verify refresh token
        from jose import jwt, JWTError
        payload = jwt.decode(
            refresh_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        
        user_id = int(payload.get("sub"))
        token_type = payload.get("type")
        
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type"
            )
        
        # Check if refresh token exists and is not revoked
        db_refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).first()
        
        if not db_refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
def logout(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Logout user and revoke refresh token"""
    try:
        body = request.json()
        refresh_token = body.get("refresh_token")
        
        if refresh_token:
            revoke_refresh_token(refresh_token, db)
        
        return {"message": "Successfully logged out"}
        
    except Exception:
        return {"message": "Successfully logged out"}
