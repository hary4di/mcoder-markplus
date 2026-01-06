"""
Automated Development Environment Setup for M-Code Pro
Checks dependencies, creates .env, initializes database
"""
import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(text):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Verify Python 3.11+"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("❌ ERROR: Python 3.11 or higher required")
        print(f"   Current: Python {version.major}.{version.minor}")
        print(f"   Download: https://www.python.org/downloads/")
        return False
    
    print("✅ Python version OK")
    return True

def install_requirements():
    """Install Python dependencies"""
    print_header("Installing Dependencies")
    
    print("Upgrading pip...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        print("✅ pip upgraded")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Failed to upgrade pip: {e}")
    
    print("\nInstalling packages from requirements.txt...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              check=True, capture_output=True, text=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to install dependencies")
        print(f"   {e.stderr}")
        return False

def create_env_file():
    """Create .env file with defaults"""
    print_header("Configuring Environment Variables")
    
    env_path = Path('.env')
    if env_path.exists():
        print("⚠️  .env file already exists")
        overwrite = input("   Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("✅ Keeping existing .env")
            return True
    
    print("\n📋 Configuring .env file...")
    print("   (Press Enter to skip optional fields)")
    
    # Get OpenAI API key
    openai_key = input("\n🔑 Enter OpenAI API Key (required): ").strip()
    while not openai_key:
        print("❌ OpenAI API key is required for classification")
        openai_key = input("🔑 Enter OpenAI API Key: ").strip()
    
    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    
    # Optional: Brevo API key for email
    print("\n📧 Email Configuration (Optional - for OTP password reset)")
    brevo_key = input("   Brevo API Key (press Enter to skip): ").strip()
    
    # Write .env file
    from datetime import datetime
    env_content = f"""# M-Code Pro Development Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# OpenAI API
OPENAI_API_KEY={openai_key}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development
FLASK_DEBUG=1

# Database
DATABASE_URL=sqlite:///instance/users.db

# Classification Settings
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.5
CATEGORY_SAMPLE_RATIO=0.8
MAX_SAMPLE_SIZE=500
ENABLE_STRATIFIED_SAMPLING=true

# Parallel Processing
ENABLE_PARALLEL_PROCESSING=true
PARALLEL_MAX_WORKERS=5
RATE_LIMIT_DELAY=0.1

# Email (Optional - for OTP)
"""
    
    if brevo_key:
        env_content += f"BREVO_API_KEY={brevo_key}\n"
    else:
        env_content += "# BREVO_API_KEY=your_brevo_api_key_here\n"
    
    env_content += """OTP_EMAIL_FROM=noreply@markplusinc.com

# Kobo Integration (Optional - rarely used)
AUTO_UPLOAD_TO_KOBO=false
# KOBO_API_TOKEN=your_kobo_token
# KOBO_ASSET_ID=your_asset_id
"""
    
    env_path.write_text(env_content, encoding='utf-8')
    print(f"✅ Created .env file")
    return True

def create_folders():
    """Create required folders"""
    print_header("Creating Required Folders")
    
    folders = [
        'instance',
        'files/uploads',
        'files/uploads/backups',
        'files/uploads/logos',
        'files/uploads/profile_photos',
        'files/logs',
        'files/logo'
    ]
    
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✅ {folder}/")
    
    return True

def init_database():
    """Initialize database with Flask-Migrate"""
    print_header("Initializing Database")
    
    # Set environment variable for Flask
    os.environ['FLASK_APP'] = 'run_app.py'
    
    # Check if migrations folder exists
    migrations_path = Path('migrations')
    if not migrations_path.exists():
        print("Initializing Flask-Migrate...")
        try:
            result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'init'], 
                                  check=True, capture_output=True, text=True)
            print("✅ Flask-Migrate initialized")
        except subprocess.CalledProcessError as e:
            print(f"❌ ERROR: Failed to initialize Flask-Migrate")
            print(f"   {e.stderr}")
            return False
    else:
        print("✅ Flask-Migrate already initialized")
    
    # Create initial migration
    print("\nCreating database migration...")
    try:
        result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'migrate', 
                               '-m', 'Add classification job tracking'], 
                              check=True, capture_output=True, text=True)
        print("✅ Migration created")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Note: {e.stderr.split('ERROR')[0] if 'ERROR' in e.stderr else 'Migration may already exist'}")
    
    # Apply migrations
    print("\nApplying database migrations...")
    try:
        result = subprocess.run([sys.executable, '-m', 'flask', 'db', 'upgrade'], 
                              check=True, capture_output=True, text=True)
        print("✅ Database updated")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to apply migrations")
        print(f"   {e.stderr}")
        return False

def create_admin_user():
    """Create default admin user"""
    print_header("Creating Admin User")
    
    # Check if setup_admin.py exists
    if not Path('setup_admin.py').exists():
        print("⚠️  setup_admin.py not found - skipping admin creation")
        print("   You can create admin manually later")
        return True
    
    print("Would you like to create an admin user now?")
    create = input("(Y/n): ").strip().lower()
    
    if create in ('', 'y', 'yes'):
        try:
            result = subprocess.run([sys.executable, 'setup_admin.py'], 
                                  check=True, capture_output=True, text=True)
            print(result.stdout)
            print("✅ Admin user created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Note: {e.stderr}")
            print("   You can create one later with: python setup_admin.py")
    else:
        print("⏭️  Skipped - you can create admin later with: python setup_admin.py")
    
    return True

def print_next_steps():
    """Print instructions for running the app"""
    print_header("✅ Setup Complete!")
    
    print(f"""
🎉 Development environment is ready!

📝 Next Steps:

1. Run development server:
   python run_app.py

2. Open browser:
   http://127.0.0.1:5000

3. Login with your admin credentials

📚 Documentation:
   - README.md: User guide
   - PROJECT_OVERVIEW.md: Technical overview
   - .github/copilot-instructions.md: AI agent guide

⚠️  Important:
   - .env contains your OpenAI API key - keep it secret!
   - Don't commit .env to git (already in .gitignore)

💡 Tips:
   - To create admin user later: python setup_admin.py
   - To reset database: delete instance/users.db and re-run this script
   - For production deployment: See PROJECT_OVERVIEW.md

Need help? Contact: haryadi@markplusinc.com
""")

def main():
    """Main setup workflow"""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              M-Code Pro - Dev Setup Script                 ║
║         MarkPlus AI-Powered Classification System          ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("Python Version", check_python_version),
        ("Dependencies", install_requirements),
        ("Folders", create_folders),
        ("Environment Config", create_env_file),
        ("Database", init_database),
        ("Admin User", create_admin_user)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at step: {step_name}")
            print("   Please fix the error and run setup again")
            return False
    
    print_next_steps()
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
