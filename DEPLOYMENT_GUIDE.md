# Phase 1 Deployment Guide
**M-Code Pro - Redis + Celery Implementation**

## 📋 Pre-Deployment Checklist

### Local Development Testing
- [ ] Test Redis connection: `redis-cli ping` → Should return "PONG"
- [ ] Test Celery worker: `python celery_worker.py`
- [ ] Test task submission: Start development server + submit classification
- [ ] Verify progress tracking in Redis: `redis-cli KEYS progress:*`
- [ ] Verify database migration: `python add_task_id_column.py`
- [ ] Test with 2-3 concurrent classifications

### Backup Production
- [ ] Backup PostgreSQL database:
  ```bash
  ssh root@145.79.10.104
  pg_dump -U mcoder_app mcoder_production > /backup/mcoder_$(date +%Y%m%d_%H%M%S).sql
  ```
- [ ] Backup application files:
  ```bash
  tar -czf /backup/mcoder_files_$(date +%Y%m%d_%H%M%S).tar.gz /opt/markplus/mcoder-markplus/files/
  ```

---

## 🚀 Production Deployment Steps

### Step 1: Install Redis (30 minutes)

```bash
# SSH to VPS
ssh root@145.79.10.104

# Install Redis
apt update
apt install redis-server -y

# Configure Redis
nano /etc/redis/redis.conf

# Find and update these settings:
# maxmemory 2gb
# maxmemory-policy allkeys-lru
# save 900 1
# save 300 10
# bind 127.0.0.1 ::1

# Start Redis
systemctl start redis-server
systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG

# Test from Python
python3 << EOF
import redis
r = redis.from_url('redis://localhost:6379/0')
r.set('test', 'hello')
print(r.get('test'))  # Should print: b'hello'
EOF
```

### Step 2: Upload Updated Code (15 minutes)

```powershell
# From local Windows machine
cd "C:\Users\hp\OneDrive - MarkPlus Indonesia ,PT\MARKPLUS\Automation\koding"

# Upload new files
scp requirements.txt root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp celery_app.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp celery_worker.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp -r tasks root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp add_task_id_column.py root@145.79.10.104:/opt/markplus/mcoder-markplus/

# Upload updated files
scp app/models.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/
scp config.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp gunicorn.conf.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
```

### Step 3: Install Python Dependencies (10 minutes)

```bash
# SSH to VPS
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install redis celery kombu

# Verify installation
python -c "import redis; import celery; print('Redis:', redis.__version__); print('Celery:', celery.__version__)"
```

### Step 4: Run Database Migration (5 minutes)

```bash
# Still on VPS
cd /opt/markplus/mcoder-markplus

# Run migration script
python add_task_id_column.py

# Verify column added
python << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('classification_jobs')]
    print('task_id' in columns)  # Should print: True
EOF
```

### Step 5: Update Nginx Configuration (10 minutes)

```bash
# Edit Nginx config
nano /etc/nginx/sites-available/mcoder

# Update timeout settings:
```

```nginx
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    
    # UPDATED: Increase all timeouts to 600s (10 minutes)
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    send_timeout 600s;
    
    # WebSocket support for SSE (Server-Sent Events)
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

```bash
# Test Nginx config
nginx -t

# Reload Nginx
systemctl reload nginx
```

### Step 6: Create Celery Supervisor Config (15 minutes)

```bash
# Create Celery supervisor config
nano /etc/supervisor/conf.d/mcoder-celery.conf
```

```ini
[program:mcoder-celery]
command=/opt/markplus/mcoder-markplus/venv/bin/celery -A celery_app worker --loglevel=info --concurrency=4 -Q classification,default -n worker@%%h
directory=/opt/markplus/mcoder-markplus
user=root
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/mcoder/celery-stdout.log
stderr_logfile=/var/log/mcoder/celery-stderr.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
redirect_stderr=false
environment=PATH="/opt/markplus/mcoder-markplus/venv/bin",REDIS_URL="redis://localhost:6379"
priority=999
```

```bash
# Reload supervisor config
supervisorctl reread
supervisorctl update

# Check Celery worker status
supervisorctl status mcoder-celery
# Should show: RUNNING
```

### Step 7: Update .env File (5 minutes)

```bash
# Edit .env
nano /opt/markplus/mcoder-markplus/.env

# Add Redis URL:
# REDIS_URL=redis://localhost:6379
```

### Step 8: Restart Application (5 minutes)

```bash
# Restart Gunicorn
supervisorctl restart mcoder-markplus

# Restart Celery
supervisorctl restart mcoder-celery

# Check status
supervisorctl status

# Should see both running:
# mcoder-markplus    RUNNING   pid 12345, uptime 0:00:05
# mcoder-celery      RUNNING   pid 12346, uptime 0:00:05
```

---

## ✅ Post-Deployment Testing

### Test 1: Redis Connection
```bash
redis-cli ping
# Expected: PONG

redis-cli KEYS *
# Expected: (empty array) or existing keys
```

### Test 2: Celery Worker
```bash
supervisorctl status mcoder-celery
# Expected: RUNNING

tail -50 /var/log/mcoder/celery-stdout.log
# Should see worker startup messages
```

### Test 3: Classification (Single User)
1. Open browser: https://m-coder.flazinsight.com
2. Login as test user
3. Upload files (kobo + raw)
4. Select 1 variable
5. Click "Start Classification"
6. **Expected**: Task submits instantly, redirects to progress page
7. **Expected**: Progress updates in real-time
8. **Expected**: Classification completes successfully
9. **Expected**: Results downloadable

### Test 4: Progress in Redis
```bash
# While classification is running:
redis-cli KEYS progress:*
# Should show: progress:<job_id>

redis-cli GET progress:<job_id>
# Should show JSON with progress data
```

### Test 5: Concurrent Users (Load Test)
1. Open 3 browser windows (different users if possible)
2. Start classification simultaneously in all 3
3. **Expected**: All 3 progress without blocking each other
4. **Expected**: No errors, no timeouts, no 502
5. **Expected**: All complete successfully

### Test 6: Background Processing
1. Start classification
2. Close browser tab (or logout)
3. Wait 2-3 minutes
4. Login again
5. Go to Results page
6. **Expected**: Classification completed even though browser was closed

---

## 📊 Monitoring Commands

### Check Application Status
```bash
supervisorctl status

# Expected:
# mcoder-celery      RUNNING   pid 12346, uptime 0:10:23
# mcoder-markplus    RUNNING   pid 12345, uptime 0:10:28
```

### Check Redis Status
```bash
redis-cli INFO stats
redis-cli DBSIZE
redis-cli KEYS progress:*
```

### Check Logs
```bash
# Gunicorn logs
tail -f /var/log/mcoder/error.log

# Celery logs
tail -f /var/log/mcoder/celery-stdout.log

# Nginx logs
tail -f /var/log/nginx/error.log
```

### Check Resources
```bash
# Memory usage
free -h

# Disk usage
df -h

# Process list
ps aux | grep -E "(gunicorn|celery|redis)"
```

---

## 🐛 Troubleshooting

### Issue: Celery Worker Not Starting
```bash
# Check logs
cat /var/log/mcoder/celery-stderr.log

# Try starting manually
cd /opt/markplus/mcoder-markplus
source venv/bin/activate
celery -A celery_app worker --loglevel=debug
```

### Issue: Redis Connection Failed
```bash
# Check Redis status
systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis logs
tail -50 /var/log/redis/redis-server.log
```

### Issue: Tasks Not Processing
```bash
# Check Celery worker logs
tail -100 /var/log/mcoder/celery-stdout.log

# Check Redis queue
redis-cli LLEN celery

# Inspect task
redis-cli GET celery-task-meta-<task_id>
```

### Issue: 502 Bad Gateway
```bash
# Check Gunicorn status
supervisorctl status mcoder-markplus

# Check Nginx error logs
tail -50 /var/log/nginx/error.log

# Restart Gunicorn
supervisorctl restart mcoder-markplus
```

---

## 🔄 Rollback Procedure

If deployment fails:

```bash
# Stop new services
supervisorctl stop mcoder-celery

# Restore old code (if needed)
cd /opt/markplus
mv mcoder-markplus mcoder-markplus-new
mv mcoder-markplus-backup mcoder-markplus

# Restore database
psql -U mcoder_app mcoder_production < /backup/mcoder_YYYYMMDD_HHMMSS.sql

# Restore old Gunicorn config
# (workers=1, timeout=300)

# Restart Gunicorn
supervisorctl restart mcoder-markplus

# Test application
curl -I https://m-coder.flazinsight.com
```

---

## 📝 Success Criteria

Phase 1 deployment is successful if:
- [ ] Redis running and accessible
- [ ] Celery worker running with 4 concurrent processes
- [ ] Gunicorn running with 4 workers
- [ ] Single classification completes successfully
- [ ] 3 concurrent classifications work without blocking
- [ ] Background processing works (task survives browser close)
- [ ] No 502 errors
- [ ] Progress tracking works in real-time
- [ ] Results downloadable after completion

---

## 📞 Support

If you encounter issues:
1. Check logs (Gunicorn, Celery, Nginx, Redis)
2. Review SCALABILITY_PLAN.md troubleshooting section
3. Contact developer: haryadi@markplusinc.com / +62 812-8933-008

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Status**: ⏳ Pending / ✅ Success / ❌ Failed  
**Notes**: _____________
