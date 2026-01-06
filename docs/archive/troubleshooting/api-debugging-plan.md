# API Rate Limiting Investigation Plan

**Date:** 2026-01-04
**Status:** In Progress
**Branch:** `debug/api-rate-limiting-investigation`

---

## Context

External user feedback reveals our assumptions about rate limiting may be wrong:

1. ✅ User hits API **every minute for 24 hours** with zero 429 errors
2. ❌ User has **never seen a Retry-After header** in 429 responses
3. 🔍 Rate limiting appears to be **sliding window**, not fixed interval
4. 🚨 REST API only provides **5-minute resolution** (not real-time)

**Our situation:**
- We get 429 errors quickly
- Our backfill is MORE conservative than the successful user
- Something fundamental is different about our approach

---

## Hypothesis

**Primary:** We're not being rate-limited - something else is causing 429s
**Alternative:** Our API keys/MAC address have different limits
**Unlikely:** User is wrong about their experience

---

## Systematic Experiments

### Phase 1: Validate Basic Connectivity ✅ CRITICAL

**Goal:** Confirm our credentials work at all

#### Experiment 1.1: Single Device List Call
```bash
curl "https://api.ambientweather.net/v1/devices?apiKey=YOUR_KEY&applicationKey=YOUR_APP_KEY"
```

**Expected:** 200 OK with device list
**If 429:** Credentials may be flagged/banned
**If 401:** API keys invalid
**If 200:** Credentials work, issue is elsewhere

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 1.2: Single Device Data Call
```bash
curl "https://api.ambientweather.net/v1/devices/MAC_ADDRESS?apiKey=YOUR_KEY&applicationKey=YOUR_APP_KEY&limit=1"
```

**Expected:** 200 OK with 1 reading
**If 429:** Problem confirmed
**If 200:** Basic calls work

**Status:** [ ] Not Started
**Result:** _____

---

### Phase 2: Test Frequency Tolerance 🔬

**Goal:** Replicate the user's "every minute for 24 hours" success

#### Experiment 2.1: 10 Requests at 1-Minute Intervals
```python
# Script: tests/experiment_01_minute_intervals.py
for i in range(10):
    response = requests.get(endpoint)
    print(f"{i+1}. Status: {response.status_code}")
    time.sleep(60)  # 1 minute
```

**Expected:** All 200 OK (like the external user)
**If 429s appear:** Our account has different limits
**If all 200:** We can be more aggressive

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 2.2: 60 Requests at 1-Minute Intervals (1 Hour)
Same as 2.1, but run for 1 hour (60 iterations)

**Expected:** All 200 OK
**If 429:** Note when it starts

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 2.3: Burst Test (Sliding Window Detection)
```python
# Replicate user's observation:
# "2 req/sec for 5 seconds = OK, 6 seconds = 429"

for burst_duration in [5, 6, 7, 8]:
    print(f"Testing {burst_duration} second burst...")
    for i in range(burst_duration * 2):  # 2 req/sec
        response = requests.get(endpoint)
        print(f"  {i+1}. {response.status_code}")
        time.sleep(0.5)
    time.sleep(10)  # Cool down
```

**Expected:** 429 appears after ~6 seconds of bursting
**Outcome:** Confirms sliding window behavior

**Status:** [ ] Not Started
**Result:** _____

---

### Phase 3: Validate Our Current Code 🐛

**Goal:** Find what's different about our implementation

#### Experiment 3.1: Test Our API Client Directly
```python
# Run our actual client code
from weather_app.api.ambient_client import AmbientWeatherClient

client = AmbientWeatherClient(api_key, app_key)
devices = client.get_devices()
print(f"Devices: {devices}")

data = client.get_device_data(mac_address, limit=1)
print(f"Data: {data}")
```

**Expected:** Should work if Phase 1 passed
**If fails:** Issue is in our client code

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 3.2: Compare Headers/Query Params
```python
# Our request
our_request = {
    "url": "...",
    "params": {...},
    "headers": {...}
}

# Working curl request
curl_equivalent = "..."

# Compare and document differences
```

**Look for:**
- Extra headers we're sending
- Query param encoding differences
- User-Agent strings
- Anything unexpected

**Status:** [ ] Not Started
**Result:** _____

---

### Phase 4: Test Historical Data Retrieval 📊

**Goal:** Understand if historical queries have different limits

#### Experiment 4.1: Small Date Range (1 Day)
```python
# Get 1 day of data (288 5-minute readings)
end_date = datetime.now()
start_date = end_date - timedelta(days=1)

response = client.get_device_data(
    mac_address,
    end_date=end_date,
    limit=288
)
```

**Expected:** 200 OK
**If 429:** Even small historical queries trigger it

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 4.2: Multiple Small Queries vs One Large Query
```python
# Approach A: One large query
response = client.get_device_data(mac, limit=1000)

# Approach B: 10 small queries
for i in range(10):
    response = client.get_device_data(mac, limit=100)
    time.sleep(60)
```

**Compare:** Which approach triggers 429s faster?

**Status:** [ ] Not Started
**Result:** _____

---

### Phase 5: Authentication & Account Status 🔑

**Goal:** Rule out account-level issues

#### Experiment 5.1: Check API Key Format
```python
print(f"API Key length: {len(api_key)}")
print(f"App Key length: {len(app_key)}")
print(f"API Key format: {api_key[:4]}...{api_key[-4:]}")
print(f"App Key format: {app_key[:4]}...{app_key[-4:]}")
```

**Verify:**
- Keys are correct length
- No whitespace/newlines
- No special characters causing issues

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 5.2: Test with Fresh API Keys
If possible, generate NEW API keys from Ambient Weather dashboard and test

**Expected:** Same behavior if account-level limit
**If different:** Old keys may be rate-limited/flagged

**Status:** [ ] Not Started (requires user action)
**Result:** _____

---

### Phase 6: Network & Infrastructure 🌐

**Goal:** Rule out local network issues

#### Experiment 6.1: Test from Different Network
Run same API call from:
- Home network
- Mobile hotspot
- VPN
- Different geographic location

**Expected:** Same behavior everywhere
**If different:** IP-based rate limiting?

**Status:** [ ] Not Started
**Result:** _____

---

#### Experiment 6.2: Check for IP Blocking
```bash
# Check our public IP
curl ifconfig.me

# Test if IP is on any blocklists
# (Ambient may block known VPS/cloud IPs)
```

**Status:** [ ] Not Started
**Result:** _____

---

## Decision Tree

```
START
  │
  ├─ Phase 1 (Basic): Single calls work?
  │   ├─ NO → Credentials invalid/banned → Contact Ambient Support
  │   └─ YES → Continue to Phase 2
  │
  ├─ Phase 2 (Frequency): Can hit API every minute?
  │   ├─ NO → Account has stricter limits → Ask external user about account type
  │   └─ YES → Continue to Phase 3
  │
  ├─ Phase 3 (Our Code): Our client works same as curl?
  │   ├─ NO → Bug in our code → Fix implementation
  │   └─ YES → Continue to Phase 4
  │
  ├─ Phase 4 (Historical): Historical queries different?
  │   ├─ YES → Adjust strategy for historical vs real-time
  │   └─ NO → Continue to Phase 5
  │
  ├─ Phase 5 (Auth): Fresh keys work better?
  │   ├─ YES → Old keys flagged → Use new keys
  │   └─ NO → Continue to Phase 6
  │
  └─ Phase 6 (Network): Different network helps?
      ├─ YES → IP-based limiting → Use different network/VPN
      └─ NO → Contact external user for more details
```

---

## Test Scripts to Create

### 1. `tests/experiment_basic_connectivity.py`
- Single device list call
- Single device data call
- Log full request/response

### 2. `tests/experiment_frequency_test.py`
- 10 calls at 1-minute intervals
- 60 calls at 1-minute intervals
- Burst test (sliding window)

### 3. `tests/experiment_our_client.py`
- Test our AmbientWeatherClient
- Compare our requests vs working curl
- Log all headers/params

### 4. `tests/experiment_historical_data.py`
- 1-day query
- Multiple small vs one large
- Date range variations

### 5. `tests/experiment_diagnostics.py`
- Check API key formats
- Network diagnostics
- Request/response logging

---

## Success Criteria

We've solved the problem when:
- [ ] We can hit the API every minute for 1 hour without 429s (like external user)
- [ ] We understand the actual rate limits
- [ ] We have a working backfill strategy
- [ ] We've documented the root cause

---

## Notes & Observations

### User Feedback Summary
- Every minute for 24 hours = 1,440 requests/day ✅ No 429s
- Burst: 2 req/sec for 5 sec ✅ OK
- Burst: 2 req/sec for 6 sec ❌ 429
- Recovery: 5 seconds of no requests to stop 429ing
- No Retry-After header ever seen

### Our Current Behavior
- [Document what we're experiencing]
- [When do we get 429s?]
- [What's different from the user?]

---

## Next Steps After Debugging

Once we identify the issue:

1. **Update code** to match working approach
2. **Document findings** in troubleshooting guide
3. **Share results** with external user
4. **Update API client** with proper rate limiting
5. **Test backfill** with new understanding

---

## Questions for External User (If Still Stuck)

Only ask if we can't solve it ourselves:

1. What type of Ambient Weather account do you have? (Free/paid?)
2. Can you share your exact request format? (curl command with keys redacted)
3. How did you discover the sliding window behavior?
4. What is your "direct ingestion service"? (Technical details)
5. Any other tips for working with Ambient's API?

---

**Status Tracking:**
- [ ] Phase 1 Complete
- [ ] Phase 2 Complete
- [ ] Phase 3 Complete
- [ ] Phase 4 Complete
- [ ] Phase 5 Complete
- [ ] Phase 6 Complete
- [ ] Root cause identified
- [ ] Solution implemented
- [ ] Tests passing

**Last Updated:** 2026-01-04
