#!/usr/bin/env python3
"""
Fix admin user role in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserRole

def fix_admin_role():
    """Fix admin user role from USER to ADMIN"""
    db = SessionLocal()
    
    try:
        # Find admin user
        admin_user = db.query(User).filter(User.email == "admin@foodyeh.com").first()
        
        if admin_user:
            print(f"Found admin user: {admin_user.email}")
            print(f"Current role: {admin_user.role}")
            
            if admin_user.role == UserRole.USER:
                # Fix the role
                admin_user.role = UserRole.ADMIN
                db.commit()
                print("✅ Fixed admin role from USER to ADMIN!")
                
                # Verify the fix
                db.refresh(admin_user)
                print(f"New role: {admin_user.role}")
                print(f"Role value: {admin_user.role.value}")
                
            else:
                print("✅ Admin role is already correct!")
                
        else:
            print("❌ Admin user not found!")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_admin_role()
