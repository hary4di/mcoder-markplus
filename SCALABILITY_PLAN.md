# M-Code Pro - Scalability & Modernization Plan
**Date**: January 8, 2026  
**Target**: Support 20+ concurrent users, Modern UI/UX, Multi-source data support

---

## 🎯 **PROBLEMS IDENTIFIED**

### 1. **Scalability Issues** 🔴 CRITICAL
**Current State**:
- Gunicorn: 1 worker only (in-memory progress tracking)
- 12 concurrent users = crashes, errors, stuck processes
- Classification blocks request thread (user must keep browser open)

**Impact**:
- Cannot scale beyond 5-10 users
- Poor user experience (macet, error)
- Production instability

### 2. **UI/UX Issues** 🟡 HIGH
**Current State**:
- Menu redundancy: "Start Classification" menu not needed
- Navigation: 3 clicks to start classification (Dashboard → Classify → Upload)
- Not intuitive for new users
- No visual feedback for background tasks

**Impact**:
- User confusion
- Inefficient workflow
- Hard to expand (tabulation, non-Kobo sources)

### 3. **502 Bad Gateway** 🔴 CRITICAL
**Current State**:
- Nginx timeout (likely 60s default)
- Gunicorn timeout: 300s but conflicts with Nginx
- View result page crashes after classification

**Impact**:
- Users cannot see results
- Data loss perception
- Production unusable

---

## 🚀 **SOLUTION ARCHITECTURE**

### **Phase 1: Immediate Fixes** (Week 1 - Jan 8-12, 2026)
**Goal**: Make production stable for 20+ users

#### 1.1 Implement Celery + Redis
**Why**: Proper background task queue, industry standard
- **Redis**: Message broker, progress tracking, session storage
- **Celery**: Distributed task queue (async classification)
- **Benefit**: Classification runs independent of HTTP request

**Technical Changes**:
```
app/
├── celery_app.py          # NEW - Celery initialization
├── tasks/                 # NEW - Celery tasks
│   ├── __init__.py
│   ├── classification.py  # Classification as Celery task
│   └── progress.py        # Progress tracking with Redis
├── models.py              # Add task_id field to ClassificationJob
└── routes.py              # Submit classification → Celery task
```

**Infrastructure**:
- Install Redis on VPS
- Configure Celery workers (4-8 workers recommended)
- Update Gunicorn to 4+ workers (no longer limited by in-memory)

#### 1.2 Fix Nginx Timeout
```nginx
# /etc/nginx/sites-available/mcoder
location / {
    proxy_connect_timeout 600s;
    proxy_send_timeout 600s;
    proxy_read_timeout 600s;
    send_timeout 600s;
}
```

#### 1.3 Database Connection Pool
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,        # Up from default 5
    'max_overflow': 40,     # Handle burst traffic
    'pool_pre_ping': True,  # Check connection before use
    'pool_recycle': 3600    # Recycle after 1 hour
}
```

**Expected Outcome**:
- ✅ Support 20+ concurrent users
- ✅ Classification continues if user closes browser
- ✅ No more 502 errors
- ✅ Stable production environment

**Time Estimate**: 2-3 days
**Deployment**: Requires VPS maintenance window (2-3 hours downtime)

---

### **Phase 2: UI/UX Redesign** (Week 2 - Jan 13-19, 2026)
**Goal**: Simplify navigation, modern interface, intuitive workflow

#### 2.1 Navigation Redesign
**Current**:
```
Dashboard → Start Classification → Upload Files → Select Variables → Run
                (redundant)
```

**Proposed**:
```
Dashboard (with quick action cards)
├─ Upload & Classify  ← Direct action
├─ Results History    ← View past jobs
├─ Analytics          ← Super admin only
└─ Settings
```

**Dashboard Cards** (Hero Section):
1. **Upload New Dataset** - Primary CTA, large card with icon
2. **Recent Classifications** - 5 latest jobs with status badges
3. **Quick Stats** - Files processed, variables, success rate
4. **Tabulation Module** - Coming Soon badge (Phase 3)

#### 2.2 Unified Upload Interface
**Design**:
- Single-page workflow with progress steps
- Drag & drop file upload (not just file picker)
- Live preview of detected variables
- One-click "Start Classification" button
- No separate "Start Classification" menu

**Steps Visualization**:
```
┌─────────────────────────────────────────┐
│  Step 1: Upload    Step 2: Select      │
│     [●]                [○]              │
│      ↓                  ↓               │
│  Drop files here   → Select variables   │
└─────────────────────────────────────────┘
```

#### 2.3 Real-Time Progress
**Features**:
- Live progress bar with percentage
- Current step indicator (e.g., "Generating categories: 45%")
- Estimated time remaining
- Cancel button (stop Celery task)
- Toast notifications when complete

#### 2.4 Results Page Enhancement
**New Features**:
- **Data Source Badge**: Kobo / Excel / CSV (for future multi-source)
- **Processing Status**: Success / Partial / Failed with color coding
- **Quick Actions**: Re-run, Download, Share, Archive
- **Visual Category Distribution**: Chart.js pie/bar charts
- **Confidence Score Overview**: Average + distribution

**Mockup**:
```
┌──────────────────────────────────────────┐
│ 📊 Classification Results                │
│ ──────────────────────────────────────  │
│ [Kobo] Dataset: ASDP_Berkendara.xlsx    │
│ ⏱️ Processed: 2m 34s | ✓ 142 responses  │
│                                          │
│ Variables Classified:                    │
│ ┌─────────────────────────────────────┐ │
│ │ E1: Evaluasi Produk                 │ │
│ │ 🏷️ 8 categories | 📈 92% confidence │ │
│ │ [View Details] [Download CSV]       │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ [📥 Download All] [🔄 Re-run] [📤 Share]│
└──────────────────────────────────────────┘
```

#### 2.5 Mobile-Responsive Design
**Requirements**:
- Touch-friendly buttons (min 44x44px)
- Collapsible sidebar for mobile
- Swipe gestures for navigation
- Bottom navigation bar for mobile
- Optimized for tablets (survey team in field)

**Expected Outcome**:
- ✅ 50% less clicks to start classification
- ✅ Intuitive for new users (no training needed)
- ✅ Modern, professional appearance
- ✅ Mobile-friendly for field teams

**Time Estimate**: 5-7 days
**Deployment**: No downtime, gradual rollout

---

### **Phase 3: Multi-Source Data Support** (Week 3-4 - Jan 20-Feb 2, 2026)
**Goal**: Support non-Kobo data sources (Excel, CSV, Google Sheets, SQL)

#### 3.1 Data Source Abstraction
**Architecture**:
```python
# app/data_sources/
├── __init__.py
├── base.py              # BaseDataSource interface
├── kobo.py              # KoboDataSource (existing)
├── excel.py             # ExcelDataSource (existing, refactor)
├── csv.py               # CSVDataSource (new)
├── google_sheets.py     # GoogleSheetsDataSource (new)
└── sql.py               # SQLDataSource (new - PostgreSQL, MySQL)
```

**Interface**:
```python
class BaseDataSource:
    def read_data(self) -> pd.DataFrame:
        """Read data from source"""
        pass
    
    def get_variables(self) -> List[Variable]:
        """Detect open-ended variables"""
        pass
    
    def write_results(self, results: pd.DataFrame):
        """Write classified results"""
        pass
```

#### 3.2 Upload Interface Enhancement
**Features**:
- **Source selector**: Dropdown (Kobo / Excel / CSV / Google Sheets / SQL)
- **Source-specific options**:
  - Kobo: Asset ID, API token
  - Excel/CSV: File upload
  - Google Sheets: Sheet URL, OAuth
  - SQL: Connection string, table name
- **Smart variable detection**: Auto-detect regardless of source

#### 3.3 Output Format Options
**Formats**:
- Excel (.xlsx) - Default
- CSV (.csv) - For analytics tools
- JSON (.json) - For API integration
- SQL INSERT - Direct to database
- Google Sheets - Update existing sheet

**Expected Outcome**:
- ✅ Support all major data sources
- ✅ Flexible for different team workflows
- ✅ Future-proof architecture

**Time Estimate**: 7-10 days
**Deployment**: Backward compatible, no breaking changes

---

### **Phase 4: Tabulation Module** (Q1 2026 - Feb-Mar)
**Goal**: Auto-generate cross-tabulation tables

**Features** (see TABULATION_SPEC.md):
- Cross-tabulation with demographic variables
- Statistical significance testing
- Export to Excel with formatting
- Dashboard for tabulation history

**Integration**:
- New menu: "Tabulation" in sidebar
- Workflow: Select classified data → Select demographics → Generate tables
- Same Celery architecture (background processing)

**Expected Outcome**:
- ✅ Complete survey workflow (Upload → Classify → Tabulate → Report)
- ✅ Reduce manual work by 80%

**Time Estimate**: 15-20 days
**Deployment**: Major feature release

---

## 📊 **TECHNICAL SPECIFICATIONS**

### Redis Configuration
```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
```

### Celery Configuration
```python
# celery_config.py
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Jakarta'
enable_utc = True

# Task routing
task_routes = {
    'app.tasks.classification.*': {'queue': 'classification'},
    'app.tasks.progress.*': {'queue': 'default'},
}

# Worker configuration
worker_prefetch_multiplier = 2
worker_max_tasks_per_child = 1000
task_acks_late = True
task_reject_on_worker_lost = True
```

### Gunicorn Configuration (Updated)
```python
# gunicorn.conf.py
workers = 4  # Up from 1 (multi-worker safe with Redis)
worker_class = 'sync'
worker_connections = 1000
max_requests = 2000
max_requests_jitter = 100
timeout = 120  # Reduce (requests are async now)
keepalive = 5
```

### Nginx Configuration (Updated)
```nginx
# /etc/nginx/sites-available/mcoder
upstream mcoder_app {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name m-coder.flazinsight.com;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://mcoder_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeout configuration
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        send_timeout 600s;
        
        # WebSocket support (for SSE)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    location /static/ {
        alias /opt/markplus/mcoder-markplus/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 📈 **PERFORMANCE TARGETS**

### Current vs Target

| Metric | Current | Target (Phase 1) | Target (Phase 4) |
|--------|---------|------------------|------------------|
| Concurrent Users | 5 (crashes at 12) | 20 | 50+ |
| Classification Speed | ~2min for 100 responses | ~1.5min | ~1min (with caching) |
| Uptime | 95% (crashes often) | 99.5% | 99.9% |
| Response Time (p95) | 3-5s | < 2s | < 1s |
| Memory Usage | ~500MB (1 worker) | ~2GB (4 workers + Redis) | ~4GB |
| CPU Usage | 80-100% (blocking) | 40-60% (async) | 30-50% |

### Scalability Testing Plan
```bash
# Load testing with Locust
# Simulate 20 concurrent users for 30 minutes
locust -f load_test.py --host=https://m-coder.flazinsight.com --users=20 --spawn-rate=2
```

**Success Criteria**:
- ✅ 0 errors under 20 concurrent users
- ✅ p95 response time < 2 seconds
- ✅ All classifications complete successfully
- ✅ No 502/504 errors
- ✅ Memory usage stable (no leaks)

---

## 🗓️ **IMPLEMENTATION TIMELINE**

### Week 1 (Jan 8-12, 2026) - **CRITICAL PATH**
- [x] Day 1: Plan approval, Redis installation
- [ ] Day 2: Celery setup, basic task implementation
- [ ] Day 3: Migrate classification to Celery tasks
- [ ] Day 4: Testing + fixes
- [ ] Day 5: Production deployment + monitoring

### Week 2 (Jan 13-19, 2026)
- [ ] Day 1-2: UI/UX wireframes + approval
- [ ] Day 3-4: Dashboard redesign implementation
- [ ] Day 5: Upload interface redesign
- [ ] Weekend: Testing + refinement

### Week 3 (Jan 20-26, 2026)
- [ ] Day 1-2: Results page enhancement
- [ ] Day 3: Mobile responsive optimization
- [ ] Day 4-5: User testing + fixes

### Week 4 (Jan 27-Feb 2, 2026)
- [ ] Day 1-3: Multi-source data support
- [ ] Day 4: Integration testing
- [ ] Day 5: Documentation + deployment

### Q1 2026 (Feb-Mar)
- [ ] Tabulation module development
- [ ] Advanced analytics features
- [ ] Performance optimization

---

## 💰 **RESOURCE REQUIREMENTS**

### Infrastructure
- **Redis Server**: Included in VPS (2GB RAM allocated)
- **Celery Workers**: 4-8 processes (CPU intensive)
- **Total Memory**: 4GB recommended (upgrade from 2GB if needed)
- **Storage**: +10GB for Redis persistence

### Development
- **Phase 1**: 3 days full-time (critical)
- **Phase 2**: 7 days full-time (UX heavy)
- **Phase 3**: 10 days full-time
- **Phase 4**: 20 days full-time

### External
- **UI/UX Consultant**: Optional but recommended for Phase 2
- **Load Testing**: Can use free Locust
- **Monitoring**: Consider Sentry (error tracking) - $26/month

---

## 🚦 **RISK MITIGATION**

### Risk 1: Downtime During Migration
**Impact**: HIGH  
**Probability**: MEDIUM  
**Mitigation**:
- Schedule maintenance window (Sunday 2-5 AM WIB)
- Prepare rollback script
- Test in development first
- Keep backup of old code

### Risk 2: Learning Curve (Celery/Redis)
**Impact**: MEDIUM  
**Probability**: LOW  
**Mitigation**:
- Extensive documentation
- Step-by-step tutorials
- Monitoring dashboards
- On-call support (developer)

### Risk 3: Performance Degradation
**Impact**: HIGH  
**Probability**: LOW  
**Mitigation**:
- Load testing before production
- Gradual rollout (A/B testing)
- Monitoring alerts (CPU, memory, error rate)
- Quick rollback capability

---

## 📝 **SUCCESS METRICS**

### Phase 1 Success Criteria
- ✅ 20 concurrent users without errors
- ✅ Classification continues after browser close
- ✅ No 502 errors for 7 days
- ✅ Average uptime > 99%

### Phase 2 Success Criteria
- ✅ 50% reduction in clicks to start classification
- ✅ 90% user satisfaction score (survey)
- ✅ < 5% bounce rate on upload page
- ✅ Mobile usability score > 85 (Google PageSpeed)

### Phase 3 Success Criteria
- ✅ Support 3+ data sources
- ✅ 95% successful imports from all sources
- ✅ No regression in existing functionality

### Phase 4 Success Criteria
- ✅ Tabulation module used by 80% of users
- ✅ 80% time saving vs manual tabulation
- ✅ Positive user feedback

---

## 🔧 **MONITORING & MAINTENANCE**

### Monitoring Stack
```yaml
# Recommended tools
- Application: Sentry (error tracking)
- Infrastructure: Prometheus + Grafana
- Logs: ELK Stack or Loki
- Uptime: UptimeRobot (free tier)
- APM: New Relic or DataDog (optional)
```

### Key Metrics to Track
1. **Application**:
   - Request rate (req/s)
   - Error rate (%)
   - Response time (p50, p95, p99)
   - Active users (concurrent)

2. **Celery**:
   - Task queue length
   - Task processing time
   - Worker utilization
   - Failed tasks

3. **Infrastructure**:
   - CPU usage (%)
   - Memory usage (%)
   - Disk I/O
   - Network bandwidth

4. **Business**:
   - Classifications per day
   - Success rate (%)
   - User retention
   - Average job size

### Alerting Rules
```yaml
# Alert thresholds
- Error rate > 5% for 5 minutes → Critical
- Response time p95 > 3s for 10 minutes → Warning
- Celery queue > 100 tasks for 15 minutes → Warning
- Memory usage > 90% for 5 minutes → Critical
- Failed tasks > 10 in 1 hour → Warning
```

---

## 📚 **DOCUMENTATION REQUIREMENTS**

### User Documentation
- [ ] User Guide (PDF + web version)
- [ ] Video tutorials (upload, classify, results)
- [ ] FAQ section
- [ ] Troubleshooting guide

### Developer Documentation
- [ ] Architecture diagram
- [ ] API documentation (if exposing API)
- [ ] Database schema
- [ ] Deployment guide
- [ ] Code comments and docstrings

### Operational Documentation
- [ ] Runbook (common issues + fixes)
- [ ] Deployment checklist
- [ ] Rollback procedure
- [ ] Monitoring guide
- [ ] Backup & restore procedure

---

## 🎓 **TEAM TRAINING**

### Technical Training (Developer)
- Redis basics (1 hour)
- Celery architecture (2 hours)
- Debugging distributed systems (1 hour)
- Performance profiling (1 hour)

### User Training (End Users)
- New UI walkthrough (30 minutes)
- Best practices (30 minutes)
- Troubleshooting (30 minutes)
- Q&A session

---

## ✅ **APPROVAL & SIGN-OFF**

**Plan Prepared By**: AI Development Team  
**Date**: January 8, 2026  
**Status**: Awaiting Approval

**Stakeholder Review**:
- [ ] Technical Lead (Developer)
- [ ] Product Owner (Haryadi)
- [ ] Infrastructure Team (VPS Admin)
- [ ] End Users Representative

**Approved By**: ________________  
**Date**: ________________

---

**Next Steps**:
1. Review and approve this plan
2. Schedule Phase 1 implementation (Week 1)
3. Allocate resources (infrastructure + time)
4. Begin execution

**Questions or Concerns**: Contact development team

---

**Document Version**: 1.0  
**Last Updated**: January 8, 2026  
**Next Review**: After Phase 1 completion
