"""
Status router for checking order status and system health.
"""

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
import structlog
from models.order import HealthCheck
from services.auth import get_current_user
from services.mqtt_client import get_mqtt_service
from utils.rate_limiter import rate_limiter
from config import settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/status", tags=["status"])

# Track application startup time for uptime calculation
startup_time = time.time()


@router.get("/health", response_model=HealthCheck)
async def health_check(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Health check endpoint.
    
    Returns system health status including MQTT and database connectivity.
    Requires authentication.
    """
    # Rate limiting check
    rate_limiter.check_rate_limit(request)
    
    try:
        # Get MQTT service status
        mqtt_service = get_mqtt_service()
        mqtt_status = "healthy" if mqtt_service.is_healthy() else "unhealthy"
        
        # In production, check database connectivity
        # try:
        #     db.execute("SELECT 1")
        #     db_status = "healthy"
        # except Exception as e:
        #     logger.error(f"Database health check failed: {e}")
        #     db_status = "unhealthy"
        db_status = "healthy"  # Mock for demo
        
        # Calculate uptime
        uptime = time.time() - startup_time
        
        health_check = HealthCheck(
            status="healthy" if mqtt_status == "healthy" and db_status == "healthy" else "degraded",
            timestamp=datetime.utcnow(),
            version=settings.app_version,
            mqtt_status=mqtt_status,
            database_status=db_status,
            uptime=uptime
        )
        
        logger.debug("Health check performed", 
                    status=health_check.status,
                    mqtt_status=mqtt_status,
                    db_status=db_status)
        
        return health_check
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@router.get("/mqtt")
async def mqtt_status(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed MQTT connection status.
    
    Requires authentication.
    """
    # Rate limiting check
    rate_limiter.check_rate_limit(request)
    
    try:
        mqtt_service = get_mqtt_service()
        status_info = mqtt_service.get_connection_status()
        
        logger.debug("MQTT status retrieved", connected=status_info["connected"])
        return status_info
        
    except Exception as e:
        logger.error(f"MQTT status check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MQTT status"
        )


@router.get("/order/{order_id}")
async def get_order_status_detailed(
    order_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed status of a specific order.
    
    Requires authentication and is rate limited.
    """
    try:
        # Rate limiting check
        rate_limiter.check_rate_limit(request)
        
        # Validate order ID format
        if not order_id.startswith("ORD-") or len(order_id) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid order ID format"
            )
        
        # In production, fetch detailed order information from database
        # order = db.query(Order).filter(Order.order_id == order_id).first()
        # if not order:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Order not found"
        #     )
        
        # For demo purposes, return mock detailed status
        detailed_status = {
            "order_id": order_id,
            "status": "preparing",
            "progress": 75,  # Percentage complete
            "estimated_completion": datetime.utcnow().isoformat(),
            "current_step": "dispensing",
            "steps": [
                {"name": "order_received", "status": "completed", "timestamp": datetime.utcnow().isoformat()},
                {"name": "item_selected", "status": "completed", "timestamp": datetime.utcnow().isoformat()},
                {"name": "dispensing", "status": "in_progress", "timestamp": datetime.utcnow().isoformat()},
                {"name": "ready_for_pickup", "status": "pending", "timestamp": None}
            ],
            "error_message": None,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        logger.debug("Detailed order status retrieved", 
                    order_id=order_id, 
                    user_id=current_user.get("sub"))
        
        return detailed_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting detailed order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order status"
        )


@router.get("/system")
async def system_status(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get system-wide status information.
    
    Requires authentication and is rate limited.
    """
    try:
        # Rate limiting check
        rate_limiter.check_rate_limit(request)
        
        # Get MQTT service status
        mqtt_service = get_mqtt_service()
        mqtt_status = mqtt_service.get_connection_status()
        
        # In production, get additional system metrics
        system_status = {
            "timestamp": datetime.utcnow().isoformat(),
            "mqtt": mqtt_status,
            "database": {
                "status": "healthy",
                "connection_pool": "active",
                "last_backup": "2024-01-15T10:30:00Z"
            },
            "rate_limiting": {
                "enabled": True,
                "limits": {
                    "per_minute": settings.rate_limit_per_minute,
                    "per_hour": settings.rate_limit_per_hour
                }
            },
            "security": {
                "jwt_enabled": True,
                "cors_enabled": True,
                "rate_limiting_enabled": True,
                "admin_ip_whitelist": len(settings.admin_whitelist_ips) > 0
            },
            "uptime": time.time() - startup_time,
            "version": settings.app_version
        }
        
        logger.debug("System status retrieved", user_id=current_user.get("sub"))
        return system_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system status"
        )


@router.get("/rate-limits")
async def get_rate_limit_info(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current rate limit information for the requesting client.
    
    Requires authentication.
    """
    try:
        rate_limit_info = rate_limiter.get_rate_limit_info(request)
        
        logger.debug("Rate limit info retrieved", user_id=current_user.get("sub"))
        return rate_limit_info
        
    except Exception as e:
        logger.error(f"Error getting rate limit info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get rate limit information"
        )


@router.post("/mqtt/reconnect")
async def reconnect_mqtt(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Force MQTT reconnection.
    
    Requires authentication and admin privileges.
    """
    try:
        # Check if user has admin role
        user_role = current_user.get("role", "user")
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        mqtt_service = get_mqtt_service()
        
        # Disconnect and reconnect
        mqtt_service.disconnect()
        success = mqtt_service.connect()
        
        if success:
            logger.info("MQTT reconnection initiated by admin", user_id=current_user.get("sub"))
            return {"message": "MQTT reconnection initiated successfully"}
        else:
            logger.error("MQTT reconnection failed", user_id=current_user.get("sub"))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MQTT reconnection failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reconnecting MQTT: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reconnect MQTT"
        ) 