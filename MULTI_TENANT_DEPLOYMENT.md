# Multi-Tenant Company System - Deployment Guide

**Date**: January 9, 2026  
**Version**: v1.4.0 - Multi-Tenant Implementation

## 🎯 What's New

### Multi-Tenant Company System
- **Company Model**: Isolated settings per company
- **Per-Company Settings**:
  - Logo (company-specific branding)
  - OpenAI API Key (independent AI usage)
  - Brevo API Key & Sender Email (company-specific email)
  - Brevo Sender Name
  - OpenAI Model selection

### Database Changes
- New table: `companies`
- Updated table: `users` (added `company_id` foreign key)
- Settings migration: SystemSettings → Company model

### Benefits
✅ Each company (MarkPlus, subsidiaries, clients) can have independent settings  
✅ Logo uploads isolated per company  
✅ API keys not shared between companies  
✅ Email settings customizable per company  
✅ Scalable for multiple business units

---

## 📋 Deployment Steps

### Step 1: Upload Files to VPS

From local Windows machine:

```powershell
# Upload updated files
scp app/models.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/
scp init_companies.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
```

### Step 2: Connect to VPS via SSH

```powershell
ssh root@145.79.10.104
```

### Step 3: Navigate to Application Directory

```bash
cd /opt/markplus/mcoder-markplus
```

### Step 4: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 5: Run Company Initialization Script

```bash
python init_companies.py
```

**Expected Output**:
```
======================================================================
MULTI-TENANT COMPANY INITIALIZATION
======================================================================

[1/5] Creating database tables...
✓ Database tables created/verified

[2/5] Checking existing companies...
✓ No existing companies found

[3/5] Creating default MarkPlus company...
✓ Created MarkPlus Indonesia (ID: 1)
   - Logo: logo_markplus_20250109_165432.png
   - Brevo Email: msurvey@markplusinc.com
   - OpenAI Key: Set

[4/5] Migrating existing users to MarkPlus...
   - Migrated: haryadi@markplusinc.com → MarkPlus Indonesia
   - Migrated: aisyahamini07@yahoo.com → MarkPlus Indonesia
✓ Migrated 2 users to MarkPlus

[5/5] Summary:
----------------------------------------------------------------------
Total Companies: 1

MarkPlus Indonesia (ID: 1, Code: MARKPLUS)
  - Active: Yes
  - Users: 2
  - Logo: logo_markplus_20250109_165432.png
  - Brevo: msurvey@markplusinc.com
  - OpenAI: Configured

======================================================================
✓ MULTI-TENANT INITIALIZATION COMPLETED
======================================================================

Next steps:
1. Restart the application
2. Each company admin can now configure their own settings
3. Logo, API keys, and email settings are isolated per company
```

### Step 6: Restart Application

```bash
supervisorctl restart mcoder-markplus
```

### Step 7: Verify Application Status

```bash
supervisorctl status mcoder-markplus
```

Expected: `mcoder-markplus RUNNING`

### Step 8: Check Logs

```bash
tail -50 /var/log/mcoder/gunicorn.log
```

Look for errors or successful startup messages.

---

## ✅ Testing Multi-Tenant Features

### Test 1: Company Settings Page

1. Login as admin: https://m-coder.flazinsight.com/login
2. Navigate to **System Settings**
3. Verify:
   - ✅ Company name displayed at top
   - ✅ OpenAI API Key section (company-specific)
   - ✅ Brevo Email Settings section (company-specific)
   - ✅ Save buttons work correctly

### Test 2: Logo Upload

1. Navigate to **Upload Logo**
2. Upload a test logo image
3. Verify:
   - ✅ Logo appears in preview
   - ✅ Logo saved with company code in filename (e.g., `logo_MARKPLUS_20250109_165432.png`)
   - ✅ Logo displays in navbar/dashboard
   - ✅ Delete button works

### Test 3: Company Isolation

**Scenario**: Create a second company and test isolation

1. Add new company via psql:
   ```sql
   INSERT INTO companies (name, code, is_active, created_at, updated_at)
   VALUES ('Test Company', 'TESTCO', true, NOW(), NOW());
   ```

2. Update a test user to new company:
   ```sql
   UPDATE users SET company_id = 2 WHERE email = 'test@test.com';
   ```

3. Login as test user and verify:
   - ✅ Can only see/edit TESTCO logo
   - ✅ Cannot see MARKPLUS logo
   - ✅ Settings isolated between companies

---

## 🔧 Troubleshooting

### Issue 1: "No company assigned to your account"

**Symptom**: Admin Settings page shows error  
**Cause**: User has `company_id = NULL`  
**Fix**:
```sql
UPDATE users SET company_id = 1 WHERE company_id IS NULL;
```

### Issue 2: Logo not displaying

**Symptom**: No logo in navbar after upload  
**Cause**: Logo filename not saved to company table  
**Fix**:
1. Check database: `SELECT id, name, logo_filename FROM companies;`
2. If NULL, re-upload logo via UI

### Issue 3: Settings not saving

**Symptom**: Save button clicked but changes not persisted  
**Check**:
1. Browser console for JavaScript errors
2. Gunicorn logs: `tail -50 /var/log/mcoder/gunicorn.log`
3. Database connection: `SELECT * FROM companies WHERE id = 1;`

### Issue 4: PostgreSQL Connection Error (Local)

**Symptom**: `no pg_hba.conf entry for host "114.4.213.158"`  
**Cause**: Trying to run init_companies.py from local Windows machine  
**Fix**: Always run database scripts **ON VPS**, not locally

---

## 🗃️ Database Schema Changes

### New Table: companies

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    logo_filename VARCHAR(255),
    brevo_api_key VARCHAR(255),
    brevo_sender_email VARCHAR(120),
    brevo_sender_name VARCHAR(100),
    openai_api_key VARCHAR(255),
    openai_model VARCHAR(50) DEFAULT 'gpt-4o-mini',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Updated Table: users

```sql
ALTER TABLE users ADD COLUMN company_id INTEGER;
ALTER TABLE users ADD FOREIGN KEY (company_id) REFERENCES companies(id);
ALTER TABLE users ALTER COLUMN company_id SET DEFAULT 1;
```

### Data Migration

1. Create default company: **MarkPlus Indonesia** (ID: 1, Code: MARKPLUS)
2. Migrate existing settings from `system_settings` to `companies` table
3. Update all users: `company_id = 1` (MarkPlus Indonesia)

---

## 📊 Current Production State

**After Deployment**:

- **Companies**: 1 (MarkPlus Indonesia)
- **Users**: 2 (both assigned to MarkPlus Indonesia)
- **Logo**: Company-specific (saved as `logo_MARKPLUS_*.png`)
- **API Keys**: Migrated to Company model
- **Email Settings**: Migrated to Company model

**Settings Storage**:
- ✅ Company-specific: Logo, OpenAI Key, Brevo Key, Sender Email
- ✅ Global (shared): Invalid patterns, classification settings, AI prompts, parallel processing

---

## 🚀 Next Steps (Future)

### Phase 2: Company Management UI (Optional)

Create admin interface for Super Admin to:
- Create new companies
- Edit company details
- Assign users to companies
- View company statistics
- Activate/deactivate companies

**Route**: `/admin/companies`  
**Access**: Super Admin only  
**Priority**: Low (can be done manually via database for now)

---

## 📝 Rollback Plan (If Needed)

If issues occur, rollback to previous version:

```bash
cd /opt/markplus/mcoder-markplus
git checkout b044657  # Before multi-tenant implementation
supervisorctl restart mcoder-markplus
```

**Note**: Rollback will lose Company table and company_id foreign key. Users may see errors until database is restored to pre-multi-tenant state.

**Safe Rollback**: Keep git backup at commit `7ce4500` (multi-tenant implementation).

---

## ✅ Success Criteria

Deployment successful if:

✅ Application starts without errors  
✅ Admin Settings page displays company-specific settings  
✅ Logo upload works and displays correctly  
✅ Settings save to Company table (verify in database)  
✅ All existing users assigned to MarkPlus Indonesia  
✅ Classification still works with company-specific OpenAI key  

---

## 📞 Support

**Developer**: Haryadi  
**Email**: haryadi@markplusinc.com  
**WhatsApp**: +62 812-8933-008

**Production**: https://m-coder.flazinsight.com  
**Database**: PostgreSQL mcoder_production  
**Server**: 145.79.10.104 (Hostinger VPS)

---

**End of Deployment Guide**
