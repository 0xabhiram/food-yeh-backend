"""
Security utilities for Foodyeh API.
Provides input sanitization, rate limiting, and security validation functions.
"""

import re
import hashlib
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# In-memory rate limiting storage (use Redis in production)
_rate_limit_store: Dict[str, List[float]] = {}
_account_lockout: Dict[str, Dict] = {}

class SecurityUtils:
    """Security utility functions for input validation and sanitization."""
    
    # SQL injection patterns
    SQL_PATTERNS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'UNION', 'EXEC', 'EXECUTE', 'SCRIPT', '--', '/*', '*/', 'xp_', 'sp_'
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=', 'onclick=',
        '<iframe', '<object', '<embed', 'data:text/html', 'expression('
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = ['..', '../', '..\\', '..\\\\', '/etc/', '/var/', 'C:\\']
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize user input to prevent injection attacks.
        
        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
            
        Raises:
            HTTPException: If input contains malicious patterns
        """
        if not input_str:
            return ""
        
        # Check length
        if len(input_str) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long. Maximum {max_length} characters allowed."
            )
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_str)
        
        # Check for SQL injection patterns
        for pattern in SecurityUtils.SQL_PATTERNS:
            if pattern.lower() in sanitized.lower():
                logger.warning(f"SQL injection pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        # Check for XSS patterns
        for pattern in SecurityUtils.XSS_PATTERNS:
            if pattern.lower() in sanitized.lower():
                logger.warning(f"XSS pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
        
        return sanitized.strip()
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Validate and sanitize filename to prevent path traversal.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Validated filename
            
        Raises:
            HTTPException: If filename is invalid
        """
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename is required"
            )
        
        # Check for path traversal patterns
        for pattern in SecurityUtils.PATH_TRAVERSAL_PATTERNS:
            if pattern in filename:
                logger.warning(f"Path traversal attempt detected: {filename}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filename"
                )
        
        # Check for dangerous characters
        if re.search(r'[<>:"/\\|?*]', filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid characters in filename"
            )
        
        return filename
    
    @staticmethod
    def validate_email(email: str) -> str:
        """
        Validate email format and sanitize.
        
        Args:
            email: Email to validate
            
        Returns:
            Validated email
            
        Raises:
            HTTPException: If email is invalid
        """
        email = email.strip().lower()
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Sanitize email
        return SecurityUtils.sanitize_input(email, max_length=254)
    
    @staticmethod
    def validate_password_strength(password: str) -> str:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            HTTPException: If password is too weak
        """
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        if not re.search(r'[A-Z]', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter"
            )
        
        if not re.search(r'[a-z]', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter"
            )
        
        if not re.search(r'\d', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one number"
            )
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one special character"
            )
        
        return password

class RateLimiter:
    """Rate limiting implementation for API endpoints."""
    
    def __init__(self):
        self.store = _rate_limit_store
        self.lockout_store = _account_lockout
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        """
        Check if request is rate limited.
        
        Args:
            key: Rate limit key (usually IP or user ID)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()
        
        # Clean old entries
        if key in self.store:
            self.store[key] = [t for t in self.store[key] if now - t < window]
        else:
            self.store[key] = []
        
        # Check if rate limited
        if len(self.store[key]) >= limit:
            return True
        
        # Add current request
        self.store[key].append(now)
        return False
    
    def record_failed_login(self, username: str) -> int:
        """
        Record failed login attempt and check for account lockout.
        
        Args:
            username: Username that failed login
            
        Returns:
            Number of failed attempts
        """
        now = time.time()
        
        if username not in self.lockout_store:
            self.lockout_store[username] = {
                'attempts': 0,
                'first_attempt': now,
                'locked_until': None
            }
        
        user_data = self.lockout_store[username]
        
        # Check if account is locked
        if user_data['locked_until'] and now < user_data['locked_until']:
            remaining = int(user_data['locked_until'] - now)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Account locked. Try again in {remaining} seconds"
            )
        
        # Reset if lockout period has passed
        if user_data['locked_until'] and now >= user_data['locked_until']:
            user_data['attempts'] = 0
            user_data['locked_until'] = None
        
        # Increment failed attempts
        user_data['attempts'] += 1
        
        # Lock account after 5 failed attempts
        if user_data['attempts'] >= 5:
            user_data['locked_until'] = now + 900  # 15 minutes
            logger.warning(f"Account locked: {username}")
        
        return user_data['attempts']
    
    def reset_failed_attempts(self, username: str):
        """Reset failed login attempts for successful login."""
        if username in self.lockout_store:
            self.lockout_store[username]['attempts'] = 0
            self.lockout_store[username]['locked_until'] = None

# Global rate limiter instance
rate_limiter = RateLimiter()

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: dict = None):
    """
    Log security events for monitoring.
    
    Args:
        event_type: Type of security event
        user_id: User ID involved
        ip_address: IP address involved
        details: Additional details
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details or {}
    }
    logger.warning("Security event", extra=log_data)
