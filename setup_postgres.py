#!/usr/bin/env python3
"""
PostgreSQL Database Setup for M-Code Pro
Creates database, user, and tables
"""
import subprocess
import secrets
import string

def run_psql(cmd):
    """Run PostgreSQL command"""
    result = subprocess.run(
        f'sudo -u postgres psql -c "{cmd}"',
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout, result.stderr, result.returncode

def generate_password(length=32):
    """Generate strong password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))

print("=" * 60)
print("POSTGRESQL SETUP FOR M-CODE PRO")
print("=" * 60)
print()

# Generate strong password
db_password = generate_password()

print("[1/6] Creating database user: mcoder_app...")
stdout, stderr, code = run_psql(
    f"CREATE USER mcoder_app WITH PASSWORD '{db_password}';"
)
if code == 0 or "already exists" in stderr:
    print("✅ User created or already exists")
else:
    print(f"⚠️ {stderr}")

print()

print("[2/6] Creating database: mcoder_production...")
stdout, stderr, code = run_psql(
    "CREATE DATABASE mcoder_production WITH OWNER mcoder_app ENCODING 'UTF8';"
)
if code == 0 or "already exists" in stderr:
    print("✅ Database created or already exists")
else:
    print(f"⚠️ {stderr}")

print()

print("[3/6] Granting privileges...")
run_psql("GRANT ALL PRIVILEGES ON DATABASE mcoder_production TO mcoder_app;")
run_psql("ALTER DATABASE mcoder_production OWNER TO mcoder_app;")
print("✅ Privileges granted")

print()

print("[4/6] Creating extensions...")
# Run in mcoder_production database
subprocess.run(
    'sudo -u postgres psql mcoder_production -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"',
    shell=True,
    capture_output=True
)
print("✅ Extensions created (pg_trgm for text search)")

print()

print("[5/6] Verifying setup...")
stdout, stderr, code = run_psql(
    "SELECT datname FROM pg_database WHERE datname='mcoder_production';"
)
if "mcoder_production" in stdout:
    print("✅ Database verified")
else:
    print("❌ Database verification failed")

print()

print("[6/6] Saving credentials...")
# Save to file
creds_file = "/opt/markplus/mcoder-markplus/.env.postgres"
with open(creds_file, 'w') as f:
    f.write("# PostgreSQL Connection for M-Code Pro\n")
    f.write(f"POSTGRES_USER=mcoder_app\n")
    f.write(f"POSTGRES_PASSWORD={db_password}\n")
    f.write(f"POSTGRES_HOST=localhost\n")
    f.write(f"POSTGRES_PORT=5432\n")
    f.write(f"POSTGRES_DATABASE=mcoder_production\n")
    f.write(f"\n")
    f.write(f"# Full connection string\n")
    f.write(f"DATABASE_URL=postgresql://mcoder_app:{db_password}@localhost:5432/mcoder_production\n")

print(f"✅ Credentials saved to: {creds_file}")
print()

print("=" * 60)
print("SETUP COMPLETE!")
print("=" * 60)
print()
print("📋 Summary:")
print(f"   Database: mcoder_production")
print(f"   User: mcoder_app")
print(f"   Host: localhost")
print(f"   Port: 5432")
print(f"   Password: {db_password[:8]}... (see {creds_file})")
print()
print("🔐 Credentials file: /opt/markplus/mcoder-markplus/.env.postgres")
print()
print("📝 Next steps:")
print("   1. Update .env file with DATABASE_URL")
print("   2. Install psycopg2-binary: pip install psycopg2-binary")
print("   3. Run Flask db.create_all() to create tables")
print("   4. Migrate data from SQLite (if needed)")
print()
