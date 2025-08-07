"""
Structured logging configuration for Foodyeh API with security focus.
This module configures structlog for production use with Fail2Ban integration.
"""

import sys
import logging
import structlog
from pathlib import Path
from typing import Any, Dict, List

# Create log directory
log_dir = Path("/var/log/foodyeh")
log_dir.mkdir(parents=True, exist_ok=True)

# Security log file for Fail2Ban
SECURITY_LOG_FILE = "/var/log/foodyeh/api.log"
GENERAL_LOG_FILE = "/var/log/foodyeh/app.log"
ERROR_LOG_FILE = "/var/log/foodyeh/error.log"

def configure_logging(debug: bool = False) -> None:
    """
    Configure structured logging with security focus.
    
    Args:
        debug: Enable debug logging
    """
    
    # Configure standard logging
    # Create error handler
    error_handler = logging.FileHandler(ERROR_LOG_FILE)
    error_handler.setLevel(logging.ERROR)
    
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(GENERAL_LOG_FILE),
            error_handler,
        ]
    )
    
    # Configure structlog processors
    processors: List[Any] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ]
    
    # Add security-specific processor
    processors.insert(-1, add_security_context)
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def add_security_context(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add security context to log entries.
    
    Args:
        logger: The logger instance
        method_name: The logging method name
        event_dict: The event dictionary
        
    Returns:
        Enhanced event dictionary with security context
    """
    # Add security event type if not present
    if "event" not in event_dict:
        if method_name in ["warning", "error"]:
            event_dict["event"] = "security_alert"
        else:
            event_dict["event"] = "log_entry"
    
    # Add security level
    if method_name in ["warning", "error"]:
        event_dict["security_level"] = "high" if method_name == "error" else "medium"
    
    # Add timestamp if not present
    if "timestamp" not in event_dict:
        from datetime import datetime
        event_dict["timestamp"] = datetime.utcnow().isoformat()
    
    return event_dict

def get_security_logger() -> structlog.BoundLogger:
    """
    Get a security-focused logger for Fail2Ban integration.
    
    Returns:
        Configured security logger
    """
    return structlog.get_logger("security")

def get_app_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a general application logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured application logger
    """
    return structlog.get_logger(name)

def log_security_event(
    event: str,
    ip: str,
    path: str = None,
    status_code: int = None,
    method: str = None,
    user_agent: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log a security event for Fail2Ban monitoring.
    
    Args:
        event: Security event type
        ip: Client IP address
        path: Request path
        status_code: HTTP status code
        method: HTTP method
        user_agent: User agent string
        details: Additional details
    """
    security_logger = get_security_logger()
    
    log_data = {
        "event": event,
        "ip": ip,
        "level": "warning"
    }
    
    if path:
        log_data["path"] = path
    if status_code:
        log_data["status"] = status_code
    if method:
        log_data["method"] = method
    if user_agent:
        log_data["user_agent"] = user_agent
    if details:
        log_data.update(details)
    
    security_logger.warning("Security event", **log_data)

def log_authentication_attempt(
    ip: str,
    username: str = None,
    success: bool = False,
    path: str = None,
    user_agent: str = None
) -> None:
    """
    Log authentication attempts for monitoring.
    
    Args:
        ip: Client IP address
        username: Username (if available)
        success: Whether authentication was successful
        path: Request path
        user_agent: User agent string
    """
    event = "auth_success" if success else "auth_failure"
    
    log_data = {
        "ip": ip,
        "success": success
    }
    
    if username:
        log_data["username"] = username
    if path:
        log_data["path"] = path
    if user_agent:
        log_data["user_agent"] = user_agent
    
    log_security_event(event, ip, path, user_agent=user_agent, details=log_data)

def log_rate_limit_exceeded(
    ip: str,
    path: str,
    method: str,
    user_agent: str = None
) -> None:
    """
    Log rate limit violations.
    
    Args:
        ip: Client IP address
        path: Request path
        method: HTTP method
        user_agent: User agent string
    """
    log_security_event(
        "rate_limit_exceeded",
        ip,
        path,
        method=method,
        user_agent=user_agent
    )

def log_https_violation(
    ip: str,
    path: str,
    user_agent: str = None
) -> None:
    """
    Log HTTPS enforcement violations.
    
    Args:
        ip: Client IP address
        path: Request path
        user_agent: User agent string
    """
    log_security_event(
        "https_violation",
        ip,
        path,
        user_agent=user_agent
    )

# Initialize logging when module is imported
configure_logging() 