# Quick Start for New AI Agent

> **Untuk Agent Baru**: Baca file ini untuk langsung paham project status tanpa scan banyak file!

---

## 🎯 READ THESE 3 FILES IN ORDER (Total 5 menit)

### 1. AI_AGENT_CONTEXT.md (PALING PENTING)
**Location**: `.github/AI_AGENT_CONTEXT.md`
**Isi**:
- ✅ Latest status update (Jan 14, 2026)
- ✅ Database credentials (development + production)
- ✅ Common commands (query users, restart services, etc)
- ✅ Anti-hallucination rules (CRITICAL!)
- ✅ Debugging checklist

**Baca lines**: 1-150 (paling penting)

### 2. PROJECT_OVERVIEW.md (Architecture & Roadmap)
**Location**: `PROJECT_OVERVIEW.md`
**Isi**:
- Purpose aplikasi (M-Code Pro)
- Tech stack (Flask + PostgreSQL + Redis + Celery)
- Current status (what's working, what's pending)
- Development roadmap (Phase 1-4)

**Baca lines**: 1-200 (overview) + 400-605 (roadmap)

### 3. CHANGELOG.md (Recent Changes)
**Location**: `CHANGELOG.md`
**Isi**:
- Last 30 days changes (descending order)
- Bug fixes history
- Feature implementations

**Baca lines**: 1-150 (last 2 weeks)

---

## ⚡ SUPER QUICK SUMMARY (1 menit)

### What is M-Code Pro?
- **Purpose**: AI-powered survey response classification (open-ended questions)
- **Users**: MarkPlus Indonesia internal team
- **Tech**: Flask 3.1 + PostgreSQL 16 + OpenAI GPT-4o-mini
- **Environment**: Docker (dev) + VPS Ubuntu (production)

### Current Status (Jan 14, 2026)
| Feature | Status |
|---------|--------|
| ✅ Classification Engine | Working (pure + semi open-ended) |
| ✅ User Authentication | Working (3 roles: User, Admin, Super Admin) |
| ✅ Dashboard with Real Data | **JUST COMPLETED TODAY** |
| ✅ Mobile Responsive | Working (global Force Fit CSS) |
| ✅ Results & Analytics | Working (job history, download, search) |
| ✅ PostgreSQL Backend | Working (16 users synced) |
| ✅ Docker Development | Working (4 containers healthy) |
| 🔄 Tabulation Module | Planned (Q1 2026) |
| 🔄 Multi-label Classification | Planned (Phase 2) |

### Database Schema (6 tables)
```
1. users                    - 16 accounts
2. companies                - Company data
3. classification_jobs      - Job history (UUID primary key)
4. classification_variables - Per-variable results (total_responses column!)
5. otp_tokens               - Email verification
6. system_settings          - App settings
```

### Key Files You'll Work With
```
app/
├── routes.py              - Main routes (dashboard, classify, results)
├── models.py              - Database models (User, ClassificationJob, etc)
├── templates/
│   ├── dashboard.html     - Dashboard with charts (BARU UPDATE HARI INI)
│   ├── base.html          - Base template (global mobile CSS)
│   └── results.html       - Job history list
excel_classifier.py        - Classification engine
openai_classifier.py       - OpenAI GPT-4o-mini integration
```

---

## 🔥 MOST IMPORTANT FACTS (MUST KNOW!)

### 1. Database Architecture
- ❌ **NOT SQLite anymore** - Migrated to PostgreSQL on 2025-12-28
- ✅ Development: `mcoder_development` (Docker localhost:5432)
- ✅ Production: `mcoder_production` (VPS 145.79.10.104:5432)

### 2. Job ID Format
- ✅ `job_id` is **UUID string** (e.g., `56d6edb9-5efe-4d28-be5b-716ed8f6fcc8`)
- ❌ NOT integer!
- ✅ Routes MUST use `<job_id>` NOT `<int:job_id>`

### 3. Total Responses & Variables
- ❌ ClassificationJob.total_responses is **@property method** (cannot query directly!)
- ✅ Query from `ClassificationVariable.total_responses` column instead
- ✅ Use JOIN with ClassificationJob for user filtering

**Correct Query:**
```python
# ✅ CORRECT
total_responses = db.session.query(
    func.sum(ClassificationVariable.total_responses)
).join(ClassificationJob).filter(
    ClassificationJob.user_id == user_id
).scalar()

# ❌ WRONG (will error: "can't adapt type 'property'")
total_responses = db.session.query(
    func.sum(ClassificationJob.total_responses)  # This is @property!
).filter(...)
```

### 4. Mobile Responsive
- ✅ Global CSS in `base.html` lines 638-806
- ✅ Force Fit approach: `max-width: 100vw`, `overflow-x: hidden`
- ✅ Breakpoints: 768px (tablet), 576px (mobile)

### 5. Common Commands
```bash
# Restart Flask (after code changes)
docker-compose restart flask-app

# Check logs
docker-compose logs flask-app --tail=30

# Query users (development)
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT id, email, is_admin FROM users;"

# Container status
docker-compose ps
```

---

## 🚨 COMMON MISTAKES TO AVOID

### ❌ Don't Do This:
1. Assume SQLite database (it's PostgreSQL now!)
2. Use `<int:job_id>` in routes (job_id is UUID string)
3. Query `ClassificationJob.total_responses` directly (it's @property, use ClassificationVariable table)
4. Add new packages without updating `requirements.txt`
5. Deploy without testing in Docker first

### ✅ Always Do This:
1. Check environment (dev vs production) before commands
2. Use `<job_id>` for routes (supports UUID)
3. Query ClassificationVariable table for aggregations
4. Update `requirements.txt` when adding packages
5. Test in Docker before deployment

---

## 📞 NEXT STEPS FOR NEW AGENT

### Step 1: Read Context (5 menit)
- [ ] Read AI_AGENT_CONTEXT.md lines 1-150
- [ ] Read PROJECT_OVERVIEW.md lines 1-200
- [ ] Read CHANGELOG.md lines 1-150

### Step 2: Verify Environment (2 menit)
```bash
# Check containers
docker-compose ps

# Check database
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "\dt"

# Check users
docker exec mcoder-postgres psql -U mcoder_dev -d mcoder_development -c "SELECT COUNT(*) FROM users;"
```

### Step 3: Test Dashboard (1 menit)
- Open http://localhost:5000/dashboard
- Login dengan: haryadi@markplusinc.com / (password dari user)
- Verify KPI cards show real numbers (not 40,000, 215,000)

### Step 4: Ready to Work! 🚀
- You now understand the project architecture
- You know where to find things
- You understand database schema
- You can avoid common mistakes

---

## 💡 PRO TIPS

### When User Asks About Data:
1. **First**, check if data exists in database (query first!)
2. **Never** assume or fabricate data
3. Always show SQL query results as proof

### When Making Changes:
1. **Read** existing code context (5-10 lines before/after)
2. **Test** in Docker before recommending
3. **Update** documentation (CHANGELOG.md) after major changes

### When Debugging:
1. **Check logs** first: `docker-compose logs flask-app --tail=50`
2. **Verify database** connection
3. **Test route** in browser or curl
4. **Read error** message completely (don't guess!)

---

## 📋 CURRENT PRIORITIES (Jan 14, 2026)

### ✅ DONE (Today)
- Dashboard connected to real database
- Mobile responsive global
- Charts updated with real data
- Bug fixes (property query, UUID routes)

### 🔄 IN PROGRESS
- None (stable state)

### 📋 NEXT UP (Future)
- 🔴 Phase 1: Scalability (Redis + Celery) - untuk 20+ concurrent users
- 🟡 Phase 2: UI/UX Modernization - remove menu redundancy, dashboard redesign
- 🟢 Phase 3: Multi-source data support (Excel, CSV, Google Sheets)
- 🔵 Phase 4: Tabulation module (Q1 2026)

See PROJECT_OVERVIEW.md lines 400-605 for detailed roadmap.

---

**Last Updated**: 2026-01-14 00:45 WIB  
**Maintainer**: AI Agent + Human Developer  
**Chat Performance**: Create new chat if lagging (>500 messages)
