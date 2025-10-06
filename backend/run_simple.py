#!/usr/bin/env python3
"""
Simple run script for Foodyeh backend using SQLite
This bypasses all MySQL authentication issues
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the backend with SQLite"""
    print("🚀 Starting Foodyeh Backend with SQLite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app'):
        print("❌ Error: 'app' directory not found. Please run this from the backend directory.")
        return
    
    # Create .env if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        env_content = """# Foodyeh Backend Configuration (SQLite)
DATABASE_URL=sqlite:///./foodyeh.db
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS512
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379
MQTT_BROKER_URL=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=admin123
MQTT_CLIENT_ID=foodyeh_backend
CORS_ORIGINS=https://api.foodyeh.io,https://app.foodyeh.io
RATE_LIMIT_AUTH=5
RATE_LIMIT_WINDOW=60
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=600
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=5242880
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ .env file created!")
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Check if database exists, if not create it
    if not os.path.exists('foodyeh.db'):
        print("🔧 Creating SQLite database...")
        try:
            # Simple database creation
            import sqlite3
            conn = sqlite3.connect('foodyeh.db')
            conn.close()
            print("✅ SQLite database created!")
        except Exception as e:
            print(f"❌ Error creating database: {e}")
            return
    
    # Install dependencies if needed
    try:
        import fastapi
        import uvicorn
        print("✅ Dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed!")
    
    # Run the server
    print("\n🌐 Starting server...")
    print("📋 Server will be available at: http://0.0.0.0:8000")
    print("📋 API docs at: http://0.0.0.0:8000/docs")
    print("📋 Login credentials: admin@foodyeh.io / Admin123!")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

if __name__ == "__main__":
    main()
