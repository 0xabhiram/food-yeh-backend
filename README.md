# Foodyeh Backend & Frontend (Flutter + FastAPI)

A production-ready Flutter app with a FastAPI backend. This repo contains both the mobile frontend and the Python backend, along with optional nginx/systemd configs.

- Frontend: Flutter (Material 3, dark theme)
- Backend: FastAPI (JWT auth, CORS, logging, rate limiting)
- Optional: MQTT integration (can be enabled later)

## Quick Start

### Prerequisites
- Flutter SDK 3.8+
- Python 3.10+
- Git

### 1) Backend (FastAPI)
```bash
cd backend
python -m venv venv
# Windows PowerShell: .\venv\Scripts\Activate.ps1
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp env_example.txt .env  # or create .env manually

# Run dev server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2) Frontend (Flutter)
```bash
cd frontend
flutter pub get
flutter run
```

## Environment Variables (Backend)
Common variables (set in `.env`):
```
ENV=production
SECRET_KEY=change-me
CORS_ORIGINS=*
# DATABASE_URL=postgresql://user:pass@host:5432/dbname (optional)
```

## Production Deployment (Linux)
1) Run backend via systemd on 127.0.0.1:8000
2) Put nginx in front (80/443) → proxy to uvicorn
3) Use Let’s Encrypt for TLS

Example systemd unit:
```ini
[Unit]
Description=Foodyeh FastAPI Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/foodyeh
EnvironmentFile=/opt/foodyeh/.env
ExecStart=/opt/foodyeh/venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Minimal nginx site:
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable HTTPS with certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com --non-interactive --agree-tos -m you@example.com
```

## Repository Structure
```
foodyeh-poc-1/
├─ backend/        # FastAPI app
├─ frontend/       # Flutter app
├─ nginx/          # Nginx configs (optional)
├─ systemd/        # systemd service files (optional)
├─ mosquitto/      # MQTT configs (optional)
└─ logrotate/      # Log rotation (optional)
```

## Links
- GitHub Repo: https://github.com/0xabhiram/food-yeh-backend.git

## License
MIT
