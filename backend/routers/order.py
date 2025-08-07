"""
Order router for handling vending machine orders.
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import structlog
from models.order import (
    OrderCreate, OrderResponse, OrderStatusUpdate, OrderListResponse,
    Order, OrderLog, OrderStatus
)
from services.auth import get_current_user
from services.mqtt_client import get_mqtt_service
from utils.rate_limiter import rate_limiter
from config import settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/order", tags=["orders"])


def get_db():
    """Get database session (placeholder for now)."""
    # In production, this would return a real database session
    return None


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new vending machine order.
    
    Requires authentication and is rate limited.
    """
    try:
        # Rate limiting check
        rate_limiter.check_rate_limit(request)
        
        # Generate unique order ID
        order_id = f"ORD-{uuid.uuid4()}"
        
        # Create order record
        order = Order(
            order_id=order_id,
            item_id=order_data.item_id,
            slot_id=order_data.slot_id,
            quantity=order_data.quantity,
            status=OrderStatus.PENDING,
            order_type=order_data.order_type,
            user_id=current_user.get("sub"),
            ip_address=request.client.host if request.client else None
        )
        
        # In production, save to database
        # db.add(order)
        # db.commit()
        # db.refresh(order)
        
        # Log order creation
        logger.info("Order created", 
                   order_id=order_id, 
                   item_id=order_data.item_id,
                   slot_id=order_data.slot_id,
                   user_id=current_user.get("sub"))
        
        # Publish order to MQTT
        mqtt_service = get_mqtt_service()
        if mqtt_service.publish_order(
            order_id=order_id,
            item_id=order_data.item_id,
            slot_id=order_data.slot_id,
            quantity=order_data.quantity
        ):
            logger.info("Order published to MQTT", order_id=order_id)
        else:
            logger.error("Failed to publish order to MQTT", order_id=order_id)
            # Don't fail the request, but log the issue
        
        # Create response
        response = OrderResponse(
            order_id=order_id,
            item_id=order_data.item_id,
            slot_id=order_data.slot_id,
            quantity=order_data.quantity,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_status(
    order_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of a specific order.
    
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
        
        # In production, fetch from database
        # order = db.query(Order).filter(Order.order_id == order_id).first()
        # if not order:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Order not found"
        #     )
        
        # For demo purposes, return mock data
        # In production, this would be the actual order from database
        mock_order = OrderResponse(
            order_id=order_id,
            item_id="demo-item",
            slot_id=1,
            quantity=1,
            status=OrderStatus.PREPARING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        logger.debug("Order status retrieved", order_id=order_id, user_id=current_user.get("sub"))
        return mock_order
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get order status"
        )


@router.get("/", response_model=OrderListResponse)
async def list_orders(
    request: Request,
    page: int = 1,
    per_page: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List orders for the current user.
    
    Requires authentication and is rate limited.
    """
    try:
        # Rate limiting check
        rate_limiter.check_rate_limit(request)
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if per_page < 1 or per_page > 100:
            per_page = 20
        
        # In production, fetch from database with pagination
        # orders = db.query(Order).filter(
        #     Order.user_id == current_user.get("sub")
        # ).offset((page - 1) * per_page).limit(per_page).all()
        # total = db.query(Order).filter(
        #     Order.user_id == current_user.get("sub")
        # ).count()
        
        # For demo purposes, return mock data
        mock_orders = [
            OrderResponse(
                order_id=f"ORD-{uuid.uuid4()}",
                item_id="demo-item-1",
                slot_id=1,
                quantity=1,
                status=OrderStatus.COMPLETED,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            OrderResponse(
                order_id=f"ORD-{uuid.uuid4()}",
                item_id="demo-item-2",
                slot_id=2,
                quantity=2,
                status=OrderStatus.PREPARING,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        response = OrderListResponse(
            orders=mock_orders,
            total=len(mock_orders),
            page=page,
            per_page=per_page
        )
        
        logger.debug("Orders listed", user_id=current_user.get("sub"), page=page)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list orders"
        )


@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update order status (typically called by MQTT handlers).
    
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
        
        # In production, update database
        # order = db.query(Order).filter(Order.order_id == order_id).first()
        # if not order:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Order not found"
        #     )
        # 
        # # Log the status change
        # log_entry = OrderLog(
        #     order_id=order_id,
        #     action="status_update",
        #     status_before=order.status,
        #     status_after=status_update.status,
        #     user_id=current_user.get("sub"),
        #     ip_address=request.client.host if request.client else None,
        #     details=f"Status updated to {status_update.status}"
        # )
        # 
        # order.status = status_update.status
        # order.updated_at = datetime.utcnow()
        # 
        # if status_update.error_message:
        #     order.error_message = status_update.error_message
        # 
        # if status_update.estimated_completion:
        #     order.estimated_completion = status_update.estimated_completion
        # 
        # db.add(log_entry)
        # db.commit()
        
        logger.info("Order status updated", 
                   order_id=order_id, 
                   new_status=status_update.status,
                   user_id=current_user.get("sub"))
        
        return {"message": "Order status updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )


@router.delete("/{order_id}")
async def cancel_order(
    order_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order.
    
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
        
        # In production, update database
        # order = db.query(Order).filter(Order.order_id == order_id).first()
        # if not order:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail="Order not found"
        #     )
        # 
        # # Check if order can be cancelled
        # if order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Order cannot be cancelled"
        #     )
        # 
        # order.status = OrderStatus.CANCELLED
        # order.updated_at = datetime.utcnow()
        # 
        # # Log the cancellation
        # log_entry = OrderLog(
        #     order_id=order_id,
        #     action="order_cancelled",
        #     status_before=order.status,
        #     status_after=OrderStatus.CANCELLED,
        #     user_id=current_user.get("sub"),
        #     ip_address=request.client.host if request.client else None,
        #     details="Order cancelled by user"
        # )
        # 
        # db.add(log_entry)
        # db.commit()
        
        # Publish cancellation to MQTT
        mqtt_service = get_mqtt_service()
        mqtt_service.publish_admin_command("cancel_order", {"order_id": order_id})
        
        logger.info("Order cancelled", 
                   order_id=order_id, 
                   user_id=current_user.get("sub"))
        
        return {"message": "Order cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel order"
        ) 