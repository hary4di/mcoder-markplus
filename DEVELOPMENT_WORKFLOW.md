# Development-Production Workflow - M-Coder Platform

## 📊 Status Saat Ini

### Development (Lokal - Windows)
- **Path**: `C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding`
- **Environment**: Python local, development database
- **Git**: Initialized (belum push ke remote)
- **Testing**: Run manual dengan `python run_app.py`

### Production (VPS - Ubuntu)
- **Path**: `/opt/markplus/mcoder-markplus/`
- **Environment**: Gunicorn + Supervisor, production database
- **Git**: ❌ **BELUM SETUP** (deployed manual via ZIP upload)
- **URL**: https://m-coder.flazinsight.com

## ⚠️ Masalah Saat Ini

1. **❌ Tidak Ada Version Control di Production**
   - File di lokal dan VPS bisa berbeda
   - Sulit tracking perubahan
   - Risiko overwrite code yang sudah bekerja

2. **❌ No Automated Deployment**
   - Update manual via ZIP upload
   - Time consuming (compress, upload, extract, restart)
   - Error prone (lupa restart service, lupa update dependencies)

3. **❌ Environment Variables Bisa Beda**
   - `.env` di lokal vs production berbeda
   - Bisa cause different behavior

## ✅ Solusi: Git-Based Deployment Workflow

### 1. Setup Git Repository (RECOMMENDED)

#### Option A: GitHub Private Repository (Gratis)

**Di Lokal (Windows):**
```powershell
cd "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding"

# Initialize git if not exists
git init

# Create .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Flask
instance/
*.db
*.sqlite3

# Environment
.env
.env.local
.env.production

# Files
files/uploads/*
files/output/*
files/logo/*
!files/uploads/.gitkeep
!files/output/.gitkeep
!files/logo/.gitkeep

# Logs
files/logs/*.log
files/logs/*.txt
!files/logs/.gitkeep

# OS
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo

# Backups
*.backup_*
backups/

# Temporary
*.tmp
*.temp
"@ | Out-File -FilePath .gitignore -Encoding utf8

# Add all files
git add .

# Commit
git commit -m "Initial commit: M-Coder Platform"

# Create GitHub repository (via web browser)
# https://github.com/new
# Repository name: mcoder-markplus (PRIVATE!)

# Add remote (ganti YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/mcoder-markplus.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Di VPS (Production):**
```bash
# SSH ke VPS
ssh root@145.79.10.104

# Navigate to directory
cd /opt/markplus/

# Backup current directory
mv mcoder-markplus mcoder-markplus.backup-$(date +%Y%m%d-%H%M%S)

# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/mcoder-markplus.git

cd mcoder-markplus/

# Setup production .env (JANGAN commit ke git!)
cat > .env << 'EOF'
# Flask Configuration
SECRET_KEY=PRODUCTION_SECRET_KEY_HERE  # Generate baru!
FLASK_ENV=production

# OpenAI API
OPENAI_API_KEY=your_production_key

# Instance
INSTANCE_NAME=markplus

# Database
DATABASE_URL=sqlite:///instance/users.db

# Email (if enabled)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Logo
LOGO_UPLOAD_FOLDER=files/logo
MAX_LOGO_SIZE_MB=5

# Classification
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.7
ENABLE_PARALLEL_PROCESSING=true
PARALLEL_MAX_WORKERS=5
RATE_LIMIT_DELAY=0.1
EOF

# Rebuild virtual environment
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

# Create directories
mkdir -p files/uploads files/output files/logo files/logs
mkdir -p instance

# Setup database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Restart service
supervisorctl restart mcoder-markplus
```

#### Option B: Gitea Self-Hosted (Alternatif)

Bisa install Gitea di VPS yang sama untuk private Git server.

---

### 2. Development Workflow

#### Daily Development Flow:

```powershell
# 1. Pull latest dari production (sync)
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Develop & test locally
python run_app.py
# Test di: http://localhost:5000

# 4. Commit changes
git add .
git commit -m "feat: Add new feature XYZ"

# 5. Push to GitHub
git push origin feature/new-feature

# 6. Merge to main (via GitHub Pull Request atau manual)
git checkout main
git merge feature/new-feature
git push origin main
```

#### Deploy to Production:

```bash
# SSH ke VPS
ssh root@145.79.10.104

# Navigate to app directory
cd /opt/markplus/mcoder-markplus

# Pull latest code
git pull origin main

# Update dependencies (if requirements.txt changed)
source venv/bin/activate
pip install -r requirements.txt

# Restart application
supervisorctl restart mcoder-markplus

# Check status
supervisorctl status mcoder-markplus
curl http://localhost:8000
```

---

### 3. Quick Deploy Script

**Di Lokal (`deploy.ps1`):**
```powershell
# deploy.ps1 - Quick deploy script
param(
    [string]$message = "Update from local"
)

Write-Host "🚀 Deploying M-Coder Platform..." -ForegroundColor Cyan

# Commit dan push
git add .
git commit -m $message
git push origin main

Write-Host "✅ Code pushed to GitHub" -ForegroundColor Green

# Deploy ke VPS
Write-Host "📦 Deploying to VPS..." -ForegroundColor Yellow
ssh root@145.79.10.104 "cd /opt/markplus/mcoder-markplus && git pull origin main && source venv/bin/activate && pip install -r requirements.txt && supervisorctl restart mcoder-markplus && supervisorctl status mcoder-markplus"

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Check: https://m-coder.flazinsight.com" -ForegroundColor Cyan
```

**Usage:**
```powershell
# Deploy dengan custom message
.\deploy.ps1 -message "Fix bug in classification"

# Deploy dengan default message
.\deploy.ps1
```

**Di VPS (`update.sh`):**
```bash
#!/bin/bash
# update.sh - Quick update script di VPS

echo "🔄 Updating M-Coder Platform..."

cd /opt/markplus/mcoder-markplus

# Pull latest
git pull origin main

# Check if requirements changed
if git diff HEAD@{1} HEAD --name-only | grep -q requirements.txt; then
    echo "📦 Requirements changed, updating..."
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Restart
supervisorctl restart mcoder-markplus

# Check status
sleep 2
supervisorctl status mcoder-markplus

echo "✅ Update complete!"
```

---

### 4. Environment-Specific Configuration

**PENTING:** `.env` file **JANGAN** di-commit ke Git!

#### .env.example (Commit ini ke Git):
```env
# Template for .env file
# Copy this to .env and fill with actual values

# Flask Configuration
SECRET_KEY=generate_random_secret_key_here
FLASK_ENV=development

# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Instance
INSTANCE_NAME=markplus

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=

# Classification
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.7
ENABLE_PARALLEL_PROCESSING=true
PARALLEL_MAX_WORKERS=5
```

#### Setup .env di Production:
```bash
# Copy template
cp .env.example .env

# Edit dengan production values
nano .env
```

---

### 5. Database Migration Strategy

Saat ini pakai SQLite, jadi migration simple:

**When Adding New Tables/Columns:**

```python
# Di lokal, test migration
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Commit model changes
git add app/models.py
git commit -m "feat: Add new User field"
git push

# Di VPS, run migration setelah pull
cd /opt/markplus/mcoder-markplus
git pull
source venv/bin/activate
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
supervisorctl restart mcoder-markplus
```

---

### 6. Rollback Strategy

Jika ada masalah di production:

```bash
# Di VPS
cd /opt/markplus/mcoder-markplus

# Lihat commit history
git log --oneline -10

# Rollback ke commit sebelumnya
git reset --hard <commit-hash>

# Atau rollback ke version sebelumnya
git reset --hard HEAD~1

# Restart
supervisorctl restart mcoder-markplus
```

---

## 🎯 Best Practices

### ✅ DO:
1. **Selalu test di local dulu** sebelum deploy
2. **Commit dengan message yang jelas**: `feat:`, `fix:`, `docs:`, `refactor:`
3. **Pull dulu sebelum push** untuk avoid conflicts
4. **Backup database production** sebelum major changes
5. **Use `.env` untuk sensitive data**, jangan hardcode
6. **Test di production** setelah deploy (check logs)

### ❌ DON'T:
1. **JANGAN commit `.env`** file ke Git
2. **JANGAN commit database files** (`instance/*.db`)
3. **JANGAN commit uploaded files** (`files/uploads/`, `files/output/`)
4. **JANGAN edit langsung di production** without Git
5. **JANGAN deploy tanpa test di local**
6. **JANGAN lupa restart service** setelah deploy

---

## 🔍 Troubleshooting

### Error di Production tapi OK di Local:

**1. Check Environment Variables:**
```bash
# Di VPS
cat /opt/markplus/mcoder-markplus/.env
# Pastikan semua key ada dan benar
```

**2. Check Dependencies:**
```bash
# Di VPS
source venv/bin/activate
pip list
# Bandingkan dengan lokal: pip freeze > requirements.txt
```

**3. Check Logs:**
```bash
# Application logs
tail -100 /var/log/mcoder/gunicorn.log

# Nginx logs
tail -100 /var/log/nginx/mcoder-error.log
```

**4. Check File Permissions:**
```bash
# Harus writable untuk uploads, logs, database
ls -la /opt/markplus/mcoder-markplus/files/
ls -la /opt/markplus/mcoder-markplus/instance/
```

**5. Check Python Version:**
```bash
# Di VPS
python --version
# Harus sama dengan lokal (3.12.3)
```

---

## 📝 Deployment Checklist

Sebelum deploy ke production:

- [ ] Code tested locally
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] `.env` updated if needed
- [ ] `requirements.txt` updated if new packages
- [ ] Committed with clear message
- [ ] Pushed to GitHub
- [ ] Backup production database (if major changes)
- [ ] Pull on production
- [ ] Run migrations (if any)
- [ ] Restart service
- [ ] Check logs for errors
- [ ] Test on https://m-coder.flazinsight.com
- [ ] Monitor for 5-10 minutes

---

## 🚀 Next Steps

1. **Setup GitHub Repository** (5 menit)
2. **Create `.gitignore`** (2 menit)
3. **Push lokal code ke GitHub** (5 menit)
4. **Setup Git di VPS** (10 menit)
5. **Test deploy workflow** (10 menit)
6. **Create deploy scripts** (5 menit)

**Total setup time: ~40 menit**

Setelah setup, **setiap deployment cuma 2-3 menit!**

---

## 📞 Support

Jika ada masalah:
1. Check logs di VPS
2. Compare `.env` files
3. Check Git status: `git status`, `git log`
4. Rollback if needed: `git reset --hard HEAD~1`
5. Contact DevOps if service down

---

**Last Updated**: December 26, 2025  
**Maintainer**: MarkPlus Indonesia IT Team
