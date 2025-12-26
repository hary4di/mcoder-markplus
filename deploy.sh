#!/bin/bash
# M-Coder Platform - Deployment Script
# Run this script on your VPS to deploy/update the application

set -e  # Exit on error

echo "🚀 M-Coder Platform Deployment Script"
echo "======================================"

# Configuration
APP_DIR="/opt/markplus/mcoder"
VENV_DIR="$APP_DIR/venv"
REPO_URL="YOUR_GITHUB_REPO_URL"  # Optional: jika pakai Git

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root user
if [ "$USER" != "root" ]; then
    log_error "This script must be run as 'root' user"
    log_info "Run: sudo su - or ssh root@your-vps"
    exit 1
fi

# Navigate to app directory
cd $APP_DIR
log_info "Changed directory to: $(pwd)"

# Update code (if using Git)
# log_info "Pulling latest code from Git..."
# git pull origin main

# Activate virtual environment
log_info "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/Update dependencies
log_info "Installing Python dependencies..."
pip install -r requirements.txt --upgrade

# Database migrations (if needed)
log_info "Running database setup..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database tables created/updated')"

# Generate favicon (if logo exists)
if [ -f "generate_favicon.py" ]; then
    log_info "Generating favicon files..."
    python generate_favicon.py || log_warn "Favicon generation skipped"
fi

# Collect static files (if needed)
# log_info "Collecting static files..."
# python collect_static.py

# Restart application
log_info "Restarting application via Supervisor..."
sudo supervisorctl restart mcoder

# Check status
sleep 2
sudo supervisorctl status mcoder

# Reload Nginx
log_info "Reloading Nginx..."
sudo nginx -t && sudo systemctl reload nginx

echo ""
log_info "======================================"
log_info "✅ Deployment completed successfully!"
log_info "======================================"
log_info "Check logs: sudo tail -f /var/log/mcoder/gunicorn.log"
log_info "Check status: sudo supervisorctl status mcoder"
echo ""
