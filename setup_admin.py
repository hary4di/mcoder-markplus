"""
Quick script to create admin user
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User

# Create app and context
app = create_app()

with app.app_context():
    # Create database tables
    db.create_all()
    
    # Admin credentials
    username = "haryadi@markplusinc.com"
    email = "haryadi@markplusinc.com"
    password = "MarkPlus"
    full_name = "Haryadi"
    
    # Check if user exists
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"User '{username}' already exists!")
    else:
        # Create admin
        admin = User(
            username=username,
            email=email,
            full_name=full_name,
            is_admin=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"✓ Admin user created successfully!")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"\nAccess the app at: http://localhost:5000")
