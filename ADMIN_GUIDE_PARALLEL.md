# Admin Guide: Parallel Processing Settings

## Overview
Admin dapat mengatur konfigurasi parallel processing melalui web interface tanpa perlu edit file `.env` secara manual.

## Accessing Settings

1. Login sebagai **Admin**
2. Navigate ke **Admin Settings** (gear icon di navbar)
3. Klik tab **"Parallel Processing"** (icon ⚡)

## Configuration Options

### 1. Enable/Disable Parallel Processing
**Toggle Switch** - Enable atau disable parallel mode

- ✅ **Enabled**: System akan gunakan parallel processing untuk dataset ≥100 responses
- ❌ **Disabled**: System akan gunakan sequential mode (slower but stable)

**Recommendation**: Keep ENABLED untuk most cases

---

### 2. Number of Workers
**Range**: 1-15 workers
**Default**: 5 workers

Jumlah "robot" yang bekerja secara bersamaan untuk memproses batches.

**Guidelines**:
- **1-3 workers**: Safe untuk free/Tier 1 OpenAI account
- **5 workers**: ✓ Recommended untuk production (Tier 2+)
- **10+ workers**: Advanced users only (Tier 3+, risk rate limits)

---

### 3. Rate Limit Delay
**Range**: 0.01-1.0 seconds
**Default**: 0.1 seconds

Delay antara setiap API request untuk mencegah throttling.

**Guidelines**:
- **0.2s**: Very safe (conservative)
- **0.1s**: ✓ Recommended (balanced)
- **0.05s**: Fast but risky (aggressive)

---

## Quick Presets

System menyediakan 3 preset konfigurasi:

### 🛡️ Conservative (Safe)
- Workers: 3
- Delay: 0.2s
- Speedup: 2-3x
- **Use when**: First time, unstable network, free OpenAI tier

### ✅ Balanced (Recommended)
- Workers: 5
- Delay: 0.1s
- Speedup: 3-5x
- **Use when**: Production deployment, Tier 2 OpenAI

### ⚡ Aggressive (Fast)
- Workers: 10
- Delay: 0.05s
- Speedup: 6-8x
- **Use when**: Large datasets, Tier 3+ OpenAI, need maximum speed
- **⚠️ Warning**: May hit rate limits!

---

## Performance Estimator

Built-in calculator untuk estimate processing time:

1. Enter **number of responses** (default: 2482)
2. System automatically calculates:
   - Sequential time (e.g., 17 minutes)
   - Parallel time (e.g., 3-5 minutes)
   - Speedup factor (e.g., 4.2x)

**Formula**:
```
Sequential Rate: ~146 responses/minute
Parallel Rate: ~146 × workers × 0.85
Time Reduction: 1/speedup
```

---

## How It Works

### Automatic Mode Selection
System **automatically** chooses processing mode:

```python
if dataset_size >= 100 and parallel_enabled:
    use_parallel()  # 3-5x faster
else:
    use_sequential()  # stable
```

### During Classification
User akan melihat log output:

**Parallel Mode:**
```
[4/9] Classification: PARALLEL MODE (1328 responses - 3-5x FASTER!)
   Valid responses for API: 1200
   Skipped (existing/invalid/empty): 128
   [PARALLEL STATS] Total time: 183.5s
   [PARALLEL STATS] Rate: 654 responses/minute
   [PARALLEL STATS] Speedup: 4.2x vs sequential
```

**Sequential Mode:**
```
[4/9] Classification: SEQUENTIAL MODE (1328 responses)
   Classifying... 120/1328 (9%)
   ...
```

---

## OpenAI Rate Limits

### Check Your Tier
Visit: https://platform.openai.com/account/limits

### Tier Recommendations
| Tier | RPM | Recommended Workers | Max Safe Workers |
|------|-----|-------------------|-----------------|
| Free | 500 | 3 | 3 |
| Tier 1 | 500 | 3 | 5 |
| Tier 2 | 5,000 | **5** ✓ | 10 |
| Tier 3 | 10,000 | 10 | 15 |

**RPM** = Requests Per Minute

---

## Troubleshooting

### Problem: Rate Limit Errors (429)
**Symptoms**: API returns "Rate limit exceeded"

**Solutions**:
1. Reduce workers: 10 → 5 → 3
2. Increase delay: 0.1 → 0.2 → 0.3
3. Check OpenAI tier limits
4. Wait 60 seconds and retry

---

### Problem: Slow Performance (No Speedup)
**Symptoms**: Parallel mode not much faster than sequential

**Causes & Solutions**:
1. **Dataset too small** (<100 responses)
   - Solution: System auto-uses sequential (optimal)
   
2. **High rate limit delay** (>0.2s)
   - Solution: Reduce delay to 0.1s
   
3. **Too few workers** (1-2)
   - Solution: Increase to 5 workers
   
4. **Network latency**
   - Solution: Check internet connection, try different time

---

### Problem: Classification Results Different
**Symptoms**: Results vary between runs

**Explanation**:
- AI is probabilistic (temperature=0.1, not 0)
- Slight variations are **NORMAL**
- Parallel vs sequential should be **highly consistent** (same categories)

**If major differences**:
- Check categories generated (logs/generated_categories.json)
- Verify same sample size used
- Check if multi-label mode changed

---

## Best Practices

### 1. Initial Setup
```
1. Start with "Balanced" preset (5 workers, 0.1s delay)
2. Run test classification on small dataset (100-200 rows)
3. Monitor logs for errors
4. Adjust if needed
```

### 2. Production Deployment
```
✓ Use "Balanced" preset
✓ Enable parallel processing
✓ Monitor first few runs
✓ Check logs for rate limit errors
```

### 3. Tuning for Performance
```
1. If NO errors after 3 runs:
   → Increase workers (5 → 7 → 10)
   → Reduce delay (0.1 → 0.08 → 0.05)

2. If RATE LIMIT errors occur:
   → Reduce workers (10 → 7 → 5)
   → Increase delay (0.05 → 0.1 → 0.2)
```

### 4. Cost Optimization
```
- Parallel processing does NOT increase OpenAI API cost
- Same number of tokens processed
- Only difference: FASTER completion time
- Cost = tokens used (same in both modes)
```

---

## Saving Settings

### Database & .env Sync
When you save settings:
1. **Database** (SystemSettings table) is updated
2. **.env file** is also updated automatically
3. Both sources stay in sync

### Priority
```
Database Settings > .env Settings > Hardcoded Defaults
```

If database has setting → use it
Else if .env has setting → use it
Else → use default

---

## Testing Changes

### Before Production
1. **Test with small dataset**: 100-200 responses
2. **Compare results**: Run both parallel and sequential on same data
3. **Check logs**: Look for errors, warnings
4. **Monitor timing**: Verify speedup matches expectation

### Verification Checklist
- [ ] No rate limit errors (429)
- [ ] Processing completes successfully
- [ ] Results are consistent
- [ ] Speedup is visible (3-5x)
- [ ] Logs show "PARALLEL MODE"

---

## Example Configurations

### Conservative Production (Safe)
```
Enable: ✅ ON
Workers: 3
Delay: 0.2s

Expected: 2-3x speedup
Risk: Very low
Best for: Critical projects, first deployment
```

### Standard Production (Recommended)
```
Enable: ✅ ON
Workers: 5
Delay: 0.1s

Expected: 3-5x speedup
Risk: Low
Best for: Most projects, daily operations
```

### High Performance (Advanced)
```
Enable: ✅ ON
Workers: 10
Delay: 0.05s

Expected: 6-8x speedup
Risk: Medium-High (rate limits possible)
Best for: Large urgent projects, Tier 3+ accounts
```

### Sequential Fallback
```
Enable: ❌ OFF

Expected: 1x (baseline)
Risk: None
Best for: Troubleshooting, small datasets (<100)
```

---

## FAQ

### Q: Apakah parallel processing lebih mahal?
**A**: Tidak! Cost sama persis (tokens sama), hanya lebih CEPAT.

### Q: Berapa speedup yang realistis?
**A**: Dengan 5 workers: 3-5x faster (17 min → 3-5 min)

### Q: Apakah hasil classification berbeda?
**A**: Tidak! Results should be highly consistent (same categories, same codes).

### Q: Kapan harus gunakan sequential mode?
**A**: 
- Dataset <100 responses (overhead not worth it)
- Troubleshooting issues
- Testing AI prompts
- Free/Tier 1 OpenAI account unstable

### Q: Bagaimana cara monitor API usage?
**A**: Visit https://platform.openai.com/usage
- Check requests per minute (RPM)
- Monitor token consumption
- View rate limit status

### Q: Apakah bisa auto-tune workers?
**A**: Currently manual. Future version may include adaptive tuning.

---

## Change History

Settings changes are logged in:
- Database: `system_settings.updated_at`
- .env file: Modified timestamp
- Application logs: Classification run logs

Review logs to see:
- When settings changed
- Who changed them (admin user)
- Performance impact

---

## Support

If you encounter issues:
1. Check logs in `files/logs/classification_*.log`
2. Review `PARALLEL_PROCESSING.md` for detailed docs
3. Contact system administrator
4. Check OpenAI status: https://status.openai.com

---

Last updated: December 2024
Version: 1.0
