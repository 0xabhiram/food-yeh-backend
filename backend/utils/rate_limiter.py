"""
Rate limiting utilities for API protection.
Supports IP-based and token-based rate limiting with Redis backend.
"""

import time
import hashlib
from typing import Optional, Tuple
from datetime import datetime, timedelta
import redis
from fastapi import HTTPException, Request
import structlog
from config import settings

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Rate limiter with Redis backend for IP and token-based limiting."""
    
    def __init__(self):
        """Initialize rate limiter with Redis connection."""
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis.ping()  # Test connection
            logger.info("Rate limiter initialized with Redis")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Get IP from various headers (for proxy/load balancer setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_token_from_request(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        return None
    
    def _generate_key(self, prefix: str, identifier: str, window: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"rate_limit:{prefix}:{identifier}:{window}"
    
    def _is_rate_limited(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int
    ) -> Tuple[bool, int, int]:
        """
        Check if request is rate limited.
        
        Returns:
            Tuple of (is_limited, current_count, remaining_seconds)
        """
        if not self.redis:
            logger.warning("Redis not available, skipping rate limiting")
            return False, 0, 0
        
        current_time = int(time.time())
        window_start = current_time - (current_time % window_seconds)
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start - 1)  # Remove expired entries
        pipe.zadd(key, {str(current_time): current_time})  # Add current request
        pipe.zcard(key)  # Get current count
        pipe.expire(key, window_seconds)  # Set expiration
        results = pipe.execute()
        
        current_count = results[2]
        is_limited = current_count > limit
        
        if is_limited:
            logger.warning(f"Rate limit exceeded for key: {key}", 
                          count=current_count, limit=limit)
        
        return is_limited, current_count, window_seconds - (current_time % window_seconds)
    
    def check_rate_limit(
        self, 
        request: Request, 
        limit_per_minute: int = None,
        limit_per_hour: int = None
    ) -> None:
        """
        Check rate limits for the request.
        
        Args:
            request: FastAPI request object
            limit_per_minute: Requests per minute (default from settings)
            limit_per_hour: Requests per hour (default from settings)
        
        Raises:
            HTTPException: If rate limit is exceeded
        """
        if not self.redis:
            return
        
        client_ip = self._get_client_ip(request)
        token = self._get_token_from_request(request)
        
        # Use settings defaults if not provided
        limit_per_minute = limit_per_minute or settings.rate_limit_per_minute
        limit_per_hour = limit_per_hour or settings.rate_limit_per_hour
        
        # Check IP-based rate limiting
        ip_key_minute = self._generate_key("ip", client_ip, "minute")
        ip_key_hour = self._generate_key("ip", client_ip, "hour")
        
        is_limited_minute, count_minute, remaining_minute = self._is_rate_limited(
            ip_key_minute, limit_per_minute, 60
        )
        
        is_limited_hour, count_hour, remaining_hour = self._is_rate_limited(
            ip_key_hour, limit_per_hour, 3600
        )
        
        if is_limited_minute:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit_type": "per_minute",
                    "limit": limit_per_minute,
                    "current": count_minute,
                    "reset_in_seconds": remaining_minute
                }
            )
        
        if is_limited_hour:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "limit_type": "per_hour",
                    "limit": limit_per_hour,
                    "current": count_hour,
                    "reset_in_seconds": remaining_hour
                }
            )
        
        # Check token-based rate limiting if token exists
        if token:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            token_key_minute = self._generate_key("token", token_hash, "minute")
            token_key_hour = self._generate_key("token", token_hash, "hour")
            
            is_limited_token_minute, count_token_minute, remaining_token_minute = self._is_rate_limited(
                token_key_minute, limit_per_minute, 60
            )
            
            is_limited_token_hour, count_token_hour, remaining_token_hour = self._is_rate_limited(
                token_key_hour, limit_per_hour, 3600
            )
            
            if is_limited_token_minute:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Token rate limit exceeded",
                        "limit_type": "per_minute",
                        "limit": limit_per_minute,
                        "current": count_token_minute,
                        "reset_in_seconds": remaining_token_minute
                    }
                )
            
            if is_limited_token_hour:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Token rate limit exceeded",
                        "limit_type": "per_hour",
                        "limit": limit_per_hour,
                        "current": count_token_hour,
                        "reset_in_seconds": remaining_token_hour
                    }
                )
        
        # Log successful rate limit check
        logger.debug("Rate limit check passed", 
                    ip=client_ip, 
                    has_token=bool(token),
                    minute_count=count_minute,
                    hour_count=count_hour)
    
    def get_rate_limit_info(self, request: Request) -> dict:
        """Get current rate limit information for the request."""
        if not self.redis:
            return {"error": "Redis not available"}
        
        client_ip = self._get_client_ip(request)
        token = self._get_token_from_request(request)
        
        info = {
            "ip": client_ip,
            "limits": {
                "per_minute": settings.rate_limit_per_minute,
                "per_hour": settings.rate_limit_per_hour
            }
        }
        
        # Get IP-based counts
        ip_key_minute = self._generate_key("ip", client_ip, "minute")
        ip_key_hour = self._generate_key("ip", client_ip, "hour")
        
        info["ip_counts"] = {
            "per_minute": self.redis.zcard(ip_key_minute),
            "per_hour": self.redis.zcard(ip_key_hour)
        }
        
        # Get token-based counts if token exists
        if token:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            token_key_minute = self._generate_key("token", token_hash, "minute")
            token_key_hour = self._generate_key("token", token_hash, "hour")
            
            info["token_counts"] = {
                "per_minute": self.redis.zcard(token_key_minute),
                "per_hour": self.redis.zcard(token_key_hour)
            }
        
        return info
    
    def clear_rate_limits(self, identifier: str, limit_type: str = "ip") -> bool:
        """
        Clear rate limits for a specific identifier.
        
        Args:
            identifier: IP address or token hash
            limit_type: "ip" or "token"
        
        Returns:
            True if successful, False otherwise
        """
        if not self.redis:
            return False
        
        try:
            minute_key = self._generate_key(limit_type, identifier, "minute")
            hour_key = self._generate_key(limit_type, identifier, "hour")
            
            self.redis.delete(minute_key, hour_key)
            logger.info(f"Cleared rate limits for {limit_type}: {identifier}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear rate limits: {e}")
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit_middleware(request: Request, call_next):
    """FastAPI middleware for rate limiting."""
    try:
        rate_limiter.check_rate_limit(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Continue without rate limiting if there's an error
    
    response = call_next(request)
    return response 