"""
Diagnose Production Issues
Run this on production server to check what's wrong
"""
import sys
import os

# Add app to path
sys.path.insert(0, '/opt/markplus/mcoder-markplus')

print("=" * 60)
print("PRODUCTION DIAGNOSIS")
print("=" * 60)

try:
    print("\n1. Importing Flask app...")
    from app import create_app, db
    print("   ✓ Flask app imported successfully")
    
    print("\n2. Creating app instance...")
    app = create_app()
    print("   ✓ App created successfully")
    
    print("\n3. Pushing app context...")
    with app.app_context():
        print("   ✓ App context active")
        
        print("\n4. Testing database connection...")
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        print("   ✓ Database connection OK")
        
        print("\n5. Checking SystemSettings table...")
        result = db.session.execute(text("SELECT COUNT(*) FROM system_settings"))
        count = result.scalar()
        print(f"   ✓ system_settings table exists with {count} rows")
        
        print("\n6. Testing SystemSettings model...")
        from app.models import SystemSettings
        settings = SystemSettings.get_settings()
        print(f"   ✓ SystemSettings.get_settings() works")
        print(f"   - app_name: {settings.app_name}")
        print(f"   - logo_filename: {settings.logo_filename}")
        
        print("\n7. Testing User model...")
        from app.models import User
        user_count = User.query.count()
        print(f"   ✓ User model OK - {user_count} users")
        
        print("\n8. Testing OTPToken model...")
        from app.models import OTPToken
        otp_count = OTPToken.query.count()
        print(f"   ✓ OTPToken model OK - {otp_count} OTP tokens")
        
        print("\n9. Testing EmailService...")
        from app.email_service import EmailService
        email_service = EmailService()
        print(f"   ✓ EmailService initialized")
        print(f"   - BREVO_API_KEY: {'SET' if os.environ.get('BREVO_API_KEY') else 'NOT SET'}")
        print(f"   - BREVO_SENDER_EMAIL: {os.environ.get('BREVO_SENDER_EMAIL', 'NOT SET')}")
        
        print("\n" + "=" * 60)
        print("ALL CHECKS PASSED ✓")
        print("=" * 60)
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    print("\nFull Traceback:")
    traceback.print_exc()
    sys.exit(1)
