# M-Code Pro - Project Overview

> **Master Documentation** untuk agent yang bekerja pada project ini.  
> **Update Terakhir**: 2 Januari 2026

---

## 🎯 TUJUAN APLIKASI

**M-Code Pro** adalah platform web untuk **klasifikasi otomatis survey open-ended** menggunakan AI (OpenAI GPT-4o-mini).

### Problem yang Diselesaikan
- Manual coding survey memakan waktu (ribuan responses × manual review)
- Inconsistent categorization antar coder
- Cost tinggi untuk tenaga coding

### Solution
- AI menganalisis responses dan generate categories otomatis
- Klasifikasi ribuan responses dalam menit (bukan hari)
- Cost efisien: ~$0.15 per 1M tokens (GPT-4o-mini)

### Target User
- **MarkPlus Indonesia** - Research & Consulting company
- Internal tool untuk analyst yang handle survey data

---

## 🚀 PRODUCTION ENVIRONMENT

| Item | Detail |
|------|--------|
| **URL** | https://m-coder.flazinsight.com |
| **VPS** | Hostinger - Ubuntu 24.04 (145.79.10.104) |
| **GitHub** | https://github.com/hary4di/mcoder-markplus |
| **Deploy** | SCP upload → supervisorctl restart |
| **Tech Stack** | Python 3.11 + Flask 3.0 + **PostgreSQL 16.11** + Bootstrap 5 |
| **Database** | mcoder_production (PostgreSQL) |
| **DB User** | mcoder_app / MarkPlus25 |
| **DB Host** | localhost:5432 |

---

## ✅ PENCAPAIAN SAAT INI (v1.3.0) - Updated Jan 5, 2026

### Fitur Core ✅
1. **Upload & Classification**
   - Upload 2 Excel files (kobo_system + raw_data)
   - AI generate categories dari sample responses
   - Classify semua responses dengan confidence score
   - Export Excel dengan columns baru (category + confidence)
   - **NEW**: Timestamped files - preserve originals, separate outputs

2. **Authentication & User Management**
   - Login dengan email + password
   - 3 role levels: User, Admin, Super Admin (@markplusinc.com)
   - Admin bisa create/edit users
   - Super Admin bisa edit semua termasuk Super Admin lain
   - Password reset via OTP email (Gmail SMTP)

3. **Results & Analytics** ✅ **MAJOR UPDATE (Jan 2-5, 2026)**
   - **NEW**: PostgreSQL database backend (mcoder_production)
   - **NEW**: Persistent database storage (production-grade)
   - **NEW**: Classification history accessible anytime (not session-based)
   - **NEW**: Job list with Date, File, Variables, Duration, Type, Expiry
   - **NEW**: Bulk Delete - Multi-select with checkboxes + delete button
   - **NEW**: Search Box - Real-time filename filtering
   - **NEW**: Expiry Countdown - Color-coded badges (24h limit tracker)
   - View detailed results per job (statistics, categories, distribution)
   - Download classified Excel files as ZIP (2 files)
   - Classification history tracking with database
   - **PRODUCTION**: Deployed Jan 5, 2026 with PostgreSQL

4. **File Management** ✅ **UPDATED (Dec 30, 2025)**
   - **Timestamped inputs**: `input_kobo_20251228_032238.xlsx`
   - **Timestamped outputs**: `output_kobo_20251228_032318.xlsx`, `output_raw_20251228_032318.xlsx`
   - **Preserves originals**: No more overwriting input files
   - **4 files per job**: 2 inputs (preserved) + 2 outputs (results)
   - **ZIP Download**: Single click download with 2 Excel files
   - **WIB Timezone**: All timestamps in Asia/Jakarta timezone
   - **24h Expiry**: Automatic download expiry after 24 hours

5. **UI/UX** ✅ **UPDATED (Dec 27-Jan 2, 2026)**
   - ✅ Branding: **"M-Code Pro"** (M bold) + "MarkPlus AI-Powered Classification System"
   - ✅ Login page: Logo MarkPlus diperbesar, subtitle konsisten
   - ✅ Navbar: Title "M-Code Pro", subtitle dengan MarkPlus bold
   - ✅ Sidebar: Logo "M-Code Pro" (M bold)
   - ✅ Header user info: 2 baris (Name + Role badge warna)
   - ✅ Hero section: Nempel rapat ke header (15px spacing)
   - ✅ No redundant welcome message flash
   - ✅ Need Help: Email + WhatsApp buttons clickable
   - ✅ Open Graph meta tags updated untuk share link
   - ✅ Results page: Professional table with 9 columns + interactive features

### Performance ⚡
- Parallel processing dengan ThreadPoolExecutor (3-5x faster)
- Real-time progress tracking dengan Server-Sent Events (SSE)
- Efficient batching untuk OpenAI API calls

### Security 🔒
- Password hashing (werkzeug)
- Session-based authentication (Flask-Login)
- Role-based access control (RBAC)
- OTP email verification untuk password reset

---

## ⚠️ HAL PENTING YANG PERLU DIPERHATIKAN

### 1. **Kobo API Integration (Skip Dulu)**
- Ada code untuk upload ke Kobo Toolbox (`kobo_uploader.py`)
- Fitur ini **TIDAK AKTIF** di production
- User hanya butuh classification + Excel export
- Jangan develop fitur Kobo kecuali user minta spesifik

### 2. **Profile Photo Upload (Pending)**
- Database sudah punya kolom `profile_photo`
- Code sudah ada tapi **ERROR** saat deploy (Flask SQLAlchemy cache issue)
- **STATUS**: Ditunda sampai ada waktu proper untuk fix
- **File terkait**: `add_profile_photo.py`, models.py dengan field profile_photo

### 3. **Git & Deployment**
- Local Windows: **TIDAK ADA Git terinstall** (git command not found)
- Deployment: Manual SCP upload file → SSH restart
- GitHub: Update dilakukan dari VPS atau manual push
- **Untuk sinkronisasi**: Copy file dari VPS ke local atau sebaliknya

### 4. **Model Limitation (GPT-4o-mini)**
- Model: gpt-4o-mini (ekonomis, akurat untuk survey coding)
- Limitation: Tidak bisa handle multi-label classification dengan baik
- Workaround: Generate single dominant category per response
- Cost: ~$0.15 per 1M tokens (sangat affordable)

### 5. **File Structure Critical**
- `files/uploads/` - User uploaded Excel
- `files/output/` - Classified results
- `files/logs/` - Classification logs, generated categories
- `instance/mcoder.db` - SQLite database
- **Jangan hapus directory structure** atau app akan error

---

## 📋 DEVELOPMENT PLAN (Next Phase)

### 🔴 Priority Tinggi - IN PLANNING

**1. Tabulation Module** (NEW - Planned Q1 2026)
   - **Purpose**: Auto-generate cross-tabulation dari classified data
   - **Scale**: Handle ratusan-ribuan tabel (production requirement)
   - **Tech Stack**: Flask + Celery + Redis + Polars + xlsxwriter
   - **Status**: 🟡 Technical spec completed (see TABULATION_SPEC.md)
   - **Impact**: Complete survey workflow (Classification → Tabulation → Report)

### 🔴 Priority Tinggi - BACKLOG
1. **Multi-Label Classification** ✅ **ALREADY IMPLEMENTED**
   - User butuh 1 response bisa punya multiple categories
   - Contoh: "Harga mahal dan pelayanan lambat" → code: "1 3"
   - **Status**: Active in code (ENABLE_MULTI_LABEL=true)
   - **Note**: Fixed outlier reclassification bug (Jan 7, 2026)

2. **Type 2 Classification (Semi Open-Ended)** 🔴 **NEXT PRIORITY**
   - Handle precoded questions dengan option "Lainnya" + open text
   - Code sudah ada: `semi_open_processor.py`
   - **Status**: Need testing + refinement
   - **Impact**: Complete classification untuk all question types

### Prioritas Sedang 🟡
3. **Profile Photo Upload (Fix)**
   - Database ready, code ready, tapi deploy error
   - Perlu fix Flask SQLAlchemy model loading issue
   - **Impact**: Nice-to-have untuk personalization

4. **Export Format Options**
   - Saat ini hanya Excel (.xlsx)
   - Target: Tambahkan CSV, JSON export options
   - **Impact**: Flexibility untuk different use cases

5. **Category Management**
   - User mungkin mau edit/merge categories setelah generate
   - Target: UI untuk review dan adjust categories
   - **Impact**: Better control untuk user

### Prioritas Rendah 🟢
6. **Documentation Portal**
   - User guide, tutorial, FAQ
   - Embed video tutorial
   - **Current**: Help button link ke email/WA saja

7. **Analytics Dashboard**
   - Graph visualizations (category trends, usage statistics)
   - Export reports
   - **Current**: Basic card statistics only

---

## 🔧 TECHNICAL NOTES UNTUK AGENT

### Database Schema (PostgreSQL)
**Connection:** `postgresql://mcoder_app:MarkPlus25@localhost:5432/mcoder_production`

```python
# User Model (app/models.py)
class User:
    id, username, email, full_name, password_hash
    profile_photo  # VARCHAR(255) - belum aktif
    is_admin, is_active
    created_at, last_login
    
    @property is_super_admin: email.endswith('@markplusinc.com')
    @property role_name: 'Super Admin' | 'Admin' | 'User'

# ClassificationJob Model
class ClassificationJob:
    id (UUID), user_id, original_filename
    kobo_file, raw_file, output_kobo, output_raw
    started_at, completed_at, status
    total_variables, total_categories, total_responses
    duration_seconds, classification_type
    results_json

# ClassificationVariable Model  
class ClassificationVariable:
    id, job_id, variable_name, question_text
    total_submissions, valid_classified, invalid_count, empty_count
    categories_generated, confidence_threshold
    categories_json, statistics_json
```

**Tables in Production:**
- users (2 users migrated)
- classification_jobs (empty - fresh database)
- classification_variables (empty)
- otp_tokens
- system_settings

**PostgreSQL Extensions:**
- pg_trgm (for text search - future tabulasi module)

### File Upload Flow
1. User upload kobo_system.xlsx + raw_data.xlsx
2. `FileProcessor` detect open-ended variables
3. User pilih variables untuk classify
4. `ExcelClassifier` jalankan 2-phase classification:
   - **Phase 1**: Sample responses → AI generate categories
   - **Phase 2**: Classify all responses into categories
5. Export Excel dengan columns: `[original] [category] [confidence]`

### Classification Logic (excel_classifier.py)
```python
# Phase 1: Generate Categories
sample = responses[:max_sample_size]  # Default 500
categories = openai.generate_categories(sample, max_categories=10)

# Phase 2: Classify All
for response in all_responses:
    result = openai.classify_response(response, categories)
    # result = {category: str, confidence: float}
```

### Parallel Processing (parallel_classifier.py)
- Use `ThreadPoolExecutor` (max_workers=5)
- Batch size = 50 responses per thread
- Progress tracking dengan shared dict (thread-safe)
- 3-5x faster daripada sequential

### API Integration
**OpenAI:**
- Endpoint: `https://api.openai.com/v1/chat/completions`
- Model: `gpt-4o-mini`
- Temperature: 0.1 (consistency)
- Response format: JSON mode

**Kobo Toolbox (Optional):**
- Endpoint: `https://kobo.humanitarianresponse.info/api/v2/`
- Method: GET submissions, PATCH submissions (bulk update)
- **Status**: Skip development kecuali user request

---

## 📞 SUPPORT CONTACT

**Developer/Support:**
- Email: haryadi@markplusinc.com
- WhatsApp: +62 812-8933-008
- Available via "Need Help?" button di dashboard

**User Base:**
- Internal MarkPlus Indonesia team
- Komunikasi: **Bahasa Indonesia** (preferred)

---

## 🎨 BRANDING GUIDELINES (Updated Today)

### Nama Aplikasi
- **Primary**: "M-Code Pro"
- **Display**: M dengan font-weight: 700 (bold), sisanya 600 (semi-bold)
- **Subtitle**: "**MarkPlus** AI-Powered Classification System" (MarkPlus bold)

### Logo
- MarkPlus corporate logo (upload via admin settings)
- Fallback: M+ icon dengan gradient purple

### Color Scheme
- Primary: #667eea (purple-blue gradient)
- Secondary: #764ba2 (deep purple)
- Accent: MarkPlus Red (#E31E24) untuk logo
- Role Badges:
  - Super Admin: Red (bg-danger)
  - Admin: Yellow (bg-warning)
  - User: Gray (bg-secondary)

### Typography
- Headers: System font stack (segoe ui, helvetica, arial)
- Body: Same, 0.9rem default
- Responsive: Smaller fonts for mobile

---

## 📝 VERSION HISTORY

### v1.2.0 (2 Jan 2026) - Current ✅
- ✅ Bulk Delete feature (multi-select with checkboxes)
- ✅ Search Box (real-time filename filtering)
- ✅ Expiry Countdown badges (color-coded 24h tracker)
- ✅ CSRF Protection properly initialized
- ✅ Results page with 9 columns (was 7)
- ✅ Enhanced UX with interactive JavaScript features

### v1.2.0 (2 Jan 2026)
- ✅ Bulk Delete with checkboxes
- ✅ Search Box (real-time filtering)
- ✅ Expiry Countdown badges (24h tracker)
- ✅ CSRF Protection fix
- ✅ Auto-delete input files after classification
- ✅ Separate output directory (files/output/)
- ✅ Enhanced UX (9 columns table, interactive features)

### v1.1.0 (28 Dec 2025)
- ✅ Database integration (Flask-Migrate + SQLAlchemy)
- ✅ Classification history with persistent storage
- ✅ Job tracking (ClassificationJob + ClassificationVariable models)
- ✅ Timestamped file management (preserve originals)
- ✅ Results page redesign (job history list)
- ✅ Fixed SQLAlchemy detached instance errors
- ✅ Fixed file overwriting issues
- ✅ Background thread request context fix

### v1.0.0 (27 Dec 2025)
- ✅ Core classification functionality
- ✅ User authentication & management  
- ✅ Rebranding: M-Code Pro
- ✅ UI/UX improvements (header, hero, help section)
- ✅ Role-based access (Super Admin feature)
- ⏸️ Profile photo upload (pending fix)

### v1.3.0 (5 Jan 2026) - Current ✅
- ✅ **PostgreSQL Migration** (mcoder_production database)
- ✅ Production-grade database backend
- ✅ Users migrated from SQLite (2 users)
- ✅ Database features enabled (job history, persistent storage)
- ✅ Fixed dotenv loading in config.py
- ✅ Classification improvements (multiple variables, normalization)

### Upcoming (v1.4.0)
- 🔄 Multi-label classification
- 🔄 Email service upgrade (Brevo)
- 🔄 Batch upload optimization
- 🔄 Date range filter & pagination (Results page)
- 🔄 Export job list to CSV/Excel

---

## 🔍 QUICK COMMANDS CHEAT SHEET

```powershell
# Deploy ke Production
scp file.py root@145.79.10.104:/opt/markplus/mcoder-markplus/path/
ssh root@145.79.10.104 "supervisorctl restart mcoder-markplus"

# Check logs
ssh root@145.79.10.104 "tail -50 /var/log/mcoder/gunicorn.log"

# Rollback (di VPS)
cd /opt/markplus/mcoder-markplus
git checkout file.py  # rollback 1 file
git reset --hard HEAD~1  # rollback 1 commit

# Database migration (jika perlu)
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus
sqlite3 instance/mcoder.db "SQL COMMAND HERE"
```

---

**END OF DOCUMENT** - Simpan dokumen ini dan update saat ada perubahan major!
