# M-Coder Platform

**Enterprise Survey Response Classification System**

Automated classification platform for open-ended survey responses using AI-powered categorization with OpenAI GPT-4o-mini.

## 🌐 Production Access

**Live Application**: https://m-coder.flazinsight.com

⚠️ **Important**: Gunakan domain **tanpa www**. Domain `www.m-coder.flazinsight.com` tidak tersedia karena limitasi Cloudflare Universal SSL (gratis) yang hanya cover 1-level subdomain. Multi-level subdomain seperti `www.m-coder` memerlukan Advanced Certificate Manager ($10/month).

## 📋 Description

M-Coder Platform is a professional web-based application designed for MarkPlus Indonesia to automate the classification and coding of open-ended survey responses. The platform features smart variable detection, real-time progress tracking, and comprehensive result analytics.

### Key Features:
- ✅ **Web-based Interface**: Modern Flask application with Bootstrap 5 UI
- ✅ **User Authentication**: Secure login system with admin roles
- ✅ **Smart Variable Detection**: Auto-detect open-ended questions from survey structure
- ✅ **AI-Powered Classification**: Dynamic categorization using OpenAI GPT-4o-mini
- ✅ **Real-time Progress Tracking**: Live updates during classification process
- ✅ **Hybrid Approach**: Initial categorization + outlier re-analysis for accuracy
- ✅ **Multi-variable Processing**: Classify multiple variables simultaneously
- ✅ **Comprehensive Results**: Detailed analytics and statistics dashboard
- ✅ **Excel Export**: Professional output with coded responses
- ✅ **Error Handling**: Robust validation and user-friendly error messages

## 🚀 Quick Start

### 1. Install Dependencies

Ensure Python 3.8+ is installed, then run:

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create or edit `.env` file with your credentials:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Kobo Toolbox API (Optional)
KOBO_ASSET_ID=your_asset_id
KOBO_API_TOKEN=your_token
KOBO_BASE_URL=https://kf.kobotoolbox.org

# Application Settings
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.7
```

### 3. Dapatkan OpenAI API Key

1. Kunjungi: https://platform.openai.com/api-keys
2. Login/Sign up dengan akun OpenAI Anda
3. Klik "Create new secret key"
4. Copy dan simpan key tersebut (hanya ditampilkan sekali)
5. Paste ke file `.env` di bagian `OPENAI_API_KEY`
6. Top up balance di: https://platform.openai.com/settings/organization/billing

**Estimasi biaya**: GPT-4o-mini sangat murah (~$0.15/1M tokens). Untuk 1000 responses, biaya sekitar $0.01 - $0.05 saja.

## 📖 Cara Penggunaan

### Mode 1: Classification Only (Excel Export)

Hanya klasifikasi dan export ke Excel (tidak upload ke Kobo):

```bash
# Set AUTO_UPLOAD_TO_KOBO=false di .env
python main.py
```

Output: Excel file dengan category labels

### Mode 2: Full Automation (Classify + Upload to Kobo) ⭐ **RECOMMENDED**

Klasifikasi + Auto-create field + Upload codes ke Kobo:

```bash
# Set AUTO_UPLOAD_TO_KOBO=true di .env
python main.py
```

Proses yang dilakukan:
1. ✓ Fetch semua submissions dari Kobo (1328 data)
2. ✓ Extract dan filter valid responses (exclude TA, tidak ada, dll)
3. ✓ Generate 10 categories via AI (80% random sample)
4. ✓ Classify semua responses dengan confidence score
5. ✓ Export ke Excel dengan results
6. ✓ **Create new field di Kobo form** (e.g., `E1_coded`)
7. ✓ **Add choices dengan kode 1-10** ke Kobo
8. ✓ **Upload classification codes** ke semua submissions

### Apa yang Terjadi di Kobo?

**Sebelum:**
```
Group_E/E1 (text): "Pilihan pembayaran lebih banyak"
```

**Sesudah:**
```
Group_E/E1 (text): "Pilihan pembayaran lebih banyak"
Group_E/E1_coded (select_one): 1  ← NEW FIELD!
```

**Choices List (e1_categories):**
```
1 = Pilihan Pembayaran
2 = Sosialisasi dan Promosi
3 = Fasilitas Pelabuhan
4 = Kebersihan dan Kenyamanan
5 = Jam Keberangkatan
6 = Tarif dan Kuota
7 = Teknologi Pembayaran
8 = Kualitas Kapal
9 = Area Tunggu
10 = Other
```

**Benefit untuk Tim Data Processing:**
- ✅ Data sudah ter-coding di Kobo
- ✅ Bisa langsung export untuk analysis
- ✅ Tidak perlu manual coding di Excel
- ✅ Choices list sudah tersedia di form

### Output Files

Setelah proses selesai, Anda akan mendapatkan:

**1. Excel File** (`files/output/classified_responses_YYYYMMDD_HHMMSS.xlsx`)
   - Berisi semua data submission
   - Kolom `E1_category`: Kategori hasil klasifikasi
   - Kolom `E1_confidence`: Confidence score (0.0 - 1.0)
   - Kolom klasifikasi ditempatkan tepat di sebelah kolom E1

**2. Summary File** (`files/output/classification_summary_YYYYMMDD_HHMMSS.json`)
   - Distribusi kategori
   - Average confidence score
   - Metadata proses klasifikasi

**3. Log Files** (`files/logs/classification_YYYYMMDD_HHMMSS.log`)
   - Detail proses execution
   - Error messages (jika ada)
   - Progress tracking

## 🧪 Testing

### Test Kobo API Connection

```bash
python explore_kobo.py
```

Output:
- Asset information
- Survey questions
- Sample E1 responses
- Data structure

### Test Kobo Client Module

```bash
python kobo_client.py
```

### Test OpenAI Classifier Module

```bash
python openai_classifier.py
```

**Catatan**: Pastikan sudah mengisi `OPENAI_API_KEY` di `.env` sebelum testing OpenAI classifier.

## 📁 Struktur Project

```
koding/
├── .env                          # Environment variables (API keys)
├── .env.example                  # Template untuk .env
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── README.md                     # Dokumentasi (file ini)
│
├── main.py                       # Main automation pipeline
├── kobo_client.py                # Kobo API client module
├── openai_classifier.py          # OpenAI classification module
├── explore_kobo.py               # Script untuk explore Kobo API
│
└── files/
    ├── Account_info.txt          # Kobo account credentials
    ├── output/                   # Classification results (Excel, JSON)
    │   ├── classified_responses_*.xlsx
    │   └── classification_summary_*.json
    └── logs/                     # Application logs
        ├── classification_*.log
        ├── asset_structure.json
        ├── sample_submissions.json
        └── generated_categories.json
```

## ⚙️ Konfigurasi

### Environment Variables

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `KOBO_ASSET_ID` | ID dari Kobo survey asset | - | ✅ |
| `KOBO_API_TOKEN` | API token untuk autentikasi | - | ✅ |
| `KOBO_BASE_URL` | Base URL Kobo server | https://kf.kobotoolbox.org | ❌ |
| `OPENAI_API_KEY` | OpenAI API key | - | ✅ |
| `MAX_CATEGORIES` | Maksimal jumlah kategori | 10 | ❌ |
| `CONFIDENCE_THRESHOLD` | Threshold untuk confidence score | 0.7 | ❌ |
| `CATEGORY_SAMPLE_RATIO` | Ratio sample untuk generate categories | 0.8 | ❌ |
| `AUTO_UPLOAD_TO_KOBO` | Auto-upload hasil ke Kobo | false | ❌ |
| `CODED_FIELD_SUFFIX` | Suffix untuk coded field name | _coded | ❌ |

## 🔍 Cara Kerja Klasifikasi

### Phase 1: Generate Categories (Dynamic)
- Analisis sample responses (max 100 untuk efisiensi)
- OpenAI generate kategori yang paling relevan
- Maksimal 10 kategori + "Other"
- Kategori disimpan untuk digunakan di phase 2

### Phase 2: Classify Responses
- Setiap response diklasifikasi ke kategori yang sudah di-generate
- Model: GPT-4o-mini (paling ekonomis)
- Temperature: 0.1 (untuk konsistensi)
- Response ambiguous/unclear → kategori "Other"

### Output Format
- Response original tetap utuh di kolom E1
- Kategori hasil klasifikasi di kolom `E1_category` (tepat di sebelah E1)
- Confidence score di kolom `E1_confidence`

## 🐛 Troubleshooting

### Error: "KOBO_ASSET_ID dan KOBO_API_TOKEN harus diset"
- Pastikan file `.env` ada dan berisi API credentials yang benar

### Error: "OPENAI_API_KEY harus diset"
- Pastikan sudah mengisi `OPENAI_API_KEY` di file `.env`
- Jangan menggunakan placeholder `your_openai_api_key_here`

### Error: "Field 'E1' not found"
- Cek nama field yang benar dengan menjalankan `python explore_kobo.py`
- Edit `e1_field_name` di `main.py` jika nama field berbeda

### Error: OpenAI rate limit
- Aplikasi sudah include retry logic
- Jika masih error, tunggu beberapa menit dan coba lagi
- Cek quota di: https://platform.openai.com/usage

### Error: Python not found
- Install Python dari: https://www.python.org/downloads/
- Atau gunakan `py` launcher di Windows: `py main.py`

## 💡 Tips

1. **Cost Optimization**: GPT-4o-mini sudah sangat ekonomis. Untuk 1000 responses, biaya hanya sekitar $0.01 - $0.05.

2. **Batch Processing**: Aplikasi memproses responses satu per satu untuk akurasi maksimal. Untuk dataset besar (>1000 responses), proses bisa memakan waktu 5-10 menit.

3. **Review Categories**: Setelah proses selesai, review file `files/logs/generated_categories.json` untuk melihat kategori yang di-generate.

4. **Manual Adjustment**: Jika ada kategori yang kurang tepat, Anda bisa edit hasil di Excel atau re-run dengan parameter berbeda.

## 📞 Support

Untuk pertanyaan atau issue, silakan hubungi tim development.

---

**Developed for MarkPlus Indonesia, PT**  
**Survey: ASDP Berkendara**  
**Last Updated: December 2025**
