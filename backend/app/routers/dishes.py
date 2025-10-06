from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.database import get_db
from app.models import Dish, User
from app.schemas import DishCreate, DishUpdate, DishResponse
import os
import uuid
from app.config import settings

router = APIRouter(prefix="/dishes", tags=["dishes"])
security = HTTPBearer()

# Auth functions for dishes router
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
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

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.get("/", response_model=List[DishResponse])
def get_dishes(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    available_only: bool = True,
    current_user: User = Depends(get_current_user),  # ✅ ADD AUTHENTICATION
    db: Session = Depends(get_db)
):
    """✅ Get dishes with role-based access control"""
    query = db.query(Dish)
    
    # ✅ SECURITY: Users see only available dishes, admins see all
    if current_user.role != "admin":
        query = query.filter(Dish.is_available == True)
        available_only = True  # Force available_only for non-admins
    
    if available_only:
        query = query.filter(Dish.is_available == True)
    
    if category:
        query = query.filter(Dish.category == category)
    
    dishes = query.offset(skip).limit(limit).all()
    return dishes


@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(
    dish_id: int,
    current_user: User = Depends(get_current_user),  # ✅ ADD AUTHENTICATION
    db: Session = Depends(get_db)
):
    """✅ Get a specific dish with access control"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    # ✅ SECURITY: Non-admins can only see available dishes
    if current_user.role != "admin" and not dish.is_available:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - dish not available"
        )
    
    return dish


@router.post("/", response_model=DishResponse)
def create_dish(
    dish_data: DishCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new dish (admin only)"""
    dish = Dish(**dish_data.dict())
    db.add(dish)
    db.commit()
    db.refresh(dish)
    return dish


@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update a dish (admin only)"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    update_data = dish_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dish, field, value)
    
    db.commit()
    db.refresh(dish)
    return dish


@router.delete("/{dish_id}")
def delete_dish(
    dish_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete a dish (admin only)"""
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    db.delete(dish)
    db.commit()
    return {"message": "Dish deleted successfully"}


@router.post("/{dish_id}/upload-image")
def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Upload image for a dish (admin only)"""
    # ✅ Enhanced file type validation
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # ✅ Enhanced file size validation
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large"
        )
    
    # ✅ Secure file extension validation
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # ✅ Validate filename for path traversal
    if '..' in file.filename or '/' in file.filename or '\\' in file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename"
        )
    
    # Get dish
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dish not found"
        )
    
    # ✅ Secure filename generation
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.upload_dir, filename)
    
    # ✅ Path traversal protection
    if not os.path.abspath(file_path).startswith(os.path.abspath(settings.upload_dir)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    # ✅ Secure file saving with content validation
    try:
        content = file.file.read()
        
        # ✅ Validate file content (basic magic number check)
        if not content.startswith(b'\xff\xd8\xff') and not content.startswith(b'\x89PNG\r\n\x1a\n') and not content.startswith(b'GIF8'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file content"
            )
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
    except Exception as e:
        # ✅ Secure error handling
        logger.error(f"File upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image"
        )
    
    # Update dish with image URL
    dish.image_url = f"/uploads/{filename}"
    db.commit()
    
    return {"message": "Image uploaded successfully", "image_url": dish.image_url}


@router.get("/categories/list")
def get_categories(
    current_user: User = Depends(get_current_user),  # ✅ ADD AUTHENTICATION
    db: Session = Depends(get_db)
):
    """✅ Get all dish categories with authentication"""
    categories = db.query(Dish.category).distinct().all()
    return [category[0] for category in categories if category[0]]
