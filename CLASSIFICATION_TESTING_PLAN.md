# Classification Testing & Optimization Plan

> **Purpose**: Testing plan untuk validasi dan optimasi parallel classification  
> **Date Created**: 2 Januari 2026  
> **Current Version**: v1.2.0

---

## 🎯 TESTING OBJECTIVES

Validasi bahwa sistem klasifikasi sudah **solid, efisien, dan tanpa kendala** untuk:
1. ✅ **Single Variable** - 1 variabel dengan berbagai ukuran data (100-5000 responses)
2. ✅ **2 Variables Parallel** - 2 variabel secara bersamaan
3. ✅ **Multiple Variables Parallel** - 3-10 variabel secara bersamaan
4. ✅ **Performance Metrics** - Speed, accuracy, memory usage, error rate

---

## 📊 CURRENT IMPLEMENTATION STATUS

### ✅ **Level 1: Batch Processing (SUDAH IMPLEMENTED)**

**Cara Kerja Saat Ini:**
```
Single Variable Klasifikasi:
├── 1000 responses
├── Split menjadi batches (batch_size=10)
├── Process 100 batches secara PARALLEL (max_workers=5)
│   ├── Worker 1: Batch 1-20 (200 responses)
│   ├── Worker 2: Batch 21-40 (200 responses)
│   ├── Worker 3: Batch 41-60 (200 responses)
│   ├── Worker 4: Batch 61-80 (200 responses)
│   └── Worker 5: Batch 81-100 (200 responses)
└── Result: 3-5x faster than sequential
```

**File**: `parallel_classifier.py`
- **Class**: `ParallelClassifier`
- **Method**: `classify_parallel()`
- **Current Settings**:
  - `max_workers=5` (concurrent batches)
  - `batch_size=10` (responses per API call)
  - `rate_limit_delay=0.1s` (delay antar batch)

**Performance:**
- **Speed**: 3-5x faster vs sequential
- **Throughput**: ~10-20 responses/second (tergantung response complexity)
- **OpenAI Cost**: ~$0.01-0.05 per 1000 responses

---

### 🔄 **Level 2: Variable-Level Parallelization (PARTIALLY IMPLEMENTED)**

**Cara Kerja:**
```
Multiple Variables:
├── User pilih 3 variables: E1, E2, E3
├── Process SEQUENTIAL per variable (satu per satu)
│   ├── E1: 1000 responses → Parallel batches (5 workers)
│   ├── Wait until E1 complete
│   ├── E2: 1000 responses → Parallel batches (5 workers)
│   ├── Wait until E2 complete
│   └── E3: 1000 responses → Parallel batches (5 workers)
└── Total time: T(E1) + T(E2) + T(E3)
```

**Current Implementation**: `app/routes.py`
- Loop through variables sequentially
- Each variable uses parallel batch processing
- Progress tracked per variable

**Limitation**:
- Variables NOT processed in parallel
- Total time = sum of all variables
- Underutilization of OpenAI API capacity

---

### 🚀 **Level 3: Full Parallelization (PLANNED - Like BigQuery)**

**Target Implementation:**
```
Multiple Variables (PARALLEL):
├── User pilih 3 variables: E1, E2, E3
├── Process ALL VARIABLES SIMULTANEOUSLY
│   ├── Thread 1 (E1): 1000 responses → Parallel batches (5 workers)
│   ├── Thread 2 (E2): 1000 responses → Parallel batches (5 workers)
│   └── Thread 3 (E3): 1000 responses → Parallel batches (5 workers)
├── Total concurrent workers: 3 variables × 5 workers = 15 API calls
└── Total time: MAX(T(E1), T(E2), T(E3)) ← HUGE SPEEDUP!
```

**Expected Performance:**
- **3 variables**: 3x faster (T/3 instead of T×3)
- **10 variables**: 10x faster
- **Limitation**: OpenAI API rate limits (TPM/RPM)

**Implementation Strategy:**
1. Add variable-level ThreadPoolExecutor
2. Nested parallelization: Variable threads → Batch threads
3. Shared progress tracking with locks
4. Rate limiting per account (not per variable)

---

## 🧪 TESTING PLAN

### **Phase 1: Single Variable Testing** ✅

**Test Cases:**
1. **Small Dataset** (100 responses)
   - Expected time: ~10-20 seconds
   - Purpose: Validate basic functionality
   
2. **Medium Dataset** (1000 responses)
   - Expected time: ~2-3 minutes
   - Purpose: Validate parallel processing efficiency
   
3. **Large Dataset** (5000 responses)
   - Expected time: ~10-15 minutes
   - Purpose: Stress test, memory usage

**Success Criteria:**
- ✅ No errors or crashes
- ✅ All responses classified
- ✅ Confidence scores reasonable (>0.5 for most)
- ✅ Categories accurate and diverse
- ✅ Memory usage stable (<2GB)
- ✅ Progress tracking accurate

---

### **Phase 2: Dual Variable Testing** 📝

**Test Cases:**
1. **2 Variables × 500 responses** (1000 total)
   - Current time: ~4-6 minutes (sequential)
   - Expected: Validate current implementation
   
2. **2 Variables × 1000 responses** (2000 total)
   - Current time: ~8-10 minutes
   - Expected: Test scalability

**Metrics to Track:**
- Total classification time
- Per-variable time
- Peak memory usage
- API errors/retries
- Final accuracy

**Success Criteria:**
- ✅ Both variables complete successfully
- ✅ Results independent (no cross-contamination)
- ✅ Output columns correct (E1_category, E1_confidence, E2_category, E2_confidence)
- ✅ Total time = sum of individual times (sequential)

---

### **Phase 3: Multiple Variable Testing** 📝

**Test Cases:**
1. **3 Variables × 500 responses** (1500 total)
2. **5 Variables × 200 responses** (1000 total)
3. **10 Variables × 100 responses** (1000 total)

**Expected Behavior (Current):**
- Sequential processing
- Total time scales linearly with # variables
- Memory usage stable

**Success Criteria:**
- ✅ All variables complete
- ✅ No memory leaks
- ✅ Accurate progress tracking
- ✅ Correct column insertion order

---

## 🔧 CONFIGURATION PARAMETERS

### **Current Settings (.env)**
```env
# Parallel Processing
ENABLE_PARALLEL_PROCESSING=true
PARALLEL_MAX_WORKERS=5          # Concurrent batches per variable
RATE_LIMIT_DELAY=0.1            # Delay between batches (seconds)

# Batch Configuration
CLASSIFICATION_BATCH_SIZE=10    # Responses per API call

# OpenAI Settings
OPENAI_API_KEY=sk-...
MAX_CATEGORIES=10
CONFIDENCE_THRESHOLD=0.5
```

### **Tuning Guidelines:**

**For Single Variable (Current):**
- `PARALLEL_MAX_WORKERS=5` → Good balance (5 concurrent API calls)
- `BATCH_SIZE=10` → Optimal untuk OpenAI (balance speed vs accuracy)
- `RATE_LIMIT_DELAY=0.1` → Avoid rate limit errors

**For Multiple Variables (Future):**
- `VARIABLE_LEVEL_WORKERS=3` → Max concurrent variables
- `BATCH_LEVEL_WORKERS=5` → Concurrent batches per variable
- Total concurrent calls = 3 × 5 = 15 (watch rate limits!)

**OpenAI Rate Limits (gpt-4o-mini):**
- **RPM** (Requests Per Minute): 500 default, 10,000 with Tier 2
- **TPM** (Tokens Per Minute): 200,000 default, 2M with Tier 2
- **Current usage**: ~50-100 RPM with 5 workers
- **Safe limit**: Max 10 workers untuk avoid 429 errors

---

## 📈 PERFORMANCE OPTIMIZATION ROADMAP

### **Milestone 1: Validate Current (Jan 2-3, 2026)** 🎯 CURRENT
- ✅ Test single variable (100, 1000, 5000 responses)
- ✅ Test 2 variables parallel
- ✅ Test multiple variables (3-10)
- ✅ Measure baseline performance
- ✅ Document bottlenecks

**Deliverable**: Testing report dengan metrics lengkap

---

### **Milestone 2: Variable-Level Parallelization (Jan 4-5, 2026)** 🚀 NEXT
**Goal**: Process multiple variables simultaneously (like BigQuery)

**Implementation Steps:**
1. Create `VariableLevelParallelClassifier` class
2. Add nested ThreadPoolExecutor:
   - Outer: Variable-level (max 3 concurrent variables)
   - Inner: Batch-level (5 workers per variable)
3. Implement shared progress tracking with locks
4. Add rate limiting logic (global across all workers)
5. Update `app/routes.py` untuk use new parallelization

**Technical Design:**
```python
class VariableLevelParallelClassifier:
    def __init__(self, max_variable_workers=3, max_batch_workers=5):
        self.max_variable_workers = max_variable_workers
        self.max_batch_workers = max_batch_workers
        self.rate_limiter = RateLimiter(max_rpm=450)  # 90% of 500 RPM limit
    
    def classify_multiple_variables(self, variable_configs):
        """Process multiple variables in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_variable_workers) as executor:
            futures = [
                executor.submit(self._classify_single_variable, config)
                for config in variable_configs
            ]
            # Collect results as they complete
            for future in as_completed(futures):
                yield future.result()
    
    def _classify_single_variable(self, config):
        """Process single variable with batch parallelization"""
        parallel_classifier = ParallelClassifier(
            classifier=self.classifier,
            max_workers=self.max_batch_workers,
            rate_limiter=self.rate_limiter  # Shared rate limiter!
        )
        return parallel_classifier.classify_parallel(...)
```

**Expected Performance:**
- **3 variables**: 2.5-3x faster
- **5 variables**: 4-5x faster
- **10 variables**: 8-10x faster

**Challenges:**
- Rate limiting coordination
- Memory management (multiple datasets in RAM)
- Error handling per variable
- Progress tracking complexity

---

### **Milestone 3: Advanced Optimizations (Jan 6-7, 2026)** 🔮 FUTURE

**Potential Enhancements:**
1. **Adaptive Batch Sizing**
   - Small responses (short text): batch_size=20
   - Large responses (long text): batch_size=5
   - Auto-adjust based on token count

2. **Response Caching**
   - Cache identical responses (e.g., "TA", "tidak ada")
   - Avoid redundant API calls
   - Expected: 5-10% savings

3. **Streaming Results**
   - Write to Excel as results complete (per variable)
   - Don't wait for all variables to finish
   - Reduce memory usage

4. **GPU-based Preprocessing** (Advanced)
   - Use local embedding model untuk initial filtering
   - Only send filtered responses to OpenAI
   - Hybrid approach: Local + Cloud

5. **Multi-Account Rate Limiting**
   - Distribute requests across multiple OpenAI accounts
   - Load balancing for massive datasets
   - 2-3x throughput increase

---

## 🎯 SUCCESS METRICS

### **Performance Targets:**
- ✅ **Throughput**: 15-20 responses/second (single variable)
- ✅ **Throughput**: 40-50 responses/second (3 variables parallel)
- ✅ **Latency**: <2 minutes untuk 1000 responses (single variable)
- ✅ **Accuracy**: >90% responses dengan confidence >0.5
- ✅ **Error Rate**: <1% failed classifications
- ✅ **Memory**: <3GB peak usage (5000 responses)
- ✅ **Cost**: <$0.10 per 1000 responses

### **Reliability Targets:**
- ✅ **Uptime**: 99%+ (no crashes during classification)
- ✅ **Retry Success**: >95% pada rate limit errors
- ✅ **Data Integrity**: 100% (no lost responses)
- ✅ **Progress Accuracy**: ±2% of actual progress

---

## 📝 TESTING CHECKLIST

**Before Each Test:**
- [ ] Check OpenAI API key valid
- [ ] Verify OpenAI account balance (min $5)
- [ ] Clear old files dari `files/uploads/`
- [ ] Check database space (SQLite size)
- [ ] Monitor system resources (Task Manager)

**During Test:**
- [ ] Record start time
- [ ] Monitor terminal output for errors
- [ ] Watch progress percentage
- [ ] Check memory usage (should be stable)
- [ ] Note any rate limit warnings

**After Test:**
- [ ] Verify all jobs completed (status='completed')
- [ ] Check output files exist and readable
- [ ] Validate column counts match expectations
- [ ] Spot-check 10-20 classifications for accuracy
- [ ] Calculate actual throughput (responses/second)
- [ ] Document any issues or anomalies

---

## 🐛 KNOWN ISSUES & WORKAROUNDS

### **Issue 1: Rate Limit Errors (429)**
**Symptom**: `Rate limit exceeded` errors
**Cause**: Too many concurrent requests
**Workaround**: 
- Reduce `PARALLEL_MAX_WORKERS` to 3-4
- Increase `RATE_LIMIT_DELAY` to 0.2-0.3s
- Upgrade OpenAI tier (Tier 2 = 10,000 RPM)

### **Issue 2: Memory Spike on Large Datasets**
**Symptom**: RAM usage >4GB
**Cause**: Loading entire dataset into pandas DataFrame
**Workaround**:
- Process in chunks (max 2000 responses per chunk)
- Clear DataFrame after each variable
- Use `gc.collect()` between variables

### **Issue 3: Slow Progress Updates**
**Symptom**: Progress stuck or jumps
**Cause**: SSE buffering or browser throttling
**Workaround**:
- Force flush in SSE (already implemented)
- Reduce update frequency (every 5% instead of 1%)
- Use WebSocket instead of SSE (future)

---

## 📞 SUPPORT & ESCALATION

**If Testing Fails:**
1. Check terminal logs for stack traces
2. Verify `.env` configuration
3. Test with smaller dataset first (100 responses)
4. Check OpenAI API status: https://status.openai.com/
5. Review CHANGELOG.md untuk recent changes

**Contact:**
- Developer: haryadi@markplusinc.com
- WhatsApp: +62 812-8933-008

---

**Last Updated**: 2 Januari 2026  
**Document Owner**: Haryadi (MarkPlus Indonesia)  
**Status**: ✅ Ready for Phase 1 Testing

