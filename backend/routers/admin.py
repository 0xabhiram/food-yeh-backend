"""
Admin router for system administration and device control.
Requires admin privileges and IP whitelist validation.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import structlog
from models.order import AdminLogEntry, AdminLogsResponse
from services.auth import get_current_admin_user, require_admin_ip
from services.mqtt_client import get_mqtt_service
from utils.rate_limiter import rate_limiter
from config import settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def get_db():
    """Get database session (placeholder for now)."""
    # In production, this would return a real database session
    return None


@router.get("/logs", response_model=AdminLogsResponse)
async def get_admin_logs(
    request: Request,
    page: int = 1,
    per_page: int = 50,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get admin logs (last 50 actions by default).
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check
        rate_limiter.check_rate_limit(request, limit_per_minute=30, limit_per_hour=100)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 50
        
        # In production, fetch from database with pagination
        # logs = db.query(OrderLog).order_by(
        #     OrderLog.created_at.desc()
        # ).offset((page - 1) * per_page).limit(per_page).all()
        # total = db.query(OrderLog).count()
        
        # For demo purposes, return mock admin logs
        mock_logs = [
            AdminLogEntry(
                id=1,
                order_id="ORD-demo-1",
                action="order_created",
                user_id="admin",
                ip_address="192.168.1.100",
                details="Order created for item demo-item-1",
                created_at=datetime.utcnow() - timedelta(minutes=5)
            ),
            AdminLogEntry(
                id=2,
                order_id="ORD-demo-2",
                action="status_update",
                user_id="system",
                ip_address="192.168.1.100",
                details="Order status updated to completed",
                created_at=datetime.utcnow() - timedelta(minutes=10)
            ),
            AdminLogEntry(
                id=3,
                order_id="ORD-demo-3",
                action="mqtt_message",
                user_id="mqtt_client",
                ip_address="192.168.1.100",
                details="MQTT message received: order confirmed",
                created_at=datetime.utcnow() - timedelta(minutes=15)
            )
        ]
        
        response = AdminLogsResponse(
            logs=mock_logs,
            total=len(mock_logs),
            page=page,
            per_page=per_page
        )
        
        logger.info("Admin logs retrieved", 
                   user_id=current_user.get("sub"), 
                   page=page,
                   per_page=per_page)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting admin logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get admin logs"
        )


@router.post("/reboot")
async def reboot_device(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Send reboot command to ESP32 device.
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check (stricter for admin commands)
        rate_limiter.check_rate_limit(request, limit_per_minute=5, limit_per_hour=20)
        
        mqtt_service = get_mqtt_service()
        
        # Publish reboot command to MQTT
        success = mqtt_service.publish_admin_command("reboot", {
            "reason": "admin_request",
            "requested_by": current_user.get("sub"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if success:
            logger.warning("Device reboot command sent", 
                          user_id=current_user.get("sub"),
                          ip_address=request.client.host if request.client else None)
            
            return {
                "message": "Reboot command sent successfully",
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            }
        else:
            logger.error("Failed to send reboot command", user_id=current_user.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send reboot command"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending reboot command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reboot command"
        )


@router.post("/override")
async def override_device(
    request: Request,
    override_data: Dict[str, Any],
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Send override command to ESP32 device.
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check (stricter for admin commands)
        rate_limiter.check_rate_limit(request, limit_per_minute=5, limit_per_hour=20)
        
        # Validate override data
        required_fields = ["command", "parameters"]
        for field in required_fields:
            if field not in override_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )
        
        # Validate command type
        allowed_commands = ["emergency_stop", "force_vend", "maintenance_mode", "test_mode"]
        command = override_data.get("command")
        if command not in allowed_commands:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid command. Allowed: {allowed_commands}"
            )
        
        mqtt_service = get_mqtt_service()
        
        # Publish override command to MQTT
        success = mqtt_service.publish_admin_command("override", {
            "command": command,
            "parameters": override_data.get("parameters", {}),
            "requested_by": current_user.get("sub"),
            "timestamp": datetime.utcnow().isoformat()
        })
        
        if success:
            logger.warning("Device override command sent", 
                          command=command,
                          user_id=current_user.get("sub"),
                          ip_address=request.client.host if request.client else None)
            
            return {
                "message": "Override command sent successfully",
                "command": command,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            }
        else:
            logger.error("Failed to send override command", 
                        command=command,
                        user_id=current_user.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send override command"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending override command: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send override command"
        )


@router.get("/system-info")
async def get_system_info(
    request: Request,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get detailed system information for administration.
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check
        rate_limiter.check_rate_limit(request, limit_per_minute=30, limit_per_hour=100)
        
        mqtt_service = get_mqtt_service()
        mqtt_status = mqtt_service.get_connection_status()
        
        system_info = {
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.app_version,
            "environment": "production",
            "mqtt": mqtt_status,
            "security": {
                "jwt_enabled": True,
                "admin_ip_whitelist": settings.admin_whitelist_ips,
                "rate_limiting": {
                    "per_minute": settings.rate_limit_per_minute,
                    "per_hour": settings.rate_limit_per_hour
                },
                "cors_origins": settings.allowed_origins
            },
            "database": {
                "type": "sqlite",
                "status": "healthy",
                "last_backup": "2024-01-15T10:30:00Z"
            },
            "redis": {
                "status": "connected",
                "url": settings.redis_url
            },
            "uptime": "2 days, 5 hours, 30 minutes",
            "memory_usage": "45%",
            "cpu_usage": "12%",
            "disk_usage": "23%"
        }
        
        logger.info("System info retrieved by admin", user_id=current_user.get("sub"))
        return system_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system information"
        )


@router.post("/clear-rate-limits")
async def clear_rate_limits(
    request: Request,
    identifier: str,
    limit_type: str = "ip",
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Clear rate limits for a specific identifier.
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check (stricter for admin commands)
        rate_limiter.check_rate_limit(request, limit_per_minute=5, limit_per_hour=20)
        
        # Validate limit type
        if limit_type not in ["ip", "token"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid limit type. Must be 'ip' or 'token'"
            )
        
        # Clear rate limits
        success = rate_limiter.clear_rate_limits(identifier, limit_type)
        
        if success:
            logger.info("Rate limits cleared by admin", 
                       identifier=identifier,
                       limit_type=limit_type,
                       user_id=current_user.get("sub"))
            
            return {
                "message": "Rate limits cleared successfully",
                "identifier": identifier,
                "limit_type": limit_type,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error("Failed to clear rate limits", 
                        identifier=identifier,
                        limit_type=limit_type,
                        user_id=current_user.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear rate limits"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing rate limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear rate limits"
        )


@router.get("/audit-trail")
async def get_audit_trail(
    request: Request,
    start_date: str = None,
    end_date: str = None,
    user_id: str = None,
    action_type: str = None,
    page: int = 1,
    per_page: int = 50,
    current_user: dict = Depends(get_current_admin_user)
):
    """
    Get audit trail with filtering options.
    
    Requires admin authentication and IP whitelist.
    """
    try:
        # Verify admin IP whitelist
        require_admin_ip(request)
        
        # Rate limiting check
        rate_limiter.check_rate_limit(request, limit_per_minute=30, limit_per_hour=100)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 50
        
        # Parse date filters
        filters = {}
        if start_date:
            try:
                filters["start_date"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO format."
                )
        
        if end_date:
            try:
                filters["end_date"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO format."
                )
        
        if user_id:
            filters["user_id"] = user_id
        
        if action_type:
            filters["action_type"] = action_type
        
        # In production, fetch from database with filters
        # query = db.query(OrderLog)
        # if filters.get("start_date"):
        #     query = query.filter(OrderLog.created_at >= filters["start_date"])
        # if filters.get("end_date"):
        #     query = query.filter(OrderLog.created_at <= filters["end_date"])
        # if filters.get("user_id"):
        #     query = query.filter(OrderLog.user_id == filters["user_id"])
        # if filters.get("action_type"):
        #     query = query.filter(OrderLog.action == filters["action_type"])
        # 
        # total = query.count()
        # logs = query.order_by(OrderLog.created_at.desc()).offset(
        #     (page - 1) * per_page
        # ).limit(per_page).all()
        
        # For demo purposes, return mock audit trail
        mock_audit_trail = {
            "logs": [
                {
                    "id": 1,
                    "timestamp": datetime.utcnow().isoformat(),
                    "user_id": "admin",
                    "action": "system_access",
                    "ip_address": "192.168.1.100",
                    "details": "Admin accessed system info"
                }
            ],
            "total": 1,
            "page": page,
            "per_page": per_page,
            "filters_applied": filters
        }
        
        logger.info("Audit trail retrieved by admin", 
                   user_id=current_user.get("sub"),
                   filters=filters)
        
        return mock_audit_trail
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit trail: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get audit trail"
        ) 