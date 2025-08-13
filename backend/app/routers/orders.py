from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, Dish, User, Payment, PaymentStatus
from app.schemas import OrderCreate, OrderResponse, PaymentCreate, PaymentResponse
from app.auth import get_current_active_user, require_admin
from app.services.mqtt_client import mqtt_client, MQTTCommand
from app.config import settings

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Validate dishes exist and are available
    total_amount = 0
    order_items = []
    
    for item in order_data.items:
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dish with ID {item.dish_id} not found"
            )
        
        if not dish.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dish '{dish.name}' is not available"
            )
        
        item_total = dish.price * item.quantity
        total_amount += item_total
        order_items.append({
            'dish': dish,
            'quantity': item.quantity,
            'unit_price': dish.price,
            'total_price': item_total
        })
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        device_id=order_data.device_id
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItem(
            order_id=order.id,
            dish_id=item_data['dish'].id,
            quantity=item_data['quantity'],
            unit_price=item_data['unit_price'],
            total_price=item_data['total_price']
        )
        db.add(order_item)
    
    db.commit()
    
    # Publish MQTT command if device_id is provided
    if order_data.device_id:
        try:
            mqtt_client.set_db_session(db)
            command = MQTTCommand(
                order_id=order.id,
                items=order_data.items,
                timestamp=datetime.utcnow()
            )
            mqtt_client.publish_command(order_data.device_id, command)
        except Exception as e:
            # Log error but don't fail the order creation
            print(f"Failed to publish MQTT command: {e}")
    
    return order


@router.get("/me", response_model=List[OrderResponse])
def get_my_orders(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Users can only see their own orders, admins can see all
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.post("/{order_id}/pay", response_model=PaymentResponse)
def process_payment(
    order_id: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process payment for an order (dummy payment)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Users can only pay for their own orders
    if current_user.role != "admin" and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to pay for this order"
        )
    
    # Check if payment already exists
    existing_payment = db.query(Payment).filter(Payment.order_id == order_id).first()
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this order"
        )
    
    # Create dummy payment (always successful for POC)
    payment = Payment(
        order_id=order_id,
        amount=order.total_amount,
        status=PaymentStatus.PAID,
        payment_method=payment_data.payment_method,
        transaction_id=f"TXN_{order_id}_{int(datetime.utcnow().timestamp())}"
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment


# Admin endpoints
@router.get("/admin/all", response_model=List[OrderResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    query = db.query(Order)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.put("/admin/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Validate status
    valid_statuses = [s.value for s in OrderStatus]
    if status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )
    
    order.status = status
    order.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"Order status updated to {status}"}
