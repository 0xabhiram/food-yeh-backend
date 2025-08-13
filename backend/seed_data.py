#!/usr/bin/env python3
"""
Seed data script for Foodyeh POC
Creates sample dishes and admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, User, Dish, UserRole
from app.auth import get_password_hash
from app.config import settings

# Sample dishes data
SAMPLE_DISHES = [
    {
        "name": "Margherita Pizza",
        "description": "Classic tomato sauce with mozzarella cheese and fresh basil",
        "price": 12.99,
        "category": "Pizza",
        "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=400"
    },
    {
        "name": "Pepperoni Pizza",
        "description": "Spicy pepperoni with melted cheese on crispy crust",
        "price": 14.99,
        "category": "Pizza",
        "image_url": "https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400"
    },
    {
        "name": "BBQ Chicken Pizza",
        "description": "BBQ sauce, grilled chicken, red onions, and cilantro",
        "price": 16.99,
        "category": "Pizza",
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400"
    },
    {
        "name": "Classic Burger",
        "description": "Beef patty with lettuce, tomato, cheese, and special sauce",
        "price": 11.99,
        "category": "Burgers",
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400"
    },
    {
        "name": "Chicken Burger",
        "description": "Grilled chicken breast with avocado and chipotle mayo",
        "price": 10.99,
        "category": "Burgers",
        "image_url": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=400"
    },
    {
        "name": "Veggie Burger",
        "description": "Plant-based patty with fresh vegetables and vegan cheese",
        "price": 12.99,
        "category": "Burgers",
        "image_url": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=400"
    },
    {
        "name": "Caesar Salad",
        "description": "Fresh romaine lettuce with parmesan cheese and croutons",
        "price": 8.99,
        "category": "Salads",
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400"
    },
    {
        "name": "Greek Salad",
        "description": "Mixed greens with feta cheese, olives, and Mediterranean dressing",
        "price": 9.99,
        "category": "Salads",
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400"
    },
    {
        "name": "Chicken Wings",
        "description": "Crispy wings with choice of buffalo, BBQ, or honey mustard sauce",
        "price": 13.99,
        "category": "Appetizers",
        "image_url": "https://images.unsplash.com/photo-1567620832904-9d64b45c9e3a?w=400"
    },
    {
        "name": "Mozzarella Sticks",
        "description": "Breaded mozzarella sticks served with marinara sauce",
        "price": 7.99,
        "category": "Appetizers",
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400"
    },
    {
        "name": "Chocolate Brownie",
        "description": "Warm chocolate brownie with vanilla ice cream",
        "price": 6.99,
        "category": "Desserts",
        "image_url": "https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400"
    },
    {
        "name": "Cheesecake",
        "description": "New York style cheesecake with berry compote",
        "price": 7.99,
        "category": "Desserts",
        "image_url": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400"
    },
    {
        "name": "Soft Drink",
        "description": "Choice of Coke, Sprite, or Fanta",
        "price": 2.99,
        "category": "Beverages",
        "image_url": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=400"
    },
    {
        "name": "Fresh Juice",
        "description": "Orange, apple, or mixed fruit juice",
        "price": 4.99,
        "category": "Beverages",
        "image_url": "https://images.unsplash.com/photo-1622597489932-893c5f2a4b5b?w=400"
    }
]


def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created")


def create_admin_user():
    """Create admin user"""
    db = SessionLocal()
    
    # Check if admin already exists
    admin_user = db.query(User).filter(User.email == "admin@foodyeh.com").first()
    if admin_user:
        print("Admin user already exists")
        db.close()
        return
    
    # Create admin user
    admin_user = User(
        email="admin@foodyeh.com",
        password_hash=get_password_hash("Admin123!"),
        first_name="Admin",
        last_name="User",
        phone="+1234567890",
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(admin_user)
    db.commit()
    print("Admin user created: admin@foodyeh.com / Admin123!")
    db.close()


def create_sample_dishes():
    """Create sample dishes"""
    db = SessionLocal()
    
    # Check if dishes already exist
    existing_dishes = db.query(Dish).count()
    if existing_dishes > 0:
        print(f"Found {existing_dishes} existing dishes, skipping seed data")
        db.close()
        return
    
    # Create dishes
    for dish_data in SAMPLE_DISHES:
        dish = Dish(**dish_data)
        db.add(dish)
    
    db.commit()
    print(f"Created {len(SAMPLE_DISHES)} sample dishes")
    db.close()


def main():
    """Main function to run all seeding operations"""
    print("Starting Foodyeh database seeding...")
    
    try:
        create_tables()
        create_admin_user()
        create_sample_dishes()
        print("Database seeding completed successfully!")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
