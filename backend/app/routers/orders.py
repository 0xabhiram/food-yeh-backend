from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
from jose import JWTError, jwt

from app.database import get_db
from app.models import Order, OrderItem, User, Dish
from app.schemas import OrderCreate, OrderResponse, OrderStatus
from app.services.mqtt_client import mqtt_client
from app.config import settings

router = APIRouter(prefix="/orders", tags=["orders"])

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
logger = logging.getLogger(__name__)

# ✅ SECURITY: Proper JWT authentication
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
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

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order and send to ESP32 via MQTT"""
    try:
        # Validate items exist
        total_amount = 0
        items_data = []
        
        for item in order_data.items:
            dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
            if not dish:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dish with id {item.dish_id} not found"
                )
            
            if not dish.is_available:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Dish {dish.name} is not available"
                )
            
            item_total = dish.price * item.quantity
            total_amount += item_total
            
            items_data.append({
                "dishId": dish.id,
                "dishName": dish.name,
                "quantity": item.quantity,
                "price": float(dish.price)
            })
        
        # Create order in database
        order = Order(
            user_id=current_user.id,
            total_amount=total_amount,
            status=OrderStatus.PENDING,
            device_id=order_data.device_id,
            created_at=datetime.utcnow()
        )
        
        db.add(order)
        db.flush()  # Get the order ID
        
        # Create order items
        for item in order_data.items:
            dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
            order_item = OrderItem(
                order_id=order.id,
                dish_id=item.dish_id,
                quantity=item.quantity,
                unit_price=dish.price,
                total_price=dish.price * item.quantity
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        # Send order to ESP32 via MQTT
        device_id = order_data.device_id or "default_device"
        mqtt_client.publish_order_command(device_id, order.id, items_data)
        
        logger.info(f"✅ Order {order.id} created and sent to device {device_id}")
        
        return OrderResponse.from_orm(order)
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )

@router.get("/me", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    return [OrderResponse.from_orm(order) for order in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific order"""
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if user owns the order or is admin
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return OrderResponse.from_orm(order)

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
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
    
    order.status = status
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    logger.info(f"✅ Order {order_id} status updated to {status}")
    
    return {"message": f"Order status updated to {status}"}

# ✅ SECURITY: Add secure orders listing endpoint
@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """✅ Get orders with role-based access control"""
    if current_user.role == "admin":
        # ✅ Admin can see all orders
        orders = db.query(Order).all()
    else:
        # ✅ Users can only see their own orders
        orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    
    return [OrderResponse.from_orm(order) for order in orders]
