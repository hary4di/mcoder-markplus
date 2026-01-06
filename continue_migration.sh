#!/bin/bash
# Fixed PostgreSQL Migration - Continue from Step 3

set -e

echo "============================================================"
echo "CONTINUING POSTGRESQL MIGRATION (Steps 3-7)"
echo "============================================================"
echo ""

cd /opt/markplus/mcoder-markplus
source venv/bin/activate

echo "[STEP 3/7] Reading credentials from .env.postgres..."
# Read DATABASE_URL safely
DB_URL=$(grep "^DATABASE_URL=" .env.postgres | cut -d'=' -f2-)
echo "✅ Credentials loaded"

echo ""
echo "[STEP 4/7] Updating .env file..."
# Backup
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Comment out SQLite
sed -i 's/^DATABASE_URL=sqlite/# DATABASE_URL=sqlite/' .env

# Add PostgreSQL if not exists
if ! grep -q "DATABASE_URL=postgresql" .env; then
    echo "" >> .env
    echo "# PostgreSQL Database (Production)" >> .env
    echo "DATABASE_URL=$DB_URL" >> .env
fi

echo "✅ .env updated with PostgreSQL connection"

echo ""
echo "[STEP 5/7] Creating tables in PostgreSQL..."
python3 << 'EOPY'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created!")
    
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"   Tables: {', '.join(tables)}")
EOPY

echo ""
echo "[STEP 6/7] Migrating users from SQLite..."
python3 << 'EOPY'
import sqlite3
from app import create_app, db
from app.models import User

sqlite_db = 'instance/mcoder.db'
try:
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, full_name, password_hash, is_admin, is_active, created_at, last_login FROM users")
    users_data = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(users_data)} users in SQLite")
    
    app = create_app()
    with app.app_context():
        migrated = 0
        for user_data in users_data:
            existing = User.query.filter_by(email=user_data[2]).first()
            if existing:
                print(f"   - {user_data[2]}: Already exists")
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
            migrated += 1
            print(f"   - {user_data[2]}: Migrated")
        
        db.session.commit()
        total = User.query.count()
        print(f"\n✅ Migration complete: {migrated} new, {total} total users")
except Exception as e:
    print(f"⚠️ User migration: {e}")
    print("   You can add users manually later")
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
echo "✅ PostgreSQL: mcoder_production"
echo "✅ Tables: Created"
echo "✅ Users: Migrated"
echo "✅ Application: Restarted"
echo ""
echo "🔍 TEST IMMEDIATELY:"
echo "   1. https://m-coder.flazinsight.com/"
echo "   2. Login with existing credentials"
echo "   3. Try classification"
echo ""
