from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.database import get_db
from app.models import User, RefreshToken, UserRole
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.utils.security import rate_limiter, SecurityUtils, log_security_event
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Auth functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    from datetime import datetime
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def create_refresh_token(user_id: int) -> str:
    from datetime import datetime
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode = {"sub": str(user_id), "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt

def revoke_refresh_token(token: str, db: Session) -> bool:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload.get("sub"))
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).first()
        
        if refresh_token:
            refresh_token.is_revoked = True
            db.commit()
            return True
        return False
    except JWTError:
        return False

# Auth helper functions for this router
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    except JWTError:
        raise credentials_exception

@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Secure user registration with input validation (PUBLIC ENDPOINT)"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting for signup: 3 attempts per 10 minutes
    rate_key = f"auth_signup:{client_ip}"
    if rate_limiter.is_rate_limited(rate_key, limit=3, window=600):
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "signup"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    # Input validation and sanitization
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
    
    # Create new user with sanitized data
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
    
    # Log successful registration
    log_security_event("user_registered", user_id=str(db_user.id), ip_address=client_ip)
    
    return db_user

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login user and return access token (PUBLIC ENDPOINT)"""
    import logging
    logger = logging.getLogger(__name__)
    
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"auth_login:{client_ip}"
    
    # Log login attempt
    logger.info(f"🔐 LOGIN ATTEMPT: {user_data.email} from {client_ip}")
    
    # Rate limit for login: 5 attempts per 10 minutes
    if rate_limiter.is_rate_limited(rate_key, limit=5, window=600):
        logger.warning(f"🚫 RATE LIMIT EXCEEDED: {user_data.email} from {client_ip}")
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "login"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Verify user credentials
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        logger.warning(f"❌ LOGIN FAILED - USER NOT FOUND: {user_data.email} from {client_ip}")
        remaining_attempts = rate_limiter.record_failed_login(user_data.email)
        log_security_event("failed_login", ip_address=client_ip, details={"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please check your email address."
        )
    
    if not verify_password(user_data.password, user.password_hash):
        logger.warning(f"❌ LOGIN FAILED - INCORRECT PASSWORD: {user_data.email} from {client_ip}")
        remaining_attempts = rate_limiter.record_failed_login(user_data.email)
        log_security_event("failed_login", ip_address=client_ip, details={"email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please check your password and try again."
        )
    
    if not user.is_active:
        logger.warning(f"❌ LOGIN FAILED - ACCOUNT DEACTIVATED: {user_data.email} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Clear failed login attempts on successful login
    rate_limiter.reset_failed_attempts(user_data.email)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token
    from datetime import datetime
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint for Flutter app compatibility (PUBLIC ENDPOINT)"""
    import logging
    logger = logging.getLogger(__name__)
    
    client_ip = "unknown"
    
    # Log login attempt
    logger.info(f"🔐 LOGIN ATTEMPT (TOKEN): {form_data.username} from {client_ip}")
    
    # Rate limit for login: 5 attempts per 10 minutes
    rate_key = f"auth_token:{client_ip}"
    if rate_limiter.is_rate_limited(rate_key, limit=5, window=600):
        logger.warning(f"🚫 RATE LIMIT EXCEEDED (TOKEN): {form_data.username} from {client_ip}")
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "token"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Verify user credentials
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        logger.warning(f"❌ LOGIN FAILED - USER NOT FOUND (TOKEN): {form_data.username} from {client_ip}")
        remaining_attempts = rate_limiter.record_failed_login(form_data.username)
        log_security_event("failed_login", ip_address=client_ip, details={"email": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found. Please check your email address."
        )
    
    if not verify_password(form_data.password, user.password_hash):
        logger.warning(f"❌ LOGIN FAILED - INCORRECT PASSWORD (TOKEN): {form_data.username} from {client_ip}")
        remaining_attempts = rate_limiter.record_failed_login(form_data.username)
        log_security_event("failed_login", ip_address=client_ip, details={"email": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please check your password and try again."
        )
    
    if not user.is_active:
        logger.warning(f"❌ LOGIN FAILED - ACCOUNT DEACTIVATED (TOKEN): {form_data.username} from {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated"
        )
    
    # Clear failed login attempts on successful login
    rate_limiter.reset_failed_attempts(form_data.username)
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    refresh_token = create_refresh_token(user.id)
    
    # Store refresh token
    from datetime import datetime
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using refresh token (PUBLIC ENDPOINT)"""
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"auth_refresh:{client_ip}"
    if rate_limiter.is_rate_limited(rate_key, limit=10, window=600):
        log_security_event("rate_limit_exceeded", ip_address=client_ip, details={"endpoint": "refresh"})
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many refresh attempts. Please try again later."
        )
    
    try:
        body = request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
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
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
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

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

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
