#!/bin/bash
# ML-EAOS v11.0 - Deployment Script
# Phase 12: Go Live

set -e

echo "═══════════════════════════════════════════════════════════════════════"
echo "  ML-EAOS v11.0 - Production Deployment"
echo "═══════════════════════════════════════════════════════════════════════"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/opt/ml-eaos"
LOG_FILE="/var/log/ml-eaos/deploy.log"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment checks
log "Running pre-deployment checks..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    warn "Not running as root. Some features may not work."
fi

# Create log directory
sudo mkdir -p /var/log/ml-eaos

# Go-Live Checklist
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log "                    GO-LIVE CHECKLIST"
log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

checklist=(
    "Domain & SSL Certificate"
    "Database Connectivity"
    "Object Storage"
    "Email Service"
    "Monitoring & Alerting"
    "Log Aggregation"
    "Scheduled Jobs"
    "Payment Gateway"
    "Marketplace API Keys"
    "Backup Verification"
    "Security Scan"
    "Load Testing"
    "Uptime Monitoring"
    "Error Tracking"
    "CDN Configuration"
    "Firewall Rules"
    "Emergency Contacts"
    "Runbook Available"
    "Rollback Plan"
    "Communication Plan"
)

i=1
for item in "${checklist[@]}"; do
    log "[ ] $i. $item"
    ((i++))
done

log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

read -p "Have you verified all checklist items? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    error "Deployment cancelled. Please verify all checklist items first."
fi

# Deployment steps
log "Starting deployment..."

# Step 1: Create deployment directory
log "Step 1/8: Creating deployment directory..."
sudo mkdir -p "$DEPLOY_DIR"
sudo chown -R $(whoami):$(whoami) "$DEPLOY_DIR"

# Step 2: Clone/pull latest code
log "Step 2/8: Syncing code..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd "$DEPLOY_DIR"
    git pull origin main
else
    git clone https://github.com/prahlad168/Alpha-agent-Gaurangga.git "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
fi

# Step 3: Install dependencies
log "Step 3/8: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Step 4: Configure environment
log "Step 4/8: Configuring environment..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        warn "Please edit .env with your configuration!"
    fi
fi

# Step 5: Run database migrations
log "Step 5/8: Running database migrations..."
if [ -d "database/migrations" ]; then
    python manage.py migrate || warn "Migration may have issues"
fi

# Step 6: Collect static files
log "Step 6/8: Collecting static files..."
if [ -f "manage.py" ]; then
    python manage.py collectstatic --noinput || warn "Static files may not be complete"
fi

# Step 7: Restart services
log "Step 7/8: Restarting services..."
sudo systemctl restart ml-eaos || warn "Service not found. Run install-service.sh first."

# Step 8: Verify deployment
log "Step 8/8: Verifying deployment..."
sleep 5

# Health check
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    log "✅ Health check passed!"
else
    warn "Health check failed. Please check logs."
fi

log "═══════════════════════════════════════════════════════════════════════"
log "  ✅ DEPLOYMENT COMPLETE!"
log "═══════════════════════════════════════════════════════════════════════"
log ""
log "Next steps:"
log "1. Check logs: tail -f /var/log/ml-eaos/deploy.log"
log "2. Check service: systemctl status ml-eaos"
log "3. Verify dashboard: curl http://localhost:8000"
log ""
log "CEO Payout Engine ready at: ML-EAOS/ceo_payout_engine.py"
log "Production Readiness at: ML-EAOS/production_readiness.py"
