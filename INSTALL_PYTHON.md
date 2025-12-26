# Panduan Instalasi Python & Setup Environment

## ⚠️ Python Belum Terinstall atau Belum Dikonfigurasi dengan Benar

Berdasarkan test sistem, Python belum terinstall atau belum ditambahkan ke PATH. Ikuti langkah-langkah berikut:

## 📥 Instalasi Python

### Cara 1: Download dari Python.org (Recommended)

1. **Download Python**
   - Kunjungi: https://www.python.org/downloads/
   - Download versi terbaru (Python 3.11 atau 3.12)

2. **Install Python**
   - Jalankan installer yang sudah di-download
   - ⚠️ **PENTING**: Centang "Add Python to PATH" di halaman pertama installer
   - Pilih "Install Now"
   - Tunggu hingga selesai

3. **Verifikasi Instalasi**
   - Buka PowerShell baru (tutup yang lama)
   - Jalankan: `python --version`
   - Seharusnya muncul versi Python (contoh: Python 3.12.0)

### Cara 2: Install dari Microsoft Store

1. Buka Microsoft Store
2. Search "Python"
3. Install "Python 3.12" (atau versi terbaru)
4. Tunggu hingga selesai
5. Buka PowerShell baru dan test: `python --version`

## 🔧 Troubleshooting

### Problem: Python command not found

**Solusi 1: Disable Windows App Execution Aliases**
1. Buka Settings → Apps → Advanced app settings → App execution aliases
2. Disable "python.exe" dan "python3.exe"
3. Restart PowerShell

**Solusi 2: Manual Add to PATH**
1. Find Python installation folder (biasanya: `C:\Users\<username>\AppData\Local\Programs\Python\Python3xx`)
2. Buka System Properties → Environment Variables
3. Edit "Path" di User variables atau System variables
4. Tambahkan folder Python dan Python\Scripts
5. Restart PowerShell

### Problem: "Python was not found" meskipun sudah install

**Solusi:**
1. Tutup semua PowerShell/Command Prompt yang sedang buka
2. Buka PowerShell baru
3. Test lagi dengan `python --version`

## 🚀 Setelah Python Terinstall

Jalankan salah satu command berikut:

### Option 1: Menggunakan Batch Script (Paling Mudah)
```bash
.\test_kobo.bat
```
Script ini akan:
- Auto-install dependencies
- Test koneksi ke Kobo API
- Menampilkan struktur data

### Option 2: Manual Installation
```bash
# Install dependencies
python -m pip install -r requirements.txt

# Test Kobo connection
python explore_kobo.py

# Run full classification
python main.py
```

### Option 3: Menggunakan Virtual Environment (Recommended untuk Production)
```bash
# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

## 📝 Quick Test Commands

Setelah Python terinstall, test dengan commands ini:

```powershell
# 1. Check Python version
python --version

# 2. Check pip version
python -m pip --version

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Test Kobo API
python explore_kobo.py

# 5. Run full automation
python main.py
```

## 💡 Tips

1. **Selalu gunakan `python -m pip` instead of `pip`** untuk menghindari konflik
2. **Restart PowerShell** setelah install Python
3. **Run PowerShell as Administrator** jika ada permission issues
4. **Gunakan virtual environment** untuk project isolation (optional tapi recommended)

## 🆘 Jika Masih Bermasalah

Alternatif: Gunakan Anaconda/Miniconda
1. Download Anaconda: https://www.anaconda.com/download
2. Install Anaconda
3. Buka "Anaconda Prompt"
4. Navigate ke folder project
5. Run commands seperti biasa

---

**Next Step**: Setelah Python terinstall dengan benar, kembali ke [README.md](README.md) untuk panduan penggunaan aplikasi.
