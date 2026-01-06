# Contoh Prompt untuk Agent Baru

## 📋 Prompt Pembuka (Copy-paste ini saat memulai chat baru):

```
Saya lanjut develop project M-Code Pro (MarkPlus AI-Powered Classification System).

Tolong baca dokumentasi ini untuk konteks:
1. PROJECT_OVERVIEW.md - struktur project dan current status
2. CHANGELOG.md - perubahan terbaru (Dec 27, 2025)
3. .github/copilot-instructions.md - technical guide
4. TABULATION_SPEC.md - technical spec untuk Tabulation Module (jika relevant)

Project ini adalah web app Flask untuk klasifikasi survey open-ended pakai OpenAI GPT-4o-mini, 
sudah production di https://m-coder.flazinsight.com

Saya mau [jelaskan task Anda di sini].
```

## 🎯 Contoh Prompt untuk Task Spesifik:

### Bug Fix:
```
Saya lanjut project M-Code Pro. Tolong baca PROJECT_OVERVIEW.md dan CHANGELOG.md dulu.

Ada bug di halaman [nama halaman]: [jelaskan bug]

Bisa bantu fix?
```

### Tambah Fitur:
```
Saya lanjut project M-Code Pro (baca PROJECT_OVERVIEW.md + CHANGELOG.md untuk konteks).

Mau tambah fitur [nama fitur]. Requirements:
- [requirement 1]
- [requirement 2]

Cek CHANGELOG.md "Pending Features" - mungkin ada yang relate.
```

### Mulai Implement Tabulation Module:
```
Saya lanjut project M-Code Pro - mau mulai implement Tabulation Module.

Tolong baca:
1. PROJECT_OVERVIEW.md - untuk context keseluruhan
2. TABULATION_SPEC.md - full technical specification
3. CHANGELOG.md - recent changes

Saya mau mulai dari Week [1/2/3/4] sesuai implementation plan di TABULATION_SPEC.md.
[Atau: Saya mau mulai dari [specific task], tolong guide step-by-step]
```

### Deploy Changes:
```
Project M-Code Pro - mau deploy perubahan ke VPS.

Files yang sudah dimodifikasi:
- [list files]

Tolong guide deployment steps (lihat .github/copilot-instructions.md bagian "Deployment Workflow").
```

### Review Code:
```
Review code di project M-Code Pro.

File: [nama file]
Fokus: [performance/security/best practices]

Konteks ada di PROJECT_OVERVIEW.md
```

## 💡 Tips untuk Prompt yang Efektif:

1. **Selalu mention** PROJECT_OVERVIEW.md + CHANGELOG.md di awal
2. **Jelaskan konteks** task (bug fix / new feature / refactor)
3. **Specific > vague**: "Fix spacing di dashboard header" lebih baik dari "perbaiki tampilan"
4. **Mention production URL** kalau perlu test live: https://m-coder.flazinsight.com
5. **Reference files** yang relevan: "Cek app/routes.py line 565"

## 🚫 Yang TIDAK Perlu Dijelaskan Lagi:

Agent sudah tahu dari dokumentasi:
- ✅ Stack teknologi (Flask, SQLite, OpenAI)
- ✅ Deployment flow (SCP + supervisorctl)
- ✅ Branding (M-Code Pro, MarkPlus logo)
- ✅ Project structure (app/, templates/, classifiers)
- ✅ Recent changes (Dec 27, 2025)

Jadi langsung fokus ke task Anda!

## 📚 Hierarchy Dokumentasi (Agent Akan Baca Urutan Ini):

**Untuk General Development:**
1. **CHANGELOG.md** ← Recent changes (baca dulu!)
2. **PROJECT_OVERVIEW.md** ← Big picture, priorities, roadmap
3. **.github/copilot-instructions.md** ← Technical deep dive (architecture, conventions)
4. **README.md** ← User guide

**Untuk Tabulation Module Development:**
1. **TABULATION_SPEC.md** ← Complete technical specification (WAJIB baca!)
2. **PROJECT_OVERVIEW.md** ← Untuk context keseluruhan project
3. **CHANGELOG.md** ← Recent changes yang mungkin affect development

Agent akan otomatis baca yang relevan sesuai task.

---

**Note**: copilot-instructions.md memang mirip MCP (Model Context Protocol) - file markdown ini dibaca otomatis oleh GitHub Copilot untuk memberi konteks tentang project convention, architecture, dan current state.
