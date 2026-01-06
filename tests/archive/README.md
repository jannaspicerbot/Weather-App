# Test Archive

This directory contains **archived experimental and diagnostic scripts** from historical investigations and testing efforts. These files are preserved for reference but are no longer actively maintained.

---

## 📁 Directory Structure

### `api-debugging/` - API Rate Limiting Investigation

**Investigation Period:** January 4-5, 2026
**Status:** ✅ **RESOLVED**

**Root Cause Identified:** Sequential API calls with only **400ms delay** between requests violated Ambient Weather's **1 API call/second** rate limit requirement.

**Resolution:** Updated API client to enforce **1.1-second delay** between sequential calls. Rate limiting (429 errors) eliminated permanently.

**Key Finding:** The issue was **NOT an account tier limitation** (free vs paid). The free tier supports the required call frequency when proper delays are implemented.

---

### Scripts in `api-debugging/`

| Script | Purpose | Status |
|--------|---------|--------|
| `diagnose_api_fixes.py` | Tests timeout, User-Agent, and session pooling fixes | Historical diagnostic |
| `DIAGNOSTIC_README.md` | Usage guide for diagnostic script | Reference only |
| `experiment_basic_connectivity.py` | Phase 1: Basic API connectivity testing | Completed |
| `experiment_cooldown_detection.py` | Cooldown period detection (30s recovery) | Completed |
| `experiment_diagnostics.py` | General diagnostic testing | Completed |
| `experiment_frequency_test.py` | Phase 2: Frequency tolerance testing | Completed |
| `experiment_historical_data.py` | Phase 4: Historical data fetching tests | Completed |
| `experiment_our_client.py` | Phase 3: Custom client testing | Completed |
| `test_rate_limit_incremental.py` | Incremental rate limit testing | Completed |
| `check_retry_after.py` | Quick Retry-After header check | Completed |
| `manual_websocket_test.py` | WebSocket connectivity test | Completed |

---

## 🔍 Investigation Summary

### Problem
Ambient Weather API returned `429 Too Many Requests` (`above-user-rate-limit`) errors inconsistently, preventing reliable data collection.

### Investigation Phases
1. **Basic Connectivity** - Confirmed API credentials and endpoints worked
2. **Frequency Testing** - Tested various call intervals (1s, 5s, 60s)
3. **Cooldown Detection** - Discovered 30-second recovery period after 429
4. **Fix Diagnostics** - Tested timeout, User-Agent, session pooling improvements
5. **Code Review** - **FOUND ROOT CAUSE**: 400ms delay in sequential calls

### Solution Implemented
Updated `weather_app/api/client.py`:
```python
# Before (WRONG - 400ms between calls)
time.sleep(0.4)  # Too fast! Triggers rate limiting

# After (CORRECT - 1.1s between calls)
time.sleep(1.1)  # Respects 1 call/second limit
```

### Related Documentation
- **Investigation Details:** `docs/archive/troubleshooting/investigation-summary.md`
- **Phase Results:** `docs/archive/troubleshooting/phase-*-results.md`
- **Findings:** `docs/archive/troubleshooting/backend-diagnostic-findings.md`

---

## 📚 Lessons Learned

1. **Read API Documentation Carefully** - Ambient Weather clearly states "1 API call/second" limit
2. **Measure Actual Delays** - Code review revealed timing mismatch (400ms vs 1000ms)
3. **Don't Assume Account Tiers** - Free tier was sufficient when used correctly
4. **Sequential Testing** - Systematic investigation phases helped isolate the issue
5. **Document Findings** - Preserved investigation for future reference

---

## ⚠️ Usage Warning

**These scripts are NOT maintained and may not work with current codebase.**

- API endpoints may have changed
- Database schema may be different
- Dependencies may be outdated
- Error handling may be incomplete

**For current testing:** See `tests/integration/` for active test suite.

---

## 🗂️ Archive Maintenance

**Last Updated:** January 6, 2026
**Archived By:** Reorganization in branch `chore/reorganize-tests-and-docs`

If you need to reference these scripts:
1. Check git history for original context
2. Review related documentation in `docs/archive/troubleshooting/`
3. DO NOT use as-is - adapt to current architecture if needed
