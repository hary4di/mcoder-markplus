#!/bin/bash
# Minimal fix for users.html - only change display field

echo "=== Applying Minimal Fix to Production users.html ==="
echo ""

# Backup current file
cp /opt/markplus/mcoder-markplus/app/templates/users.html /opt/markplus/mcoder-markplus/app/templates/users.html.backup

# Fix 1: Change column header from Username to Name (line 23)
sed -i '23s/<th>Username<\/th>/<th>Name<\/th>/' /opt/markplus/mcoder-markplus/app/templates/users.html

# Fix 2: Change display from username to full_name (line 37)
sed -i '37s/{{ user.username }}/{{ user.full_name or user.email.split('\''@'\'')[0] }}/' /opt/markplus/mcoder-markplus/app/templates/users.html

echo "✅ Changes applied:"
echo "  - Line 23: Username → Name"
echo "  - Line 37: user.username → user.full_name"
echo ""
echo "Backup saved: users.html.backup"
echo "No restart needed - template should auto-reload"
echo ""
echo "Check: https://m-coder.flazinsight.com/users"
