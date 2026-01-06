#!/bin/bash
# Check CSRF token in production

cd /opt/markplus/mcoder-markplus

echo "Checking if base.html has CSRF token meta tag..."
grep -n "csrf-token" app/templates/base.html

echo ""
echo "Checking Flask CSRFProtect initialization..."
grep -n "CSRFProtect" app/__init__.py
