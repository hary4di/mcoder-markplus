#!/bin/bash
# Emergency Rollback - Remove Delete User Feature

cd /opt/markplus/mcoder-markplus

echo "=== EMERGENCY ROLLBACK ==="
echo "Backing up current auth.py..."
cp app/auth.py app/auth.py.broken

echo ""
echo "Reverting auth.py from git..."
git checkout HEAD -- app/auth.py

echo ""
echo "Reverting users.html from git..."
git checkout HEAD -- app/templates/users.html

echo ""
echo "Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "Starting application..."
supervisorctl start mcoder-markplus
sleep 5

echo ""
echo "Checking status..."
supervisorctl status mcoder-markplus

echo ""
echo "If RUNNING, test URL: https://m-coder.flazinsight.com/"
