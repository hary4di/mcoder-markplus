# Semi Open-Ended Processing Guide

## 📋 Overview

**Semi Open-Ended** adalah jenis pertanyaan survey yang memiliki:
- **Pilihan jawaban tetap** (pre-coded options)
- **Opsi "Lainnya"** yang memunculkan text field untuk input bebas

Contoh umum di survey Kobo Toolbox:
```
Dengan siapa Anda paling sering bepergian?
○ Suami / istri
○ Orang tua  
○ Anak
○ Teman
○ Lainnya: ___________
```

Jika responden pilih "Lainnya", muncul text box untuk input jawaban bebas.

---

## 🔍 Detection Logic

### 1. **Struktur di Kobo System**

**Survey Sheet:**
```
type            | name  | label
----------------|-------|--------------------------------------------
select_one S10  | S10   | Dengan siapa Anda paling sering bepergian...
text            | S10_L | Lainnya, sebutkan__
```

**Choices Sheet:**
```
list_name | name | label
----------|------|------------------
S10       | 1    | Suami / istri
S10       | 2    | Orang tua
S10       | 3    | Anak
S10       | 4    | Teman
S10       | 96   | Lainnya         <- Key: "Lainnya" option
```

### 2. **Detection Algorithm**

```python
1. Scan choices sheet → Find "Lainnya" in label (case-insensitive)
2. Get list_name and code (biasanya 96)
3. Find select variable yang menggunakan list tersebut
4. Find text variable yang paired (S10_L, S10_lainnya, dst)
   - Biasanya berada di row setelah select variable
   - Name pattern: {select_var}_L, {select_var}_lainnya
   - Label contains: "lainnya" atau "sebutkan"
```

**Code Pattern Recognition:**
```python
# Common patterns:
S10 → S10_L
S10 → S10_lainnya
S10 → S10_other
Q5  → Q5_L
```

---

## ⚙️ Processing Flow

### Step 1: Detection
```python
from semi_open_detector import SemiOpenDetector

detector = SemiOpenDetector('kobo_system.xlsx')
detector.load_sheets()

pairs = detector.detect_semi_open_pairs()
# Result: [{'select_var': 'S10', 'text_var': 'S10_L', 'lainnya_code': 96, ...}]
```

### Step 2: Extract "Lainnya" Responses
```python
# Filter raw data where S10 == 96
lainnya_responses = raw_data[raw_data['S10'] == 96]['S10_L']

# Example responses:
# - "Rekan kerja"
# - "Sendirian"
# - "Driver"
# - "Pemandu wisata"
```

### Step 3: Classify with AI
```python
# Use OpenAI to generate categories
categories = [
    {'category': 'Rekan Kerja/Kolega', 'category_number': 1},
    {'category': 'Sendiri', 'category_number': 2},
    {'category': 'Guide/Driver', 'category_number': 3}
]

# Classify each "Lainnya" response
for response in lainnya_responses:
    result = classifier.classify(response, categories)
    # Result: {'category': 'Rekan Kerja/Kolega', 'confidence': 0.92}
```

### Step 4: Assign New Codes
```python
# Existing codes: 1, 2, 3, 4, 96
# Max code = 96
# New codes start from 97

category_code_map = {
    'Rekan Kerja/Kolega': 7,   # Start from max_existing + 1
    'Sendiri': 8,
    'Guide/Driver': 9
}
```

### Step 5: Create Merged Variable
```python
# Logic for each row:
if S10 == 96:  # "Lainnya" selected
    S10_merged = classified_code_from_S10_L
    S10_merged_label = classified_category_from_S10_L
else:  # Pre-coded option
    S10_merged = S10
    S10_merged_label = original_label_from_choices
```

**Example Output:**
```
ID | S10 | S10_L              | S10_merged | S10_merged_label
---|-----|--------------------| -----------|--------------------
1  | 1   | (empty)            | 1          | Suami / istri
2  | 2   | (empty)            | 2          | Orang tua
3  | 96  | Rekan kerja        | 7          | Rekan Kerja/Kolega
4  | 96  | Sendirian          | 8          | Sendiri
5  | 3   | (empty)            | 3          | Anak
6  | 96  | Driver pribadi     | 9          | Guide/Driver
```

### Step 6: Update Choices Sheet
```python
# Insert new rows to choices sheet
new_choices = [
    {'list_name': 'S10', 'name': 7, 'label': 'Rekan Kerja/Kolega'},
    {'list_name': 'S10', 'name': 8, 'label': 'Sendiri'},
    {'list_name': 'S10', 'name': 9, 'label': 'Guide/Driver'}
]

# Updated choices sheet:
list_name | name | label
----------|------|----------------------
S10       | 1    | Suami / istri
S10       | 2    | Orang tua
S10       | 3    | Anak
S10       | 4    | Teman
S10       | 96   | Lainnya
S10       | 7    | Rekan Kerja/Kolega   <- New
S10       | 8    | Sendiri              <- New
S10       | 9    | Guide/Driver         <- New
```

---

## 🧪 Testing

### Quick Test
```bash
python test_semi_open.py
```

### Test with Sample Data
```python
# Prepare test files:
# 1. files/uploads/kobo_system_example.xlsx
# 2. files/uploads/raw_data_example.xlsx

# Run test
from test_semi_open import main
main()
```

**Expected Output:**
```
================== TEST 1: DETECTION OF SEMI OPEN-ENDED PAIRS ==================

🔍 Step 1: Detecting 'Lainnya' options in choices...
   Found: {'S9': 96, 'S10': 96}

🔍 Step 2: Detecting semi open-ended pairs...
✅ Detected semi open-ended pair: S10 + S10_L (code: 96)

📊 Found 1 semi open-ended pair(s):

1. S10 (code 96: Lainnya) + S10_L
   Label: Dengan siapa Anda paling sering bepergian menggunakan...
   Text field: Lainnya, sebutkan__

Continue with processing test? (y/n): 
```

---

## 📊 Statistics & Reporting

### Category Summary
```python
result['stats'] = {
    'total_responses': 1000,           # Total survey responses
    'lainnya_responses': 85,           # Responses with "Lainnya" selected
    'new_categories': 3,               # Categories generated from "Lainnya"
    'pre_coded_options': 5            # Original pre-coded options
}
```

### Cost Estimation
```
For 85 "Lainnya" responses:
- Category generation: ~$0.01
- Classification: ~$0.007
- Total: ~Rp 300

(Much cheaper than 1000 responses because only processing "Lainnya" subset!)
```

---

## ⚠️ Edge Cases & Handling

### 1. **No "Lainnya" Responses**
```python
if len(lainnya_responses) == 0:
    # Skip classification
    # Only return pre-coded results
    merged_var = select_var  # No merging needed
```

### 2. **Empty "Lainnya" Text**
```python
# Responden pilih "Lainnya" tapi tidak isi text field
if S10 == 96 and pd.isna(S10_L):
    S10_merged = 96  # Keep as "Lainnya"
    S10_merged_label = "Lainnya (tidak diisi)"
```

### 3. **Multiple "Lainnya" Options**
```python
# Some surveys have multiple "Lainnya" (e.g., 96, 97, 98)
# Handle each separately
for lainnya_code in [96, 97, 98]:
    process_lainnya(lainnya_code)
```

### 4. **Select_Multiple Questions**
```python
# For select_multiple, response is space-separated string
# Example: "1 3 96"
if '96' in str(response).split():
    # "Lainnya" is selected (along with other options)
    # Process the S10_L text field
```

---

## 🚀 Web UI Integration (Future)

### Planned Features:
1. **Auto-detect semi open-ended** during file upload
2. **Separate tab** in variable selection UI
3. **Preview merged results** before finalization
4. **Edit categories** if needed before applying
5. **Progress tracking** for semi open classification

### UI Mockup:
```
┌─────────────────────────────────────────────────────────────┐
│ Semi Open-Ended Questions Detected                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [✓] S9 + S9_L: Apa alasan Anda menggunakan...              │
│     • 78 responses with "Lainnya" option                    │
│     • Estimated cost: Rp 250                                │
│                                                              │
│ [✓] S10 + S10_L: Dengan siapa Anda paling sering...        │
│     • 85 responses with "Lainnya" option                    │
│     • Estimated cost: Rp 300                                │
│                                                              │
│ [ ] Process All Semi Open-Ended Questions                   │
│                                                              │
│ [Continue] [Skip Semi Open]                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Best Practices

### 1. **Naming Convention**
- Select variable: `S10`, `Q5`, `P3`
- Text variable: `{var}_L`, `{var}_lainnya`, `{var}_other`
- Merged variable: `{var}_merged`

### 2. **Code Assignment**
- Pre-coded: 1-95
- "Lainnya" option: 96
- New categories from AI: 97+

### 3. **Label Guidelines**
- Keep labels concise (< 50 characters)
- Use title case: "Rekan Kerja" not "rekan kerja"
- Avoid special characters

### 4. **Quality Check**
- Review generated categories before finalizing
- Check for duplicates with pre-coded options
- Validate merged results sample

---

## 🔧 Troubleshooting

### Issue: "No 'Lainnya' options found"
**Solution:** Check choices sheet label spelling (case-insensitive)

### Issue: "Text variable not found"
**Solution:** Ensure text field is named correctly (S10_L pattern)

### Issue: "Classification failed"
**Solution:** Check OpenAI API key and quota

### Issue: "Merged variable has null values"
**Solution:** Check if lainnya responses are empty or not classified

---

## 📚 References

- **Detection Module:** `semi_open_detector.py`
- **Processing Module:** `semi_open_processor.py`
- **Test Script:** `test_semi_open.py`
- **Project Overview:** `PROJECT_OVERVIEW.md` (Section: Semi Open-Ended)

---

**Last Updated:** December 26, 2025  
**Status:** Implementation Complete (UI integration pending)
