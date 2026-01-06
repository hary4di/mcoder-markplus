#!/bin/bash
# Update PostgreSQL Password to MarkPlus25

set -e

echo "============================================================"
echo "UPDATING POSTGRESQL PASSWORD"
echo "============================================================"
echo ""

NEW_PASSWORD="MarkPlus25"

echo "[STEP 1/4] Updating PostgreSQL user password..."
sudo -u postgres psql -c "ALTER USER mcoder_app WITH PASSWORD '$NEW_PASSWORD';"
echo "✅ Password updated in PostgreSQL"

echo ""
echo "[STEP 2/4] Updating .env.postgres file..."
cd /opt/markplus/mcoder-markplus
cat > .env.postgres << EOF
# PostgreSQL Configuration for M-Code Pro
# Generated: $(date)
DATABASE_URL=postgresql://mcoder_app:$NEW_PASSWORD@localhost:5432/mcoder_production
EOF
echo "✅ .env.postgres updated"

echo ""
echo "[STEP 3/4] Updating main .env file..."
# Backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Remove old PostgreSQL lines
sed -i '/# PostgreSQL Database/d' .env
sed -i '/DATABASE_URL=postgresql/d' .env
sed -i 's/^DATABASE_URL=sqlite/# DATABASE_URL=sqlite/' .env

# Add new PostgreSQL config
echo "" >> .env
echo "# PostgreSQL Database (Production)" >> .env
echo "DATABASE_URL=postgresql://mcoder_app:$NEW_PASSWORD@localhost:5432/mcoder_production" >> .env

echo "✅ .env updated"

echo ""
echo "[STEP 4/4] Restarting application..."
supervisorctl restart mcoder-markplus
sleep 3
supervisorctl status mcoder-markplus

echo ""
echo "============================================================"
echo "PASSWORD UPDATE COMPLETE!"
echo "============================================================"
echo ""
echo "📋 New Credentials:"
echo "   Database: mcoder_production"
echo "   User: mcoder_app"
echo "   Password: $NEW_PASSWORD"
echo "   Host: localhost"
echo "   Port: 5432"
echo ""
echo "🔐 Saved in: /opt/markplus/mcoder-markplus/.env.postgres"
echo ""
