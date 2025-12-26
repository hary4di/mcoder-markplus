# Panduan Lengkap: Semi Open-Ended di Web UI

> **Status:** ✅ Terintegrasi penuh ke M-Coder Platform Web UI
> **Tanggal:** 26 Desember 2025

## 📋 Daftar Isi
1. [Apa itu Semi Open-Ended?](#apa-itu-semi-open-ended)
2. [Cara Menggunakan di Web UI](#cara-menggunakan-di-web-ui)
3. [Alur Kerja Lengkap](#alur-kerja-lengkap)
4. [Penjelasan Fitur](#penjelasan-fitur)
5. [Keuntungan Biaya](#keuntungan-biaya)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Apa itu Semi Open-Ended?

### Definisi
**Semi Open-Ended** adalah pertanyaan survey yang memiliki:
- ✅ Pilihan jawaban yang sudah ditentukan (pre-coded)
- ✅ Opsi "Lainnya" atau "Other" untuk jawaban bebas
- ✅ Kolom teks tambahan yang muncul saat "Lainnya" dipilih

### Contoh Nyata
```
Pertanyaan: Dengan siapa Anda paling sering bepergian?

Pilihan:
1. Suami / istri
2. Orang tua
3. Anak
4. Teman / Kerabat
5. Sendiri
96. Lainnya (sebutkan): __________
```

Jika responden memilih **96 (Lainnya)**, maka akan muncul kolom teks untuk mengisi jawaban bebas.

### Struktur di Kobo Toolbox

**Variables:**
- `S10` → Select variable (pilihan 1-96)
- `S10_L` → Text variable (kolom teks untuk "Lainnya")

**Di file kobo_system:**
- `survey` sheet: Berisi S10 (select_one) dan S10_L (text)
- `choices` sheet: Berisi list pilihan dengan label "lainnya" untuk code 96

---

## 💻 Cara Menggunakan di Web UI

### Langkah 1: Upload Files
1. Login ke M-Coder Platform
2. Klik **"Start Classification"**
3. Upload 2 files:
   - `kobo_system_*.xlsx` (struktur form)
   - `raw_data_*.xlsx` (data responden)
4. Klik **"Upload & Analyze"**

**Sistem akan otomatis:**
- ✅ Mendeteksi pure open-ended variables
- ✅ Mendeteksi semi open-ended pairs (S10 + S10_L)
- ✅ Menampilkan statistik untuk masing-masing

### Langkah 2: Lihat Hasil Deteksi

Setelah upload berhasil, Anda akan melihat 2 section:

#### A. **Semi Open-Ended Section** (Berwarna Biru)
Menampilkan:
- ✅ Jumlah pairs yang terdeteksi
- ✅ Preview sample responses
- ✅ Estimasi biaya (70-80% lebih murah!)

**Contoh Tampilan:**
```
┌──────────────────────────────────────────────────────────┐
│ ✓ Semi Open-Ended (Pre-coded + "Lainnya")               │
│                                            2 pairs detected│
├──────────────────────────────────────────────────────────┤
│ [✓] S10        S10_L      96    150      142             │
│     (Select)   (Text)   (Code)  (Count)  (Filled)        │
│                                                           │
│     Samples:                                              │
│     • Rekan kerja                                        │
│     • Tetangga dekat                                     │
│                                                           │
│ [✓] S15        S15_L      96    80       75              │
│     ...                                                   │
└──────────────────────────────────────────────────────────┘

Estimated Cost: Processing 217 "Lainnya" responses ≈ $0.017
vs $0.14 for full open-ended. Savings: ~88%!
```

#### B. **Pure Open-Ended Section** (Berwarna Hijau)
Menampilkan variables yang murni text tanpa pre-coded options.

### Langkah 3: Pilih Variables & Process

#### Untuk Semi Open-Ended:

1. **Select pairs** yang ingin diproses (check ✓)
2. **Atur settings:**
   - **Max Categories (New):** Maksimal kategori baru dari "Lainnya" (default: 10)
   - **Create merged column:** ✅ (direkomendasikan)
3. **Klik "Process Semi Open-Ended Variables"**

#### Settings Explained:

**Max Categories:**
- Menentukan berapa banyak kategori baru yang akan dibuat dari responses "Lainnya"
- Contoh: Jika ada 100 response "Lainnya", sistem akan kelompokkan menjadi max 10 kategori
- Range: 5-50 (default: 10)

**Create Merged Column:**
- ✅ **Enabled:** Membuat kolom baru (e.g., `S10_merged`) yang menggabungkan:
  - Pre-coded options (1-5)
  - AI-classified categories (7-16)
- ❌ **Disabled:** Hanya update S10_L_coded

### Langkah 4: Monitor Progress

Saat processing, Anda akan melihat:
```
Processing: S10 (semi open)
├─ Step 1/4: Extracting 'Lainnya' responses... 10%
├─ Step 2/4: Classifying with AI... 60%
├─ Step 3/4: Creating merged variable... 85%
└─ Step 4/4: Updating choices sheet... 100% ✓
```

### Langkah 5: Lihat Results

**Results page menampilkan:**
- ✅ Jumlah "Lainnya" yang diproses
- ✅ Kategori baru yang di-generate
- ✅ Pre-coded categories (existing)
- ✅ Total categories (combined)
- ✅ Cost efficiency (savings %)

**Contoh Result Card:**
```
┌──────────────────────────────────────────────────────────┐
│ Semi Open-Ended: S10                                     │
│ Text Variable: S10_L | Lainnya Code: 96                 │
├──────────────────────────────────────────────────────────┤
│ 142 "Lainnya" Selected                                   │
│ 8 New Categories                                          │
│ 5 Pre-coded Options                                       │
│ 13 Total Categories                                       │
│                                                           │
│ ✓ Merged Column Created: S10_merged                      │
│   Combines pre-coded (5) + AI (8) categories             │
│                                                           │
│ Cost Efficiency: Only 142 responses classified vs 1500   │
│ Estimated savings: ~88% vs pure open-ended!              │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 Alur Kerja Lengkap

```
┌─────────────────────────────────────────────────────────────┐
│ 1. UPLOAD FILES                                             │
│    ↓                                                         │
│    • kobo_system.xlsx + raw_data.xlsx                       │
│    • System auto-detect semi open-ended pairs               │
│    • Show preview & statistics                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. SELECT PAIRS                                             │
│    ↓                                                         │
│    • Choose which pairs to process                          │
│    • Set max categories (5-50)                              │
│    • Enable/disable merged column                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. PROCESSING (Background)                                  │
│    ↓                                                         │
│    • Extract "Lainnya" responses                            │
│    • Classify with OpenAI GPT-4o-mini                       │
│    • Generate new categories                                │
│    • Create merged variable                                 │
│    • Update choices sheet                                   │
│    • Save to raw_data.xlsx                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. RESULTS                                                  │
│    ↓                                                         │
│    • View statistics & cost savings                         │
│    • Download updated Excel file                            │
│    • Merged column ready for analysis                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Penjelasan Fitur

### 1. Auto-Detection

**Sistem mendeteksi pairs berdasarkan:**
- ✅ Choices sheet memiliki label "lainnya" (case-insensitive)
- ✅ Code biasanya 96, 97, atau 98
- ✅ Text variable mengikuti pattern naming:
  - `S10_L` (suffix _L)
  - `S10_lainnya` (suffix _lainnya)
  - `S10_other` (suffix _other)

**False Positive Prevention:**
- ❌ Skip jika text variable bukan type "text"
- ❌ Skip jika select variable bukan "select_one" atau "select_multiple"
- ❌ Skip jika choices tidak ada label "lainnya"

### 2. Merged Variable

**Logic:**
```python
For each row:
  If S10 == 96 (Lainnya):
    S10_merged = AI_classification_code (e.g., 7, 8, 9...)
    label = AI_category (e.g., "Rekan Kerja")
  Else:
    S10_merged = S10 (pre-coded)
    label = original_label (e.g., "Suami/istri")
```

**Hasil:**
```
| S10 | S10_L            | S10_merged | S10_merged_label |
|-----|------------------|------------|------------------|
| 1   | NaN              | 1          | Suami/istri      |
| 96  | Rekan kerja      | 7          | Rekan Kerja      |
| 3   | NaN              | 3          | Anak             |
| 96  | Tetangga         | 8          | Tetangga         |
```

### 3. Choices Sheet Update

**Before:**
```
| list_name | name | label          |
|-----------|------|----------------|
| S10_opts  | 1    | Suami/istri    |
| S10_opts  | 2    | Orang tua      |
| S10_opts  | 96   | Lainnya        |
```

**After:**
```
| list_name     | name | label          |
|---------------|------|----------------|
| S10_opts      | 1    | Suami/istri    |
| S10_opts      | 2    | Orang tua      |
| S10_opts      | 96   | Lainnya        |
| S10_merged    | 1    | Suami/istri    |  ← Pre-coded (copy)
| S10_merged    | 2    | Orang tua      |
| S10_merged    | 7    | Rekan Kerja    |  ← New from AI
| S10_merged    | 8    | Tetangga       |  ← New from AI
```

---

## 💰 Keuntungan Biaya

### Perbandingan Cost

**Scenario: Survey dengan 1,500 responden**

#### Pure Open-Ended (All Responses):
```
- Process: 1,500 responses
- Cost: 1,500 × $0.00008 = $0.12
- Rp 1,950 (@ Rp 16,250/USD)
```

#### Semi Open-Ended (Only "Lainnya"):
```
- "Lainnya" selected: 150 responses (10%)
- Process: Only 150 responses
- Cost: 150 × $0.00008 = $0.012
- Rp 195 (@ Rp 16,250/USD)

Savings: $0.108 (90%)
         Rp 1,755 (90%)
```

### Formula Cost Estimation

```python
# Pure Open-Ended
cost_pure = total_responses × $0.00008

# Semi Open-Ended
lainnya_percentage = (lainnya_count / total_responses) × 100
cost_semi = lainnya_count × $0.00008

# Savings
savings_percentage = 100 - lainnya_percentage
savings_amount = cost_pure - cost_semi
```

### Real-World Examples

**Case 1: ASDP Berkendara Survey**
- Total responden: 1,200
- S10 "Lainnya": 120 (10%)
- **Cost:** $0.0096 vs $0.096 → **Save 90%**

**Case 2: Customer Satisfaction Survey**
- Total responden: 5,000
- Q15 "Lainnya": 800 (16%)
- **Cost:** $0.064 vs $0.40 → **Save 84%**

**Case 3: Multiple Semi Open-Ended**
- Total responden: 2,000
- S10 "Lainnya": 200 (10%)
- S15 "Lainnya": 300 (15%)
- S20 "Lainnya": 150 (7.5%)
- **Total Cost:** $0.052 vs $0.48 → **Save 89%**

---

## 🔧 Troubleshooting

### Error: "No semi open-ended pairs detected"

**Penyebab:**
1. Choices sheet tidak memiliki label "lainnya"
2. Text variable tidak follow naming pattern
3. Select variable bukan type select_one/select_multiple

**Solusi:**
```
1. Check choices sheet:
   - Pastikan ada row dengan label "lainnya" (case-insensitive)
   - Code biasanya 96, 97, atau 98

2. Check survey sheet:
   - Select variable (S10): type = select_one atau select_multiple
   - Text variable harus punya suffix: _L, _lainnya, atau _other
   
3. Pastikan posisi text variable dekat dengan select variable
   (biasanya 1-3 baris setelah select variable)
```

### Error: "Text variable not found"

**Penyebab:**
Text variable name tidak match dengan pattern atau tidak ada di survey sheet.

**Solusi:**
```
Check naming pattern:
✅ S10 + S10_L
✅ S10 + S10_lainnya
✅ Q15 + Q15_other

❌ S10 + Lainnya_S10 (wrong order)
❌ S10 + S10_text (wrong suffix)
```

### Processing Stuck

**Penyebab:**
- OpenAI API quota exceeded
- Network timeout
- Invalid API key

**Solusi:**
1. Check OpenAI API key di Admin Settings
2. Verify quota di https://platform.openai.com/usage
3. Restart server jika stuck > 5 menit

### Merged Column Empty

**Penyebab:**
- "Create merged column" tidak dicentang
- Error saat merging

**Solusi:**
1. Re-run dengan "Create merged column" enabled
2. Check log file untuk error details
3. Verify pre-coded labels exist di choices sheet

---

## 📊 Best Practices

### 1. Survey Design
✅ **DO:**
- Gunakan code 96 untuk "Lainnya" (standar)
- Naming pattern: `S10` + `S10_L`
- Label "Lainnya" di choices sheet

❌ **DON'T:**
- Jangan gunakan code < 90 untuk "Lainnya"
- Jangan skip text variable
- Jangan pakai label ambiguous (e.g., "Other options")

### 2. Processing Strategy
- Set max_categories sesuai expected variety
  - Low variety (10-20 unique responses) → max 5-7
  - Medium variety (50-100 unique) → max 10-15
  - High variety (>100 unique) → max 20-30

### 3. Data Quality
- Review "Lainnya" responses sebelum process
- Remove junk responses (test data, spam)
- Merge duplicate text variables jika ada

### 4. Cost Optimization
- Batch multiple semi open-ended dalam 1 process
- Use incremental mode jika re-running
- Monitor OpenAI usage di dashboard

---

## 🚀 Advanced Usage

### Multi-Language Support
Sistem support bahasa Indonesia dan Inggris:
- Prompt AI disesuaikan dengan bahasa survey
- Categories di-generate dalam bahasa yang sama

### Select Multiple
Untuk `select_multiple` questions:
```
Response: "1 96 4" (memilih 1, Lainnya, dan 4)
         ↓
System classify S10_L jika 96 ada dalam response
```

### Custom Code Ranges
Jika "Lainnya" bukan 96:
- System auto-detect dari choices sheet
- Support multiple lainnya codes (96, 97, 98)

---

## 📚 Resources

### Dokumentasi Terkait:
- [SEMI_OPEN_GUIDE.md](SEMI_OPEN_GUIDE.md) - Technical documentation
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Complete project overview
- [TECHNOLOGY_SUMMARY.md](TECHNOLOGY_SUMMARY.md) - Quick reference

### Code Files:
- `semi_open_detector.py` - Detection module
- `semi_open_processor.py` - Processing & merging
- `app/utils.py` - Web UI integration (FileProcessor)
- `app/routes.py` - API endpoints
- `app/templates/select_variables.html` - UI components

### Test Files:
- `test_semi_open.py` - Validation script
- Sample data: `files/uploads/`

---

## 📞 Support

Jika ada kendala atau pertanyaan:
1. Check [Troubleshooting](#troubleshooting) section
2. Review log files di `files/logs/`
3. Contact: haryadi@markplusinc.com

---

**Happy Coding!** 🎉

**M-Coder Platform** - Making survey coding faster, cheaper, and smarter.
