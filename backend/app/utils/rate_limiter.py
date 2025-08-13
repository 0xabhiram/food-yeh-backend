import redis
import time
from typing import Optional
from app.config import settings

redis_client = redis.from_url(settings.redis_url)


class RateLimiter:
    def __init__(self):
        self.redis_client = redis_client
    
    def is_rate_limited(self, key: str, limit: int, window: int) -> bool:
        """Check if request is rate limited"""
        current_time = int(time.time())
        window_start = current_time - window
        
        # Remove old entries
        self.redis_client.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = self.redis_client.zcard(key)
        
        if current_count >= limit:
            return True
        
        # Add current request
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, window)
        
        return False
    
    def is_account_locked(self, email: str) -> bool:
        """Check if account is locked due to failed login attempts"""
        lock_key = f"account_lock:{email}"
        return self.redis_client.exists(lock_key) > 0
    
    def record_failed_login(self, email: str) -> int:
        """Record failed login attempt and return remaining attempts"""
        key = f"failed_logins:{email}"
        current_time = int(time.time())
        window = settings.account_lockout_duration
        
        # Remove old attempts
        self.redis_client.zremrangebyscore(key, 0, current_time - window)
        
        # Add current attempt
        self.redis_client.zadd(key, {str(current_time): current_time})
        self.redis_client.expire(key, window)
        
        # Count attempts
        attempts = self.redis_client.zcard(key)
        
        # Lock account if too many attempts
        if attempts >= settings.account_lockout_attempts:
            lock_key = f"account_lock:{email}"
            self.redis_client.setex(lock_key, window, "locked")
        
        return max(0, settings.account_lockout_attempts - attempts)
    
    def clear_failed_logins(self, email: str):
        """Clear failed login attempts for successful login"""
        key = f"failed_logins:{email}"
        lock_key = f"account_lock:{email}"
        self.redis_client.delete(key, lock_key)
    
    def get_remaining_attempts(self, email: str) -> int:
        """Get remaining login attempts"""
        key = f"failed_logins:{email}"
        current_time = int(time.time())
        window = settings.account_lockout_duration
        
        # Remove old attempts
        self.redis_client.zremrangebyscore(key, 0, current_time - window)
        
        # Count current attempts
        attempts = self.redis_client.zcard(key)
        return max(0, settings.account_lockout_attempts - attempts)


rate_limiter = RateLimiter()
