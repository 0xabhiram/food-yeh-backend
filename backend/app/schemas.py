from pydantic import BaseModel, EmailStr, validator, Field
from typing import List, Optional
import re
from datetime import datetime
from app.models import UserRole, OrderStatus, PaymentStatus


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        # ✅ Enhanced password strength validation
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # ✅ Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password.')
        
        return v
    
    @validator('email')
    def validate_email(cls, v):
        # ✅ Enhanced email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower().strip()
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        # ✅ Name validation
        if not v or len(v.strip()) < 2:
            raise ValueError('Name must be at least 2 characters long')
        if len(v) > 50:
            raise ValueError('Name must be less than 50 characters')
        if re.search(r'[<>"\']', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()
    
    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # ✅ Phone number validation
            phone_pattern = r'^\+?[1-9]\d{1,14}$'
            if not re.match(phone_pattern, v.replace(' ', '').replace('-', '')):
                raise ValueError('Invalid phone number format')
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginToken(BaseModel):
    """Schema for /auth/token endpoint (Flutter app compatibility)"""
    username: str  # This will be the email
    password: str


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Dish Schemas
class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = Field(None, max_length=100)
    is_available: bool = True


class DishCreate(DishBase):
    pass


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=100)
    is_available: Optional[bool] = None


class DishResponse(DishBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Order Item Schemas
class OrderItemBase(BaseModel):
    dish_id: int
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    unit_price: float
    total_price: float
    dish: DishResponse
    
    class Config:
        from_attributes = True


# Order Schemas
class OrderCreate(BaseModel):
    items: List[OrderItemBase] = Field(..., min_items=1)
    device_id: Optional[str] = Field(None, max_length=100)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: OrderStatus
    device_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse]
    
    class Config:
        from_attributes = True


# Payment Schemas
class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str = Field(..., max_length=50)


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    status: PaymentStatus
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


# Admin Schemas
class AdminUserResponse(UserResponse):
    pass


class AdminOrderResponse(OrderResponse):
    user: UserResponse


class AdminPaymentResponse(PaymentResponse):
    order: OrderResponse


# MQTT Schemas
class MQTTCommand(BaseModel):
    order_id: int
    items: List[OrderItemBase]
    timestamp: datetime


class MQTTStatus(BaseModel):
    state: str
    timestamp: datetime
    message: Optional[str] = None
