"""
Test Brevo Email Service
Run this to verify email configuration before testing registration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Flask app to create context
from app import create_app
from app.email_service import EmailService

# Create Flask app
app = create_app()

def test_brevo_config():
    """Test Brevo configuration"""
    print("=" * 60)
    print("🔍 TESTING BREVO EMAIL SERVICE CONFIGURATION")
    print("=" * 60)
    
    # Check environment variables
    api_key = os.getenv('BREVO_API_KEY', '')
    sender_email = os.getenv('BREVO_SENDER_EMAIL', '')
    sender_name = os.getenv('BREVO_SENDER_NAME', '')
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {'✅ Set' if api_key and api_key != 'your_brevo_api_key_here' else '❌ Not configured'}")
    if api_key and api_key != 'your_brevo_api_key_here':
        print(f"            {api_key[:20]}...{api_key[-10:]}")
    print(f"   Sender Email: {sender_email}")
    print(f"   Sender Name: {sender_name}")
    
    if not api_key or api_key == 'your_brevo_api_key_here':
        print("\n❌ BREVO_API_KEY not configured!")
        print("   Please follow BREVO_SETUP_GUIDE.md to setup Brevo")
        return False
    
    return True

def test_send_email():
    """Test sending actual email"""
    print("\n" + "=" * 60)
    print("📧 TESTING EMAIL SENDING")
    print("=" * 60)
    
    # Get recipient email
    recipient_email = input("\n📮 Enter YOUR email for testing (e.g., your@gmail.com): ").strip()
    
    if not recipient_email or '@' not in recipient_email:
        print("❌ Invalid email address")
        return False
    
    recipient_name = input("👤 Enter your name: ").strip() or "Test User"
    
    print(f"\n📤 Sending test OTP email to {recipient_email}...")
    
    # Send email with app context
    with app.app_context():
        email_service = EmailService()
        test_otp = "123456"
        
        success, message = email_service.send_registration_otp(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            otp_code=test_otp
        )
    
    if success:
        print(f"\n✅ SUCCESS! {message}")
        print(f"\n📬 Please check your inbox at {recipient_email}")
        print("   (Also check spam/junk folder if not found)")
        print(f"\n🔢 Test OTP Code: {test_otp}")
        print("\nIf email received, Brevo is configured correctly! ✨")
        return True
    else:
        print(f"\n❌ FAILED! {message}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check API key is correct in .env")
        print("   2. Verify sender email in Brevo dashboard")
        print("   3. Check Brevo logs: https://app.brevo.com/")
        print("   4. See BREVO_SETUP_GUIDE.md for details")
        return False

def main():
    """Main test function"""
    print("\n")
    print("╔════════════════════════════════════════════════════════╗")
    print("║       Brevo Email Service Test - M-Code Pro           ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Test configuration
    if not test_brevo_config():
        print("\n⚠️  Please configure Brevo first (see BREVO_SETUP_GUIDE.md)")
        return
    
    # Ask to test sending
    print("\n" + "=" * 60)
    test_send = input("Do you want to test sending email? (y/n): ").strip().lower()
    
    if test_send == 'y':
        test_send_email()
    else:
        print("\n✅ Configuration check completed. Ready to test registration!")
    
    print("\n" + "=" * 60)
    print("📚 For setup guide, see: BREVO_SETUP_GUIDE.md")
    print("=" * 60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
