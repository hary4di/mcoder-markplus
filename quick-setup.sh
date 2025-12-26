#!/bin/bash
# M-Coder Platform - Quick Setup Script for VPS
# Run this on your VPS: bash quick-setup.sh

set -e
echo "🚀 M-Coder Platform - VPS Setup"
echo "================================"

# 1. Create directories
echo "📁 Creating directory structure..."
mkdir -p /opt/markplus/mcoder
mkdir -p /var/log/mcoder
chown -R root:root /opt/markplus/mcoder
chown -R root:root /var/log/mcoder

# 2. Install system dependencies
echo "📦 Installing system dependencies..."
apt update
apt install -y python3.12-venv python3-pip supervisor libjpeg-dev zlib1g-dev

# 3. Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
cd /opt/markplus/mcoder
python3.12 -m venv venv
source venv/bin/activate

# 4. Install Gunicorn
echo "⚙️ Installing Gunicorn..."
pip install --upgrade pip
pip install gunicorn

echo ""
echo "✅ Setup completed!"
echo "================================"
echo "Next steps:"
echo "1. Upload your code to: /opt/markplus/mcoder"
echo "2. cd /opt/markplus/mcoder"
echo "3. source venv/bin/activate"
echo "4. pip install -r requirements.txt"
echo ""
