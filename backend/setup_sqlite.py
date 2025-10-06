#!/usr/bin/env python3
"""
Simple SQLite setup script for Foodyeh backend
This bypasses all MySQL authentication issues
"""

import os
import sys
import sqlite3
from pathlib import Path

def setup_sqlite_database():
    """Set up SQLite database and create tables"""
    print("🔧 Setting up SQLite database...")
    
    # Add current directory to Python path
    sys.path.append('.')
    
    try:
        # Import after adding path
        from app.database import engine, Base
        from app.models import User, Dish, Order, OrderItem
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test connection
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if admin user exists
        admin_user = db.query(User).filter(User.email == "admin@foodyeh.io").first()
        if not admin_user:
            print("📝 Creating admin user...")
            from app.auth import get_password_hash
            from app.models import UserRole
            
            admin_user = User(
                email="admin@foodyeh.io",
                password_hash=get_password_hash("Admin123!"),
                first_name="Admin",
                last_name="User",
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created: admin@foodyeh.io / Admin123!")
        
        # Check if dishes exist
        dish_count = db.query(Dish).count()
        if dish_count == 0:
            print("🍽️ Creating sample dishes...")
            from app.models import Dish, Category
            
            sample_dishes = [
                Dish(
                    name="Chicken Burger",
                    description="Juicy chicken burger with fresh vegetables",
                    price=12.99,
                    category=Category.FAST_FOOD,
                    image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
                    is_available=True
                ),
                Dish(
                    name="Margherita Pizza",
                    description="Classic pizza with tomato sauce and mozzarella",
                    price=15.99,
                    category=Category.PIZZA,
                    image_url="https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=400",
                    is_available=True
                ),
                Dish(
                    name="Caesar Salad",
                    description="Fresh romaine lettuce with Caesar dressing",
                    price=8.99,
                    category=Category.SALAD,
                    image_url="https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400",
                    is_available=True
                ),
                Dish(
                    name="Chocolate Cake",
                    description="Rich chocolate cake with cream filling",
                    price=6.99,
                    category=Category.DESSERT,
                    image_url="https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400",
                    is_available=True
                ),
                Dish(
                    name="Coffee",
                    description="Freshly brewed coffee",
                    price=3.99,
                    category=Category.BEVERAGE,
                    image_url="https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400",
                    is_available=True
                )
            ]
            
            for dish in sample_dishes:
                db.add(dish)
            db.commit()
            print(f"✅ Created {len(sample_dishes)} sample dishes!")
        
        db.close()
        print("🎉 SQLite database setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def create_env_file():
    """Create a .env file with SQLite configuration"""
    print("📝 Creating .env file...")
    
    env_content = """# Foodyeh Backend Configuration (SQLite)
# Database
DATABASE_URL=sqlite:///./foodyeh.db

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS512
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis (optional for development)
REDIS_URL=redis://localhost:6379

# MQTT
MQTT_BROKER_URL=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=admin123
MQTT_CLIENT_ID=foodyeh_backend

# Security
CORS_ORIGINS=https://api.foodyeh.io,https://app.foodyeh.io
RATE_LIMIT_AUTH=5
RATE_LIMIT_WINDOW=60
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=600

# File Upload
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created!")

def main():
    """Main setup function"""
    print("🚀 Foodyeh Backend SQLite Setup")
    print("=" * 40)
    
    # Create .env file
    create_env_file()
    
    # Setup database
    if setup_sqlite_database():
        print("\n🎯 Setup completed! You can now run:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\n📋 Login credentials:")
        print("   Email: admin@foodyeh.io")
        print("   Password: Admin123!")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
