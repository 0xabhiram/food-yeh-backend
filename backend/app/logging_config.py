"""
Enhanced logging configuration for Foodyeh API
Provides clean, structured logging with proper levels
"""

import logging
import sys
from datetime import datetime
from typing import Dict, Any

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)

class LoginFilter(logging.Filter):
    """Filter to highlight login-related logs"""
    
    def filter(self, record):
        # Highlight login attempts
        if 'LOGIN ATTEMPT' in record.getMessage():
            record.levelname = f"🔐 {record.levelname}"
        elif 'LOGIN SUCCESS' in record.getMessage():
            record.levelname = f"✅ {record.levelname}"
        elif 'LOGIN FAILED' in record.getMessage():
            record.levelname = f"❌ {record.levelname}"
        elif 'RATE LIMIT' in record.getMessage():
            record.levelname = f"🚫 {record.levelname}"
        
        return True

def setup_logging():
    """Setup enhanced logging configuration"""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add login filter
    login_filter = LoginFilter()
    console_handler.addFilter(login_filter)
    console_handler.setFormatter(formatter)
    
    # File handler for persistent logs
    file_handler = logging.FileHandler('logs/foodyeh.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('app.services.mqtt_client').setLevel(logging.WARNING)  # Reduce MQTT spam
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)  # Reduce access log spam
    
    # Keep important loggers at INFO level
    logging.getLogger('app.routers.auth').setLevel(logging.INFO)
    logging.getLogger('app.main').setLevel(logging.INFO)
    
    return logger

def log_user_action(action: str, user_id: int = None, email: str = None, ip: str = None, details: Dict[str, Any] = None):
    """Log user actions with structured format"""
    logger = logging.getLogger('app.user_actions')
    
    log_data = {
        'action': action,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'email': email,
        'ip_address': ip,
        'details': details or {}
    }
    
    logger.info(f"USER ACTION: {action} | User: {email or user_id} | IP: {ip} | Details: {details}")

def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, details: Dict[str, Any] = None):
    """Log security events with structured format"""
    logger = logging.getLogger('app.security')
    
    log_data = {
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': user_id,
        'ip_address': ip_address,
        'details': details or {}
    }
    
    logger.warning(f"SECURITY EVENT: {event_type} | User: {user_id} | IP: {ip_address} | Details: {details}")

def log_api_request(method: str, path: str, status_code: int, response_time: float, ip: str = None):
    """Log API requests with structured format"""
    logger = logging.getLogger('app.api_requests')
    
    # Color code status codes
    if status_code >= 500:
        status_color = "🔴"  # Red for server errors
    elif status_code >= 400:
        status_color = "🟡"  # Yellow for client errors
    elif status_code >= 300:
        status_color = "🔵"  # Blue for redirects
    else:
        status_color = "🟢"  # Green for success
    
    logger.info(f"API REQUEST: {method} {path} | Status: {status_color} {status_code} | Time: {response_time:.3f}s | IP: {ip}")

# Initialize logging when module is imported
setup_logging()
