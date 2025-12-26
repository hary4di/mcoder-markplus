# 🚀 M-Coder Platform - VPS Deployment Guide
## Complete Step-by-Step untuk Hostinger VPS + Domain

---

## 📋 **Prerequisites**

### Yang Anda Butuhkan:
- ✅ VPS Hostinger (minimal 2GB RAM, 2 CPU cores)
- ✅ Domain sudah terdaftar (misal: mcoder.yourdomain.com)
- ✅ SSH access ke VPS
- ✅ Root/sudo privileges
- ✅ Source code M-Coder Platform

### Spesifikasi Minimum VPS:
```
CPU: 2 cores
RAM: 2GB (recommended 4GB untuk production)
Storage: 20GB SSD
OS: Ubuntu 20.04/22.04 LTS (recommended)
```

---

## 🎯 **DEPLOYMENT OVERVIEW**

**Stack yang akan di-install:**
```
Ubuntu 22.04 LTS
    ↓
Nginx (Web Server / Reverse Proxy)
    ↓
Gunicorn (WSGI Server)
    ↓
Flask App (M-Coder Platform)
    ↓
Supervisor (Process Manager)
    ↓
PostgreSQL (Optional - bisa pakai SQLite dulu)
```

**Estimasi waktu:** 60-90 menit

---

## 📦 **PART 1: VPS INITIAL SETUP**

### Step 1: Login ke VPS via SSH

```bash
# Dari komputer Windows Anda, buka PowerShell
ssh root@your-vps-ip-address
# Masukkan password yang diberikan Hostinger
```

### Step 2: Update System

```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y build-essential git curl wget vim ufw
```

### Step 3: Create User untuk Aplikasi

```bash
# Create user 'mcoder'
sudo adduser mcoder
# Set password (gunakan password yang kuat!)

# Add to sudo group
sudo usermod -aG sudo mcoder

# Switch to mcoder user
sudo su - mcoder
```

### Step 4: Setup Firewall

```bash
# Exit dari mcoder user ke root
exit

# Allow OpenSSH
sudo ufw allow OpenSSH

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🐍 **PART 2: INSTALL PYTHON & DEPENDENCIES**

### Step 1: Install Python 3.11

```bash
# Add deadsnakes PPA
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
sudo apt install -y python3-pip

# Verify installation
python3.11 --version
```

### Step 2: Install System Dependencies

```bash
# For Pillow (image processing)
sudo apt install -y libjpeg-dev zlib1g-dev

# For PostgreSQL (optional)
# sudo apt install -y postgresql postgresql-contrib libpq-dev

# For other dependencies
sudo apt install -y libssl-dev libffi-dev
```

---

## 📂 **PART 3: UPLOAD & SETUP APPLICATION**

### Option A: Upload via SFTP (Recommended untuk pertama kali)

**Dari Windows (PowerShell):**
```powershell
# Install WinSCP atau FileZilla
# Atau gunakan SCP command:
scp -r "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding" mcoder@your-vps-ip:/home/mcoder/

# Atau compress dulu:
cd "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding"
tar -czf mcoder-app.tar.gz *
scp mcoder-app.tar.gz mcoder@your-vps-ip:/home/mcoder/
```

**Di VPS:**
```bash
# Login as mcoder
sudo su - mcoder

# Extract (jika pakai tar.gz)
cd /home/mcoder
tar -xzf mcoder-app.tar.gz
rm mcoder-app.tar.gz

# Verify files
ls -la
```

### Option B: Clone dari Git (Jika sudah ada repo)

```bash
# Login as mcoder
sudo su - mcoder
cd /home/mcoder

# Clone repository
git clone https://github.com/yourusername/mcoder-platform.git
mv mcoder-platform/* .
rm -rf mcoder-platform
```

### Step 2: Setup Python Virtual Environment

```bash
# Make sure you're in /home/mcoder
cd /home/mcoder

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn
```

### Step 3: Configure Environment Variables

```bash
# Copy production template
cp .env.production .env

# Edit .env file
nano .env

# Update these important values:
# - SECRET_KEY: Generate new: python -c "import secrets; print(secrets.token_hex(32))"
# - OPENAI_API_KEY: Your OpenAI API key
# - KOBO_API_TOKEN: Your Kobo token
# - BREVO_API_KEY: Your Brevo email key
# - PRODUCTION_DOMAIN: https://yourdomain.com

# Save: Ctrl+X, Y, Enter
```

### Step 4: Initialize Database

```bash
# Activate venv if not already
source venv/bin/activate

# Create instance directory
mkdir -p instance

# Initialize database
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized')"

# Create admin user
python setup_admin.py
```

### Step 5: Setup Directory Permissions

```bash
# Create required directories
mkdir -p files/uploads/logos files/uploads/backups
mkdir -p files/logs files/output
mkdir -p app/static

# Set permissions
chmod -R 755 files/
chmod 644 .env

# Generate favicon
python generate_favicon.py
```

### Step 6: Test Application Locally

```bash
# Run Flask development server untuk test
python run_app.py

# Jika berhasil, Ctrl+C untuk stop
```

---

## 🌐 **PART 4: INSTALL & CONFIGURE NGINX**

### Step 1: Install Nginx

```bash
# Exit dari mcoder user
exit

# Install Nginx
sudo apt install -y nginx

# Check status
sudo systemctl status nginx
```

### Step 2: Configure Nginx

```bash
# Copy nginx config
sudo cp /home/mcoder/nginx.conf /etc/nginx/sites-available/mcoder

# Edit config untuk update domain
sudo nano /etc/nginx/sites-available/mcoder

# Ganti semua 'yourdomain.com' dengan domain Anda
# Ganti path jika perlu

# Create symlink
sudo ln -s /etc/nginx/sites-available/mcoder /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 3: Setup Logging Directories

```bash
# Create log directory
sudo mkdir -p /var/log/mcoder

# Set ownership
sudo chown -R mcoder:mcoder /var/log/mcoder
```

---

## 🔧 **PART 5: INSTALL & CONFIGURE GUNICORN + SUPERVISOR**

### Step 1: Install Supervisor

```bash
# Install Supervisor
sudo apt install -y supervisor

# Check status
sudo systemctl status supervisor
```

### Step 2: Configure Supervisor

```bash
# Copy supervisor config
sudo cp /home/mcoder/supervisor.conf /etc/supervisor/conf.d/mcoder.conf

# Edit if needed
sudo nano /etc/supervisor/conf.d/mcoder.conf

# Reload Supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start application
sudo supervisorctl start mcoder

# Check status
sudo supervisorctl status mcoder
```

### Step 3: Verify Application Running

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check logs
sudo tail -f /var/log/mcoder/gunicorn.log

# Test dari curl
curl http://localhost:8000

# Jika sukses, aplikasi sudah running!
```

---

## 🔒 **PART 6: DOMAIN & SSL SETUP**

### Step 1: Point Domain ke VPS

**Di Hostinger Domain Panel:**
```
1. Login ke Hostinger
2. Go to: Domains → Your Domain → DNS/Name Servers
3. Add A Record:
   - Type: A
   - Name: @ (untuk root domain) atau subdomain (untuk mcoder.yourdomain.com)
   - Points to: YOUR_VPS_IP_ADDRESS
   - TTL: 3600
4. Add A Record untuk www (optional):
   - Type: A
   - Name: www
   - Points to: YOUR_VPS_IP_ADDRESS
   - TTL: 3600
5. Save changes
6. Wait 10-30 minutes untuk DNS propagation
```

### Step 2: Test DNS Propagation

```bash
# Dari VPS atau local
nslookup yourdomain.com
# Should return your VPS IP

# Test HTTP access
curl http://yourdomain.com
# Should return your app's HTML
```

### Step 3: Install SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to Terms of Service
# - Choose redirect (2) untuk auto-redirect HTTP to HTTPS

# Test SSL
sudo certbot renew --dry-run

# SSL auto-renewal sudah disetup via cron
```

### Step 4: Update Nginx Configuration

```bash
# Edit nginx config untuk uncomment HTTPS section
sudo nano /etc/nginx/sites-available/mcoder

# Uncomment semua baris di HTTPS server block
# Update domain name

# Test config
sudo nginx -t

# Reload
sudo systemctl reload nginx
```

### Step 5: Test HTTPS

```bash
# Test dari browser
https://yourdomain.com

# Check SSL rating
https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
```

---

## ✅ **PART 7: FINAL VERIFICATION**

### Checklist:

```bash
# 1. Application running
sudo supervisorctl status mcoder
# Should show: RUNNING

# 2. Nginx running
sudo systemctl status nginx
# Should show: active (running)

# 3. Check logs
sudo tail -100 /var/log/mcoder/gunicorn.log
sudo tail -100 /var/log/nginx/mcoder-access.log

# 4. Test endpoints
curl -I https://yourdomain.com
curl -I https://yourdomain.com/favicon.ico
curl -I https://yourdomain.com/og-image.png

# 5. Test login page
# Open browser: https://yourdomain.com
```

### Performance Test:

```bash
# Install Apache Bench (optional)
sudo apt install apache2-utils -y

# Test performance
ab -n 100 -c 10 https://yourdomain.com/
```

---

## 🔄 **PART 8: DEPLOYMENT SCRIPT (UPDATE APP)**

### Make Deployment Script Executable

```bash
# Login as mcoder
sudo su - mcoder

# Make executable
chmod +x deploy.sh

# Edit script untuk update repo URL jika pakai Git
nano deploy.sh
```

### Update Application (Future Updates)

```bash
# Login as mcoder
sudo su - mcoder
cd /home/mcoder

# Run deployment script
./deploy.sh

# Or manually:
source venv/bin/activate
git pull origin main  # Jika pakai Git
pip install -r requirements.txt --upgrade
sudo supervisorctl restart mcoder
sudo systemctl reload nginx
```

---

## 📊 **MONITORING & MAINTENANCE**

### View Logs

```bash
# Application logs
sudo tail -f /var/log/mcoder/gunicorn.log

# Nginx access logs
sudo tail -f /var/log/nginx/mcoder-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/mcoder-error.log

# Supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log
```

### Restart Services

```bash
# Restart application only
sudo supervisorctl restart mcoder

# Restart Nginx
sudo systemctl restart nginx

# Restart Supervisor
sudo systemctl restart supervisor

# Restart all
sudo supervisorctl restart mcoder && sudo systemctl restart nginx
```

### Check Resource Usage

```bash
# CPU & Memory
htop
# or
top

# Disk usage
df -h

# Application process
ps aux | grep gunicorn
```

### Backup Database

```bash
# Create backup script
cat > /home/mcoder/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/mcoder/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/mcoder/instance/users.db $BACKUP_DIR/users_$DATE.db
# Compress old backups
find $BACKUP_DIR -name "*.db" -mtime +7 -exec gzip {} \;
echo "Backup completed: users_$DATE.db"
EOF

# Make executable
chmod +x /home/mcoder/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
# 0 2 * * * /home/mcoder/backup.sh
```

---

## 🔧 **TROUBLESHOOTING**

### Issue 1: Application Not Starting

```bash
# Check Supervisor status
sudo supervisorctl status mcoder

# Check logs
sudo tail -100 /var/log/mcoder/gunicorn.log

# Try starting manually
cd /home/mcoder
source venv/bin/activate
gunicorn -c gunicorn.conf.py run_app:app

# Check for Python errors
python -c "from app import create_app; app = create_app(); print('OK')"
```

### Issue 2: Nginx 502 Bad Gateway

```bash
# Check if Gunicorn is running
ps aux | grep gunicorn

# Check Gunicorn bind address
netstat -tulpn | grep 8000

# Restart application
sudo supervisorctl restart mcoder

# Check Nginx error log
sudo tail -50 /var/log/nginx/mcoder-error.log
```

### Issue 3: Permission Denied

```bash
# Fix ownership
sudo chown -R mcoder:mcoder /home/mcoder
sudo chown -R mcoder:mcoder /var/log/mcoder

# Fix permissions
chmod -R 755 /home/mcoder
chmod 644 /home/mcoder/.env
```

### Issue 4: Domain Not Resolving

```bash
# Check DNS
nslookup yourdomain.com

# Check Nginx config
sudo nginx -t

# Check if port 80/443 open
sudo netstat -tulpn | grep nginx

# Check firewall
sudo ufw status
```

### Issue 5: SSL Certificate Issues

```bash
# Renew manually
sudo certbot renew

# Check certificate expiry
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run
```

---

## 📈 **OPTIMIZATION TIPS**

### 1. Database Optimization (Switch to PostgreSQL)

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE mcoder;
CREATE USER mcoder WITH PASSWORD 'your-strong-password';
GRANT ALL PRIVILEGES ON DATABASE mcoder TO mcoder;
\q

# Update .env
DATABASE_URL=postgresql://mcoder:password@localhost/mcoder

# Migrate data (if needed)
# ...then restart app
```

### 2. Redis Cache (untuk session)

```bash
# Install Redis
sudo apt install -y redis-server

# Update requirements.txt
echo "redis>=4.5.0" >> requirements.txt
pip install redis

# Update Flask config untuk use Redis session
```

### 3. Nginx Caching

```bash
# Add to nginx config
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;

# In location block:
proxy_cache my_cache;
proxy_cache_valid 200 1h;
```

---

## 🎉 **POST-DEPLOYMENT CHECKLIST**

- [ ] Application accessible via https://yourdomain.com
- [ ] Login page works
- [ ] Admin can upload logo
- [ ] Favicon visible in browser tab
- [ ] Open Graph preview works (test in WhatsApp)
- [ ] Classification functionality works
- [ ] File upload works (test with sample Excel)
- [ ] Email OTP works (if configured)
- [ ] SSL certificate valid (check browser padlock)
- [ ] Logs readable and no errors
- [ ] Backups configured
- [ ] Monitoring setup (optional)

---

## 📞 **SUPPORT & MAINTENANCE**

### Regular Maintenance Tasks:

**Daily:**
- Check error logs
- Monitor disk space

**Weekly:**
- Review application logs
- Check SSL certificate expiry (auto-renewed)
- Test backup restoration

**Monthly:**
- Update system packages
- Review security updates
- Performance optimization

### Useful Commands:

```bash
# Quick health check
sudo supervisorctl status && sudo systemctl status nginx && df -h

# View all logs at once
sudo tail -f /var/log/mcoder/gunicorn.log /var/log/nginx/mcoder-error.log

# Restart everything
sudo supervisorctl restart mcoder && sudo systemctl restart nginx
```

---

## 🔐 **SECURITY BEST PRACTICES**

1. **Change default SSH port**
2. **Disable root login via SSH**
3. **Use SSH keys instead of password**
4. **Keep system updated**
5. **Regular backups**
6. **Monitor logs for suspicious activity**
7. **Use strong passwords**
8. **Enable Fail2Ban** (optional)

---

**Last Updated:** December 26, 2025  
**Version:** 1.0  
**Support:** Contact IT team jika ada issue

**GOOD LUCK WITH YOUR DEPLOYMENT! 🚀**
