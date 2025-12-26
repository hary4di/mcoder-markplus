#!/bin/bash
# Restructure M-Coder for Multi-Tenant Architecture
# Run this on VPS: bash restructure_for_multitenant.sh

set -e  # Exit on error

echo "=========================================="
echo "  M-Coder Multi-Tenant Restructuring"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Stop services
echo -e "${YELLOW}[1/7] Stopping services...${NC}"
supervisorctl stop mcoder 2>/dev/null || echo "Service not running"
sleep 2

# Step 2: Rename directory
echo -e "${YELLOW}[2/7] Renaming directory...${NC}"
cd /opt/markplus
if [ -d "mcoder" ]; then
    if [ -d "mcoder-markplus" ]; then
        echo -e "${RED}Error: mcoder-markplus already exists!${NC}"
        exit 1
    fi
    mv mcoder mcoder-markplus
    echo -e "${GREEN}✓ Renamed: mcoder → mcoder-markplus${NC}"
else
    echo -e "${RED}Error: /opt/markplus/mcoder not found!${NC}"
    exit 1
fi

# Step 3: Update configuration files
echo -e "${YELLOW}[3/7] Updating configuration files...${NC}"
cd /opt/markplus/mcoder-markplus

# Update paths in all config files
for file in supervisor.conf nginx.conf gunicorn.conf.py deploy.sh; do
    if [ -f "$file" ]; then
        sed -i 's|/opt/markplus/mcoder|/opt/markplus/mcoder-markplus|g' "$file"
        echo -e "${GREEN}✓ Updated: $file${NC}"
    fi
done

# Update .env if exists
if [ -f ".env" ]; then
    # Add instance identifier
    if ! grep -q "INSTANCE_NAME" .env; then
        echo "" >> .env
        echo "# Instance Identifier" >> .env
        echo "INSTANCE_NAME=markplus" >> .env
        echo -e "${GREEN}✓ Added INSTANCE_NAME to .env${NC}"
    fi
fi

# Step 4: Update Supervisor configuration
echo -e "${YELLOW}[4/7] Updating Supervisor configuration...${NC}"
if [ -f "/etc/supervisor/conf.d/mcoder.conf" ]; then
    mv /etc/supervisor/conf.d/mcoder.conf /etc/supervisor/conf.d/mcoder-markplus.conf
    echo -e "${GREEN}✓ Renamed supervisor config${NC}"
fi

# Copy updated config
cp supervisor.conf /etc/supervisor/conf.d/mcoder-markplus.conf

# Update program name in supervisor config
sed -i 's/\[program:mcoder\]/[program:mcoder-markplus]/' /etc/supervisor/conf.d/mcoder-markplus.conf

supervisorctl reread
supervisorctl update
echo -e "${GREEN}✓ Supervisor updated${NC}"

# Step 5: Update Nginx configuration
echo -e "${YELLOW}[5/7] Updating Nginx configuration...${NC}"

# Remove old symlink if exists
rm -f /etc/nginx/sites-enabled/mcoder

# Copy new config
cp nginx.conf /etc/nginx/sites-available/mcoder-markplus

# Create new symlink
ln -sf /etc/nginx/sites-available/mcoder-markplus /etc/nginx/sites-enabled/mcoder-markplus

# Test nginx config
nginx -t
if [ $? -eq 0 ]; then
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx updated${NC}"
else
    echo -e "${RED}✗ Nginx configuration error!${NC}"
    exit 1
fi

# Step 6: Create shared resources directory
echo -e "${YELLOW}[6/7] Creating shared resources directory...${NC}"
cd /opt/markplus

mkdir -p mcoder-shared/scripts
mkdir -p mcoder-shared/templates
mkdir -p mcoder-shared/backups

echo -e "${GREEN}✓ Created: /opt/markplus/mcoder-shared/${NC}"

# Create deploy_new_company.sh script
cat > mcoder-shared/scripts/deploy_new_company.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
# Deploy New Company Instance
# Usage: ./deploy_new_company.sh <company_name> <port> <domain>
# Example: ./deploy_new_company.sh company2 8001 mcoder.company2.com

set -e

COMPANY_NAME=$1
PORT=$2
DOMAIN=$3

if [ -z "$COMPANY_NAME" ] || [ -z "$PORT" ] || [ -z "$DOMAIN" ]; then
    echo "Usage: ./deploy_new_company.sh <company_name> <port> <domain>"
    echo "Example: ./deploy_new_company.sh company2 8001 mcoder.company2.com"
    exit 1
fi

INSTANCE_DIR="/opt/markplus/mcoder-$COMPANY_NAME"

echo "=========================================="
echo "  Deploy New Company: $COMPANY_NAME"
echo "=========================================="
echo "Port: $PORT"
echo "Domain: $DOMAIN"
echo ""

# 1. Copy from MarkPlus instance
echo "[1/8] Copying files from MarkPlus instance..."
cp -r /opt/markplus/mcoder-markplus $INSTANCE_DIR
echo "✓ Files copied"

# 2. Clean sensitive data
echo "[2/8] Cleaning sensitive data..."
cd $INSTANCE_DIR
rm -rf instance/*.db
rm -rf files/uploads/*
rm -rf files/output/*
rm -rf files/logo/*
rm -rf venv
rm -rf __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "✓ Data cleaned"

# 3. Update port in configs
echo "[3/8] Updating configuration files..."
sed -i "s/8000/$PORT/g" gunicorn.conf.py
sed -i "s/mcoder-markplus/mcoder-$COMPANY_NAME/g" supervisor.conf
sed -i "s/mcoder-markplus/mcoder-$COMPANY_NAME/g" gunicorn.conf.py
sed -i "s/mcoder-markplus/mcoder-$COMPANY_NAME/g" nginx.conf
sed -i "s/mcoder-markplus/mcoder-$COMPANY_NAME/g" deploy.sh

# Update domain in nginx config (if exists)
if grep -q "server_name" nginx.conf; then
    sed -i "s/server_name .*/server_name $DOMAIN;/" nginx.conf
fi

# Update .env
if [ -f ".env" ]; then
    sed -i "s/INSTANCE_NAME=markplus/INSTANCE_NAME=$COMPANY_NAME/" .env
    # Clear API keys (admin will set via dashboard)
    sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=/" .env
    sed -i "s/BREVO_API_KEY=.*/BREVO_API_KEY=/" .env
fi
echo "✓ Configs updated"

# 4. Create virtual environment
echo "[4/8] Creating virtual environment..."
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install gunicorn -q
echo "✓ Virtual environment ready"

# 5. Initialize database
echo "[5/8] Initializing database..."
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized')"
echo "✓ Database initialized"
echo ""
echo "⚠️  IMPORTANT: Run 'python setup_admin.py' to create admin user"
echo ""

# 6. Configure Supervisor
echo "[6/8] Configuring Supervisor..."
cp supervisor.conf /etc/supervisor/conf.d/mcoder-$COMPANY_NAME.conf
supervisorctl reread
supervisorctl update
echo "✓ Supervisor configured"

# 7. Configure Nginx
echo "[7/8] Configuring Nginx..."
cp nginx.conf /etc/nginx/sites-available/mcoder-$COMPANY_NAME
ln -sf /etc/nginx/sites-available/mcoder-$COMPANY_NAME /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
echo "✓ Nginx configured"

# 8. Start service
echo "[8/8] Starting service..."
supervisorctl start mcoder-$COMPANY_NAME
sleep 2
supervisorctl status mcoder-$COMPANY_NAME
echo "✓ Service started"

echo ""
echo "=========================================="
echo "  ✅ Deployment Complete!"
echo "=========================================="
echo "Instance: mcoder-$COMPANY_NAME"
echo "Directory: $INSTANCE_DIR"
echo "Port: $PORT (internal)"
echo "Domain: $DOMAIN"
echo ""
echo "Next Steps:"
echo "1. Point DNS A record: $DOMAIN → VPS IP"
echo "2. Wait for DNS propagation (10-30 minutes)"
echo "3. Install SSL: certbot --nginx -d $DOMAIN"
echo "4. Create admin user:"
echo "   cd $INSTANCE_DIR"
echo "   source venv/bin/activate"
echo "   python setup_admin.py"
echo "5. Access: https://$DOMAIN"
echo ""
DEPLOY_SCRIPT

chmod +x mcoder-shared/scripts/deploy_new_company.sh
echo -e "${GREEN}✓ Created: deploy_new_company.sh${NC}"

# Create backup script
cat > mcoder-shared/scripts/backup_instance.sh << 'BACKUP_SCRIPT'
#!/bin/bash
# Backup M-Coder Instance
# Usage: ./backup_instance.sh <instance_name>
# Example: ./backup_instance.sh mcoder-markplus

INSTANCE=$1
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/markplus/mcoder-shared/backups"

if [ -z "$INSTANCE" ]; then
    echo "Usage: ./backup_instance.sh <instance_name>"
    echo "Example: ./backup_instance.sh mcoder-markplus"
    exit 1
fi

if [ ! -d "/opt/markplus/$INSTANCE" ]; then
    echo "Error: Instance $INSTANCE not found!"
    exit 1
fi

mkdir -p $BACKUP_DIR/$INSTANCE

echo "Backing up: $INSTANCE"

# Backup database
if [ -f "/opt/markplus/$INSTANCE/instance/users.db" ]; then
    cp /opt/markplus/$INSTANCE/instance/users.db \
       $BACKUP_DIR/$INSTANCE/users_$DATE.db
    echo "✓ Database backed up"
fi

# Backup files
tar -czf $BACKUP_DIR/$INSTANCE/files_$DATE.tar.gz \
   /opt/markplus/$INSTANCE/files/ 2>/dev/null || true
echo "✓ Files backed up"

# Backup .env
if [ -f "/opt/markplus/$INSTANCE/.env" ]; then
    cp /opt/markplus/$INSTANCE/.env \
       $BACKUP_DIR/$INSTANCE/env_$DATE
    echo "✓ Configuration backed up"
fi

# Keep only last 7 days
find $BACKUP_DIR/$INSTANCE -mtime +7 -delete 2>/dev/null || true

echo "✅ Backup completed: $INSTANCE at $DATE"
echo "Location: $BACKUP_DIR/$INSTANCE/"
BACKUP_SCRIPT

chmod +x mcoder-shared/scripts/backup_instance.sh
echo -e "${GREEN}✓ Created: backup_instance.sh${NC}"

# Copy template files
echo -e "${YELLOW}Copying template files...${NC}"
cp /opt/markplus/mcoder-markplus/.env.production mcoder-shared/templates/.env.template 2>/dev/null || true
cp /opt/markplus/mcoder-markplus/nginx.conf mcoder-shared/templates/nginx.conf.template
cp /opt/markplus/mcoder-markplus/supervisor.conf mcoder-shared/templates/supervisor.conf.template
echo -e "${GREEN}✓ Templates copied${NC}"

# Step 7: Start services
echo -e "${YELLOW}[7/7] Starting services...${NC}"
supervisorctl start mcoder-markplus
sleep 3

# Check status
STATUS=$(supervisorctl status mcoder-markplus | awk '{print $2}')
if [ "$STATUS" == "RUNNING" ]; then
    echo -e "${GREEN}✓ Service running${NC}"
else
    echo -e "${RED}✗ Service not running. Check logs.${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  ✅ Restructuring Complete!${NC}"
echo "=========================================="
echo ""
echo "New Structure:"
echo "/opt/markplus/"
echo "├── mcoder-markplus/      ← Renamed (MarkPlus instance)"
echo "└── mcoder-shared/        ← Shared resources"
echo "    ├── scripts/"
echo "    │   ├── deploy_new_company.sh"
echo "    │   └── backup_instance.sh"
echo "    ├── templates/"
echo "    └── backups/"
echo ""
echo "Verification:"
echo "  Directory: $(ls -d /opt/markplus/mcoder-markplus 2>/dev/null && echo 'OK' || echo 'NOT FOUND')"
echo "  Supervisor: $(supervisorctl status mcoder-markplus | awk '{print $2}')"
echo "  Nginx: $(systemctl is-active nginx)"
echo ""
echo "Test Application:"
echo "  curl http://localhost:8000"
echo ""
echo "Next Steps:"
echo "1. ✅ Structure now multi-tenant ready"
echo "2. Configure domain and SSL"
echo "3. Test application access"
echo "4. When ready to add new company:"
echo "   /opt/markplus/mcoder-shared/scripts/deploy_new_company.sh company2 8001 domain.com"
echo ""
