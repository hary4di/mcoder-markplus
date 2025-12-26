#!/bin/bash
# Setup Git repository on VPS for automated deployment

set -e  # Exit on error

echo "=========================================="
echo "Setting up Git on VPS for M-Coder"
echo "=========================================="

cd /opt/markplus/

# Backup current directory
if [ -d "mcoder-markplus" ]; then
    BACKUP_DIR="mcoder-markplus.backup-$(date +%Y%m%d_%H%M%S)"
    echo "Backing up current directory to $BACKUP_DIR..."
    mv mcoder-markplus "$BACKUP_DIR"
fi

# Clone repository
echo "Cloning repository from GitHub..."
git clone https://github.com/hary4di/mcoder-markplus.git

cd mcoder-markplus/

# Setup production .env
echo "Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with production values:"
    echo "   nano .env"
    echo ""
    echo "   Required changes:"
    echo "   - SECRET_KEY=<generate new secret key>"
    echo "   - OPENAI_API_KEY=<your production API key>"
    echo "   - FLASK_ENV=production"
    echo ""
fi

# Setup virtual environment
echo "Setting up Python virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create necessary directories
echo "Creating directories..."
mkdir -p files/uploads files/output files/logo files/logs instance

# Create .gitkeep files
touch files/uploads/.gitkeep
touch files/output/.gitkeep
touch files/logo/.gitkeep
touch files/logs/.gitkeep

# Initialize database
echo "Initializing database..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Restart service: supervisorctl restart mcoder-markplus"
echo "3. Check status: supervisorctl status mcoder-markplus"
echo "4. View logs: tail -f /var/log/mcoder/gunicorn.log"
echo ""
echo "After this, you can use quick-deploy.ps1 from Windows for automatic deployment!"
echo ""
