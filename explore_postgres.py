#!/usr/bin/env python3
"""
PostgreSQL Setup Explorer for M-Code Pro
"""
import subprocess
import sys

def run_command(cmd, shell=False):
    """Run command and return output"""
    try:
        result = subprocess.run(
            cmd if not shell else cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

print("=" * 60)
print("POSTGRESQL SETUP EXPLORATION")
print("=" * 60)
print()

# 1. Check if PostgreSQL installed
print("[1/7] PostgreSQL Installation Check...")
output = run_command("which psql && psql --version", shell=True)
if "psql" in output:
    print("✅ PostgreSQL installed:")
    print(f"   {output.strip()}")
else:
    print("❌ PostgreSQL NOT installed")
    sys.exit(1)

print()

# 2. Check service status
print("[2/7] PostgreSQL Service Status...")
output = run_command("systemctl is-active postgresql", shell=True)
if "active" in output:
    print("✅ PostgreSQL service is ACTIVE")
else:
    print(f"⚠️ Service status: {output.strip()}")

print()

# 3. List databases
print("[3/7] Existing Databases...")
output = run_command("sudo -u postgres psql -l -t", shell=True)
if output:
    lines = [l.strip() for l in output.split('\n') if l.strip() and '|' in l]
    print(f"   Found {len(lines)} databases:")
    for line in lines[:10]:
        parts = line.split('|')
        if len(parts) >= 1:
            print(f"   - {parts[0].strip()}")

print()

# 4. List users
print("[4/7] PostgreSQL Users...")
output = run_command("sudo -u postgres psql -c '\\du' -t", shell=True)
if output:
    lines = [l.strip() for l in output.split('\n') if l.strip() and '|' in l]
    print(f"   Found {len(lines)} users:")
    for line in lines[:10]:
        parts = line.split('|')
        if len(parts) >= 1:
            print(f"   - {parts[0].strip()}")

print()

# 5. Check disk space
print("[5/7] Disk Space...")
output = run_command("df -h /", shell=True)
print(output)

print()

# 6. PostgreSQL config
print("[6/7] PostgreSQL Configuration...")
output = run_command("sudo -u postgres psql -c 'SHOW data_directory;' -t", shell=True)
print(f"   Data Directory: {output.strip()}")

output = run_command("sudo -u postgres psql -c 'SHOW port;' -t", shell=True)
print(f"   Port: {output.strip()}")

output = run_command("sudo -u postgres psql -c 'SHOW max_connections;' -t", shell=True)
print(f"   Max Connections: {output.strip()}")

print()

# 7. Recommendations
print("[7/7] Recommendations for M-Code Pro...")
print()
print("📊 Proposed Database Structure:")
print("   Database Name: mcoder_production")
print("   Owner: mcoder_app (new user)")
print("   Schema: public (default)")
print()
print("📁 Proposed Tables:")
print("   - users (authentication)")
print("   - classification_jobs (job tracking)")
print("   - classification_variables (per-variable results)")
print("   - classification_responses (detailed responses) [FUTURE]")
print("   - tabulation_jobs (tabulasi module) [Q1 2026]")
print("   - tabulation_tables (generated tables) [Q1 2026]")
print()
print("🔐 Security:")
print("   - Dedicated DB user: mcoder_app")
print("   - Strong password")
print("   - Limited permissions (no superuser)")
print()
print("=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)
