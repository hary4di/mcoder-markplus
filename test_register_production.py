#!/usr/bin/env python3
"""
Test register route on production server
"""
import sys
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

from app import create_app

app = create_app()
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['TESTING'] = True

with app.test_client() as client:
    print("Testing GET /auth/register...")
    try:
        response = client.get('/auth/register')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Register page loads successfully")
        else:
            print(f"✗ Error: {response.status_code}")
            print(response.data.decode()[:500])
    except Exception as e:
        print(f"✗ Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
