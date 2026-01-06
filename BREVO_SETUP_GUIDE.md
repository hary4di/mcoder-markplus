# Brevo Email Service Setup Guide

## 📧 Cara Setup Brevo untuk Development & Production

### Step 1: Create Brevo Account (FREE)

1. **Kunjungi**: https://www.brevo.com/
2. **Sign Up** dengan email MarkPlus atau personal
3. **Verify email** dari Brevo
4. **Complete onboarding** (isi company info, dll)

**Free Plan Benefits:**
- ✅ **300 emails/day** (cukup untuk development & small production)
- ✅ Unlimited contacts
- ✅ Email templates
- ✅ API access
- ✅ No credit card required

---

### Step 2: Get API Key

1. **Login** ke Brevo dashboard: https://app.brevo.com/
2. **Click nama Anda** di kanan atas → **SMTP & API**
3. **Tab "API Keys"**
4. **Click "Create a new API key"**
5. **Name**: "M-Code Pro Development" (atau apapun)
6. **Copy API key** (contoh: `xkeysib-abc123...`)
7. **Save** API key (hanya ditampilkan sekali!)

**Screenshot lokasi:**
```
Dashboard → [Your Name] → SMTP & API → API Keys → Create New
```

---

### Step 3: Configure Development (.env)

Edit file `.env` di local development:

```env
# Email Configuration (Brevo)
BREVO_API_KEY=xkeysib-your_actual_api_key_here_abc123def456
BREVO_SENDER_EMAIL=msurvey@markplusinc.com
BREVO_SENDER_NAME=M-Code Pro
```

**IMPORTANT:**
- Replace `your_brevo_api_key_here` dengan API key ASLI
- Jangan commit API key ke Git (sudah ada di .gitignore)
- Sender email harus email MarkPlus yang verified

---

### Step 4: Verify Sender Email (REQUIRED!)

Brevo **HARUS verify sender email** sebelum bisa kirim email:

1. **Dashboard Brevo** → **Senders, Domains & Dedicated IPs**
2. **Tab "Senders"**
3. **Add a Sender**
4. **Email**: `msurvey@markplusinc.com` (atau email MarkPlus lain)
5. **Name**: `M-Code Pro`
6. **Brevo kirim verification email** ke msurvey@markplusinc.com
7. **Check inbox** msurvey → click verification link
8. **Status jadi "Verified" ✅**

**Jika tidak punya akses ke msurvey@markplusinc.com:**
- Gunakan email personal Anda dulu untuk testing
- Update `.env`: `BREVO_SENDER_EMAIL=your_email@gmail.com`
- Verify email Anda di Brevo
- Production nanti baru pakai email MarkPlus

---

### Step 5: Test Email Service

Restart aplikasi dan test registration:

```powershell
# Stop aplikasi (Ctrl+C)
# Restart
python run_app.py
```

**Test Steps:**
1. Register dengan email REAL Anda (Gmail, Yahoo, dll)
2. Check inbox Anda (atau spam folder)
3. Harusnya ada email dari "M-Code Pro" dengan OTP code
4. Copy OTP dan verify

**Expected Email Content:**
```
From: M-Code Pro <msurvey@markplusinc.com>
Subject: Verify Your Email - M-Code Pro
Body: 6-digit OTP code dengan design profesional
```

---

### Step 6: Troubleshooting

#### ❌ Error: "Brevo API key not configured"

**Check:**
- `.env` file punya `BREVO_API_KEY` dengan value yang benar
- Restart aplikasi setelah edit `.env`
- API key tidak ada spasi di awal/akhir

**Fix:**
```env
# WRONG
BREVO_API_KEY= xkeysib-abc123  # Ada spasi

# CORRECT
BREVO_API_KEY=xkeysib-abc123
```

#### ❌ Error: "Brevo API error: Unauthorized"

**Causes:**
- API key salah atau expired
- API key belum activated

**Fix:**
1. Generate API key baru di Brevo dashboard
2. Copy dengan benar (no extra characters)
3. Update `.env`
4. Restart app

#### ❌ Email tidak diterima

**Check:**
1. **Sender email verified?** (Step 4)
2. **Spam folder?** (check spam/junk mail)
3. **Brevo dashboard → Logs** (check email status: sent/delivered/bounced)
4. **Daily limit reached?** (free: 300/day)
5. **Recipient email valid?**

**Brevo Email Logs:**
```
Dashboard → Campaigns → Transactional → Check status
```

#### ❌ Error: "Sender email not verified"

**Fix:**
- Complete Step 4 (verify sender email di Brevo)
- Tunggu sampai status "Verified" (beberapa menit)
- Atau gunakan email lain yang sudah verified

---

### Step 7: Production Deployment

**After Development Testing Success:**

1. **Create separate API key** untuk production:
   - Brevo Dashboard → API Keys
   - Create new: "M-Code Pro Production"
   - Copy key

2. **Update production .env** (via SSH):
```bash
ssh root@145.79.10.104
nano /opt/markplus/mcoder-markplus/.env

# Add:
BREVO_API_KEY=xkeysib-production_key_here
BREVO_SENDER_EMAIL=msurvey@markplusinc.com
BREVO_SENDER_NAME=M-Code Pro

# Save: Ctrl+O, Enter, Ctrl+X
supervisorctl restart mcoder-markplus
```

3. **Test production registration**:
   - https://m-coder.flazinsight.com/register
   - Register dengan email test
   - Check email received

---

## 📊 Brevo Free Plan Limits

| Feature | Free Plan |
|---------|-----------|
| **Daily Email** | 300 emails/day |
| **Monthly Email** | 9,000 emails/month |
| **Contacts** | Unlimited |
| **API Access** | ✅ Yes |
| **Support** | Email support |
| **Cost** | $0/month |

**For Production:**
- If > 300 registrations/day → Upgrade ke Lite Plan ($25/month = 20,000 emails/month)
- Current usage: ~10-20 registrations/day → Free plan cukup!

---

## 🔒 Security Best Practices

**DO:**
- ✅ Keep API key secret (never commit to Git)
- ✅ Use different API keys for dev/prod
- ✅ Verify sender email before production
- ✅ Monitor Brevo dashboard regularly
- ✅ Set up SPF/DKIM records (optional, better deliverability)

**DON'T:**
- ❌ Share API key di chat/email
- ❌ Commit API key to Git
- ❌ Use personal email as sender in production
- ❌ Exceed daily limits (risk account suspension)

---

## 📞 Support

**Brevo Support:**
- Dashboard: https://app.brevo.com/
- Docs: https://developers.brevo.com/
- Support: https://help.brevo.com/

**Internal Support:**
- Developer: haryadi@markplusinc.com
- WhatsApp: +62 812-8933-008

---

## ✅ Quick Setup Checklist

- [ ] Create Brevo account (https://www.brevo.com/)
- [ ] Get API key from Brevo dashboard
- [ ] Add API key to `.env` file
- [ ] Verify sender email in Brevo
- [ ] Restart application
- [ ] Test registration with real email
- [ ] Check email received (inbox or spam)
- [ ] Verify OTP code works
- [ ] Deploy to production (after dev testing success)

---

**Last Updated**: January 6, 2026
**Status**: Ready for Development & Production
