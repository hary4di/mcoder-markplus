# AI Agent Context - M-Code Pro

> **CRITICAL REFERENCE** untuk AI assistant (GitHub Copilot, Claude, GPT-4)  
> **Selalu baca file ini PERTAMA** sebelum memberikan saran atau melakukan perubahan
> **LAST UPDATE**: 2026-01-14 00:45 WIB

---

## 📌 LATEST STATUS (Jan 14, 2026) - READ THIS FIRST!

### ✅ COMPLETED TODAY: Dashboard Real Data Implementation
**Achievement**: Dashboard 100% connected to PostgreSQL database with live metrics
**Impact**: No more hardcoded values - all data real-time dari database

**What Changed:**
1. ✅ Backend queries implemented (6+ SQLAlchemy queries in app/routes.py)
2. ✅ KPI cards updated (total classifications, responses, active jobs, variables)
3. ✅ Trend calculations (7-day percentage changes dengan arrows)
4. ✅ Recent Projects table (dynamic loop dari database)
5. ✅ Charts connected (Area Chart 30-day history, Donut Chart pure vs semi)
6. ✅ Bug fixes:
   - Fixed "can't adapt type 'property'" error (query ClassificationVariable table, not @property)
   - Fixed "invalid literal for int()" error (change `<int:job_id>` to `<job_id>` untuk UUID)
7. ✅ Mobile responsive global (Force Fit CSS di base.html)
8. ✅ Sidebar redesigned (Clean White floating theme)

**Files Modified Today:**
- `app/routes.py` - Lines 63-219 (Dashboard route dengan 156 lines queries)
- `app/templates/dashboard.html` - KPI cards, Recent Projects table, Charts
- `app/templates/base.html` - Global mobile CSS (lines 638-806)
- `CHANGELOG.md` - Updated dengan progress hari ini

**Testing:**
- ✅ Flask restarted 3x tanpa error
- ✅ Dashboard accessible di http://localhost:5000/dashboard
- ✅ All metrics working with real data
- ✅ Mobile responsive confirmed

---

## 🚨 ANTI-HALLUCINATION RULES

### Rule #1: Always Check Environment First
```bash
# Development (Docker)?
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT current_database();"

# Production (VPS)?
ssh root@145.79.10.104 "PGPASSWORD=MarkPlus25 psql -U mcoder_app -d mcoder_production -c 'SELECT current_database();'"
```

**NEVER assume:**
- ❌ SQLite masih digunakan (migrated to PostgreSQL on 2025-12-28)
- ❌ Database di production sama dengan development
- ❌ Users table kosong (ada 16 users dari production)

### Rule #2: Database Schema Knowledge

**6 Tables Always Present:**
```
1. users              - 16 accounts (haryadi@markplusinc.com = Super Admin)
2. companies          - Company data (foreign key untuk users)
3. classification_jobs - Job history dengan UUID
4. classification_variables - Per-variable results
5. otp_tokens         - Email verification tokens
6. system_settings    - App configuration (Brevo API keys, etc)
```

**To verify schema:**
```bash
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "\dt"
```

### Rule #3: Credentials Reference

| Environment | Database | User | Password | Host |
|-------------|----------|------|----------|------|
| **Development** | mcoder_development | mcoder_dev | DevPassword123 | localhost:5432 |
| **Production** | mcoder_production | mcoder_app | MarkPlus25 | 145.79.10.104:5432 |

**Container Names (Development):**
- `mcoder-postgres` - PostgreSQL 16-alpine
- `mcoder-redis` - Redis 7-alpine
- `mcoder-flask` - Flask app
- `mcoder-celery` - Background worker

### Rule #4: Required Dependencies

**CRITICAL**: Flask cannot start without PostgreSQL driver
```python
# requirements.txt MUST include:
psycopg2-binary>=2.9.9
```

**To verify:**
```bash
cat requirements.txt | grep psycopg2
```

### Rule #5: Configuration Files

**DATABASE_URL in 3 locations:**
1. `.env` - Used by Flask when running locally without Docker
2. `docker-compose.yml` (flask-app service) - Used by Flask in Docker
3. `docker-compose.yml` (celery-worker service) - Used by Celery

**Format:**
```
# Development (Docker)
DATABASE_URL=postgresql://mcoder_dev:DevPassword123@postgres:5432/mcoder_development
# Note: "postgres" is Docker service name, NOT "localhost"

# Production (VPS)
DATABASE_URL=postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production
# Note: "localhost" because psql runs on same VPS as Flask
```

---

## 📋 COMMON TASKS (Copy-Paste Ready)

### Query Users in Development
```bash
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT id, username, email, full_name, is_admin FROM users ORDER BY id;"
```

### Query Users in Production
```bash
ssh root@145.79.10.104 "PGPASSWORD=MarkPlus25 psql -U mcoder_app -d mcoder_production -c 'SELECT id, username, email, full_name, is_admin FROM users ORDER BY id;'"
```

### Sync Data from Production to Development
```bash
# 1. Dump companies (foreign key dependency)
ssh root@145.79.10.104 "PGPASSWORD=MarkPlus25 pg_dump -U mcoder_app -d mcoder_production -t companies --data-only --column-inserts" > production_companies.sql

# 2. Import companies
cat production_companies.sql | docker exec -i mcoder-postgres psql -U mcoder_dev -d mcoder_development

# 3. Dump users
ssh root@145.79.10.104 "PGPASSWORD=MarkPlus25 pg_dump -U mcoder_app -d mcoder_production -t users --data-only --column-inserts" > production_users.sql

# 4. Import users
cat production_users.sql | docker exec -i mcoder-postgres psql -U mcoder_dev -d mcoder_development
```

### Check Docker Services
```bash
docker-compose ps
# Expected: All "Up" or "Up (healthy)"
```

### View Flask Logs
```bash
docker-compose logs flask-app --tail=20
# Check for "ModuleNotFoundError" or database connection errors
```

### Restart Services
```bash
docker-compose restart flask-app celery-worker
```

### Rebuild After requirements.txt Changes
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 🔍 DEBUGGING CHECKLIST

When user reports error, check in this order:

### 1. Which Environment?
- [ ] Development (localhost:5000, Docker)
- [ ] Production (m-coder.flazinsight.com, VPS)

### 2. Service Status
```bash
docker-compose ps
# Look for "Restarting" or "Exit 1"
```

### 3. Flask Logs
```bash
docker-compose logs flask-app --tail=50
# Common errors:
# - ModuleNotFoundError: No module named 'psycopg2' → Add psycopg2-binary to requirements.txt
# - FATAL: no pg_hba.conf entry → Check DATABASE_URL points to correct host
# - relation "users" does not exist → Run flask db upgrade
```

### 4. PostgreSQL Connection
```bash
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT 1;"
# Should return: 1
```

### 5. Database Has Data?
```bash
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT COUNT(*) FROM users;"
# Should return: 16 (or more)
```

---

## 🎯 PROJECT CONTEXT

### Current State (2026-01-12)
- ✅ Docker environment working (PostgreSQL 16 + Redis 7)
- ✅ 16 users migrated from production
- ✅ Dashboard redesigned (ApexCharts, world-class analytics)
- ✅ Login working with production credentials
- 🔄 Testing phase: Dashboard with PostgreSQL backend

### Tech Stack
- **Backend**: Flask 3.1 + Python 3.11
- **Database**: PostgreSQL 16 (migrated from SQLite on 2025-12-28)
- **Queue**: Redis 7 + Celery 5.6
- **Frontend**: Bootstrap 5 + ApexCharts 3.x
- **AI**: OpenAI GPT-4o-mini (classification engine)

### Key Files
- `PROJECT_OVERVIEW.md` - Master documentation (605 lines)
- `CHANGELOG.md` - Change history with dates
- `docker-compose.yml` - Service definitions
- `requirements.txt` - Python dependencies (MUST include psycopg2-binary)
- `config.py` - Loads .env via python-dotenv
- `.env` - Environment variables (DATABASE_URL, OPENAI_API_KEY, etc)

### Recent Changes (Last 48 hours)
1. Dashboard redesign with ApexCharts (world-class analytics)
2. PostgreSQL driver installed (psycopg2-binary)
3. Database migration from production (16 users + companies)
4. Docker environment fully operational
5. Login working, ready for testing

---

## ⚠️ WHAT NOT TO DO

### Never Suggest These (Causes Errors):
❌ "Use SQLite for simplicity" - Project requires PostgreSQL for production parity
❌ "Connect to production database for testing" - Security risk, use development Docker
❌ "Install psycopg2 (without -binary)" - Requires PostgreSQL development headers
❌ "Change DATABASE_URL to localhost in docker-compose.yml" - Use service name "postgres"
❌ "Assume users table is empty" - 16 users already exist
❌ "Hardcode passwords in code" - Always use environment variables

### Always Do These:
✅ Check if dependency exists in requirements.txt before suggesting install
✅ Verify environment (development vs production) before commands
✅ Include complete code context (3-5 lines before/after) in edits
✅ Test suggested commands in development first
✅ Document breaking changes in CHANGELOG.md
✅ Update PROJECT_OVERVIEW.md when architecture changes

---

## 📞 ESCALATION

If user reports:
- "Invalid email or password" → Check users table has data (16 users expected)
- "ModuleNotFoundError: psycopg2" → Add psycopg2-binary to requirements.txt
- "FATAL: no pg_hba.conf entry" → DATABASE_URL pointing to wrong host
- "ERR_EMPTY_RESPONSE" → Flask crashed, check logs with `docker-compose logs flask-app`
- "502 Bad Gateway" (production only) → Check Gunicorn/Supervisor on VPS

---

**Last Updated**: 2026-01-12  
**Maintainer**: AI Agent + Human Developer  
**Status**: ✅ Production Ready (Development environment mirroring production)
