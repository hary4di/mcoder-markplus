#!/bin/bash
echo "=== NGINX CONFIGURATION CHECK ==="
echo ""

echo "1. Nginx status:"
systemctl status nginx | head -5

echo ""
echo "2. Test port 8000 (actual gunicorn port):"
curl -s -o /dev/null -w "HTTP Status on port 8000: %{http_code}\n" http://localhost:8000/users

echo ""
echo "3. Show nginx config for mcoder:"
cat /etc/nginx/sites-enabled/mcoder* 2>/dev/null || cat /etc/nginx/conf.d/mcoder* 2>/dev/null || echo "Config not found in standard location"

echo ""
echo "4. Check nginx error log:"
tail -20 /var/log/nginx/error.log

echo ""
echo "5. Check nginx access log:"
tail -10 /var/log/nginx/access.log

echo ""
echo "6. Test actual URL from localhost:"
curl -s -I https://m-coder.flazinsight.com/users

echo ""
echo "=== END ==="
