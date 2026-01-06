# Production Deployment Guide - M-Code Pro

**Last Updated**: January 5, 2026  
**Version**: v1.3.0 - Pure Open-Ended Classification (Production Ready)

---

## 🎯 Pre-Deployment Checklist

### Code Status
- ✅ Multiple variables classification working
- ✅ File management optimized (output/ directory)
- ✅ Category normalization ("Lainnya" only)
- ✅ Duration format enhanced
- ✅ Download fix implemented
- ✅ All tests passed locally

### Files to Deploy
```
app/
├── __init__.py
├── routes.py ← MODIFIED (output directory)
├── models.py
├── templates/
│   ├── results.html ← MODIFIED (duration format)
│   └── classification_progress.html ← MODIFIED (file display)
excel_classifier.py ← MODIFIED (preserve columns)
openai_classifier.py ← MODIFIED (normalization)
requirements.txt
.env (check if updated)
```

---

## 📦 Deployment Steps

### 1. Backup Production Database
```bash
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus
cp instance/mcoder.db instance/mcoder_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. Upload Files to VPS
```powershell
# From local Windows
scp app/routes.py root@145.79.10.104:/opt/markplus/mcoder-markplus/app/
scp app/templates/results.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/
scp app/templates/classification_progress.html root@145.79.10.104:/opt/markplus/mcoder-markplus/app/templates/
scp excel_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp openai_classifier.py root@145.79.10.104:/opt/markplus/mcoder-markplus/
scp CHANGELOG.md root@145.79.10.104:/opt/markplus/mcoder-markplus/
```

### 3. Create Output Directory (if not exists)
```bash
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus
mkdir -p files/output
touch files/output/.gitkeep
chmod 755 files/output
```

### 4. Restart Application
```bash
ssh root@145.79.10.104
supervisorctl restart mcoder-markplus
supervisorctl status mcoder-markplus
```

### 5. Verify Deployment
```bash
# Check logs
tail -50 /var/log/mcoder/gunicorn.log

# Check process
ps aux | grep gunicorn
```

### 6. Test in Production
- [ ] Access https://m-coder.flazinsight.com
- [ ] Login with test account
- [ ] Upload 2 Excel files (kobo + raw)
- [ ] Select 2-3 variables
- [ ] Start classification
- [ ] Wait for completion
- [ ] Check output files in files/output/
- [ ] Verify all coded columns present
- [ ] Download ZIP file
- [ ] Check categories (no "Other", only "Lainnya")
- [ ] Test download multiple times
- [ ] Test bulk delete

---

## 🔍 Post-Deployment Verification

### Expected Behavior
1. **File Structure**
   ```
   files/
   ├── uploads/          ← Input files (auto-deleted after processing)
   └── output/           ← Output files (kept for 24 hours)
       ├── output_kobo_YYYYMMDD_HHMMSS.xlsx
       └── output_raw_YYYYMMDD_HHMMSS.xlsx
   ```

2. **Multiple Variables**
   - Upload → Select E1, E2, E3
   - Result: 1 file pair with E1_coded, E2_coded, E3_coded

3. **Progress Page**
   - Shows only 2 download links (not duplicated)

4. **Results Page**
   - Duration shows "Xm Ys" format when >60s
   - Download works multiple times
   - Bulk delete functional

5. **Categories**
   - No "Other" category
   - Only "Lainnya" for miscellaneous items
   - No duplicate categories

### Monitoring Points
```bash
# Disk space usage
du -sh /opt/markplus/mcoder-markplus/files/output/

# Active classifications
ps aux | grep python | grep gunicorn

# Recent logs
tail -100 /var/log/mcoder/gunicorn.log | grep ERROR
```

---

## 🐛 Rollback Plan (If Issues Found)

### Quick Rollback
```bash
ssh root@145.79.10.104
cd /opt/markplus/mcoder-markplus

# Restore from git
git checkout app/routes.py
git checkout app/templates/results.html
git checkout app/templates/classification_progress.html
git checkout excel_classifier.py
git checkout openai_classifier.py

# Restart
supervisorctl restart mcoder-markplus
```

### Database Rollback (if needed)
```bash
# Restore backup
cd /opt/markplus/mcoder-markplus
cp instance/mcoder_backup_YYYYMMDD_HHMMSS.db instance/mcoder.db
supervisorctl restart mcoder-markplus
```

---

## 📊 Performance Metrics

### Expected Performance
- **1 variable, 150 responses**: ~30-60 seconds
- **2 variables, 150 responses**: ~1-2 minutes
- **7 variables, 150 responses**: ~5-10 minutes
- **Throughput**: ~3-5 responses/second (with parallel batch processing)

### Resource Usage
- **Memory**: ~300-500 MB per classification job
- **Disk**: ~1-2 MB per output file pair
- **Network**: API calls to OpenAI (minimal)

---

## 🔐 Security Checks

- [ ] .env file permissions: `chmod 600 .env`
- [ ] Database permissions: `chmod 644 instance/mcoder.db`
- [ ] Upload directory permissions: `chmod 755 files/uploads/`
- [ ] Output directory permissions: `chmod 755 files/output/`
- [ ] No API keys in logs
- [ ] HTTPS enabled (Cloudflare)
- [ ] Firewall rules active

---

## 📞 Support Contacts

**Developer**: haryadi@markplusinc.com  
**WhatsApp**: +62 812-8933-008  
**VPS**: Hostinger - 145.79.10.104  
**Domain**: https://m-coder.flazinsight.com

---

## 🚀 Next Phase: Semi Open-Ended Classification

**Coming Soon**: Type 2 Classification (precoded with "Others" option)
- File: `semi_open_processor.py` (already exists)
- Status: Ready for development
- Expected: Q1 2026

---

**Deployment Date**: _____________  
**Deployed By**: _____________  
**Test Result**: ☐ PASS ☐ FAIL  
**Notes**: _____________________________________________

