#!/bin/bash
# Complete PostgreSQL Migration for M-Code Pro
# This script runs all steps automatically

set -e  # Exit on error

echo "============================================================"
echo "M-CODE PRO - POSTGRESQL MIGRATION"
echo "============================================================"
echo ""

# Step 1: Setup PostgreSQL Database
echo "[STEP 1/7] Creating PostgreSQL database and user..."
cd /opt/markplus/mcoder-markplus
python3 setup_postgres.py

echo ""
echo "[STEP 2/7] Installing psycopg2-binary..."
source venv/bin/activate
pip install psycopg2-binary --quiet

echo ""
echo "[STEP 3/7] Reading PostgreSQL credentials..."
source .env.postgres

echo ""
echo "[STEP 4/7] Updating .env file..."
# Backup original .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Update DATABASE_URL in .env
if grep -q "DATABASE_URL=" .env; then
    # Comment out old SQLite line
    sed -i 's/^DATABASE_URL=sqlite/# DATABASE_URL=sqlite/' .env
fi

# Add PostgreSQL DATABASE_URL if not exists
if ! grep -q "DATABASE_URL=postgresql" .env; then
    echo "" >> .env
    echo "# PostgreSQL Database (Production)" >> .env
    echo "DATABASE_URL=$DATABASE_URL" >> .env
fi

echo "✅ .env updated"

echo ""
echo "[STEP 5/7] Creating tables in PostgreSQL..."
python3 << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ All tables created successfully!")
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"   Tables created: {', '.join(tables)}")
EOPY

echo ""
echo "[STEP 6/7] Migrating users from SQLite to PostgreSQL..."
python3 << 'EOPY'
import sqlite3
from app import create_app, db
from app.models import User

# Read from SQLite
sqlite_db = 'instance/mcoder.db'
conn = sqlite3.connect(sqlite_db)
cursor = conn.cursor()

cursor.execute("SELECT id, username, email, full_name, password_hash, is_admin, is_active, created_at, last_login FROM users")
users_data = cursor.fetchall()
conn.close()

print(f"Found {len(users_data)} users in SQLite")

# Write to PostgreSQL
app = create_app()
with app.app_context():
    for user_data in users_data:
        # Check if user already exists
        existing = User.query.filter_by(email=user_data[2]).first()
        if existing:
            print(f"   - {user_data[2]}: Already exists (skipped)")
            continue
        
        user = User(
            username=user_data[1],
            email=user_data[2],
            full_name=user_data[3],
            password_hash=user_data[4],
            is_admin=bool(user_data[5]),
            is_active=bool(user_data[6]),
            created_at=user_data[7],
            last_login=user_data[8]
        )
        db.session.add(user)
        print(f"   - {user_data[2]}: Migrated")
    
    db.session.commit()
    
    # Verify
    total = User.query.count()
    print(f"\n✅ Migration complete: {total} users in PostgreSQL")
EOPY

echo ""
echo "[STEP 7/7] Restarting application..."
supervisorctl restart mcoder-markplus
sleep 5
supervisorctl status mcoder-markplus

echo ""
echo "============================================================"
echo "MIGRATION COMPLETE!"
echo "============================================================"
echo ""
echo "✅ PostgreSQL database: mcoder_production"
echo "✅ User migrated from SQLite"
echo "✅ Application restarted"
echo ""
echo "🔍 Test immediately:"
echo "   - Homepage: https://m-coder.flazinsight.com/"
echo "   - Login: Use existing credentials"
echo "   - Results: https://m-coder.flazinsight.com/results"
echo ""
echo "📝 Credentials saved in: /opt/markplus/mcoder-markplus/.env.postgres"
echo "📝 .env backup saved as: .env.backup.*"
echo ""
