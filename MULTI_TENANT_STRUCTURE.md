# Multi-Tenant Structure for M-Coder Platform

## Current vs Recommended Structure

### ❌ Current Structure (Not Multi-Tenant Ready)
```
/opt/markplus/
├── mcoder/                    ← Generic name, not scalable
│   ├── app/
│   ├── instance/users.db
│   ├── .env
│   └── venv/
├── twitter-analytics/
└── youtube-analytics/
```

### ✅ Recommended Structure (Multi-Tenant Ready)
```
/opt/markplus/
├── mcoder-markplus/          ← Instance 1: MarkPlus (Port 8000)
│   ├── app/
│   ├── instance/
│   │   └── users.db          ← Isolated database
│   ├── files/
│   │   ├── uploads/
│   │   ├── output/
│   │   └── logo/
│   ├── venv/                 ← Isolated Python environment
│   ├── .env                  ← MarkPlus API keys
│   ├── gunicorn.conf.py
│   ├── nginx.conf
│   └── supervisor.conf
│
├── mcoder-company2/          ← Instance 2: Future Company (Port 8001)
│   ├── app/                  ← Same codebase
│   ├── instance/
│   │   └── users.db          ← Separate database
│   ├── files/                ← Separate files
│   ├── venv/
│   ├── .env                  ← Different API keys
│   └── configs/
│
├── mcoder-shared/            ← Shared resources (optional)
│   ├── scripts/
│   │   ├── deploy_new_company.sh
│   │   ├── backup_database.sh
│   │   └── update_all_instances.sh
│   └── templates/
│       ├── nginx.conf.template
│       ├── supervisor.conf.template
│       └── .env.template
│
├── twitter-analytics/        ← Existing apps (unchanged)
└── youtube-analytics/
```

---

## Port Allocation Strategy

| Instance | Port (Internal) | Nginx Domain | Purpose |
|----------|----------------|--------------|---------|
| mcoder-markplus | 8000 | mcoder.markplus.co.id | MarkPlus internal |
| mcoder-company2 | 8001 | mcoder.company2.com | Future client |
| mcoder-company3 | 8002 | mcoder.company3.com | Future client |
| orange-survey | 3000 | orange.flazinsight.com | Existing app |

---

## Isolation Guarantees

### ✅ What's Isolated:
1. **Database**: Each instance has own SQLite file in `instance/users.db`
2. **Files**: Uploads, outputs, logos in separate `files/` directory
3. **Configuration**: Each `.env` has different API keys
4. **Virtual Environment**: Separate Python packages (upgrades don't affect others)
5. **Process**: Separate Gunicorn workers managed by Supervisor
6. **Domain**: Different subdomains/domains per instance

### ✅ What's Shared:
1. **Codebase**: Same `app/` folder structure (easier updates)
2. **Nginx**: One Nginx server proxies to all instances
3. **System Packages**: Python 3.12, image libraries (efficient)
4. **SSL Certificates**: Managed centrally via Certbot

---

## Benefits of This Structure

### 🎯 For Current Deployment (MarkPlus Only):
- ✅ Clear naming: `mcoder-markplus` instead of generic `mcoder`
- ✅ Easy to add more instances later
- ✅ Professional structure for future expansion
- ✅ Documentation self-explanatory

### 🚀 For Future Multi-Tenant:
- ✅ Add new company: Copy folder + change port + add nginx config
- ✅ Independent scaling: Each instance can have different resources
- ✅ Security: Complete data isolation between companies
- ✅ Maintenance: Update one, test, then update others
- ✅ Backup: Easy to backup per-company
- ✅ Billing: Track resource usage per instance

---

## Migration Steps (Restructure Current Deployment)

### Step 1: Rename Current Folder
```bash
cd /opt/markplus
mv mcoder mcoder-markplus
```

### Step 2: Update Configuration Files
```bash
cd /opt/markplus/mcoder-markplus

# Update supervisor.conf
sed -i 's|/opt/markplus/mcoder|/opt/markplus/mcoder-markplus|g' supervisor.conf

# Update nginx.conf
sed -i 's|/opt/markplus/mcoder|/opt/markplus/mcoder-markplus|g' nginx.conf

# Update gunicorn.conf.py
sed -i 's|/opt/markplus/mcoder|/opt/markplus/mcoder-markplus|g' gunicorn.conf.py

# Update deploy.sh
sed -i 's|/opt/markplus/mcoder|/opt/markplus/mcoder-markplus|g' deploy.sh
```

### Step 3: Update Supervisor & Nginx
```bash
# Update supervisor config path
cp supervisor.conf /etc/supervisor/conf.d/mcoder-markplus.conf
supervisorctl reread
supervisorctl update

# Update nginx config
cp nginx.conf /etc/nginx/sites-available/mcoder-markplus
rm /etc/nginx/sites-enabled/mcoder  # Remove old symlink
ln -s /etc/nginx/sites-available/mcoder-markplus /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### Step 4: Restart Services
```bash
supervisorctl restart mcoder-markplus
systemctl status nginx
```

### Step 5: Verify
```bash
# Check if app running
curl http://localhost:8000

# Check logs
tail -f /var/log/mcoder/gunicorn.log
```

---

## Deployment Script for New Company

When ready to add new company:

```bash
#!/bin/bash
# File: /opt/markplus/mcoder-shared/scripts/deploy_new_company.sh

COMPANY_NAME=$1
PORT=$2
DOMAIN=$3

# Example: ./deploy_new_company.sh "company2" 8001 "mcoder.company2.com"

# 1. Copy from MarkPlus instance
cp -r /opt/markplus/mcoder-markplus /opt/markplus/mcoder-$COMPANY_NAME

# 2. Clean data
cd /opt/markplus/mcoder-$COMPANY_NAME
rm -rf instance/*.db
rm -rf files/uploads/*
rm -rf files/output/*
rm -rf venv

# 3. Update configs
sed -i "s/8000/$PORT/g" gunicorn.conf.py
sed -i "s/mcoder-markplus/mcoder-$COMPANY_NAME/g" supervisor.conf
sed -i "s/markplus.co.id/$DOMAIN/g" nginx.conf

# 4. Setup environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Initialize database
python setup_admin.py

# 6. Configure services
cp supervisor.conf /etc/supervisor/conf.d/mcoder-$COMPANY_NAME.conf
cp nginx.conf /etc/nginx/sites-available/mcoder-$COMPANY_NAME
ln -s /etc/nginx/sites-available/mcoder-$COMPANY_NAME /etc/nginx/sites-enabled/

# 7. Start services
supervisorctl reread
supervisorctl update
supervisorctl start mcoder-$COMPANY_NAME
systemctl reload nginx

echo "✅ New instance deployed: mcoder-$COMPANY_NAME"
echo "🌐 Domain: $DOMAIN"
echo "🔌 Port: $PORT"
echo "📝 Next: Point DNS A record to VPS IP"
```

---

## Cost & Resource Estimation

### Single VPS (2-core, 2GB RAM):
- ✅ Can handle: 3-5 instances
- Each instance: ~300MB RAM baseline + 200MB per concurrent classification
- Network: Shared bandwidth (sufficient for survey data)

### When to Add More VPS:
- More than 5 companies
- Heavy concurrent usage (100+ users/instance)
- Each company needs dedicated resources for SLA

---

## Security Considerations

### ✅ Already Implemented:
- Database isolation (separate SQLite files)
- File isolation (separate directories)
- Process isolation (separate Gunicorn workers)
- Configuration isolation (separate .env)

### 🔒 Additional Security (If Needed):
1. **User-level isolation**: Create separate Linux users per instance
   ```bash
   useradd -m mcoder-markplus
   useradd -m mcoder-company2
   chown -R mcoder-markplus:mcoder-markplus /opt/markplus/mcoder-markplus
   ```

2. **Firewall rules**: Restrict internal ports
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw deny 8000:8010/tcp  # Internal ports not accessible externally
   ```

3. **SELinux/AppArmor**: Additional kernel-level isolation (advanced)

---

## Backup Strategy (Per Instance)

### Automated Backup Script:
```bash
#!/bin/bash
# File: /opt/markplus/mcoder-shared/scripts/backup_instance.sh

INSTANCE=$1
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/markplus/backups"

mkdir -p $BACKUP_DIR/$INSTANCE

# Backup database
cp /opt/markplus/$INSTANCE/instance/users.db \
   $BACKUP_DIR/$INSTANCE/users_$DATE.db

# Backup files
tar -czf $BACKUP_DIR/$INSTANCE/files_$DATE.tar.gz \
   /opt/markplus/$INSTANCE/files/

# Backup .env (encrypted)
gpg -c /opt/markplus/$INSTANCE/.env \
   -o $BACKUP_DIR/$INSTANCE/env_$DATE.gpg

# Keep only last 7 days
find $BACKUP_DIR/$INSTANCE -mtime +7 -delete

echo "✅ Backup completed: $INSTANCE at $DATE"
```

### Cron Job:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/markplus/mcoder-shared/scripts/backup_instance.sh mcoder-markplus
```

---

## Monitoring (Future)

### Per-Instance Metrics:
- **Resource usage**: RAM, CPU per Gunicorn process
- **API usage**: OpenAI API calls per company
- **Storage**: File uploads size per instance
- **Performance**: Classification speed, response time

### Tools:
- Supervisor status dashboard
- Custom Flask endpoint: `/api/health`
- Log aggregation: Centralized log viewer

---

## Summary Checklist

### ✅ Current State:
- [x] App deployed to `/opt/markplus/mcoder`
- [x] SQLite database isolated
- [x] Configuration in .env
- [x] Gunicorn + Supervisor + Nginx configured

### 🔄 Restructure Tasks:
- [ ] Rename `mcoder` → `mcoder-markplus`
- [ ] Update all config file paths
- [ ] Update Supervisor config name
- [ ] Update Nginx config name
- [ ] Test application still works
- [ ] Create `mcoder-shared/` directory
- [ ] Move deployment scripts to shared/

### 📝 Documentation:
- [ ] Multi-tenant deployment guide
- [ ] New company onboarding process
- [ ] Pricing & contract templates
- [ ] Admin guide for managing multiple instances

---

## Next Steps After Restructuring

1. ✅ **Complete MarkPlus Deployment**
   - Finish Nginx + SSL setup
   - Point domain to VPS
   - Test full workflow
   - Train MarkPlus team

2. 📋 **Prepare for Future Multi-Tenant**
   - Keep `deploy_new_company.sh` script ready
   - Document pricing strategy
   - Prepare contract templates

3. 🚀 **When Company 2 Arrives**
   - Run deployment script (5 minutes)
   - Configure domain DNS
   - Setup SSL certificate
   - Create admin account
   - Train their team

**Estimated Time to Add New Company: 30 minutes**
(10 min deployment + 15 min DNS/SSL + 5 min testing)
