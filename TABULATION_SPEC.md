# Tabulation Module - Technical Specification

> **M-Code Pro - Phase 2 Development**  
> **Created**: 27 December 2025  
> **Status**: 🟡 Planning Phase  
> **Target**: Q1 2026 (3-4 weeks implementation)

---

## 📋 Executive Summary

**What**: Automated cross-tabulation system that generates ratusan-ribuan tabel dari classified survey data.

**Why**: After classification, users need batch tabulation for analysis. Manual Excel pivot tables tidak scalable untuk ratusan variables.

**How**: Hybrid architecture dengan Flask Web UI + Celery background workers + Polars untuk high-performance data processing.

---

## 🎯 Requirements

### Functional Requirements

**FR1: Data Upload & Variable Selection**
- User upload classified Excel file (hasil dari M-Code Pro classification)
- System auto-detect available variables (columns)
- User select row variables dan column variables untuk cross-tabulation
- Support batch selection (multiple tables in one job)

**FR2: Tabulation Processing**
- Generate cross-tabulation dengan format:
  ```
  Header Row: Column variable categories
  Total Row: Total responden (raw count)
  Data Rows: Row variable categories dengan percentage per column
  ```
- Support berbagai aggregate functions (count, mean, sum)
- Handle missing data dengan proper indicators (N/A, -, etc)

**FR3: Output Generation**
- Export Excel dengan multiple sheets (1 table = 1 sheet)
- Batch files jika >100 sheets (split ke multiple Excel files)
- Format professional (header styling, borders, percentage format)
- Include metadata sheet (job info, processing time, variables used)

**FR4: Job Management**
- Queue system untuk background processing
- Real-time progress tracking
- Email notification saat job selesai
- Job history dengan download links (retain 7 days)

### Non-Functional Requirements

**NFR1: Performance**
- Target: 1000 tabel dalam 10-15 menit
- Support concurrent users (min 5 simultaneous jobs)
- Memory efficient (max 4GB per worker)
- No browser timeout (background processing)

**NFR2: Scalability**
- Horizontal scaling dengan multiple Celery workers
- Handle datasets up to 10 juta rows
- Support 100-1000 tables per job

**NFR3: Reliability**
- Job retry mechanism (max 3 attempts)
- Error handling dengan clear messages
- Data validation before processing
- Graceful degradation jika worker unavailable

---

## 🏗️ Architecture Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Interface                        │
│  (Flask Web - Reuse M-Code Pro Auth & Layout)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    Flask Application                        │
│  - Upload endpoint                                          │
│  - Variable selection UI                                    │
│  - Job queue submission                                     │
│  - Progress monitoring (SSE)                                │
│  - Download management                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ Queue Job
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                      Redis Queue                            │
│  - Job metadata storage                                     │
│  - Progress tracking                                        │
│  - Result caching                                           │
└────────────────────┬────────────────────────────────────────┘
                     │ Workers Pickup
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   Celery Workers (3-5x)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Worker Process                                      │  │
│  │  1. Read Excel with Polars (lazy loading)            │  │
│  │  2. Batch processing (50-100 tables per batch)       │  │
│  │  3. Parallel crosstab generation                     │  │
│  │  4. Format & validate results                        │  │
│  │  5. Write to Excel with xlsxwriter (streaming)       │  │
│  │  6. Update progress in Redis                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  Processing Engine:                                         │
│  - Polars (data processing - 10-100x faster than pandas)   │
│  - xlsxwriter (Excel generation with streaming mode)       │
│  - multiprocessing (parallel within worker)                │
└────────────────────┬────────────────────────────────────────┘
                     │ Save Results
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    File Storage                             │
│  - /files/tabulations/[job_id]/                             │
│  - Excel outputs (with expiry 7 days)                       │
│  - Job logs & metadata                                      │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Web Framework** | Flask 3.0 | Reuse existing M-Code Pro infrastructure |
| **Task Queue** | Celery 5.3 | Industry-standard for background jobs |
| **Message Broker** | Redis 7.0 | Fast, reliable, supports pub/sub for progress |
| **Data Processing** | Polars 0.20+ | 10-100x faster than pandas, memory efficient |
| **Excel Generation** | xlsxwriter 3.1+ | C-optimized, streaming mode for large files |
| **Progress Tracking** | Server-Sent Events (SSE) | Real-time updates tanpa WebSocket complexity |
| **Job Monitoring** | Flower 2.0 | Visual monitoring untuk Celery workers |

### Database Schema (Additions to M-Code Pro)

```sql
-- New table: tabulation_jobs
CREATE TABLE tabulation_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id VARCHAR(36) UNIQUE NOT NULL,  -- UUID
    classification_id INTEGER,  -- Link to classification results (optional)
    
    -- Job metadata
    input_file VARCHAR(255) NOT NULL,
    total_tables INTEGER NOT NULL,
    variables_config TEXT,  -- JSON: [{row: 'A1', col: 'B1'}, ...]
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'queued',  -- queued, processing, completed, failed
    progress INTEGER DEFAULT 0,  -- 0-100
    current_step VARCHAR(255),
    
    -- Results
    output_files TEXT,  -- JSON array: ['file1.xlsx', 'file2.xlsx']
    error_message TEXT,
    
    -- Timing
    queued_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (classification_id) REFERENCES classification_results(id)
);

-- Index untuk performance
CREATE INDEX idx_job_status ON tabulation_jobs(status, user_id);
CREATE INDEX idx_job_created ON tabulation_jobs(queued_at DESC);
```

---

## 🔧 Implementation Plan

### Week 1: Infrastructure Setup

**Day 1-2: Install Dependencies**
```bash
# Install Redis
sudo apt install redis-server
sudo systemctl enable redis-server

# Install Celery & dependencies
pip install celery[redis] flower polars xlsxwriter pyarrow

# Update requirements.txt
echo "celery[redis]==5.3.4" >> requirements.txt
echo "flower==2.0.1" >> requirements.txt
echo "polars==0.20.3" >> requirements.txt
echo "xlsxwriter==3.1.9" >> requirements.txt
```

**Day 3-4: Setup Celery Application**
```python
# app/celery_app.py
from celery import Celery
from flask import Flask

def create_celery(app: Flask) -> Celery:
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery
```

**Day 5: Testing & Benchmarking**
- Compare Polars vs pandas performance
- Test xlsxwriter streaming mode
- Verify Redis connection & job queuing

**Deliverable**: Working Celery setup dengan monitoring via Flower

---

### Week 2: Core Processing Engine

**Day 1-2: Polars Crosstab Implementation**
```python
# tabulation/processor.py
import polars as pl
from typing import List, Dict

class TabulationProcessor:
    def __init__(self, file_path: str):
        # Lazy loading untuk memory efficiency
        self.df = pl.read_excel(file_path, engine='openpyxl')
    
    def generate_crosstab(
        self, 
        row_var: str, 
        col_var: str,
        aggregate: str = 'count'
    ) -> pl.DataFrame:
        """
        Generate cross-tabulation dengan format:
        - Top row: Total responden
        - Data rows: Percentage per column
        """
        # Count matrix
        ct = self.df.pivot(
            values=row_var,  # What to count
            index=row_var,   # Row variable
            columns=col_var, # Column variable
            aggregate_function='count'
        )
        
        # Calculate column totals
        totals = ct.select(pl.exclude('index')).sum()
        
        # Convert to percentages
        ct_pct = ct.select([
            pl.col('index'),
            *(pl.col(c) / totals[c] * 100 for c in ct.columns[1:])
        ])
        
        # Add total row
        total_row = pl.DataFrame({
            'index': ['Total Responden'],
            **{c: [totals[c]] for c in ct.columns[1:]}
        })
        
        result = pl.concat([total_row, ct_pct])
        return result
    
    def batch_process(
        self, 
        table_configs: List[Dict],
        progress_callback=None
    ) -> List[pl.DataFrame]:
        """Process multiple tables dengan progress tracking"""
        results = []
        total = len(table_configs)
        
        for idx, config in enumerate(table_configs):
            ct = self.generate_crosstab(
                config['row_var'],
                config['col_var']
            )
            results.append(ct)
            
            if progress_callback:
                progress_callback(idx + 1, total)
        
        return results
```

**Day 3-4: Excel Export dengan Formatting**
```python
# tabulation/excel_writer.py
import xlsxwriter
import polars as pl

class TabulationExcelWriter:
    def __init__(self, output_path: str):
        # Streaming mode untuk large files
        self.workbook = xlsxwriter.Workbook(
            output_path,
            {'constant_memory': True}
        )
        self._setup_formats()
    
    def _setup_formats(self):
        """Define cell formats"""
        self.header_format = self.workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center'
        })
        
        self.total_format = self.workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1,
            'num_format': '#,##0'
        })
        
        self.pct_format = self.workbook.add_format({
            'border': 1,
            'num_format': '0.0%'
        })
    
    def write_crosstab(
        self, 
        sheet_name: str, 
        df: pl.DataFrame,
        metadata: Dict = None
    ):
        """Write single crosstab to sheet"""
        ws = self.workbook.add_worksheet(sheet_name[:31])  # Excel limit
        
        # Write headers
        for col_idx, col_name in enumerate(df.columns):
            ws.write(0, col_idx, col_name, self.header_format)
        
        # Write data
        for row_idx, row in enumerate(df.iter_rows(), start=1):
            for col_idx, value in enumerate(row):
                if row_idx == 1:  # Total row
                    ws.write(row_idx, col_idx, value, self.total_format)
                elif col_idx == 0:  # First column (labels)
                    ws.write(row_idx, col_idx, value)
                else:  # Data cells (percentages)
                    ws.write(row_idx, col_idx, value/100, self.pct_format)
        
        # Auto-width columns
        for col_idx in range(len(df.columns)):
            ws.set_column(col_idx, col_idx, 15)
    
    def close(self):
        self.workbook.close()
```

**Day 5: Integration Testing**
- Test dengan sample dataset (100 tables)
- Verify output format matches requirements
- Benchmark performance

**Deliverable**: Working processor + Excel writer

---

### Week 3: Web Integration

**Day 1-2: Flask Routes & UI**
```python
# app/routes_tabulation.py
from flask import Blueprint, request, session, render_template
from app.celery_app import celery
from app.models import TabulationJob

tabulation_bp = Blueprint('tabulation', __name__, url_prefix='/tabulation')

@tabulation_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        # Save file
        file_path = save_upload(file)
        
        # Detect variables
        variables = detect_variables(file_path)
        
        return render_template('tabulation/select_variables.html',
                               variables=variables,
                               file_path=file_path)
    
    return render_template('tabulation/upload.html')

@tabulation_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    config = request.json
    
    # Create job
    job = TabulationJob(
        user_id=current_user.id,
        input_file=config['file_path'],
        total_tables=len(config['tables']),
        variables_config=json.dumps(config['tables'])
    )
    db.session.add(job)
    db.session.commit()
    
    # Queue Celery task
    task = process_tabulation.delay(job.id)
    job.job_id = task.id
    db.session.commit()
    
    return jsonify({'job_id': job.job_id})

@tabulation_bp.route('/progress/<job_id>')
@login_required
def progress(job_id):
    """SSE endpoint for real-time progress"""
    def generate():
        while True:
            job = TabulationJob.query.filter_by(job_id=job_id).first()
            if not job:
                break
            
            data = {
                'status': job.status,
                'progress': job.progress,
                'current_step': job.current_step
            }
            yield f"data: {json.dumps(data)}\n\n"
            
            if job.status in ['completed', 'failed']:
                break
            
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')
```

**Day 3-4: Celery Task Implementation**
```python
# app/tasks/tabulation.py
from app.celery_app import celery
from tabulation.processor import TabulationProcessor
from tabulation.excel_writer import TabulationExcelWriter

@celery.task(bind=True, max_retries=3)
def process_tabulation(self, job_id: int):
    """Main Celery task untuk tabulation"""
    job = TabulationJob.query.get(job_id)
    
    try:
        # Update status
        job.status = 'processing'
        job.started_at = datetime.now()
        db.session.commit()
        
        # Load data
        processor = TabulationProcessor(job.input_file)
        table_configs = json.loads(job.variables_config)
        
        # Progress callback
        def update_progress(current, total):
            job.progress = int((current / total) * 100)
            job.current_step = f"Processing table {current}/{total}"
            db.session.commit()
        
        # Process all tables
        results = processor.batch_process(
            table_configs,
            progress_callback=update_progress
        )
        
        # Write to Excel
        output_path = f"files/tabulations/{job.job_id}/results.xlsx"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        writer = TabulationExcelWriter(output_path)
        for idx, (config, result) in enumerate(zip(table_configs, results)):
            sheet_name = f"Table_{idx+1}"
            writer.write_crosstab(sheet_name, result, metadata=config)
        writer.close()
        
        # Update job
        job.status = 'completed'
        job.completed_at = datetime.now()
        job.output_files = json.dumps([output_path])
        db.session.commit()
        
        # Send email notification
        send_email_notification(job)
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()
        
        # Retry
        raise self.retry(exc=e, countdown=60)
```

**Day 5: Templates & Frontend JS**
- Create upload form
- Variable selection UI (checkboxes with preview)
- Progress page with SSE connection
- Download page with file list

**Deliverable**: Working end-to-end flow (upload → process → download)

---

### Week 4: Testing, Optimization & Deployment

**Day 1-2: Load Testing**
```python
# tests/test_tabulation_load.py
import pytest
from concurrent.futures import ThreadPoolExecutor

def test_concurrent_jobs():
    """Test 5 concurrent tabulation jobs"""
    def submit_job():
        # Submit job via API
        response = client.post('/tabulation/generate', json=config)
        return response.json()['job_id']
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(submit_job) for _ in range(5)]
        job_ids = [f.result() for f in futures]
    
    # Wait for completion
    for job_id in job_ids:
        wait_for_completion(job_id)
    
    assert all_jobs_completed(job_ids)

def test_large_dataset():
    """Test with 1000 tables"""
    config = generate_config(num_tables=1000)
    job_id = submit_job(config)
    
    start = time.time()
    wait_for_completion(job_id)
    duration = time.time() - start
    
    assert duration < 900  # Max 15 minutes
```

**Day 3: Performance Optimization**
- Profile memory usage with memory_profiler
- Optimize Polars queries (lazy evaluation)
- Tune Celery worker settings (concurrency, prefetch)
- Implement result caching for repeated requests

**Day 4: Documentation**
- User guide (how to use tabulation module)
- API documentation
- Deployment guide
- Troubleshooting common issues

**Day 5: VPS Deployment**
```bash
# Deploy to production VPS
# 1. Install Redis
sudo apt install redis-server

# 2. Update application code
git pull origin main

# 3. Install new dependencies
pip install -r requirements.txt

# 4. Start Celery workers
celery -A app.celery_app worker \
    --queue=tabulation \
    --concurrency=8 \
    --loglevel=info \
    --logfile=/var/log/celery/tabulation.log &

# 5. Start Flower monitoring
celery -A app.celery_app flower --port=5555 &

# 6. Restart Flask app
supervisorctl restart mcoder-markplus
```

**Deliverable**: Production-ready tabulation module

---

## 📊 Performance Targets

### Benchmarks (Target vs Actual)

| Metric | Target | Testing | Production |
|--------|--------|---------|------------|
| **100 tables** | 1-2 min | TBD | TBD |
| **500 tables** | 5-7 min | TBD | TBD |
| **1000 tables** | 10-15 min | TBD | TBD |
| **Memory per worker** | <4 GB | TBD | TBD |
| **Concurrent jobs** | 5+ | TBD | TBD |
| **File size (1000 sheets)** | ~50 MB | TBD | TBD |

### Scalability Plan

**Current Setup (Single VPS):**
- 1 Flask app server
- 3-5 Celery workers (1 worker = 1 CPU core)
- 1 Redis instance
- Capacity: ~10 concurrent jobs

**Scale-Up (If Needed):**
- Add more workers (scale horizontally)
- Increase worker concurrency
- Upgrade VPS (more CPU cores, RAM)
- Redis clustering for distributed queue

**Scale-Out (Future):**
- Separate worker servers (dedicated processing nodes)
- Load balancer untuk Flask apps
- Distributed Redis (Redis Cluster)
- Capacity: 100+ concurrent jobs

---

## 🚨 Risk Management

### Technical Risks

**Risk 1: Memory Overflow**
- **Impact**: Worker crashes, job fails
- **Mitigation**:
  - Polars streaming mode (lazy evaluation)
  - xlsxwriter constant_memory option
  - Batch processing (limit 50-100 tables per batch)
  - Worker memory limits (ulimit)

**Risk 2: Excel File Corruption**
- **Impact**: User can't open output file
- **Mitigation**:
  - Validate output file before marking job complete
  - Retry mechanism for write failures
  - Keep temporary files until validation passes
  - Log checksums for integrity verification

**Risk 3: Queue Congestion**
- **Impact**: Long wait times, poor UX
- **Mitigation**:
  - Priority queue (premium users first)
  - Job scheduling during off-peak hours
  - Email notification instead of blocking UI
  - Queue monitoring with alerts

**Risk 4: Data Validation Issues**
- **Impact**: Wrong results, user complaints
- **Mitigation**:
  - Pre-flight checks (file format, variables exist)
  - Sample validation (show preview before full process)
  - Cross-check totals (row sum = column sum)
  - Unit tests for edge cases

### Operational Risks

**Risk 5: Worker Downtime**
- **Impact**: Jobs stuck in queue
- **Mitigation**:
  - Health checks every minute
  - Auto-restart on failure (supervisor)
  - Multiple workers (redundancy)
  - Dead letter queue for failed jobs

**Risk 6: Redis Data Loss**
- **Impact**: Lost job progress, need resubmit
- **Mitigation**:
  - Redis persistence (AOF + RDB)
  - Regular backups
  - Job metadata also in PostgreSQL/SQLite
  - Retry mechanism

---

## 🔐 Security Considerations

**Data Privacy:**
- User files stored separately (per user directory)
- Auto-delete after 7 days
- No data shared between users
- Encrypted at rest (filesystem level)

**Access Control:**
- Only file owner can download results
- Admin can view all jobs (for support)
- API endpoints require authentication
- Rate limiting to prevent abuse

**Input Validation:**
- File size limits (max 500 MB)
- File type validation (only .xlsx, .csv)
- Variable name sanitization (prevent injection)
- Timeout limits (max 1 hour per job)

---

## 📈 Success Metrics

**Usage Metrics:**
- Number of tabulation jobs per day
- Average processing time per job
- Success rate (completed vs failed)
- User satisfaction (survey after download)

**Performance Metrics:**
- Job queue length (should be near 0)
- Worker utilization (should be 60-80%)
- Error rate (should be <1%)
- Memory usage per worker

**Business Metrics:**
- Time saved vs manual tabulation
- Cost per job (compute + storage)
- User adoption rate
- Support tickets related to tabulation

---

## 🔄 Maintenance Plan

**Daily:**
- Monitor Celery worker health
- Check Redis memory usage
- Review failed jobs log
- Clear expired files (>7 days)

**Weekly:**
- Performance review (slow queries)
- Capacity planning (queue trends)
- Update dependencies (security patches)
- Backup job history database

**Monthly:**
- User feedback review
- Feature usage analysis
- Cost optimization review
- Documentation updates

---

## 📚 Reference Links

**Documentation:**
- [Polars User Guide](https://pola-rs.github.io/polars-book/)
- [Celery Best Practices](https://docs.celeryproject.org/en/stable/userguide/tasks.html)
- [xlsxwriter Documentation](https://xlsxwriter.readthedocs.io/)
- [Redis Persistence](https://redis.io/topics/persistence)

**Related Documents:**
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Overall project context
- [CHANGELOG.md](CHANGELOG.md) - Recent changes
- [README.md](README.md) - User guide

---

## ✅ Checklist for Implementation

**Prerequisites:**
- [ ] Redis installed and running
- [ ] Celery tested with simple task
- [ ] Polars benchmark completed
- [ ] VPS resources verified (CPU, RAM, disk)

**Development:**
- [ ] Database schema migrated
- [ ] TabulationProcessor class implemented
- [ ] TabulationExcelWriter class implemented
- [ ] Celery task created and tested
- [ ] Flask routes and templates created
- [ ] SSE progress tracking working
- [ ] Email notifications configured

**Testing:**
- [ ] Unit tests (processor, writer)
- [ ] Integration tests (end-to-end flow)
- [ ] Load tests (concurrent jobs)
- [ ] Performance tests (1000 tables)
- [ ] UI/UX testing (responsive, clear errors)

**Deployment:**
- [ ] Production config updated
- [ ] Workers deployed and monitored
- [ ] Flower monitoring accessible
- [ ] Backup procedures tested
- [ ] Rollback plan documented

**Documentation:**
- [ ] User guide written
- [ ] API documented
- [ ] Troubleshooting guide created
- [ ] Team training completed

---

**END OF SPECIFICATION**

For questions or clarifications, refer to:
- Technical Lead: [Your Name]
- Project Manager: [PM Name]
- Repository: https://github.com/hary4di/mcoder-markplus
