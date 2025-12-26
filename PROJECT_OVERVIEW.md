# PROJECT OVERVIEW - M-Coder Platform

> **Master Project Documentation** - This document serves as the primary reference for all agents working on this project and will be continuously updated as development progresses.

> ⚠️ **IMPORTANT NOTE**: All communication with users in chat MUST use **Bahasa Indonesia**. Users prefer to communicate in Indonesian for project discussions and feedback.

## 🌐 DEPLOYMENT INFORMATION

### Production Environment
- **VPS Provider**: Hostinger
- **Server IP**: 145.79.10.104
- **OS**: Ubuntu 24.04 LTS
- **Domain**: flazinsight.com (managed via Cloudflare)
- **Application URL**: https://m-coder.flazinsight.com
- **Instance Path**: /opt/markplus/mcoder-markplus/

### Version Control & Deployment
- **Repository**: https://github.com/hary4di/mcoder-markplus
- **Visibility**: Public repository
- **Current Commit**: b02a93a - "Initial commit: M-Coder Platform"
- **Deployment Method**: Git-based automated workflow
- **Local Development**: Windows (OneDrive sync path)
- **Production**: VPS Ubuntu via Git pull

### Deployment Workflow (Development → Production)
**Automated Deployment (Recommended):**
```powershell
# From Windows local development
.\quick-deploy.ps1 -message "Deskripsi perubahan"
```

Script otomatis akan:
1. ✅ Git commit dengan message
2. ✅ Push ke GitHub
3. ✅ SSH ke VPS
4. ✅ Pull code terbaru
5. ✅ Update dependencies (jika ada perubahan requirements.txt)
6. ✅ Restart service via supervisorctl
7. ✅ Report deployment status

**Manual Deployment:**
```powershell
# Local (Windows)
git add .
git commit -m "Pesan commit"
git push
```

```bash
# VPS (Production)
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus
git pull
supervisorctl restart mcoder-markplus
```

**Rollback (jika ada masalah):**
```bash
# Di VPS
cd /opt/markplus/mcoder-markplus
git log --oneline -10  # Lihat commit history
git reset --hard <commit-hash>  # Rollback ke commit tertentu
supervisorctl restart mcoder-markplus
```

### Multi-Tenant Architecture
- **Structure**: Modular design supporting multiple company instances
- **Port Strategy**: Each instance runs on separate internal port (8000, 8001, 8002...)
- **Isolation**: Separate database, files, venv per instance
- **Web Server**: Nginx reverse proxy on port 80/443
- **Process Manager**: Supervisor for auto-restart
- **WSGI Server**: Gunicorn (4 workers, 300s timeout)

### SSL/TLS Configuration
- **Provider**: Cloudflare (Free tier)
- **SSL Mode**: Flexible (Cloudflare HTTPS → Origin HTTP)
- **Certificate**: Cloudflare Universal SSL (free)

### ⚠️ KNOWN LIMITATION: WWW Subdomain
**Issue**: `www.m-coder.flazinsight.com` tidak dapat digunakan karena:
- `www.m-coder` adalah **multi-level subdomain** (2 tingkat)
- Cloudflare Universal SSL (gratis) hanya cover **1-level subdomain**
- Contoh covered: `m-coder.flazinsight.com` ✅, `orange.flazinsight.com` ✅
- Contoh NOT covered: `www.m-coder.flazinsight.com` ❌

**Solusi**:
- ✅ **Menggunakan**: `https://m-coder.flazinsight.com` (tanpa www)
- ❌ **TIDAK menggunakan**: `www.m-coder.flazinsight.com`
- DNS record `www.m-coder` telah dihapus untuk menghindari konfusi

**Alternative (Paid Solution)**:
- Total TLS feature memerlukan **Advanced Certificate Manager** ($10/month)
- Atau order **Advanced Certificate** khusus untuk multi-level subdomain
- Saat ini solusi gratis lebih praktis dengan menggunakan domain tanpa www

---

## 💻 TECHNOLOGY STACK

### **"Dibuat Pakai Apa?"** - Quick Answer

**M-Coder Platform** adalah aplikasi web modern yang dibangun dengan:

**Backend:**
- **Python 3.11+** - Bahasa pemrograman utama
- **Flask 3.0** - Web framework untuk routing dan templating
- **SQLAlchemy** - ORM untuk database operations
- **SQLite** - Database untuk user accounts dan settings
- **OpenAI GPT-4o-mini** - AI engine untuk klasifikasi teks

**Frontend:**
- **Bootstrap 5.3** - CSS framework untuk responsive UI
- **Bootstrap Icons** - Icon library
- **JavaScript (Vanilla)** - Interaktivitas dan AJAX
- **Jinja2** - Template engine (built-in Flask)
- **HTML5 & CSS3** - Markup dan styling

**Libraries & Tools:**
- **pandas** - Excel file processing dan data manipulation
- **openpyxl** - Read/write Excel files (.xlsx)
- **requests** - HTTP client untuk Kobo API integration
- **python-dotenv** - Environment variables management
- **Flask-Login** - User authentication dan session management
- **smtplib** (built-in) - Email service untuk OTP
- **concurrent.futures** (built-in) - Parallel processing dengan ThreadPoolExecutor
- **threading** (built-in) - Thread-safe operations dan synchronization

**Development Tools:**
- **VS Code** - Code editor
- **Git** - Version control
- **pip** - Package manager
- **virtualenv** - Python virtual environment

---

## 🏗️ ARSITEKTUR TEKNIS

### Application Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT LAYER                           │
│  (Browser: Chrome, Firefox, Safari, Edge)                   │
│                                                              │
│  HTML + CSS (Bootstrap 5) + JavaScript                      │
│  • Responsive Design (Mobile-first)                         │
│  • AJAX untuk real-time updates                             │
│  • Server-Sent Events (SSE) untuk progress tracking         │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/HTTPS
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                   Flask Web Application                      │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Routes (app/routes.py)                             │   │
│  │  • Dashboard, Upload, Classification, Results       │   │
│  │  • User Management, Profile, Settings               │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Authentication (app/auth.py)                       │   │
│  │  • Login, Register, Forgot/Reset Password           │   │
│  │  • Flask-Login session management                   │   │
│  │  • Role-based access control                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Business Logic                                      │   │
│  │  • FileProcessor (app/utils.py)                     │   │
│  │  • ExcelClassifier (excel_classifier.py)            │   │
│  │  • ProgressTracker (app/progress_tracker.py)        │   │
│  └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Data Access Layer                                   │   │
│  │  • Models (app/models.py) - SQLAlchemy ORM          │   │
│  │  • Database Session Management                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     DATA LAYER                               │
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │  SQLite DB    │  │  Excel Files │  │  Log Files      │  │
│  │  (users.db)   │  │  (uploads/)  │  │  (files/logs/)  │  │
│  └───────────────┘  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  EXTERNAL SERVICES                           │
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  OpenAI API      │         │  Gmail SMTP      │         │
│  │  (Classification)│         │  (Email OTP)     │         │
│  └──────────────────┘         └──────────────────┘         │
│                                                              │
│  ┌──────────────────┐                                       │
│  │  Kobo Toolbox API│  [OPTIONAL]                          │
│  │  (Data Upload)   │                                       │
│  └──────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘
```

### Folder Structure

```
koding/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory, extensions init
│   ├── models.py                # SQLAlchemy models (User, Settings)
│   ├── routes.py                # Main routes (dashboard, classify, results)
│   ├── auth.py                  # Authentication routes (login, register, etc)
│   ├── forms.py                 # WTForms (if used)
│   ├── utils.py                 # FileProcessor, helpers
│   ├── email_service.py         # SMTP email sending
│   ├── progress_tracker.py      # Thread-safe progress monitoring
│   ├── static/                  # Static assets
│   │   ├── css/                # Custom CSS
│   │   ├── js/                 # Custom JavaScript
│   │   └── images/             # Images, icons
│   └── templates/              # Jinja2 HTML templates
│       ├── base.html           # Base layout dengan sidebar
│       ├── login.html          # Authentication pages
│       ├── dashboard.html      # Main dashboard
│       ├── classify.html       # Upload & classification
│       ├── results.html        # Results viewer
│       └── ...                 # Other pages
│
├── files/                       # Working directory
│   ├── uploads/                # User uploaded Excel files
│   ├── output/                 # Classified Excel outputs
│   ├── logs/                   # Application logs
│   └── logo/                   # Company logo files
│
├── instance/                    # Instance-specific files
│   └── users.db                # SQLite database
│
├── config.py                    # Configuration class
├── run_app.py                   # Application entry point
├── excel_classifier.py          # Excel-based classification module
├── parallel_classifier.py       # Parallel processing helper (NEW!)
├── openai_classifier.py         # OpenAI API client
├── kobo_client.py              # Kobo API client
├── kobo_uploader.py            # Kobo upload functionality
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (SECRET!)
├── .gitignore                  # Git ignore rules
├── README.md                   # Project readme
├── PROJECT_OVERVIEW.md         # This file
├── PARALLEL_PROCESSING.md      # Parallel processing documentation (NEW!)
└── ADMIN_GUIDE_PARALLEL.md     # Admin guide for parallel settings (NEW!)
```

### Design Patterns Used

1. **MVC Pattern** (Model-View-Controller)
   - **Model:** `app/models.py` - Database models
   - **View:** `app/templates/` - HTML templates
   - **Controller:** `app/routes.py`, `app/auth.py` - Route handlers

2. **Factory Pattern**
   - `create_app()` function in `app/__init__.py`
   - Allows multiple app instances with different configs

3. **Blueprint Pattern**
   - `main` blueprint untuk main routes
   - `auth` blueprint untuk authentication routes
   - Modular dan scalable

4. **Repository Pattern**
   - SQLAlchemy models encapsulate database access
   - Clean separation of data layer

5. **Service Layer Pattern**
   - `FileProcessor` untuk file handling
   - `ExcelClassifier` untuk classification logic
   - `ProgressTracker` untuk progress monitoring
   - `EmailService` untuk email operations

---

## 🔧 CARA KERJA APLIKASI (Technical Flow)

### 1. Application Startup

```python
# run_app.py
from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()  # Create tables if not exist
    
app.run(host='0.0.0.0', port=5000, debug=True)
```

### 2. Request Flow Example (Classification)

```
User clicks "Upload & Analyze"
    ↓
JavaScript AJAX request ke /upload_files
    ↓
Flask route handler (@app.route('/upload_files'))
    ↓
FileProcessor.process_files()
    ├─ Validate Excel files
    ├─ Read kobo_system survey sheet
    ├─ Auto-detect open-ended variables
    └─ Save to session
    ↓
Return JSON response { success: true, redirect: '/select-variables' }
    ↓
User selects variables & settings
    ↓
Submit ke /start_classification
    ↓
Background thread starts
    ├─ ProgressTracker initialized
    ├─ For each variable:
    │   ├─ ExcelClassifier.classify_variable()
    │   │   ├─ Phase 1: Generate categories (OpenAI API)
    │   │   ├─ Phase 2: Classify responses (OpenAI API)
    │   │   └─ Phase 3: Outlier re-analysis
    │   └─ Update progress
    └─ Save results to Excel
    ↓
Client polls /progress via SSE
    ↓
Display real-time progress updates
    ↓
Redirect to /results on completion
```

### 3. Authentication Flow

```
User opens /login
    ↓
Enter username & password
    ↓
POST to /login
    ↓
User.query.filter_by(username=...).first()
    ↓
check_password(password) - bcrypt verify
    ↓
If valid:
    login_user(user, remember=remember_me)
    ↓
    Flask-Login creates session
    ↓
    Redirect to /dashboard
Else:
    Flash error message
    ↓
    Show login form again
```

### 4. OTP Email Flow

```
User clicks "Forgot Password"
    ↓
Enter email
    ↓
POST to /forgot-password
    ↓
Generate 6-digit OTP
otp = ''.join([str(random.randint(0,9)) for _ in range(6)])
    ↓
Store in database
user.otp = otp
user.otp_expiry = now + 10 minutes
    ↓
Send email via SMTP
send_password_reset_email(email, name, otp)
    ↓
User checks email
    ↓
Enter OTP in /reset-password
    ↓
Validate OTP
    ├─ Check expiry: now < user.otp_expiry
    └─ Check match: otp == user.otp
    ↓
If valid:
    Allow password reset
    user.set_password(new_password)
    user.otp = None  # Clear OTP
    ↓
    Redirect to /login
```

---

## 🎯 PRIMARY PROJECT GOAL

Build an **Automated Web-Based Dashboard with User-Friendly Interface** for automating the coding/classification process of open-ended survey responses. This application is designed for **non-technical users** without a technical background.

### Target Users
- **Research Team** at MarkPlus Indonesia
- **Data Processors** handling survey data
- **Analysts** requiring coded results for analysis
- **Non-technical users** who only need to operate the application without understanding the underlying mechanics

### Application Modes
1. **Web Dashboard** (Primary) - Flask-based GUI for easy operation
2. **Command-Line** (Alternative) - For technical users and automation scripts

---

## 📊 JENIS PERTANYAAN YANG DI-HANDLE

Aplikasi ini akan menghandle **2 jenis pertanyaan open-ended**:

### 1. **Open-Ended Murni** ✅ *[STATUS: COMPLETED]*
- Pertanyaan yang sejak awal sudah terbuka (tidak ada pilihan jawaban)
- Responden bebas menulis jawaban apapun
- **Contoh**: 
  - "Pengembangan apa yang diharapkan di Ferizy?"
  - "Saran dan masukan untuk perbaikan layanan?"

**Implementation Status:**
- ✅ Module classification (OpenAI GPT-4o-mini) - COMPLETED
- ✅ Excel classifier with hybrid approach - COMPLETED
- ✅ Kobo API integration - COMPLETED
- ✅ Validation & invalid response handling - COMPLETED
- ✅ Web Dashboard Interface - COMPLETED
- ⏳ Progress Tracking - IN PROGRESS (migrating to AJAX polling)

### 2. **Semi Open-Ended (Pre-Coded)** ✅ *[STATUS: IMPLEMENTED]*
- Pertanyaan dengan pilihan jawaban yang sudah ada
- Terdapat opsi "Lainnya" yang memunculkan kolom tambahan untuk jawaban terbuka
- **Contoh**:
  ```
  Q: Dengan siapa Anda paling sering bepergian menggunakan layanan ASDP?
  [ ] Suami / istri
  [ ] Orang tua
  [ ] Anak
  [ ] Teman
  [✓] Lainnya: ________ ← Jika dipilih, akan muncul field S10_L untuk text input
  ```

**Implementation Status:**
- ✅ Detection module (semi_open_detector.py) - COMPLETED
- ✅ Processing module (semi_open_processor.py) - COMPLETED
- ✅ Merge logic (pre-coded + classified) - COMPLETED
- ✅ Choices sheet update - COMPLETED
- ✅ Web UI integration - COMPLETED
  * File upload detection (/upload-files route)
  * Dedicated UI section in select_variables.html
  * Background processing (run_semi_open_background)
  * Results display with cost savings info

**How It Works:**
1. **Detection Phase:**
   - Scan choices sheet untuk opsi "Lainnya" (biasanya code 96)
   - Identify pair: select variable (S10) + text variable (S10_L)
   - Extract question labels dan metadata

2. **Classification Phase:**
   - Extract responses yang pilih "Lainnya" (S10 = 96)
   - Classify S10_L text responses menggunakan AI
   - Generate categories untuk "Lainnya" responses

3. **Merging Phase:**
   - Create merged variable (S10_merged)
   - Logic: 
     * If S10 != 96 → use original pre-coded label
     * If S10 = 96 → use AI classification dari S10_L
   - Assign new codes (starting from max_existing_code + 1)

4. **Update Phase:**
   - Insert new categories ke choices sheet
   - Add new list items dengan codes baru
   - Save merged results to Excel

**Example Output:**
```
Original Data:
S10  | S10_L                    | S10_merged | S10_merged_label
-----|--------------------------|------------|---------------------------
1    | (empty)                  | 1          | Suami / istri
2    | (empty)                  | 2          | Orang tua
96   | Rekan kerja              | 7          | Rekan Kerja/Kolega
96   | Sendirian                | 8          | Sendiri
3    | (empty)                  | 3          | Anak

Choices Sheet (Updated):
list_name | name | label
----------|------|------------------------
S10       | 1    | Suami / istri
S10       | 2    | Orang tua
S10       | 3    | Anak
S10       | 4    | Teman
S10       | 96   | Lainnya
S10       | 7    | Rekan Kerja/Kolega    <- New from AI
S10       | 8    | Sendiri               <- New from AI
```

---

## 🏗️ ARSITEKTUR APLIKASI

### Current Architecture (Dual-Mode: Web + CLI)

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  • Excel Files Upload (via Dashboard)                       │
│    - kobo_system_*.xlsx (Form structure + choices)          │
│    - Raw_Data_*.xlsx (Survey responses)                     │
│  • [Future] Kobo Toolbox API (Live data)                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    WEB INTERFACE                             │
├─────────────────────────────────────────────────────────────┤
│  Flask Application (app/)                                    │
│  • User Authentication (Flask-Login)                        │
│  • File Upload Interface                                    │
│  • Variable Selection UI                                    │
│  • Progress Monitoring Dashboard                            │
│  • Results Display & Download                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 PROCESSING LAYER                             │
├─────────────────────────────────────────────────────────────┤
│  1. Classification Engine (excel_classifier.py)             │
│     • Load Excel files                                      │
│     • Extract responses per variable                        │
│     • Coordinate classification process                     │
│     • Support PARALLEL PROCESSING (3-5x faster) ⚡          │
│                                                              │
│  2. Parallel Processing (parallel_classifier.py) [NEW!]     │
│     • Multi-worker concurrent batch processing              │
│     • ThreadPoolExecutor with configurable workers          │
│     • Thread-safe progress tracking with Lock               │
│     • Rate limiting to prevent API throttling               │
│     • Auto-selection: ≥100 responses → parallel mode        │
│     • Performance: 5 workers = 3-5x speedup                 │
│       Example: 2,482 responses: 17 min → 3-5 min ⚡         │
│                                                              │
│  3. AI Classification (openai_classifier.py)                │
│     Phase 1: Generate Categories                            │
│       • Sample 100% data (max 500)                          │
│       • Context-aware (question text)                       │
│       • Max 10 categories (configurable)                    │
│                                                              │
│     Phase 2: Classify Responses                             │
│       • Batch API calls (10 responses per request)          │
│       • Sequential OR Parallel mode (auto-select)           │
│       • Return category + confidence score                  │
│                                                              │
│     Phase 3: Outlier Re-analysis (Hybrid Approach)          │
│       • Identify low-confidence responses (<50%)            │
│       • Generate new categories if ≥10 outliers             │
│       • Re-classify outliers with updated categories        │
│                                                              │
│  4. Response Validation                                      │
│     - Filter invalid responses (TA, tidak ada, N/A, etc.)   │
│     - Empty responses → keep as null (Kobo logic)           │
│     - Invalid text → Code 99 (special category)             │
│                                                              │
│  5. Excel Processing (excel_classifier.py)                  │
│     - Process Excel-based workflow                          │
│     - Update kobo_system file with choices                  │
│     - Insert coded columns next to source columns           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT LAYER                               │
├─────────────────────────────────────────────────────────────┤
│  1. Excel Export                                             │
│     • Raw data + coded columns                              │
│     • kobo_system updated with choices                      │
│                                                              │
│  2. Kobo Upload (Optional - AUTO_UPLOAD_TO_KOBO=true)       │
│     • Create new field in Kobo form (e.g., E1_coded)        │
│     • Add choices list (1-10, 99)                           │
│     • Upload classification codes to all submissions        │
│                                                              │
│  3. Logs & Reports                                           │
│     • Classification logs with timestamps                   │
│     • Generated categories JSON                             │
│     • Sample responses for review                           │
│     • Summary statistics                                    │
└─────────────────────────────────────────────────────────────┘
```

### Target Architecture (GUI-based) *[FUTURE]*

```
┌─────────────────────────────────────────────────────────────┐
│                    GUI INTERFACE                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │              LOGIN SCREEN                            │   │
│  │  Username: [___________]                            │   │
│  │  Password: [___________]                            │   │
│  │           [Login Button]                            │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           MAIN DASHBOARD                             │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Project Selection                           │   │   │
│  │  │  [ ] Kobo API (Live Data)                    │   │   │
│  │  │  [ ] Excel Files (Offline Data)              │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Question Type                               │   │   │
│  │  │  ( ) Open-Ended Murni                        │   │   │
│  │  │  ( ) Semi Open-Ended (Pre-Coded)             │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │  Variables to Process                        │   │   │
│  │  │  [✓] E1 - Pengembangan Ferizy               │   │   │
│  │  │  [✓] E2 - Kemudahan Akses Aplikasi           │   │   │
│  │  │  [ ] E3 - ...                                │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                      │   │
│  │  Settings:                                           │   │
│  │  Max Categories: [10 ▼]                             │   │
│  │  Confidence Threshold: [0.50]                       │   │
│  │  Auto Upload to Kobo: [✓]                           │   │
│  │                                                      │   │
│  │  [    Start Classification    ]                     │   │
│  │                                                      │   │
│  │  Progress: [████████░░░░░░░░] 45%                  │   │
│  │  Status: Classifying E1 responses...                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           RESULTS VIEWER                             │   │
│  │  Categories Generated: 8                             │   │
│  │  Responses Classified: 1,328                         │   │
│  │  Average Confidence: 0.85                            │   │
│  │                                                       │   │
│  │  [View Excel Output]  [View Logs]  [Export Report]  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 SECURITY & AUTHENTICATION

### Requirement
- **Username & Password Authentication** diperlukan sebelum mengakses aplikasi
- Mencegah akses tidak sah dari orang yang tidak berwenang
- User credentials disimpan secara secure (encrypted)

### Implementation Status
- ✅ Authentication system - COMPLETED
- ✅ User management - COMPLETED
- ✅ Password encryption - COMPLETED (bcrypt)
- ✅ Session management - COMPLETED (Flask-Login)
- ✅ Role-based access control (super_admin, user) - COMPLETED
- ✅ Mobile-responsive authentication pages - COMPLETED

**Implementation Details:**
- Framework: **Flask** with Flask-Login extension
- Password hashing: **bcrypt** (via werkzeug.security)
- Session management: **Flask-Login** with remember me functionality
- Database: **SQLite** with SQLAlchemy ORM
- User roles: super_admin (full access), user (limited access)
- Mobile-responsive design for all auth pages
- OTP verification for password reset

### Authentication Pages (Mobile-Responsive)

#### 1. **Login Page** (`/login`)
**Features:**
- Username/email and password fields
- "Remember Me" checkbox for persistent session
- "Forgot Password?" link
- Responsive grid layout (col-12 col-sm-10 col-md-8 col-lg-5 col-xl-4)
- Adaptive padding (p-3 p-sm-4 p-md-5)
- Logo with responsive sizes (50px/45px desktop, 38px/40px mobile)
- Error flash messages for invalid credentials

**Implementation:**
```
app/templates/login.html - Main template
app/auth.py - Login route handler with Flask-Login
app/models.py - User model dengan check_password()
```

#### 2. **Register Page** (`/register`)
**Features:**
- Name, username, email, password, confirm password fields
- Email validation
- Password strength requirements
- Auto-login after successful registration
- Responsive design matching login page

**Validation:**
- Unique username dan email
- Password minimum 6 characters
- Password confirmation must match

#### 3. **Forgot Password Flow** (`/forgot-password`)
**Features:**
- Email input untuk request password reset
- Email validation (must exist in database)
- Generate 6-digit OTP code
- Send OTP via email (valid 10 minutes)
- Store OTP in database dengan expiry timestamp
- Responsive design

**Implementation:**
```python
# Generate OTP
otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
otp_expiry = datetime.utcnow() + timedelta(minutes=10)

# Store in user record
user.otp = otp
user.otp_expiry = otp_expiry
db.session.commit()

# Send email
send_password_reset_email(user.email, user.name, otp)
```

#### 4. **Reset Password Page** (`/reset-password`)
**Features:**
- OTP verification (6-digit code)
- New password input
- Confirm password input
- OTP expiry validation (max 10 minutes)
- Password update setelah OTP valid
- Auto-redirect to login after success

**Security:**
- OTP hanya valid 10 menit
- OTP di-clear setelah berhasil digunakan
- OTP validation case-insensitive
- Brute-force protection via expiry

### Email Service Integration

**Configuration:** (`app/email_service.py`)
- **SMTP Server:** Gmail (smtp.gmail.com:587)
- **TLS Encryption:** Enabled untuk security
- **From Address:** Configurable via `MAIL_USERNAME` in `.env`

**Environment Variables Required:**
```env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
```

**Email Templates:**
1. **Password Reset Email**
   - Subject: "M-Coder Platform - Password Reset Request"
   - Content: OTP code, expiry time (10 minutes)
   - Sender: M-Coder Team
   - HTML formatted dengan styling

**Email Sending Function:**
```python
def send_password_reset_email(to_email, user_name, otp):
    """Send OTP email untuk password reset"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "M-Coder Platform - Password Reset Request"
        
        # HTML body dengan OTP
        html = f"""
        <html>
        <body>
            <p>Hi {user_name},</p>
            <p>Your OTP code: <strong>{otp}</strong></p>
            <p>Valid for 10 minutes.</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send via SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email error: {str(e)}")
        return False
```

**Error Handling:**
- Try-catch untuk handle SMTP errors
- Logging untuk debugging
- User-friendly error messages
- Fallback jika email gagal terkirim

### Database Schema for Authentication

**User Model:** (`app/models.py`)
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user' or 'super_admin'
    otp = db.Column(db.String(6), nullable=True)  # For password reset
    otp_expiry = db.Column(db.DateTime, nullable=True)  # OTP expiry time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash password menggunakan bcrypt"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password terhadap hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_otp_valid(self):
        """Check apakah OTP masih valid (belum expired)"""
        if not self.otp or not self.otp_expiry:
            return False
        return datetime.utcnow() < self.otp_expiry
```

### Session Management

**Flask-Login Configuration:**
```python
# config.py
SECRET_KEY = 'your-secret-key-here'  # For session encryption
PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Session expiry

# app/__init__.py
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
```

**Login Protection:**
```python
# Protect routes dengan @login_required decorator
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Access current user dengan current_user
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
```

### Mobile-Responsive Authentication Design

**Breakpoints:**
- **< 576px** (Small mobile): Reduced padding, smaller logos, compact buttons
- **576px - 768px** (Mobile): Medium padding, standard sizes
- **768px - 992px** (Tablet): Increased padding, larger elements
- **> 992px** (Desktop): Full padding, optimal spacing

**Responsive Features:**
- Adaptive form widths (col-12 → col-lg-5 → col-xl-4)
- Logo size variants (d-none d-sm-inline classes)
- Font size adjustments (fs-4 fs-md-3)
- Button padding variations (10px mobile, 12px desktop)
- Input field sizing adapts to screen width

**CSS Media Queries:**
```css
@media (max-width: 576px) {
    .auth-card { padding: 1.5rem !important; }
    .auth-card h2 { font-size: 1.4rem !important; }
    .btn-auth { font-size: 0.95rem; padding: 10px; }
    .form-label { font-size: 0.85rem; }
}
```

---

## 🔄 WORKFLOW APLIKASI

### Workflow Open-Ended Murni (Current)

```
START
  ↓
[1] User Login → Verify credentials
  ↓
[2] Select Data Source
  ├─→ Kobo API (Live)
  └─→ Excel Files (Offline)
  ↓
[3] Select Question Type
  └─→ Open-Ended Murni
  ↓
[4] Select Variables to Process (E1, E2, etc.)
  ↓
[5] Configure Settings
  ├─ Max Categories
  ├─ Confidence Threshold
  └─ Auto Upload to Kobo
  ↓
[6] START CLASSIFICATION
  ↓
[7] Fetch Data
  ├─ From Kobo API OR
  └─ From Excel Files
  ↓
[8] Extract Responses for Each Variable
  ↓
[9] Validate Responses
  ├─ Filter invalid (TA, tidak ada, N/A)
  ├─ Keep empty as null
  └─ Mark invalid text → Code 99
  ↓
[10] Phase 1: Generate Categories (AI)
  ├─ Sample 100% data (max 500)
  ├─ Context-aware classification
  └─ Generate max 10 categories
  ↓
[11] Phase 2: Classify All Responses (AI)
  ├─ Auto-select mode:
  │   ├─ ≥100 responses → Parallel mode (ThreadPoolExecutor) ⚡
  │   └─ <100 responses → Sequential mode
  ├─ Parallel Processing (NEW!):
  │   ├─ Split into batches (configurable workers: 1-15)
  │   ├─ Concurrent API calls with rate limiting
  │   ├─ Thread-safe progress tracking
  │   └─ 3-5x speedup vs sequential
  ├─ Sequential Processing (fallback):
  │   ├─ Batch by 10 responses
  │   └─ One batch at a time
  └─ Output: category + confidence score for each response
  ↓
[12] Phase 3: Outlier Re-analysis (Hybrid)
  ├─ Identify outliers (confidence < 50%)
  ├─ If ≥10 outliers → Generate new categories
  └─ Re-classify outliers
  ↓
[13] Export Results
  ├─ Update Excel files
  │   ├─ Insert coded columns
  │   └─ Update kobo_system choices
  │
  └─ (Optional) Upload to Kobo
      ├─ Create new field (E1_coded)
      ├─ Add choices list
      └─ Upload codes to submissions
  ↓
[14] Show Results Summary
  ├─ Categories generated
  ├─ Responses classified
  ├─ Confidence statistics
  └─ Output file locations
  ↓
[15] User Review & Export
  ├─ View Excel output
  ├─ View logs
  └─ Export report
  ↓
END
```

### Workflow Semi Open-Ended (Future)

```
[Coming Soon - To Be Designed]
```

---

## 📦 MODULES & FILES

### Core Processing Modules

| File | Purpose | Status |
|------|---------|--------|
| `excel_classifier.py` | Excel-based classification workflow | ✅ COMPLETED |
| `openai_classifier.py` | AI classification engine (GPT-4o-mini) | ✅ COMPLETED |
| `parallel_classifier.py` | ⚡ Multi-worker concurrent batch processing | ✅ COMPLETED |
| `kobo_client.py` | Kobo Toolbox API client | ✅ COMPLETED |
| `kobo_uploader.py` | Upload results to Kobo | ✅ COMPLETED |
| `main.py` | CLI-based pipeline orchestrator | ✅ COMPLETED |

### Web Application (Dashboard)

| File/Folder | Purpose | Status |
|------|---------|--------|
| `run_app.py` | Flask application entry point | ✅ COMPLETED |
| `config.py` | Flask configuration | ✅ COMPLETED |
| `app/__init__.py` | Flask app factory | ✅ COMPLETED |
| `app/routes.py` | Main routes & classification logic | ✅ COMPLETED |
| `app/auth.py` | Authentication routes (login/logout) | ✅ COMPLETED |
| `app/models.py` | Database models (User) | ✅ COMPLETED |
| `app/forms.py` | Flask-WTF forms | ✅ COMPLETED |
| `app/utils.py` | File processor utilities | ✅ COMPLETED |
| `app/progress_tracker.py` | Progress tracking for background jobs | ⏳ IN PROGRESS |
| `app/email_service.py` | Email service for OTP | ✅ COMPLETED |
| `app/templates/` | HTML templates (Jinja2) | ✅ COMPLETED |
| `app/templates/admin_settings.html` | Admin settings panel (6 tabs) | ✅ COMPLETED |
| `app/static/` | CSS, JS, images | ✅ COMPLETED |
| `instance/` | Instance folder (database) | ✅ COMPLETED |

### Admin Settings Panel (NEW!)

**Location:** `/admin/settings` (Admin-only access)

**6 Configuration Tabs:**

1. **OpenAI API** ⚙️
   - API Key configuration
   - Model selection (gpt-4o-mini, gpt-4o, gpt-4-turbo)
   - Usage tips and cost information

2. **Brevo Email** 📧
   - Brevo API Key for OTP emails
   - Sender email and name configuration
   - Connection test button

3. **Classification Settings** 🎯
   - Invalid category label & code
   - Max categories per variable
   - Multi-label configuration:
     * Enable/disable multi-label
     * Min category confidence (0.3-0.9)
     * Max categories per response (1-5)
     * Single category threshold (0.7-1.0)

4. **Parallel Processing** ⚡ (NEW!)
   - Enable/disable parallel mode
   - Number of workers (1-15) - concurrent batch processing
   - Rate limit delay (0.01-1.0s) - API throttle prevention
   - Quick presets:
     * Conservative: 3 workers, 0.2s delay (safe)
     * Balanced: 5 workers, 0.1s delay (recommended)
     * Aggressive: 10 workers, 0.05s delay (fast but risky)
   - Performance calculator (estimate speedup)
   - Configuration guide with OpenAI tier limits

5. **AI Prompts** 💬
   - Multi-label classification prompt template
   - Single-label classification prompt template
   - Variable placeholders for customization

6. **Invalid Patterns** ⚠️
   - List of invalid response patterns
   - Case-insensitive matching
   - Auto-code as 99 without AI call

**Database Storage:**
- All settings saved to `system_settings` table
- Auto-sync with `.env` file on save
- Priority: Database > .env > defaults

**Key Features:**
- Real-time input validation
- Tooltips with helpful explanations
- Preset buttons for quick configuration
- Visual feedback on changes
- Admin-only access control
- Mobile-responsive design

### Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Environment variables & API keys | ✅ CONFIGURED |
| `.env.example` | Example environment file | ✅ COMPLETED |
| `requirements.txt` | Python dependencies | ✅ COMPLETED |
| `.gitignore` | Git ignore rules | ✅ COMPLETED |

### Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | User documentation | ✅ COMPLETED |
| `PROJECT_OVERVIEW.md` | This file - Project blueprint | ✅ IN PROGRESS |
| `INSTALL_PYTHON.md` | Python installation guide | ✅ COMPLETED |
| `.github/copilot-instructions.md` | AI coding guide | ✅ COMPLETED |

### Setup & Utility Scripts

| File | Purpose | Status |
|------|---------|--------|
| `setup_admin.py` | Create admin user for dashboard | ✅ COMPLETED |
| `create_admin.bat` | Batch file to create admin | ✅ COMPLETED |
| `run.bat` | Windows batch runner for CLI mode | ✅ COMPLETED |

### Data Directories

| Folder | Purpose | Contents |
|--------|---------|----------|
| `files/uploads/` | Uploaded Excel files | User data files |
| `files/logs/` | Classification logs | JSON logs, samples |
| `files/output/` | Classification results | Excel outputs |

---

## 🎨 WEB DASHBOARD (CURRENT IMPLEMENTATION)

Untuk development GUI, ada beberapa opsi framework:

### Option 1: **Desktop Application (Tkinter)** ⭐ *RECOMMENDED for Non-Tech Users*
**Pros:**
- Native Python, tidak perlu install browser
- Simple dan straightforward
- User bisa double-click executable file
- Tidak perlu port/server setup

**Cons:**
- Tampilan kurang modern
- Customization terbatas
- Deployment butuh executable builder (PyInstaller)

**Stack:**
- `tkinter` - Main GUI framework
- `ttkbootstrap` - Modern styling untuk tkinter
- `PyInstaller` - Build .exe file

### Option 2: **Web Application (Flask)** ⭐ *RECOMMENDED for Modern UI*
**Pros:**
- UI lebih modern dan responsive
- Mudah di-customize dengan Bootstrap/Tailwind
- Cross-platform (Windows, Mac, Linux)
- Bisa diakses dari browser

**Cons:**
- Perlu running web server (localhost)
- User harus buka browser
- Setup sedikit lebih complex

**Stack:**
- `Flask` - Web framework
- `Flask-Login` - Authentication
- `Bootstrap 5` - Modern UI styling
- `SQLite` - User database

### Option 3: **Hybrid (Electron-like with Eel)**
**Pros:**
- Web UI tapi packaging seperti desktop app
- Modern UI dengan HTML/CSS/JS
- Single executable file

**Cons:**
- File size besar
- Memory usage lebih tinggi

**Stack:**
- `Eel` - Python-JavaScript bridge
- `React` atau `Vue.js` - Frontend framework

---

## ⚙️ CONFIGURATION (.env)

### Current Settings

```env
# Kobo Toolbox API
KOBO_ASSET_ID=aQJhqngNsednTaWshNJwN6
KOBO_API_TOKEN=ce8031937f379146a0487560a91ae2abcdc478be
KOBO_BASE_URL=https://kf.kobotoolbox.org

# OpenAI API
OPENAI_API_KEY=sk-proj-...  # AI classification engine
MODEL=gpt-4o-mini  # Most economical (~$0.15/1M tokens)

# Classification Settings
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.7
CATEGORY_SAMPLE_RATIO=1.0  # 100% sampling
MAX_SAMPLE_SIZE=500
ENABLE_STRATIFIED_SAMPLING=true

# Hybrid Approach Settings
MIN_CONFIDENCE_THRESHOLD=0.50  # Outlier threshold
MIN_OUTLIERS_FOR_NEW_CATEGORY=10
MAX_NEW_CATEGORIES=3

# Invalid Response Handling
INVALID_RESPONSE_CATEGORY=Tidak Ada Jawaban
INVALID_RESPONSE_CODE=99

# Kobo Upload Settings
AUTO_UPLOAD_TO_KOBO=true
CODED_FIELD_SUFFIX=_coded

# Parallel Processing Settings (NEW!)
ENABLE_PARALLEL_PROCESSING=true  # Enable for 3-5x speedup
PARALLEL_MAX_WORKERS=5  # Number of concurrent workers (1-15)
RATE_LIMIT_DELAY=0.1  # Delay between API requests (seconds)
# Presets:
#   Conservative: 3 workers, 0.2s delay (safe for free tier)
#   Balanced: 5 workers, 0.1s delay (recommended for Tier 2)
#   Aggressive: 10 workers, 0.05s delay (Tier 3+, risky)

# Authentication & Security
SECRET_KEY=your_secret_key_for_session_encryption
# Generate dengan: python -c "import secrets; print(secrets.token_hex(32))"

# Email Service (untuk Password Reset OTP)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password
# Cara setup Gmail App Password:
# 1. Enable 2FA di Google Account
# 2. Generate App Password di: https://myaccount.google.com/apppasswords
# 3. Gunakan App Password (bukan password utama)
```

**Email Service Configuration Notes:**
- **SMTP Server:** Gmail (smtp.gmail.com:587) dengan TLS encryption
- **Security:** Jangan gunakan password utama Gmail, harus App Password
- **Alternative SMTP:** Bisa gunakan Outlook, Yahoo, atau SMTP server lain
- **Testing:** Test email dengan `python -c "from app.email_service import test_email; test_email()"`

### Future Settings (GUI)

```env
# Session Management
SESSION_TIMEOUT=3600  # 1 hour
PERMANENT_SESSION_LIFETIME=604800  # 7 days (for "Remember Me")

# GUI Settings
THEME=light  # light or dark
LANGUAGE=id  # id or en
```

---

## 📊 DATA FLOW

### Auto-Detection Strategy 🎯

**Detection Algorithm** (implemented in `app/utils.py`)
```python
Read kobo_system → survey sheet
Filter rows where:
  - type = "text" (text field questions)
  - name NOT in profile_fields (nama, alamat, telepon, email, ktp, dll)
  - name NOT starts with "S" (screening/demografi fields)
  - label NOT contains "lainnya" OR "sebutkan" (excludes semi open-ended)
Return: List of pure open-ended evaluation questions
```

**Profile Fields yang Di-exclude**:
```
nama, name, alamat, address, telepon, phone, hp, email, ktp, nik,
interviewer, enumerator, tanggal, date, waktu, time, lokasi, wilayah
```

**Example Detection**:
```
kobo_system survey sheet:
┌──────────┬──────────┬─────────────────────────────────────────────┐
│ type     │ name     │ label                                       │
├──────────┼──────────┼─────────────────────────────────────────────┤
│ text     │ nama     │ Nama responden                              │ ❌ EXCLUDED (profil)
│ text     │ alamat   │ Alamat rumah                                │ ❌ EXCLUDED (profil)
│ text     │ telepon  │ No telepon                                  │ ❌ EXCLUDED (profil)
│ text     │ email    │ Email (jika ada)                            │ ❌ EXCLUDED (profil)
│ text     │ S1       │ Nama kapal yang digunakan                   │ ❌ EXCLUDED (screening)
│ integer  │ S2       │ Umur                                        │ ❌ EXCLUDED (not text)
│ text     │ E1       │ Pengembangan apa yang diharapkan...         │ ✅ DETECTED
│ text     │ E2       │ Bagaimana tingkat kemudahan...              │ ✅ DETECTED
│ text     │ E3       │ Alasan lainnya, sebutkan...                 │ ❌ EXCLUDED (semi OE)
└──────────┴──────────┴─────────────────────────────────────────────┘

Detected: E1, E2 (hanya pertanyaan evaluasi open-ended murni)
Excluded: profil (nama, alamat, dll), screening (S*), semi OE (label "lainnya/sebutkan")
```

---

## 🚀 DEPLOYMENT & INFRASTRUCTURE

### Development Environment

**Local Development:**
```bash
# Clone repository
git clone <repo-url>
cd koding

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env  # Edit dengan credentials

# Initialize database
python setup_admin.py

# Run application
python run_app.py

# Access: http://localhost:5000
```

**System Requirements:**
- Python 3.11 or higher
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Internet connection (untuk OpenAI API)

### Production Deployment Options

#### Option 1: **Windows Server (On-Premise)**
**Recommended untuk MarkPlus internal deployment**

```bash
# Install Python 3.11+
# Install dependencies
pip install -r requirements.txt

# Install production WSGI server
pip install waitress

# Create service script (run_production.py)
from waitress import serve
from app import create_app

app = create_app()
serve(app, host='0.0.0.0', port=5000, threads=4)

# Run as Windows Service (using NSSM)
nssm install MCoder "C:\Python311\python.exe" "C:\path\to\run_production.py"
nssm start MCoder
```

**Setup IIS Reverse Proxy (Optional):**
- Install URL Rewrite Module
- Configure reverse proxy ke localhost:5000
- Setup SSL certificate
- Configure domain (e.g., mcoder.markplusinc.com)

#### Option 2: **Linux Server (VPS/Cloud)**

```bash
# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx

# Setup project
cd /var/www/koding
pip install -r requirements.txt
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/mcoder.service

[Unit]
Description=M-Coder Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/koding
Environment="PATH=/var/www/koding/venv/bin"
ExecStart=/var/www/koding/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run_app:app

[Install]
WantedBy=multi-user.target

# Start service
sudo systemctl start mcoder
sudo systemctl enable mcoder

# Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/mcoder

server {
    listen 80;
    server_name mcoder.markplusinc.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable SSL with Let's Encrypt
sudo certbot --nginx -d mcoder.markplusinc.com
```

#### Option 3: **Cloud Platform (Managed)**

**Heroku:**
```bash
# Create Procfile
web: gunicorn run_app:app

# Deploy
heroku create mcoder-markplus
git push heroku main
heroku config:set SECRET_KEY=xxx OPENAI_API_KEY=yyy
```

**Railway.app / Render.com:**
- Connect GitHub repository
- Set environment variables via dashboard
- Auto-deploy on git push

**AWS / Azure / Google Cloud:**
- Deploy on EC2 / App Service / Cloud Run
- Setup managed database (RDS, Azure SQL)
- Configure load balancer & auto-scaling

### Database Migration Strategy

**Development (SQLite):**
```python
# Good for: Development, testing, small teams
DATABASE_URL = 'sqlite:///instance/users.db'
Max users: ~50
Max concurrent: 5-10
```

**Production (PostgreSQL):**
```python
# Good for: Production, large teams, high traffic
DATABASE_URL = 'postgresql://user:pass@host:5432/mcoder'
Max users: Unlimited
Max concurrent: 100+

# Migration steps:
1. Install psycopg2: pip install psycopg2-binary
2. Update config.py: SQLALCHEMY_DATABASE_URI
3. Export data: flask db-export
4. Import to PostgreSQL: flask db-import
```

### Scaling Considerations

**Vertical Scaling (Single Server):**
```
Current: 2 CPU, 4GB RAM → Handles ~50 concurrent users
Upgrade: 4 CPU, 8GB RAM → Handles ~200 concurrent users
Upgrade: 8 CPU, 16GB RAM → Handles ~500 concurrent users
```

**Horizontal Scaling (Multiple Servers):**
```
┌─────────────┐
│ Load Balancer│
└──────┬───────┘
       ├──────────┬──────────┐
       │          │          │
   ┌───▼───┐  ┌───▼───┐  ┌───▼───┐
   │Web App│  │Web App│  │Web App│
   │Server 1│ │Server 2│ │Server 3│
   └───┬───┘  └───┬───┘  └───┬───┘
       └──────────┴──────────┘
                  │
         ┌────────▼─────────┐
         │Shared PostgreSQL │
         │   + Redis Cache  │
         └──────────────────┘
```

### Monitoring & Maintenance

**Application Monitoring:**
```python
# Add logging
import logging
logging.basicConfig(filename='app.log', level=logging.INFO)

# Monitor metrics
- Request response time
- Error rate
- Active users
- Classification success rate
- OpenAI API usage & cost
```

**Health Check Endpoint:**
```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'database': db_connected(),
        'openai': openai_available(),
        'version': '1.0.0'
    }
```

**Backup Strategy:**
```bash
# Daily database backup
0 2 * * * python backup_database.py

# Weekly full backup
0 3 * * 0 tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/koding
```

### Security Best Practices

**Production Checklist:**
- [ ] `DEBUG = False` in production
- [ ] Strong `SECRET_KEY` (64+ characters random)
- [ ] HTTPS enabled (SSL certificate)
- [ ] Rate limiting on API endpoints
- [ ] Input validation & sanitization
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection (Jinja2 auto-escaping)
- [ ] CSRF protection (Flask-WTF)
- [ ] Password hashing (bcrypt)
- [ ] Regular security updates
- [ ] Firewall configured (only port 443, 80)
- [ ] Separate .env file (not in git)
- [ ] Database credentials in environment variables
- [ ] API keys secured (OpenAI, Kobo)
- [ ] Regular backups tested
- [ ] Access logs monitored
- [ ] Error tracking (Sentry/Rollbar)

---

## 📊 PERFORMANCE & COST OPTIMIZATION

### OpenAI API Usage & Cost

**Model Selection:**
- **GPT-4o-mini** - Most cost-effective
  - Price: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
  - Speed: Fast (~1-2 seconds per request)
  - Accuracy: High untuk classification tasks

**Cost Estimation:**
```
Scenario: 1,000 responses untuk 1 variable

Phase 1 - Generate Categories:
- Sample: 500 responses (max)
- Tokens: ~50,000 input + ~2,000 output
- Cost: $0.0075 + $0.0012 = $0.0087

Phase 2 - Classify Responses:
- Requests: 1,000 responses
- Tokens per request: ~200 input + ~50 output
- Total tokens: 200K input + 50K output
- Cost: $0.03 + $0.03 = $0.06

Phase 3 - Outlier Re-analysis (if needed):
- Outliers: ~50 responses (5%)
- Additional cost: ~$0.005

Total per variable: ~$0.08 (~Rp 1,300)
Total untuk 5 variables: ~$0.40 (~Rp 6,300)

Rate: 1 USD = Rp 15,700 (December 2025)
```

**Cost Examples in IDR:**
```
1,000 responses (1 variable)   = Rp 1,300
5,000 responses (1 variable)   = Rp 6,500
10,000 responses (1 variable)  = Rp 13,000

1,000 responses (5 variables)  = Rp 6,500
5,000 responses (5 variables)  = Rp 32,500
10,000 responses (5 variables) = Rp 65,000

1,000 responses (10 variables)  = Rp 13,000
5,000 responses (10 variables)  = Rp 65,000
10,000 responses (10 variables) = Rp 130,000
```

**Perbandingan dengan Manual Coding:**
```
Manual Coding:
- Coder rate: Rp 150,000 - Rp 300,000 per 1,000 responses
- Waktu: 1-3 hari per 1,000 responses
- Total 10,000 responses: Rp 1,500,000 - Rp 3,000,000

M-Coder (AI):
- Cost: Rp 13,000 per 10,000 responses
- Waktu: ~40 menit
- Saving: 99% lebih murah! (Rp 13K vs Rp 1.5-3 juta)
```

**Cost Optimization Strategies:**
1. **Sampling:** Limit category generation to 500 responses max
2. **Batching:** Process multiple responses in single request (future)
3. **Caching:** Cache generated categories untuk similar projects
4. **Prompt Engineering:** Reduce token usage dengan efficient prompts
5. **Model Selection:** Use cheapest model that meets accuracy requirements

### Application Performance

**Response Time Targets:**
```
Page Load: < 1 second
File Upload: < 5 seconds (depends on file size)
Classification (SEQUENTIAL MODE):
  - 100 responses: ~30 seconds
  - 500 responses: ~2 minutes
  - 1,000 responses: ~4 minutes
  - 2,500 responses: ~8 minutes
  - 5,000 responses: ~20 minutes

Classification (PARALLEL MODE - 5 workers): ⚡ NEW!
  - 100 responses: ~15 seconds (2x faster)
  - 500 responses: ~45 seconds (2.7x faster)
  - 1,000 responses: ~1 minute (4x faster)
  - 2,500 responses: ~2-3 minutes (3-4x faster)
  - 5,000 responses: ~5-7 minutes (3-4x faster)
```

**Real-World Performance Example:**
```
Dataset: 2,482 responses (E2 + E3 variables)

Sequential Processing:
  - Time: 16 minutes 58 seconds
  - Rate: 146 responses/minute
  - API calls: 248 batches (sequential)

Parallel Processing (5 workers):
  - Time: 3-5 minutes ⚡
  - Rate: 500-800 responses/minute
  - API calls: 248 batches (concurrent)
  - Speedup: 3-5x faster!
  - Savings: ~12 minutes per run
```

**Parallel Processing Configuration:**
```
Conservative: 3 workers, 0.2s delay
  - Safe for free/Tier 1 OpenAI accounts
  - Speedup: 2-3x
  
Balanced (Recommended): 5 workers, 0.1s delay
  - Optimal for Tier 2 OpenAI accounts
  - Speedup: 3-5x
  
Aggressive: 10 workers, 0.05s delay
  - For Tier 3+ OpenAI accounts
  - Speedup: 6-8x (risky - may hit rate limits)
```

**Optimization Techniques:**
1. **Lazy Loading:** Load data only when needed
2. **Pagination:** Display results in chunks (50-100 per page)
3. **Caching:** Cache frequently accessed data in Redis
4. **Database Indexing:** Index commonly queried fields
5. **Async Processing:** Background jobs untuk long-running tasks
6. **Parallel Processing:** Multi-worker concurrent batch processing ⚡ NEW!
7. **CDN:** Serve static assets dari CDN (future)

**Database Optimization:**
```sql
-- Add indexes untuk faster queries
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_classification_date ON classification_results(created_at);
```

### Scalability Metrics

**Current Capacity (Single Server):**
- Concurrent users: 10-20
- **Classifications per hour (sequential):** ~600-700 responses
- **Classifications per hour (parallel, 5 workers):** ~2,000-3,500 responses ⚡ NEW!
- Database size: Up to 1GB
- File storage: Up to 10GB

**Processing Throughput Comparison:**
```
Dataset Size    Sequential      Parallel (5w)    Speedup
─────────────────────────────────────────────────────────
100 responses   30 seconds      15 seconds       2x
500 responses   2 minutes       45 seconds       2.7x
1,000 responses 4 minutes       1 minute         4x
2,500 responses 8 minutes       2-3 minutes      3-4x
5,000 responses 20 minutes      5-7 minutes      3-4x
10,000 responses 40 minutes     12-15 minutes    3-4x
```

**Scaling Thresholds:**
- **50+ users:** Add Redis cache + PostgreSQL
- **100+ users:** Horizontal scaling + Load balancer
- **500+ users:** Microservices architecture + Message queue
- **High-volume processing:** Use parallel processing with 5-10 workers ⚡

---

### Input Files

**1. Kobo System File** (`kobo_system_*.xlsx`)
```
Sheet: survey
┌──────────┬──────────┬─────────────────────────────────────┐
│ type     │ name     │ label                               │
├──────────┼──────────┼─────────────────────────────────────┤
│ text     │ E1       │ Pengembangan apa yang diharapkan... │
│ text     │ E2       │ Bagaimana tingkat kemudahan...      │
└──────────┴──────────┴─────────────────────────────────────┘

Sheet: choices
┌───────────┬──────┬───────────────────────┐
│ list_name │ name │ label                 │
├───────────┼──────┼───────────────────────┤
│ (empty initially - will be populated)   │
└───────────┴──────┴───────────────────────┘
```

**2. Raw Data File** (`Raw_Data_*.xlsx`)
```
┌─────┬──────────────────────────────────┬──────────────────────────┐
│ ID  │ E1                               │ E2                       │
├─────┼──────────────────────────────────┼──────────────────────────┤
│ 1   │ Pilihan pembayaran lebih banyak  │ Mudah digunakan          │
│ 2   │ Fasilitas toilet ditambah        │ Perlu perbaikan server   │
│ 3   │ TA                               │ Aplikasi sering error    │
│ 4   │ (empty)                          │ (empty)                  │
└─────┴──────────────────────────────────┴──────────────────────────┘
```

### Output Files

**1. Updated Raw Data** (with coded columns)
```
┌─────┬──────────────────────────────────┬──────────┬──────────────────────────┬──────────┐
│ ID  │ E1                               │ E1_coded │ E2                       │ E2_coded │
├─────┼──────────────────────────────────┼──────────┼──────────────────────────┼──────────┤
│ 1   │ Pilihan pembayaran lebih banyak  │ 1        │ Mudah digunakan          │ 2        │
│ 2   │ Fasilitas toilet ditambah        │ 3        │ Perlu perbaikan server   │ 5        │
│ 3   │ TA                               │ 99       │ Aplikasi sering error    │ 7        │
│ 4   │ (empty)                          │ (null)   │ (empty)                  │ (null)   │
└─────┴──────────────────────────────────┴──────────┴──────────────────────────┴──────────┘
```

**2. Updated Kobo System** (with choices)
```
```
Sheet: choices
┌─────────────┬──────┬───────────────────────────────┐
│ list_name   │ name │ label                         │
├─────────────┼──────┼───────────────────────────────┤
│ E1_codes    │ 1    │ Pilihan Pembayaran            │
│ E1_codes    │ 2    │ Sosialisasi dan Promosi       │
│ E1_codes    │ 3    │ Fasilitas Pelabuhan           │
│ ...         │ ...  │ ...                           │
│ E1_codes    │ 99   │ Tidak Ada Jawaban             │
├─────────────┼──────┼───────────────────────────────┤
│ E2_codes    │ 1    │ Kemudahan Interface           │
│ E2_codes    │ 2    │ Performa Aplikasi             │
│ ...         │ ...  │ ...                           │
└─────────────┴──────┴───────────────────────────────┘
```

**3. Kobo Form** (updated with new fields)
```
Before:
Group_E/E1 [text]

After:
Group_E/E1 [text]
Group_E/E1_coded [select_one E1_codes]  ← NEW FIELD
```

---

## 🚀 DEVELOPMENT ROADMAP

### Phase 1: Core Automation ✅ **COMPLETED**
- [x] Kobo API client
- [x] OpenAI classification engine
- [x] Response validation logic
- [x] Excel processing workflow
- [x] Kobo upload functionality
- [x] Hybrid approach (outlier re-analysis)
- [x] CLI-based pipeline
- [x] Logging & error handling

### Phase 2: GUI Development 🔄 **IN PROGRESS**
- [x] Choose GUI framework (Flask selected)
- [x] Design UI mockups (Bootstrap 5 with sidebar)
- [x] Implement authentication system (Flask-Login with admin roles)
- [x] Build main dashboard
- [x] File selection & upload interface ⭐ **COMPLETED 2025-01-13**
  - [x] Dual file upload (kobo_system + raw_data)
  - [x] Auto-detect open-ended variables from survey structure
  - [x] Variable statistics display (response count, avg length, samples)
  - [x] Question context input for better classification
  - [x] Classification settings (max categories, confidence threshold)
- [x] Classification execution ⭐ **COMPLETED 2025-01-13**
  - [x] Integration with ExcelClassifier
  - [x] Multi-variable processing
  - [x] Session storage for results
  - [x] Error handling and user feedback
- [x] Results viewer ⭐ **COMPLETED 2025-01-13**
  - [x] Overall statistics dashboard
  - [x] Per-variable detailed results
  - [x] Category generation summary
  - [x] Output file listing
- [x] Progress tracking display ⭐ **COMPLETED 2025-01-13**
  - [x] Real-time progress monitoring dengan Server-Sent Events
  - [x] Background processing dengan threading
  - [x] Variable-by-variable progress indicator
  - [x] Activity log dengan timestamps
  - [x] Overall progress bar dengan percentage
  - [x] Elapsed time tracking
  - [x] Completion/error handling
- [ ] Settings configuration panel
- [ ] File download functionality

### Phase 3: Enhanced Features 📋 **FUTURE**
- [ ] Support for Semi Open-Ended (Pre-Coded)
- [ ] Multi-language support (ID/EN)
- [ ] Batch processing multiple projects
- [ ] Export to various formats (PDF, CSV, JSON)
- [ ] Category editing & manual override
- [ ] Confidence threshold adjustment per variable
- [ ] API rate limiting & cost tracking
- [ ] Historical data & audit log

### Phase 4: Deployment & Distribution 📦 **FUTURE**
- [ ] Build executable (.exe for Windows)
- [ ] Installation wizard
- [ ] Auto-update mechanism
- [ ] User manual & video tutorials
- [ ] Error reporting system
- [ ] Performance optimization

---

## 🧪 TESTING REQUIREMENTS

### Unit Tests
- [ ] `test_kobo_client.py` - Kobo API operations
- [ ] `test_openai_classifier.py` - Classification logic
- [ ] `test_excel_processor.py` - Excel file operations
- [ ] `test_validation.py` - Response validation
- [ ] `test_auth.py` - Authentication system

### Integration Tests
- [ ] `test_full_pipeline.py` - End-to-end workflow
- [ ] `test_kobo_upload.py` - Upload to Kobo
- [ ] `test_gui_workflow.py` - GUI interactions

### User Acceptance Tests
- [ ] Non-technical user can login successfully
- [ ] User can select and process variables
- [ ] Results are accurate and complete
- [ ] Output files are correctly formatted
- [ ] Error messages are clear and helpful

---

## 📝 NOTES & CONSIDERATIONS

### Technical Constraints
1. **API Rate Limits**
   - OpenAI: 3,500 requests/minute (Tier 1)
   - Kobo: No strict limit but use reasonable batching
   
2. **Cost Estimation**
   - GPT-4o-mini: ~$0.15/1M tokens
   - For 1,000 responses: ~$0.01-$0.05
   - For 10,000 responses: ~$0.10-$0.50

3. **Performance**
   - Classification: ~1-2 seconds per response
   - Batch of 100: ~2-3 minutes
   - Batch of 1,000: ~20-30 minutes

### User Experience Considerations
1. **Progress Tracking**
   - Show real-time progress bar
   - Display current step/status
   - Estimated time remaining

2. **Error Handling**
   - Clear error messages in bahasa Indonesia
   - Suggestions for resolution
   - Retry mechanism for API failures

3. **Data Privacy**
   - Survey data tidak di-share ke external services (hanya OpenAI for classification)
   - User credentials encrypted
   - Session timeout for security

### Future Enhancements
1. **Smart Categorization**
   - Learn from previous classifications
   - Reuse categories across similar projects
   - Category library management

2. **Collaboration Features**
   - Multi-user access
   - Role-based permissions (Admin, Analyst, Viewer)
   - Activity tracking

3. **Analytics Dashboard**
   - Classification statistics
   - Cost tracking
   - Performance metrics

---

## 🔗 EXTERNAL DEPENDENCIES

### Python Packages
```
# Core Dependencies
pandas>=2.0.0          # Data manipulation
openpyxl>=3.1.0        # Excel file handling
requests>=2.31.0       # HTTP requests
python-dotenv>=1.0.0   # Environment variables
openai>=1.0.0          # OpenAI API client

# Web Framework & Authentication
flask>=3.0.0           # Web framework
flask-login>=0.6.3     # Authentication & session management
flask-sqlalchemy>=3.0.0 # Database ORM
werkzeug>=3.0.0        # Security utilities (password hashing)

# Email Service
# (Built-in smtplib & email.mime modules - no external package needed)
```

### Future GUI Dependencies
```
# Option 1: Desktop (Tkinter)
ttkbootstrap>=1.10.0   # Modern tkinter styling
pillow>=10.0.0         # Image handling
pyinstaller>=5.0.0     # Executable builder

# Option 2: Web (Flask)
flask>=3.0.0           # Web framework
flask-login>=0.6.0     # Authentication
flask-wtf>=1.2.0       # Forms
werkzeug>=3.0.0        # Security utilities
```

### External APIs
- **OpenAI API** - GPT-4o-mini for text classification
- **Kobo Toolbox API** - Survey data fetch & upload

---

## 📞 SUPPORT & MAINTENANCE

### For Development Issues
- Check logs in `files/logs/`
- Review error messages in console
- Test API connections with utility scripts

### For User Issues (Post-GUI)
- User manual in `docs/USER_MANUAL.md` (future)
- Video tutorials (future)
- Error reporting within app (future)

---

## 📚 LEARNING RESOURCES

### For Developers Working on This Project
- [Kobo Toolbox API Docs](https://support.kobotoolbox.org/api.html)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/) (if web-based)
- [Tkinter Tutorial](https://docs.python.org/3/library/tkinter.html) (if desktop)

---

## 📅 VERSION HISTORY

### v0.1.0 - Initial (CLI-based)
- ✅ Core classification engine
- ✅ Kobo API integration
- ✅ Excel workflow
- ✅ Hybrid approach with outlier re-analysis
- ✅ Auto-upload to Kobo

### v1.0.0 - Current (Web Dashboard)
- ✅ User authentication system (login, register, forgot/reset password)
- ✅ Email service integration (OTP for password reset)
- ✅ Web-based GUI dengan Flask
- ✅ User-friendly workflow (upload → select → classify)
- ✅ Real-time progress tracking dengan SSE
- ✅ Results dashboard dengan statistics
- ✅ User management (super_admin & regular user roles)
- ✅ Mobile-responsive design untuk semua pages
- ✅ Session management dengan Flask-Login
- ✅ Database dengan SQLAlchemy ORM

### v1.1.0 - Target (Enhancement)
- 🎯 Advanced analytics & visualization (charts, word cloud)
- 🎯 Batch processing untuk multiple variables
- 🎯 Category management & customization
- 🎯 Export to PDF & PowerPoint
- 🎯 Email notification saat classification selesai
- 🎯 API endpoints untuk integration
- 🎯 Command-line interface untuk automation

### v2.0.0 - Future
- 🎯 Semi open-ended support
- 🎯 Multi-project management
- 🎯 Advanced analytics

---

## ✍️ DOCUMENT MAINTENANCE

**Last Updated:** December 26, 2025
**Updated By:** GitHub Copilot Agent
**Next Review:** After semi open-ended testing and user feedback

**Changelog:**
- 2025-12-26: ⭐ SEMI OPEN-ENDED WEB UI INTEGRATION COMPLETE
  - Integrated semi open-ended processing into web application:
    * Updated FileProcessor dengan detect_semi_open_pairs() dan get_semi_open_statistics()
    * Modified /upload-files route untuk auto-detect semi open-ended pairs
    * Added dedicated UI section di select_variables.html:
      - Semi open-ended pairs table dengan preview
      - Cost estimation showing 70-80% savings vs full open-ended
      - Sample "Lainnya" responses display
      - Settings: max categories, merged column option
    * Implemented run_semi_open_background() untuk async processing
    * Enhanced results.html untuk display semi open-ended summaries:
      - Lainnya responses count
      - New categories generated
      - Merged column info
      - Cost efficiency metrics
    * Complete end-to-end workflow: Upload → Detect → Select → Process → Results
  - Testing status: Ready for validation dengan real survey data
- 2025-12-26: ⭐ SEMI OPEN-ENDED BACKEND MODULES COMPLETE
  - Implemented semi open-ended (pre-coded + "Lainnya") processing:
    * Detection module (semi_open_detector.py) untuk identify pairs
    * Processing module (semi_open_processor.py) untuk classify & merge
    * Auto-detect "Lainnya" option dari choices sheet
    * Detect paired variables (e.g., S10 + S10_L)
    * Extract responses yang pilih "Lainnya"
    * Classify "Lainnya" text responses dengan AI
    * Merge pre-coded choices dengan classified categories
    * Assign new codes starting from max_existing_code + 1
    * Update choices sheet dengan new categories
    * Create merged variable (e.g., S10_merged)
  - Test script (test_semi_open.py) untuk validation
  - Full documentation dengan examples (SEMI_OPEN_GUIDE.md)
- 2025-12-26: ⭐ COMPREHENSIVE TECHNOLOGY DOCUMENTATION ADDED
  - Added complete technology stack documentation:
    * Backend: Python 3.11, Flask 3.0, SQLAlchemy, SQLite, OpenAI API
    * Frontend: Bootstrap 5, JavaScript, HTML5/CSS3, Jinja2
    * Libraries: pandas, openpyxl, Flask-Login, smtplib
  - Added technical architecture diagrams:
    * Application architecture pattern (MVC)
    * Request flow diagrams
    * Authentication flow
    * OTP email flow
  - Added folder structure with detailed explanations
  - Added design patterns documentation (MVC, Factory, Blueprint, Repository, Service Layer)
  - Added deployment & infrastructure guide:
    * Windows Server (On-Premise) setup
    * Linux Server (VPS/Cloud) dengan Nginx + Gunicorn
    * Cloud platform options (Heroku, Railway, AWS, Azure)
    * Database migration strategy (SQLite → PostgreSQL)
    * Scaling considerations (vertical & horizontal)
  - Added monitoring & maintenance section
  - Added security best practices checklist
  - Added performance & cost optimization:
    * OpenAI API cost estimation (~$0.08 per 1,000 responses)
    * Response time targets
    * Scalability metrics
  - Created TECHNOLOGY_SUMMARY.md untuk quick reference
- 2025-12-26: ⭐ AUTHENTICATION & EMAIL SERVICE DOCUMENTATION ADDED
  - Added comprehensive authentication system documentation:
    * Login, Register, Forgot Password, Reset Password flows
    * OTP (6-digit) email verification for password reset
    * OTP expiry (10 minutes) with database validation
    * Mobile-responsive authentication pages
    * Session management dengan Flask-Login
    * Password hashing dengan bcrypt (werkzeug.security)
  - Email Service Integration documented:
    * SMTP configuration (Gmail with TLS)
    * Email templates untuk password reset OTP
    * Environment variables (MAIL_USERNAME, MAIL_PASSWORD)
    * Gmail App Password setup instructions
    * Error handling dan logging
  - Database schema untuk User model dengan OTP fields
  - Role-based access control (super_admin, user)
  - Security best practices (bcrypt, session encryption)
- 2025-12-26: ⭐ MOBILE-RESPONSIVE DESIGN COMPLETE
  - Implemented full mobile-responsive design across all pages
  - Mobile Navigation:
    * Hamburger menu button with slide-in sidebar animation
    * Sidebar overlay (click to close) for better UX
    * Full-screen mobile layout (no sidebar visible by default)
    * Close button inside sidebar for explicit dismiss
    * Auto-close on navigation and window resize
  - Desktop Navigation:
    * User dropdown menu in navbar (avatar, name, role, logout)
    * Profile and Settings links in dropdown
    * Sidebar remains visible with hover expansion
    * Logout moved from sidebar to navbar dropdown
  - Dashboard Mobile Optimization:
    * Stats cards in 2x2 grid layout (col-6 col-md-3)
    * Compact card styling (smaller fonts, padding, icons)
    * Vertical layout in cards on mobile
    * Mobile Quick Actions section with 2-button grid
    * Prominent CTA button in hero section
  - Classify Page Mobile:
    * Compact step labels (Upload, Variables, Classify)
    * Shortened helper text while keeping clarity
    * Responsive file input descriptions
    * Compact detection rules with mobile version
    * Reduced padding and spacing for mobile
  - Authentication Pages:
    * Fully responsive login, register, forgot/reset password
    * Adaptive grid columns (col-12 col-sm-10 col-md-8 col-lg-5)
    * Progressive padding (p-3 p-sm-4 p-md-5)
    * Responsive logo sizes and typography
  - Profile Page:
    * Responsive grid layout (col-12 col-md-4 for sidebar)
    * Adaptive icon sizes and spacing
  - Breakpoints: 768px (mobile/tablet), 576px (small mobile)
  - All changes maintain desktop functionality while optimizing mobile UX
- 2025-01-13: ⭐ COMPREHENSIVE LANGUAGE AUDIT & PROGRESS TRACKING FIX
  - Completed thorough audit of all Indonesian text in application
  - Updated all progress tracker messages to professional English
  - Updated all flash messages in routes.py to English
  - Fixed SSE (Server-Sent Events) stream for proper real-time updates
  - Removed stream_with_context for better compatibility
  - Added logging to background thread for debugging
  - Added small delays between progress updates for smooth UI transitions
  - Added exception tracking with traceback for better error diagnosis
- 2025-01-13: ⭐ REBRANDING TO INSIGHTCODER PLATFORM
  - Updated application name from "Kobo Coding" to "InsightCoder Platform"
  - Changed logo icon to lightbulb (bi-lightbulb-fill) for better enterprise branding
  - Translated all dashboard UI text to professional English
  - Updated all page titles and branding consistently across templates
  - Added APP_NAME and APP_VERSION constants to config.py
  - Updated README.md with professional enterprise description
- 2025-01-13: ⭐ REAL-TIME PROGRESS TRACKING IMPLEMENTED
  - Created ProgressTracker class untuk thread-safe progress monitoring
  - Background processing dengan threading untuk non-blocking classification
  - Server-Sent Events (SSE) endpoint untuk real-time updates
  - Progress page dengan live indicators:
    * Overall progress bar dengan percentage
    * Current variable dan step display
    * Variables completed counter
    * Elapsed time tracker
    * Activity log dengan timestamps
    * Auto-redirect ke results saat selesai
  - Error handling dengan user-friendly messages
- 2025-01-13: ⭐ CORE KLASIFIKASI SELESAI DIIMPLEMENTASIKAN
  - Integrasi penuh dengan ExcelClassifier (hybrid approach dengan outlier re-analysis)
  - Route start_classification untuk eksekusi klasifikasi multi-variabel
  - Template results.html dengan dashboard statistik lengkap
  - Session-based result storage untuk akses hasil klasifikasi
  - Error handling dan user feedback dalam Bahasa Indonesia
- 2025-01-13: Implemented file upload with smart auto-detect variables from kobo_system structure
  - Added FileProcessor utility class with detection algorithm
  - Created upload workflow routes (upload_files, select_variables, start_classification)
  - Built variable selection interface with statistics and settings
  - Detection strategy: reads survey sheet, filters type=text, name≥S1, excludes "lainnya/sebutkan"
  - UPDATED: Detection algorithm refined to exclude profile fields (nama, alamat, telepon, dll) and screening fields (S*)
- 2025-12-30: Completed authentication system with admin roles
  - User management interface with create/edit capabilities
  - Flask-Login session management
  - Bootstrap 5 UI with sidebar navigation
- 2025-12-25: Initial document creation with comprehensive project overview

---

**🎯 REMINDER:** This document is the **single source of truth** for this project. All agents working on this project should read and follow the guidelines, architecture, and workflow defined here. Update this document whenever there are significant changes to the project scope, architecture, or implementation.
