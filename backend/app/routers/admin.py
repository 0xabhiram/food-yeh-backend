from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Order, Payment, UserRole
from app.schemas import AdminUserResponse, AdminOrderResponse, AdminPaymentResponse
from app.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[AdminUserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role_filter: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if role_filter:
        if role_filter not in [role.value for role in UserRole]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role filter"
            )
        query = query.filter(User.role == role_filter)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get a specific user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Toggle user active status (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'}"}


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    if role not in [r.value for r in UserRole]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user.role = role
    db.commit()
    
    return {"message": f"User role updated to {role}"}


@router.get("/orders", response_model=List[AdminOrderResponse])
def get_all_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    user_id: int = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all orders with user details (admin only)"""
    query = db.query(Order)
    
    if status_filter:
        from app.models import OrderStatus
        if status_filter not in [s.value for s in OrderStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )
        query = query.filter(Order.status == status_filter)
    
    if user_id:
        query = query.filter(Order.user_id == user_id)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@router.get("/payments", response_model=List[AdminPaymentResponse])
def get_all_payments(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get all payments with order details (admin only)"""
    query = db.query(Payment)
    
    if status_filter:
        from app.models import PaymentStatus
        if status_filter not in [s.value for s in PaymentStatus]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status filter"
            )
        query = query.filter(Payment.status == status_filter)
    
    payments = query.offset(skip).limit(limit).all()
    return payments


@router.get("/dashboard/stats")
def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (admin only)"""
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Total counts
    total_users = db.query(func.count(User.id)).scalar()
    total_orders = db.query(func.count(Order.id)).scalar()
    total_payments = db.query(func.count(Payment.id)).scalar()
    
    # Revenue stats
    total_revenue = db.query(func.sum(Payment.amount)).filter(Payment.status == "paid").scalar() or 0
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = db.query(func.count(Order.id)).filter(Order.created_at >= week_ago).scalar()
    recent_revenue = db.query(func.sum(Payment.amount)).filter(
        Payment.status == "paid",
        Payment.created_at >= week_ago
    ).scalar() or 0
    
    # Order status breakdown
    order_statuses = db.query(
        Order.status,
        func.count(Order.id)
    ).group_by(Order.status).all()
    
    status_breakdown = {status: count for status, count in order_statuses}
    
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "total_payments": total_payments,
        "total_revenue": float(total_revenue),
        "recent_orders": recent_orders,
        "recent_revenue": float(recent_revenue),
        "order_status_breakdown": status_breakdown
    }
