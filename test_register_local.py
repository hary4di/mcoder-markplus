"""
Test register route locally
"""
from app import create_app

app = create_app()

with app.test_client() as client:
    print("Testing GET /auth/register...")
    response = client.get('/auth/register')
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Register page loads successfully")
    else:
        print(f"✗ Error: {response.data.decode()}")
