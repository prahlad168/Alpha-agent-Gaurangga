# 🚀 GAURANGA - Production Deployment Guide

```
===============================================
  GAURANGA PRODUCTION DEPLOYMENT
  Version: 2.0.0
  Last Updated: 2026-07-11
===============================================
```

---

## 📋 Prerequisites

1. Ubuntu/Debian server (or any Linux with systemd)
2. Python 3.8+
3. Git
4. Domain name (optional)
5. Gemini API Key (free from https://aistudio.google.com/)

---

## 🚀 Quick Start (One-Command Deploy)

```bash
# SSH to server, then run:
cd /opt && git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga
bash deploy/production-deploy.sh
```

---

## 📦 Deployment Steps

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-venv git curl lsof

# Create user (optional)
sudo useradd -m -s /bin/bash gauranga
sudo mkdir -p /opt
sudo chown gauranga:gauranga /opt
```

### Step 2: Clone Repository

```bash
# As gauranga user
sudo su - gauranga
cd /opt
git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git
cd Alpha-agent-Gaurangga
```

### Step 3: Configure Environment

```bash
# Edit .env file
nano server/.env

# Add your Gemini API Key:
GEMINI_API_KEY=your-actual-gemini-api-key
```

Get free Gemini API key: https://aistudio.google.com/

### Step 4: Install Dependencies

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 5: Deploy Server

```bash
# Quick deploy
bash deploy/production-deploy.sh

# Or manually:
bash deploy/start.sh
```

---

## 🔧 Server Management

### Start Server
```bash
bash deploy/start.sh
```

### Stop Server
```bash
bash deploy/stop.sh
```

### Restart Server
```bash
bash deploy/restart.sh
```

### Check Status
```bash
bash deploy/status.sh
```

### View Logs
```bash
tail -f logs/gauranga.log
```

---

## ⚙️ Auto-Start Setup

### Option 1: Systemd Service (Recommended)

```bash
# Copy service file
sudo cp deploy/gauranga.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable gauranga

# Start service
sudo systemctl start gauranga

# Check status
sudo systemctl status gauranga
```

### Option 2: Cron Job

```bash
# Edit crontab
crontab -e

# Add these lines:
@reboot bash /opt/Alpha-agent-Gaurangga/deploy/rc.local-start.sh
*/5 * * * * bash /opt/Alpha-agent-Gaurangga/deploy/health-monitor.sh
```

### Option 3: rc.local

```bash
# Edit rc.local
sudo nano /etc/rc.local

# Add before "exit 0":
bash /opt/Alpha-agent-Gaurangga/deploy/rc.local-start.sh
```

---

## 🌐 Production Web Server (Nginx + Gunicorn)

For production with Nginx:

```bash
# Install Nginx
sudo apt install -y nginx

# Install Gunicorn
pip install gunicorn

# Create Nginx config
sudo nano /etc/nginx/sites-available/gauranga
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /opt/Alpha-agent-Gaurangga/static/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/gauranga /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 SSL/HTTPS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:5000/api/health
```

### Status Endpoint
```bash
curl http://localhost:5000/api/status
```

### Health Monitor Script
```bash
# Run manually
bash deploy/health-monitor.sh

# Or add to cron for auto-restart
*/5 * * * * bash /opt/Alpha-agent-Gaurangga/deploy/health-monitor.sh
```

---

## 🔧 Troubleshooting

### Server won't start?
```bash
# Check logs
tail -f logs/gauranga.log

# Check port
lsof -i :5000

# Check Python
python3 --version
```

### API not working?
```bash
# Verify .env file
cat server/.env | grep API_KEY

# Test Gemini
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
```

### Memory issues?
```bash
# Check memory
free -h

# Monitor process
top -p $(cat deploy/gauranga.pid)
```

---

## 📁 File Structure

```
Alpha-agent-Gaurangga/
├── server/
│   ├── gauranga_server.py    # Main server
│   ├── requirements.txt       # Python deps
│   ├── .env                   # Environment
│   └── venv/                 # Virtual env
├── deploy/
│   ├── start.sh              # Start script
│   ├── stop.sh               # Stop script
│   ├── restart.sh            # Restart script
│   ├── status.sh             # Status script
│   ├── production-deploy.sh  # Production deploy
│   ├── health-monitor.sh     # Health monitor
│   ├── rc.local-start.sh     # Boot startup
│   ├── install-service.sh    # Service installer
│   └── gauranga.service      # systemd unit
├── js/
│   └── *-agent.js           # 10 MVP agents
├── agents/
│   └── *-agent.md           # Agent docs
├── logs/
│   └── gauranga.log         # Server logs
└── index.html               # Web interface
```

---

## 🌐 Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/status` | GET | Server status |
| `/api/chat` | POST | Chat with AI |

---

## 📞 Support

- GitHub: https://github.com/prahlad168/Alpha-agent-Gaurangga
- Owner: i Made Purna Ananda (Pak Pur)
- WhatsApp: 081337558787

---

```
===============================================
  "Dari nol menjadi satu, dari satu menjadi banyak."
                                      - Pak Pur
===============================================
```
