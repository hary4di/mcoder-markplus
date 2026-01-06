"""
Update user full_name in production database
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    print("Current users:")
    users = User.query.all()
    for u in users:
        print(f"  {u.id}: {u.username} | {u.email} | {u.full_name}")
    
    print("\nUpdating full_name...")
    
    # Update based on known emails
    updates = {
        'haryadi@markplusinc.com': 'Haryadi',
        'aisyahamini07@yahoo.com': 'Noor Aisyah Amini',
        'zaenal.mutaqin@markplusinc.com': 'Zainal Mutaqin'
    }
    
    for email, full_name in updates.items():
        user = User.query.filter_by(email=email).first()
        if user:
            user.full_name = full_name
            print(f"  Updated: {email} → {full_name}")
    
    db.session.commit()
    print("\n✅ Database updated!")
    
    print("\nVerification:")
    users = User.query.all()
    for u in users:
        print(f"  {u.id}: {u.username} | {u.email} | {u.full_name}")
