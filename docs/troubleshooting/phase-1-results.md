# Phase 1 Results: Basic Connectivity Test

**Date:** 2026-01-04
**Time:** 09:55-09:56 PST
**Duration:** ~1 minute
**Status:** ❌ CRITICAL FINDING

---

## Summary

We successfully called the Ambient Weather API but **immediately hit rate limits** after just 2 API calls. This is drastically different from the external user who can make **1,440 calls in 24 hours** without issues.

---

## Test Results

### Test 1.1: Device List API ✅ SUCCESS

**Endpoint:** `GET /v1/devices`

**Request:**
```
URL: https://api.ambientweather.net/v1/devices
Params: apiKey=...d579, applicationKey=...1364
Time: 2026-01-04T09:56:04.311428
```

**Response:**
```
Status: 200 OK
Response Time: 0.31s
Body: 1 device found
  - MAC: C8:C9:A3:10:36:F4
  - Name: Default
```

**Headers (notable):**
- `Content-Type: application/json; charset=utf-8`
- `X-Powered-By: Express`
- `Access-Control-Allow-Origin: *`
- `Server: cloudflare`
- **NO Rate Limit Headers**

**Verdict:** ✅ API credentials work, device list endpoint accessible

---

### Test 1.2: Device Data API ❌ RATE LIMITED

**Endpoint:** `GET /v1/devices/{macAddress}`

**Request:**
```
URL: https://api.ambientweather.net/v1/devices/C8:C9:A3:10:36:F4
Params: limit=1, apiKey=...d579, applicationKey=...1364
Time: 2026-01-04T09:56:04.628738
```

**Response:**
```
Status: 429 Too Many Requests
Response Time: 0.30s
Body: {"error":"above-user-rate-limit"}
```

**Headers (notable):**
- `Content-Type: application/json; charset=utf-8`
- **Retry-After: NOT PRESENT** ← Confirms external user's observation
- `Server: cloudflare`

**Verdict:** ❌ Rate limited after just 2 total API calls

---

## Critical Findings

### 1. Immediate Rate Limiting

We got rate limited (`429`) after:
- **1 successful call** to `/v1/devices`
- **1 call** to `/v1/devices/{mac}` (the one that failed)
- **Total time elapsed:** <1 second between calls

This is **extremely aggressive** rate limiting.

### 2. No Retry-After Header

✅ **Confirms external user's report:** They said they've never seen a `Retry-After` header in 429 responses.

Our response:
```json
{
  "error": "above-user-rate-limit"
}
```

No guidance on when to retry.

### 3. Comparison to External User

| Metric | Our Experience | External User |
|--------|---------------|---------------|
| Calls before 429 | **2 calls** | **1,440+ calls (24 hours)** |
| Retry-After header | Not present | Not present (confirmed) |
| Time to rate limit | **<1 second** | Never seen it |

**Conclusion:** Our account has **drastically** different rate limits.

---

## Hypotheses

### Hypothesis 1: Account Type Difference (MOST LIKELY)
- External user may have paid/premium account
- We may have free/trial account with strict limits
- Different account tiers = different rate limits

**Evidence:**
- 720x difference in allowed calls (2 vs 1,440+)
- Both using same API endpoints
- Both experiencing no Retry-After header

**Next Step:** Ask external user about account type

### Hypothesis 2: Account Flagged/Restricted
- Our API keys may be flagged for abuse
- Previous testing may have triggered restrictions
- Account may need verification/activation

**Evidence:**
- Immediate rate limiting
- "above-user-rate-limit" suggests user-specific limit

**Next Step:** Check Ambient Weather dashboard for account status

### Hypothesis 3: API Call Sequence Matters
- Device list API doesn't count toward limits?
- Device data API has separate, stricter limits?
- First call to device data triggers cooldown?

**Evidence:**
- Device list succeeded (200 OK)
- Device data immediately failed (429)

**Next Step:** Test device data API in isolation (after cooldown)

### Hypothesis 4: Previous Testing Triggered Lockout
- Our previous API testing sessions may have accumulated
- Account may be in "penalty box" mode
- Rate limit resets may be slower than we think

**Evidence:**
- We've made many test calls over past weeks
- May have hit daily/weekly quota

**Next Step:** Wait 24 hours and retest

---

## Key Differences from External User

Based on their feedback:

| Aspect | External User | Us |
|--------|---------------|-----|
| **Frequency** | Every minute for 24 hours | Rate limited in <1 second |
| **Total calls** | 1,440+ successful | 1 success, then lockout |
| **Burst behavior** | 2 req/sec for 5 sec OK | Not tested (locked out) |
| **429 frequency** | Extremely rare | Immediate |
| **Retry-After** | Never seen | Never seen (confirmed) |
| **Recovery time** | 5 seconds after burst | Unknown (need to test) |

---

## What We Learned

### ✅ Confirmed
1. Our API credentials are valid (device list works)
2. We can successfully call at least one endpoint
3. No Retry-After header in 429 responses (matches user report)
4. Response format: `{"error":"above-user-rate-limit"}`

### ❌ Blocked
1. Cannot access device data endpoint
2. Rate limits are much stricter than external user
3. Cannot proceed with frequency testing (Phase 2)
4. Cannot test our client code (Phase 3)

### ❓ Unknown
1. ✅ **RESOLVED:** Lockout period is 30 seconds (see [cooldown-test-results.md](cooldown-test-results.md))
2. What triggers the rate limit? (appears to be 2 calls in quick succession)
3. Is this account-level or endpoint-level? (likely account-level)
4. ✅ **RESOLVED:** Yes, we can access after 30-second cooldown

---

## Recommended Next Steps

### Immediate Actions

1. **Document cooldown period**
   - Create test to check when we can call API again
   - Test every 1 minute for 10 minutes
   - Test every 5 minutes for 30 minutes
   - Document recovery time

2. **Check Ambient Weather Dashboard**
   - Log into ambientweather.net/account
   - Check API key status
   - Look for usage limits/quotas
   - Check for account verification requirements

3. **Test isolated device data call**
   - Wait for cooldown
   - Call ONLY `/v1/devices/{mac}` (skip device list)
   - See if it succeeds or still 429s

### Questions for External User

1. **What type of Ambient Weather account do you have?**
   - Free tier?
   - Paid subscription?
   - Developer account?

2. **Can you share your account settings?**
   - Any special API access enabled?
   - Any rate limit notifications in dashboard?

3. **How did you discover the sliding window behavior?**
   - Did you ever hit 429s during testing?
   - What was your testing methodology?

4. **When did you create your API keys?**
   - Recently or long ago?
   - Any special activation process?

---

## Technical Details

### Full Request/Response Logs

#### Test 1.1: Device List (SUCCESS)
```
REQUEST:
  GET https://api.ambientweather.net/v1/devices
  Params: apiKey=dfa...d579, applicationKey=914...1364

RESPONSE:
  Status: 200 OK
  Time: 0.31s
  Headers:
    Date: Sun, 04 Jan 2026 17:56:05 GMT
    Content-Type: application/json; charset=utf-8
    Transfer-Encoding: chunked
    Connection: keep-alive
    X-Powered-By: Express
    Access-Control-Allow-Origin: *
    ETag: W/"679-nUD3Zu8CkLMrAZdwoa3mMA"
    Vary: Accept-Encoding
    Content-Encoding: gzip
    cf-cache-status: DYNAMIC
    Server: cloudflare
    CF-RAY: 9b8c9c50b8ce816e-PDX

  Body: [
    {
      "macAddress": "C8:C9:A3:10:36:F4",
      "info": {
        "name": "Default",
        ...
      },
      ...
    }
  ]
```

#### Test 1.2: Device Data (RATE LIMITED)
```
REQUEST:
  GET https://api.ambientweather.net/v1/devices/C8:C9:A3:10:36:F4
  Params: limit=1, apiKey=dfa...d579, applicationKey=914...1364

RESPONSE:
  Status: 429 Too Many Requests
  Time: 0.30s
  Headers:
    Date: Sun, 04 Jan 2026 17:56:06 GMT
    Content-Type: application/json; charset=utf-8
    Content-Length: 33
    Connection: keep-alive
    X-Powered-By: Express
    Access-Control-Allow-Origin: *
    ETag: W/"21-DY983xAsea5u7XZJmjbNnA"
    Vary: Accept-Encoding
    cf-cache-status: DYNAMIC
    Server: cloudflare
    CF-RAY: 9b8c9c529eefc153-PDX

  Body: {"error":"above-user-rate-limit"}
```

**Notable:** No `Retry-After`, `X-RateLimit-*`, or similar headers

---

## Conclusion

**Phase 1 Status:** ❌ FAILED (cannot proceed to Phase 2)

**Root Cause:** Account rate limits are 720x stricter than external user

**Next Steps:**
1. Contact external user for account type information
2. Test cooldown period to understand recovery time
3. Check Ambient Weather dashboard for account restrictions
4. Consider generating new API keys if account is flagged

**Blocker:** Cannot test frequency tolerance, client code, or any real usage until rate limit issue is resolved.

---

**Last Updated:** 2026-01-04 09:56 PST
