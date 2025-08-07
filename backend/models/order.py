"""
Pydantic models for order data validation and database models.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderType(str, Enum):
    """Order type enumeration."""
    VEND = "vend"
    RESTOCK = "restock"
    MAINTENANCE = "maintenance"


# Pydantic Models for API
class OrderCreate(BaseModel):
    """Model for creating a new order."""
    item_id: str = Field(..., description="Item identifier", min_length=1, max_length=50)
    slot_id: int = Field(..., description="Slot number", ge=1, le=100)
    quantity: int = Field(1, description="Quantity to vend", ge=1, le=10)
    order_type: OrderType = Field(OrderType.VEND, description="Type of order")
    
    @validator('item_id')
    def validate_item_id(cls, v):
        if not v.strip():
            raise ValueError("Item ID cannot be empty")
        return v.strip()


class OrderResponse(BaseModel):
    """Model for order response."""
    order_id: str
    item_id: str
    slot_id: int
    quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Model for updating order status."""
    order_id: str = Field(..., description="Order identifier")
    status: OrderStatus = Field(..., description="New status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")


class OrderListResponse(BaseModel):
    """Model for list of orders response."""
    orders: List[OrderResponse]
    total: int
    page: int
    per_page: int


# Database Models
class Order(Base):
    """Database model for orders."""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, index=True, nullable=False)
    item_id = Column(String(50), nullable=False)
    slot_id = Column(Integer, nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    status = Column(String(20), default=OrderStatus.PENDING, nullable=False)
    order_type = Column(String(20), default=OrderType.VEND, nullable=False)
    user_id = Column(String(50), nullable=True)  # JWT subject
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    error_message = Column(Text, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Order(order_id='{self.order_id}', status='{self.status}')>"


class OrderLog(Base):
    """Database model for order logs."""
    __tablename__ = "order_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    status_before = Column(String(20), nullable=True)
    status_after = Column(String(20), nullable=True)
    user_id = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<OrderLog(order_id='{self.order_id}', action='{self.action}')>"


# Utility Models
class HealthCheck(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: datetime
    version: str
    mqtt_status: str
    database_status: str
    uptime: float


class AdminLogEntry(BaseModel):
    """Model for admin log entries."""
    id: int
    order_id: str
    action: str
    user_id: Optional[str]
    ip_address: Optional[str]
    details: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AdminLogsResponse(BaseModel):
    """Model for admin logs response."""
    logs: List[AdminLogEntry]
    total: int
    page: int
    per_page: int 