# 🚀 M-Coder Deployment - Quick Start Guide
## Setup di VPS Hostinger dengan Existing Apps

---

## 📊 **CURRENT VPS STATUS:**

**Installed:**
- Ubuntu 24.04
- Nginx (running, managing SSL)
- Python 3.12.3  
- Node.js v20.19.5 + PM2
- Existing apps: orange-survey, suharyadi.com

**M-Coder Will Use:**
- Port: 8000 (Gunicorn, internal only)
- Domain: mcoder.yourdomain.com (atau subdomain pilihan Anda)
- Location: `/opt/markplus/mcoder/`
- Process Manager: Supervisor
- Web Server: Nginx (reverse proxy)

---

## 🎯 **DEPLOYMENT STEPS:**

### **STEP 1: Prepare Files di Windows**

```powershell
# 1. Compress project (exclude unnecessary files)
cd "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding"

# Create archive (exclude cache, database, logs)
$exclude = @('__pycache__', '*.pyc', 'instance', 'venv', 'files/uploads', 'test_*', 'node_modules')
Compress-Archive -Path * -DestinationPath mcoder-deploy.zip -Force

# 2. Upload ke VPS
scp mcoder-deploy.zip root@145.79.10.104:/opt/markplus/mcoder/
scp quick-setup.sh root@145.79.10.104:/opt/markplus/
```

### **STEP 2: SSH ke VPS dan Run Setup**

```bash
# Login ke VPS
ssh root@145.79.10.104

# Run quick setup
cd /opt/markplus
chmod +x quick-setup.sh
bash quick-setup.sh

# Extract project
cd /opt/markplus/mcoder
unzip mcoder-deploy.zip
rm mcoder-deploy.zip

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### **STEP 3: Configure Environment**

```bash
cd /opt/markplus/mcoder

# Copy production environment template
cp .env.production .env

# Edit .env
nano .env

# Update these values:
# SECRET_KEY - generate: python -c "import secrets; print(secrets.token_hex(32))"
# OPENAI_API_KEY - your API key
# KOBO_API_TOKEN - your token
# BREVO_API_KEY - your email key
# PRODUCTION_DOMAIN - https://mcoder.yourdomain.com

# Save: Ctrl+X, Y, Enter
```

### **STEP 4: Initialize Application**

```bash
cd /opt/markplus/mcoder
source venv/bin/activate

# Create required directories
mkdir -p instance files/uploads/logos files/logs app/static

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized')"

# Create admin user
python setup_admin.py

# Generate favicon
python generate_favicon.py

# Test app locally
python run_app.py
# If OK, press Ctrl+C to stop
```

### **STEP 5: Configure Supervisor**

```bash
# Copy supervisor config
cp /opt/markplus/mcoder/supervisor.conf /etc/supervisor/conf.d/mcoder.conf

# Edit paths if needed
nano /etc/supervisor/conf.d/mcoder.conf

# Update Supervisor
supervisorctl reread
supervisorctl update

# Start M-Coder
supervisorctl start mcoder

# Check status
supervisorctl status mcoder
# Should show: RUNNING
```

### **STEP 6: Configure Nginx**

```bash
# Copy nginx config
cp /opt/markplus/mcoder/nginx.conf /etc/nginx/sites-available/mcoder

# Edit domain name
nano /etc/nginx/sites-available/mcoder
# Change: yourdomain.com → mcoder.yourdomain.com (or your chosen subdomain)

# Enable site
ln -s /etc/nginx/sites-available/mcoder /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

### **STEP 7: Point Domain**

**Di Hostinger Domain Panel:**
1. Login → Domains → DNS/Name Servers
2. Add A Record:
   - Type: A
   - Name: mcoder (for mcoder.yourdomain.com)
   - Points to: 145.79.10.104
   - TTL: 3600
3. Save
4. Wait 10-30 minutes for DNS propagation

**Test DNS:**
```bash
# From VPS or your computer
nslookup mcoder.yourdomain.com
# Should return: 145.79.10.104
```

### **STEP 8: Install SSL Certificate**

```bash
# Install Certbot (if not already)
apt install -y certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d mcoder.yourdomain.com

# Follow prompts:
# - Enter email
# - Agree to Terms
# - Choose redirect HTTP→HTTPS (option 2)

# Test SSL renewal
certbot renew --dry-run

# Uncomment HTTPS block in nginx config
nano /etc/nginx/sites-available/mcoder
# Uncomment the server block for SSL (lines after "# HTTPS Configuration")

# Reload Nginx
nginx -t && systemctl reload nginx
```

### **STEP 9: Verify Deployment**

```bash
# 1. Check application status
supervisorctl status mcoder
# Should show: RUNNING

# 2. Check Nginx
systemctl status nginx
# Should show: active (running)

# 3. Check logs
tail -50 /var/log/mcoder/gunicorn.log

# 4. Test HTTP (before SSL)
curl -I http://mcoder.yourdomain.com

# 5. Test HTTPS (after SSL)
curl -I https://mcoder.yourdomain.com

# 6. Test endpoints
curl https://mcoder.yourdomain.com/favicon.ico
curl https://mcoder.yourdomain.com/og-image.png

# 7. Open in browser
https://mcoder.yourdomain.com
```

---

## 📁 **FINAL DIRECTORY STRUCTURE:**

```
/opt/markplus/
├── mcoder/                          ← M-Coder Platform
│   ├── app/                         ← Flask application
│   ├── instance/                    ← SQLite database
│   │   └── users.db
│   ├── files/                       ← Upload & output
│   │   ├── uploads/logos/
│   │   ├── logs/
│   │   └── output/
│   ├── venv/                        ← Python virtual environment
│   ├── .env                         ← Production config
│   ├── gunicorn.conf.py
│   ├── supervisor.conf
│   ├── nginx.conf
│   └── requirements.txt
│
├── twitter-analytics/               ← Existing app (keep)
└── youtube-analytics/               ← Existing app (keep)

/var/www/
├── orange-survey-backend/           ← Node.js app (keep)
├── orange-survey-frontend/          ← Frontend (keep)
└── suharyadi.com/                   ← Website (keep)

/var/log/
└── mcoder/                          ← M-Coder logs
    ├── gunicorn.log
    ├── error.log
    └── access.log

/etc/nginx/sites-enabled/
├── orange.flazinsight.com          ← Existing (keep)
├── suharyadi.com                   ← Existing (keep)
└── mcoder                          ← NEW!

/etc/supervisor/conf.d/
└── mcoder.conf                     ← NEW!
```

---

## 🔄 **UPDATE DEPLOYMENT (Future Updates):**

```bash
# 1. SSH to VPS
ssh root@145.79.10.104

# 2. Backup current version
cd /opt/markplus
tar -czf mcoder-backup-$(date +%Y%m%d-%H%M%S).tar.gz mcoder/

# 3. Navigate to app directory
cd /opt/markplus/mcoder

# 4. Activate virtual environment
source venv/bin/activate

# 5. Pull updates (if using Git)
# git pull origin main

# Or upload new files via SCP
# scp -r updated-files/* root@145.79.10.104:/opt/markplus/mcoder/

# 6. Update dependencies
pip install -r requirements.txt --upgrade

# 7. Database migration (if needed)
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 8. Restart application
supervisorctl restart mcoder

# 9. Reload Nginx (if config changed)
nginx -t && systemctl reload nginx

# 10. Verify
supervisorctl status mcoder
tail -50 /var/log/mcoder/gunicorn.log
curl -I https://mcoder.yourdomain.com
```

---

## 🛠️ **MANAGEMENT COMMANDS:**

### Start/Stop/Restart:
```bash
supervisorctl start mcoder
supervisorctl stop mcoder
supervisorctl restart mcoder
supervisorctl status mcoder
```

### View Logs:
```bash
# Application logs
tail -f /var/log/mcoder/gunicorn.log

# Error logs
tail -f /var/log/mcoder/error.log

# Nginx access
tail -f /var/log/nginx/mcoder-access.log

# All logs at once
tail -f /var/log/mcoder/*.log
```

### Monitor Resources:
```bash
# Process list
ps aux | grep gunicorn

# Memory usage
free -h

# Disk usage
df -h

# Top processes
htop
```

---

## 🔒 **SECURITY CHECKLIST:**

- [ ] Strong passwords for admin user
- [ ] `.env` file permissions: `chmod 600 .env`
- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] Regular backups setup
- [ ] Monitor logs for suspicious activity
- [ ] Keep system updated: `apt update && apt upgrade`

---

## 📊 **PORTS ALLOCATION:**

```
Port 80/443  → Nginx (reverse proxy)
Port 3000    → PM2 (orange-survey-backend)
Port 8000    → Gunicorn (M-Coder) ← Internal only
```

---

## 🎯 **SUBDOMAIN RECOMMENDATIONS:**

Option 1: **mcoder.yourdomain.com** ← Professional
Option 2: **survey-ai.yourdomain.com**
Option 3: **classification.yourdomain.com**

---

## ✅ **POST-DEPLOYMENT CHECKLIST:**

- [ ] Application accessible via https://mcoder.yourdomain.com
- [ ] Login page works
- [ ] Admin can upload logo
- [ ] Favicon visible
- [ ] Open Graph preview works
- [ ] Classification works
- [ ] File upload works
- [ ] SSL valid
- [ ] Logs clean
- [ ] Performance good

---

## 📞 **TROUBLESHOOTING:**

### Issue: Can't connect to site
```bash
# Check Nginx
systemctl status nginx

# Check M-Coder
supervisorctl status mcoder

# Check ports
netstat -tulpn | grep -E ':(80|443|8000)'
```

### Issue: 502 Bad Gateway
```bash
# Check if Gunicorn running
ps aux | grep gunicorn

# Restart M-Coder
supervisorctl restart mcoder

# Check logs
tail -50 /var/log/mcoder/gunicorn.log
```

### Issue: Permission errors
```bash
chown -R root:root /opt/markplus/mcoder
chmod 755 /opt/markplus/mcoder
chmod 600 /opt/markplus/mcoder/.env
```

---

**Ready to deploy? Follow the steps starting from STEP 1!** 🚀
