#!/bin/bash
# Test /users route directly on VPS

echo "Testing /users route on production..."
echo ""

# Test with curl
echo "1. Testing HTTP request to /users:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:5000/users

echo ""
echo "2. Full response from /users:"
curl -s http://localhost:5000/users | head -50

echo ""
echo "3. Check if gunicorn is listening:"
netstat -tlnp | grep 5000

echo ""
echo "Done!"
