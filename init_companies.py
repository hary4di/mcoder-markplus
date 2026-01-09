"""
Initialize Companies for Multi-Tenant System

This script creates default companies and migrates existing users.
Run this ONCE after adding Company model to database.
"""
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Company, User, SystemSettings
from config import Config

def init_companies():
    """Initialize companies and migrate existing data"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("MULTI-TENANT COMPANY INITIALIZATION")
        print("=" * 70)
        print()
        
        # Step 1: Create tables if not exist
        print("[1/5] Creating database tables...")
        try:
            db.create_all()
            print("✓ Database tables created/verified")
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return
        
        # Step 2: Check if companies already exist
        print("\n[2/5] Checking existing companies...")
        existing_companies = Company.query.all()
        if existing_companies:
            print(f"✓ Found {len(existing_companies)} existing companies:")
            for company in existing_companies:
                print(f"   - {company.name} (ID: {company.id}, Code: {company.code})")
        else:
            print("✓ No existing companies found")
        
        # Step 3: Create default MarkPlus company
        print("\n[3/5] Creating default MarkPlus company...")
        markplus = Company.query.filter_by(code='MARKPLUS').first()
        
        if not markplus:
            # Migrate settings from SystemSettings to MarkPlus company
            logo_filename = SystemSettings.get_setting('logo_filename', None)
            brevo_api_key = SystemSettings.get_setting('brevo_api_key', None)
            brevo_sender_email = SystemSettings.get_setting('brevo_sender_email', None)
            brevo_sender_name = SystemSettings.get_setting('brevo_sender_name', 'M-Code Pro')
            
            # Get OpenAI key from environment
            openai_api_key = os.environ.get('OPENAI_API_KEY')
            
            markplus = Company(
                name='MarkPlus Indonesia',
                code='MARKPLUS',
                logo_filename=logo_filename,
                brevo_api_key=brevo_api_key,
                brevo_sender_email=brevo_sender_email,
                brevo_sender_name=brevo_sender_name,
                openai_api_key=openai_api_key,
                openai_model='gpt-4o-mini',
                is_active=True
            )
            db.session.add(markplus)
            db.session.commit()
            print(f"✓ Created MarkPlus Indonesia (ID: {markplus.id})")
            print(f"   - Logo: {logo_filename or 'None'}")
            print(f"   - Brevo Email: {brevo_sender_email or 'None'}")
            print(f"   - OpenAI Key: {'Set' if openai_api_key else 'Not Set'}")
        else:
            print(f"✓ MarkPlus Indonesia already exists (ID: {markplus.id})")
        
        # Step 4: Migrate existing users to MarkPlus company
        print("\n[4/5] Migrating existing users to MarkPlus...")
        users_without_company = User.query.filter(
            (User.company_id == None) | (User.company_id == 0)
        ).all()
        
        if users_without_company:
            for user in users_without_company:
                user.company_id = markplus.id
                print(f"   - Migrated: {user.email} → MarkPlus Indonesia")
            db.session.commit()
            print(f"✓ Migrated {len(users_without_company)} users to MarkPlus")
        else:
            print("✓ All users already have company assignment")
        
        # Step 5: Summary
        print("\n[5/5] Summary:")
        print("-" * 70)
        
        all_companies = Company.query.all()
        print(f"Total Companies: {len(all_companies)}")
        for company in all_companies:
            user_count = User.query.filter_by(company_id=company.id).count()
            print(f"\n{company.name} (ID: {company.id}, Code: {company.code})")
            print(f"  - Active: {'Yes' if company.is_active else 'No'}")
            print(f"  - Users: {user_count}")
            print(f"  - Logo: {company.logo_filename or 'Not Set'}")
            print(f"  - Brevo: {company.brevo_sender_email or 'Not Set'}")
            print(f"  - OpenAI: {'Configured' if company.openai_api_key else 'Not Set'}")
        
        print("\n" + "=" * 70)
        print("✓ MULTI-TENANT INITIALIZATION COMPLETED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Restart the application")
        print("2. Each company admin can now configure their own settings")
        print("3. Logo, API keys, and email settings are isolated per company")
        print()

if __name__ == '__main__':
    init_companies()
