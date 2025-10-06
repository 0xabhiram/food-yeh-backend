#!/usr/bin/env python3
"""
Simple script to check Foodyeh database
"""

import sqlite3
import sys
import os

def check_database():
    """Check the SQLite database"""
    db_path = "foodyeh.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"🔍 Checking database: {db_path}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            print(f"  - {table_name}")
        
        print("\n" + "=" * 50)
        
        # Check each table
        for table in tables:
            table_name = table[0]
            print(f"\n📊 Table: {table_name}")
            print("-" * 30)
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            print("Columns:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"Records: {count}")
            
            # Show sample data (first 3 rows)
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
                rows = cursor.fetchall()
                print("Sample data:")
                for i, row in enumerate(rows, 1):
                    print(f"  Row {i}: {row}")
            
            if count > 3:
                print(f"  ... and {count - 3} more rows")
        
        conn.close()
        print(f"\n✅ Database check completed!")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    check_database()
