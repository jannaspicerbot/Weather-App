# API Diagnostic Testing

## Purpose

This diagnostic script tests three high-probability fixes for API connection issues:

1. **Fix #1: Request Timeouts** - Prevents hanging connections that may count against rate limits
2. **Fix #2: Custom User-Agent Header** - Avoids bot-tier rate limiting
3. **Fix #3: Session Connection Pooling** - Reuses connections instead of creating new ones

## Prerequisites

1. Ensure you have your API credentials in `.env`:
   ```bash
   AMBIENT_API_KEY=your_key_here
   AMBIENT_APP_KEY=your_app_key_here
   ```

2. **Important**: Check if any backend servers are running:
   - If `localhost:5173` is showing data, a backend is active
   - This may cause concurrent API calls that exhaust rate limits
   - Consider stopping the backend before running diagnostics

## Running the Diagnostic

```bash
# From the project root
cd "c:\GitHub Repos\Weather-App"

# Run the diagnostic script
python tests/diagnose_api_fixes.py
```

## What the Script Tests

### Test 1: Current Implementation (Baseline)
- No timeout
- Default User-Agent (`python-requests/X.X.X`)
- New connection per request

**This mimics the current `weather_app/api/client.py` implementation.**

### Test 2: Fix #1 - Add Timeout
- **30-second timeout**
- Default User-Agent
- New connection per request

### Test 3: Fix #2 - Custom User-Agent
- 30-second timeout
- **Custom User-Agent: `WeatherApp/1.0`**
- New connection per request

### Test 4: Fix #3 - Session Connection Pooling
- 30-second timeout
- Custom User-Agent
- **`requests.Session()` for connection reuse**

### Test 5: Burst Behavior
- Tests 3 rapid consecutive calls (10-second intervals)
- Compares behavior WITH and WITHOUT fixes
- Identifies if fixes help prevent rate limiting

## Interpreting Results

The script will output a summary showing which tests succeeded/failed.

### Scenario 1: All Tests Fail
**Conclusion**: Account tier is likely the root cause (rate limits too strict)
**Action**: Contact Ambient Weather support or upgrade account

### Scenario 2: Some Tests Succeed
**Conclusion**: Specific fixes help!
**Action**: Implement the successful fixes in `weather_app/api/client.py`

### Scenario 3: Gradual Improvement
**Conclusion**: Each fix contributes incrementally
**Action**: Implement all three fixes for best results

### Scenario 4: Current Implementation Works
**Conclusion**: API is working fine, issue may be:
- Concurrent requests (scheduler + manual CLI)
- Timing-specific (retry later)
**Action**: Check for background processes

## Expected Output

```
================================================================================
DIAGNOSTIC TEST RESULTS SUMMARY
================================================================================

✅ Current Implementation
   Status Code: 200
   Duration: 234.56ms
   Request Headers: {'User-Agent': 'python-requests/2.31.0'}

✅ Fix #1: Timeout Only
   Status Code: 200
   Duration: 198.23ms
   ...

================================================================================
ANALYSIS
================================================================================
Success Rate: 4/5 (80.0%)

🔍 Root Cause Analysis:
   ✅ Fix #2: Custom User-Agent SUCCEEDED - This fix helps!
   ✅ Fix #3: Session + All Fixes SUCCEEDED - This fix helps!
```

## Safety Notes

1. **Rate Limit Risk**: Tests are spaced 10 seconds apart to minimize rate limit triggers
2. **Pause Points**: The script asks for confirmation before burst tests
3. **Background Processes**: Stop any running schedulers or servers before testing
4. **Cooldown**: If you hit a rate limit (429), wait 30 seconds before retrying

## Next Steps

After running the diagnostic:

1. **Save the output** to a file for team discussion
2. **Identify which fixes helped** (if any)
3. **Implement successful fixes** in the main codebase
4. **Re-run diagnostic** to verify improvements

## Files Created in This Branch

- `tests/diagnose_api_fixes.py` - Main diagnostic script
- `tests/DIAGNOSTIC_README.md` - This file

## Branch

This work is being done in branch: `backend-bug-fixing-v02`
