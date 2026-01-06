#!/bin/bash
echo "=== CHECK ACTUAL ERROR IN APPLICATION ==="
echo ""

echo "1. Clear old logs and restart to get fresh error:"
> /var/log/mcoder/gunicorn.log
> /var/log/mcoder/gunicorn_error.log
supervisorctl restart mcoder-markplus
sleep 3

echo ""
echo "2. Make test request to /users (simulating logged in):"
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
python -c "
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Get admin user
    user = User.query.filter_by(email='haryadi@markplusinc.com').first()
    if user:
        print(f'Testing with user: {user.email}')
        
        # Test the /users route directly
        with app.test_client() as client:
            # Login first
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
            
            # Access /users
            response = client.get('/users')
            print(f'Response status: {response.status_code}')
            if response.status_code == 500:
                print('ERROR 500 - Checking traceback...')
            else:
                print('SUCCESS - No error')
" 2>&1

echo ""
echo "3. Check fresh error log:"
tail -100 /var/log/mcoder/gunicorn_error.log

echo ""
echo "4. Check stdout log:"
tail -50 /var/log/mcoder/gunicorn.log

echo ""
echo "=== END ==="
