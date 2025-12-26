"""
Flask Application Entry Point
"""
import os
from datetime import datetime
from app import create_app, db
from app.models import User

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

# Make datetime available in templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# CLI command to create admin user
@app.cli.command()
def create_admin():
    """Create initial admin user"""
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"Error: User '{username}' already exists!")
        return
    
    # Create admin user
    admin = User(
        username=username,
        email=email,
        is_admin=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"✓ Admin user '{username}' created successfully!")

# CLI command to list all users
@app.cli.command()
def list_users():
    """List all users"""
    users = User.query.all()
    
    if not users:
        print("No users found.")
        return
    
    print(f"\nTotal users: {len(users)}\n")
    print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Admin':<10} {'Active':<10}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<5} {user.username:<20} {user.email:<30} {'Yes' if user.is_admin else 'No':<10} {'Yes' if user.is_active else 'No':<10}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
