#!/bin/bash
# Migrate Users from SQLite to PostgreSQL

cd /opt/markplus/mcoder-markplus
source venv/bin/activate

echo "============================================================"
echo "MIGRATING USERS"
echo "============================================================"
echo ""

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
print("")

# Write to PostgreSQL
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
        print(f"   ✅ {user_data[2]}: Migrated")
    
    db.session.commit()
    total = User.query.count()
    print(f"\n✅ Migration complete: {migrated} new, {total} total users")
EOPY

echo ""
echo "============================================================"
echo "MIGRATION COMPLETE!"
echo "============================================================"
echo ""
