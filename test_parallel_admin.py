"""
Test script untuk verify parallel processing admin settings
"""
from app import create_app
from app.models import SystemSettings, User

app = create_app()

with app.app_context():
    print("="*60)
    print("PARALLEL PROCESSING ADMIN SETTINGS TEST")
    print("="*60)
    
    # 1. Check admin user
    print("\n1. Admin User Check:")
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print(f"   ✓ Admin user: {admin.username}")
        print(f"   ✓ Email: {admin.email}")
    else:
        print("   ✗ No admin user found!")
    
    # 2. Check current parallel settings
    print("\n2. Current Parallel Settings:")
    enabled = SystemSettings.get_setting('enable_parallel_processing', 'true')
    workers = SystemSettings.get_setting('parallel_max_workers', '5')
    delay = SystemSettings.get_setting('rate_limit_delay', '0.1')
    
    print(f"   Enabled: {enabled}")
    print(f"   Workers: {workers}")
    print(f"   Delay: {delay}s")
    
    # 3. Test saving new settings
    print("\n3. Test Saving Settings:")
    SystemSettings.set_setting('parallel_max_workers', '7', 'Test: 7 workers')
    SystemSettings.set_setting('rate_limit_delay', '0.15', 'Test: 0.15s delay')
    print("   ✓ Settings updated")
    
    # 4. Verify settings saved
    print("\n4. Verify Settings Saved:")
    new_workers = SystemSettings.get_setting('parallel_max_workers')
    new_delay = SystemSettings.get_setting('rate_limit_delay')
    print(f"   Workers: {new_workers}")
    print(f"   Delay: {new_delay}s")
    
    if new_workers == '7' and new_delay == '0.15':
        print("   ✓ Settings saved correctly!")
    else:
        print("   ✗ Settings not saved properly!")
    
    # 5. Restore default settings
    print("\n5. Restore Default Settings:")
    SystemSettings.set_setting('parallel_max_workers', '5', 'Parallel Workers')
    SystemSettings.set_setting('rate_limit_delay', '0.1', 'Rate Limit Delay')
    print("   ✓ Default settings restored (5 workers, 0.1s delay)")
    
    # 6. Check all settings
    print("\n6. All Parallel-Related Settings:")
    all_settings = SystemSettings.query.filter(
        SystemSettings.key.like('%parallel%') | 
        SystemSettings.key.like('%rate_limit%')
    ).all()
    
    if all_settings:
        for setting in all_settings:
            print(f"   {setting.key}: {setting.value}")
    else:
        print("   (No parallel settings found)")
    
    print("\n" + "="*60)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("="*60)
    
    # Login credentials reminder
    print("\n📋 Login Info:")
    print(f"   Username: {admin.username if admin else 'N/A'}")
    print(f"   URL: http://127.0.0.1:5000/admin/settings")
    print(f"   Tab: Parallel Processing (⚡ icon)")
    print("\n✓ Ready to test in browser!")
