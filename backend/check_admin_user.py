#!/usr/bin/env python3
"""
Check admin user in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserRole

def check_admin_user():
    """Check if admin user exists and has correct role"""
    db = SessionLocal()
    
    try:
        # Check admin user
        admin_user = db.query(User).filter(User.email == "admin@foodyeh.com").first()
        
        if admin_user:
            print("✅ Admin user found!")
            print(f"Email: {admin_user.email}")
            print(f"Role: {admin_user.role}")
            print(f"Role value: {admin_user.role.value}")
            print(f"Is active: {admin_user.is_active}")
            print(f"Created at: {admin_user.created_at}")
            
            # Check if role is admin
            if admin_user.role == UserRole.ADMIN:
                print("✅ Role is correctly set to ADMIN")
            else:
                print("❌ Role is NOT set to ADMIN!")
                print(f"Expected: {UserRole.ADMIN}, Got: {admin_user.role}")
                
        else:
            print("❌ Admin user NOT found!")
            print("Available users:")
            users = db.query(User).all()
            for user in users:
                print(f"- {user.email} (Role: {user.role})")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_user()
