#!/bin/bash
# ================================================
# GAURANGA - Auto-Start Service Installation
# ================================================
# This script installs GAURANGA as a systemd service
# so it auto-starts on boot
# ================================================

set -e

APP_DIR="/workspace/project/Alpha-agent-Gaurangga"
SERVICE_FILE="$APP_DIR/deploy/gauranga.service"
SYSTEMD_DIR="/etc/systemd/system"

echo "=============================================="
echo "  🚀 GAURANGA Auto-Start Installation"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root (use sudo)"
    exit 1
fi

echo "[1/5] Checking files..."
if [ ! -f "$SERVICE_FILE" ]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi
echo "✅ Service file found"

echo ""
echo "[2/5] Creating log directories..."
mkdir -p $APP_DIR/logs
touch $APP_DIR/logs/gauranga.log
touch $APP_DIR/logs/gauranga_error.log
chmod 666 $APP_DIR/logs/*.log
echo "✅ Log directories created"

echo ""
echo "[3/5] Copying service file..."
cp $SERVICE_FILE $SYSTEMD_DIR/gauranga.service
echo "✅ Service file installed"

echo ""
echo "[4/5] Reloading systemd..."
systemctl daemon-reload
echo "✅ Systemd reloaded"

echo ""
echo "[5/5] Enabling service..."
systemctl enable gauranga.service
echo "✅ Service enabled"

echo ""
echo "=============================================="
echo "  ✅ INSTALLATION COMPLETE!"
echo "=============================================="
echo ""
echo "📋 Commands:"
echo "   Start:    sudo systemctl start gauranga"
echo "   Stop:     sudo systemctl stop gauranga"
echo "   Restart:  sudo systemctl restart gauranga"
echo "   Status:   sudo systemctl status gauranga"
echo "   Logs:     sudo journalctl -u gauranga -f"
echo ""
echo "🔄 Reboot to test auto-start!"
echo ""
