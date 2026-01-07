# Windows Installer Root Cause Analysis & Test Plan

**Date:** January 6, 2026
**Status:** Investigation In Progress
**Branch:** `bugfix/windows-installer-root-cause-analysis`

---

## Executive Summary

After multiple attempted fixes (PRs #33, #37, #38), the Windows installer still has critical issues. This document provides deep root cause analysis and a systematic testing approach to fix them once and for all.

### Three Critical Issues

1. **Production .exe immediately aborts when started** - Silent crash, no error message
2. **System tray icon never appears** - App runs but no UI control
3. **Debug version doesn't use test database or show full frontend** - Configuration not working

---

## Root Cause Analysis

### Issue 1: Production .exe Immediate Abort

#### Hypothesis Tree

```
Production .exe crashes immediately
├── PyInstaller bundling issues
│   ├── Missing critical dependencies (MOST LIKELY)
│   │   ├── DuckDB binary extensions not bundled correctly
│   │   ├── PIL/pystray native dependencies missing
│   │   └── Uvicorn worker modules not found
│   ├── Resource paths broken in frozen environment
│   │   ├── sys._MEIPASS not handled correctly
│   │   ├── Frontend dist/ path resolution fails
│   │   └── Icon resource path incorrect
│   └── Import errors due to hidden imports
│       ├── Dynamic imports not detected
│       └── Circular import issues in frozen state
├── Runtime errors
│   ├── Environment variable loading fails
│   │   ├── .env file path resolution broken
│   │   └── BASE_DIR calculation incorrect when frozen
│   ├── Setup wizard tkinter issues
│   │   ├── tkinter not bundled (unlikely on Windows)
│   │   └── Wizard crashes before tray app starts
│   └── Exception handling suppresses errors (console=False)
└── Windows-specific issues
    ├── Missing VC++ redistributables
    ├── Windows Defender blocking execution
    └── DLL loading failures
```

#### Evidence Analysis

From commit history:
- PR #37: Fixed callback signatures, bundled icons → Still crashes
- PR #38: Fixed route conflicts → Dashboard displays but exe still crashes
- **Key Finding**: Changes were made to source but exe behavior suggests bundling issues

**Critical Gap**: No diagnostic logging at startup to capture WHY it crashes

### Issue 2: System Tray Icon Never Appears

#### Hypothesis Tree

```
Tray icon not visible
├── pystray Windows 11 compatibility (SUSPECTED)
│   ├── Windows 11 security model blocks unsigned tray apps
│   ├── pystray version incompatibility with Win11
│   └── Missing notification area permissions
├── Icon creation fails silently
│   ├── Image loading returns None
│   ├── pystray.Icon() raises exception caught by try-except
│   └── icon.run() starts but icon never renders
├── PyInstaller bundling
│   ├── pystray native dependencies missing
│   ├── PIL image codecs not bundled
│   └── Threading issues in frozen environment
└── App architecture issue
    ├── icon.run() is non-blocking when it should block
    ├── Main thread exits before icon renders
    └── Exception in icon creation swallowed by broad except
```

#### Evidence Analysis

From PR #37:
- Icons ARE bundled: `datas += [(str(icons_dir), 'weather_app/resources/icons')]`
- Error handling added: App continues without tray icon
- **Key Finding**: "Icon.run() executing successfully" but icon not visible

**This is NOT a bundling issue - it's a pystray/Windows 11 compatibility issue**

### Issue 3: Debug Version Configuration Not Working

#### Hypothesis Tree

```
Debug version doesn't use test DB or full frontend
├── Environment variable issues
│   ├── USE_TEST_DB not set when running debug build
│   ├── Debug spec doesn't inject environment variables
│   └── .env file not created/loaded in debug mode
├── Build configuration
│   ├── Debug spec uses same frontend dist/ (no mock data)
│   ├── Debug spec doesn't bundle test database
│   └── No runtime differentiation between prod/debug builds
└── Code logic issues
    ├── config.py doesn't detect debug mode correctly
    ├── sys.frozen detection works but USE_TEST_DB still false
    └── Frontend has no development mode when bundled
```

#### Evidence Analysis

Looking at `weather_app_debug.spec`:
- `debug=True` only enables PyInstaller debugging
- `console=True` shows console output
- **Critical Gap**: No mechanism to set USE_TEST_DB=true for debug builds
- **Critical Gap**: Frontend dist/ is production build, not dev build with mock data

**This is a configuration design issue - debug spec needs runtime hooks**

---

## The REAL Root Causes

### 1. No Diagnostic Instrumentation

**Problem:** When packaged with `console=False`, ALL errors are invisible.

**Current State:**
- launcher.py → tray_app.py → No startup logging
- Exceptions caught but not logged anywhere accessible
- User sees nothing - app just doesn't start

**Solution:**
- Add file-based logging BEFORE any imports
- Capture ALL exceptions and write to %APPDATA%/WeatherApp/crash.log
- Add PyInstaller runtime hooks to log bundling status

### 2. PyInstaller Resource Path Assumptions

**Problem:** Code assumes resources are at relative paths, but PyInstaller extracts to _MEIPASS.

**Current State:**
```python
# config.py
resources_icon = Path(__file__).parent.parent / "resources" / "icons" / "weather-app.png"
```

When frozen, this path is WRONG. Should use `sys._MEIPASS`.

**Solution:**
- Create resource path helper that detects frozen state
- All resource loading must go through this helper

### 3. No Bundling Verification

**Problem:** We don't verify critical files are actually bundled.

**Current State:**
- Spec file includes resources
- No verification they're actually in dist/
- No runtime check that files exist

**Solution:**
- Add bundling verification script
- Runtime startup check for critical resources
- Fail fast with clear error if resources missing

### 4. pystray Windows 11 Known Issue

**Problem:** pystray has known issues with Windows 11 and unsigned executables.

**Evidence:**
- App runs fine (server starts, dashboard opens)
- icon.run() executes without exception
- Icon just never appears in system tray

**Solution Options:**
1. Switch to different system tray library (infi.systray, win10toast-click)
2. Add Windows 11 permissions manifest
3. Document limitation and provide alternative launch method
4. Code-sign the executable

### 5. Debug Mode Not Actually Different

**Problem:** Debug spec is just prod spec with console=True.

**Current State:**
- Both use same frontend dist/
- Both use same environment variables
- Only difference is console window visibility

**Solution:**
- Debug spec needs runtime hook to set USE_TEST_DB=true
- Debug spec should bundle test database with sample data
- Debug spec should auto-open console for logging

---

## Comprehensive Test Plan

### Phase 1: Diagnostic Instrumentation (CRITICAL FIRST STEP)

**Goal:** Capture EXACTLY what's failing when exe runs

**Test 1.1: Add Crash Logging**
```python
# New file: weather_app/launcher/crash_logger.py
# Sets up file logging BEFORE any other imports
# Logs to %APPDATA%/WeatherApp/logs/crash.log
```

**Test 1.2: Add PyInstaller Runtime Hook**
```python
# New file: installer/windows/hooks/runtime_hook.py
# Logs all bundled resources at startup
# Verifies critical files exist
# Writes to crash.log
```

**Test 1.3: Add Resource Verification**
```python
# Modify launcher.py to verify resources before starting
# Check: frontend dist/, icons/, DuckDB extension
# Log missing resources and exit with error
```

**Success Criteria:**
- ✅ crash.log created even if app crashes immediately
- ✅ Log shows all import attempts and failures
- ✅ Log shows all bundled resource paths
- ✅ Clear error message if critical resource missing

### Phase 2: Fix Production Build

**Goal:** Production .exe starts without crashing

**Test 2.1: Fix Resource Paths**
```python
# Create: weather_app/launcher/resource_path.py
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and frozen."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = Path(__file__).parent.parent
    return Path(base_path) / relative_path
```

**Test 2.2: Verify DuckDB Bundling**
```bash
# After build, verify DuckDB extension is in dist/
dist/WeatherApp/_internal/duckdb/
```

**Test 2.3: Test Without Setup Wizard**
```python
# Temporarily disable setup wizard to isolate server startup
# if not run_setup():  # Comment out
#     sys.exit(0)
```

**Test 2.4: Test Console Version**
```bash
# Build with console=True first
# Run and capture stdout/stderr
WeatherApp.exe > output.log 2>&1
```

**Success Criteria:**
- ✅ WeatherApp.exe starts and stays running
- ✅ FastAPI server accessible at http://localhost:8000
- ✅ No crashes in crash.log
- ✅ All resources loaded successfully

### Phase 3: Fix System Tray Icon

**Goal:** Icon appears in Windows system tray

**Test 3.1: Test pystray Compatibility**
```python
# Minimal test script
import pystray
from PIL import Image

def test_tray():
    image = Image.new('RGB', (64, 64), color='red')
    icon = pystray.Icon("test", image, "Test")
    icon.run()

# Build and test on Windows 11
```

**Test 3.2: Try Alternative Libraries**
```python
# Test: infi.systray (pure Python, might work better)
# Test: win10toast-click (Windows-specific notifications)
```

**Test 3.3: Add Windows Manifest**
```xml
<!-- windows_manifest.xml -->
<trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
  <security>
    <requestedPrivileges>
      <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
    </requestedPrivileges>
  </security>
</trustInfo>
```

**Test 3.4: Notification Area Fallback**
```python
# If tray icon fails, use Windows toast notifications
# Provide alternative way to open dashboard (Start Menu shortcut)
```

**Success Criteria:**
- ✅ Icon visible in system tray, OR
- ✅ Alternative UI method working (notifications/shortcuts), AND
- ✅ User can easily access dashboard and quit app

### Phase 4: Fix Debug Build

**Goal:** Debug build uses test database and includes debugging aids

**Test 4.1: Create Runtime Hook for Debug Mode**
```python
# installer/windows/hooks/runtime_hook_debug.py
import os
os.environ['USE_TEST_DB'] = 'true'
os.environ['LOG_LEVEL'] = 'DEBUG'
# Force debug configuration
```

**Test 4.2: Bundle Test Database**
```python
# In weather_app_debug.spec
test_db = project_root / 'ambient_weather_test.duckdb'
if test_db.exists():
    datas += [(str(test_db), '.')]
```

**Test 4.3: Add Debug Startup Banner**
```python
# In debug mode, print to console:
# "===== DEBUG MODE ====="
# "Using test database: {DB_PATH}"
# "Log level: DEBUG"
```

**Test 4.4: Create Sample Test Data**
```python
# Script to create test database with mock data
# Bundle with debug build
```

**Success Criteria:**
- ✅ Debug exe shows console window with clear logging
- ✅ Debug exe uses test database (verified in console output)
- ✅ Test database contains sample data
- ✅ Dashboard shows test data, not production data

### Phase 5: Automated Testing

**Goal:** Prevent regression with automated tests

**Test 5.1: Build Verification Script**
```python
# tests/verify_build.py
# Checks dist/ for all required files
# Verifies file sizes, checksums
# Runs basic smoke test
```

**Test 5.2: Smoke Test Script**
```python
# tests/smoke_test_exe.py
# Launches exe in subprocess
# Waits 10 seconds
# Checks if process still running
# Checks if server responding
# Kills process
```

**Test 5.3: Resource Bundle Test**
```python
# tests/test_bundled_resources.py
# Extracts PyInstaller bundle
# Verifies all resources present
# Checks for missing dependencies
```

**Test 5.4: CI Integration**
```yaml
# .github/workflows/test-windows-build.yml
# Run on PR to main
# Build installer
# Run smoke tests
# Fail if tests fail
```

**Success Criteria:**
- ✅ All tests pass before merging to main
- ✅ Automated smoke test catches crashes
- ✅ Resource verification catches missing files
- ✅ CI prevents broken builds from being merged

---

## Implementation Order

### IMMEDIATE (Do This First)

1. **Add crash logging to launcher.py** - We MUST see what's failing
2. **Build with console=True** - Run and capture REAL error messages
3. **Add resource verification** - Check what's actually bundled

### NEXT (After We Have Diagnostics)

4. **Fix resource paths** - Use sys._MEIPASS when frozen
5. **Verify DuckDB bundling** - Ensure binary extensions included
6. **Test server startup in isolation** - Remove setup wizard temporarily

### THEN (Once Production Builds Work)

7. **Fix tray icon** - Test alternatives, add manifest, or provide fallback
8. **Create debug runtime hook** - Set environment variables
9. **Bundle test database** - Create and include sample data

### FINALLY (Prevent Regression)

10. **Build verification script** - Automated resource checking
11. **Smoke test suite** - Automated exe testing
12. **Update build documentation** - Include testing procedures

---

## Success Metrics

### Must Have (Release Blockers)
- ✅ Production .exe starts without crashing
- ✅ FastAPI server runs and serves dashboard
- ✅ User can access dashboard through some UI method
- ✅ crash.log provides diagnostics if something fails
- ✅ Setup wizard works on first launch

### Should Have (High Priority)
- ✅ System tray icon appears and works
- ✅ Debug build uses test database
- ✅ All three menu options work (Dashboard, Data Folder, Quit)
- ✅ Automated smoke tests pass

### Nice to Have (Future Enhancement)
- ✅ Code signing to remove security warnings
- ✅ CI integration for build testing
- ✅ Automated release builds
- ✅ Windows Store distribution

---

## Risk Mitigation

### Risk 1: pystray Cannot Be Fixed on Windows 11
**Mitigation:** Provide alternative UI (Start Menu shortcut + Windows notifications)

### Risk 2: DuckDB Binary Extensions Won't Bundle
**Mitigation:** Test with both PyInstaller and Nuitka as backup

### Risk 3: Changes Break Development Mode
**Mitigation:** Test both `python launcher.py` and `WeatherApp.exe` in all PRs

### Risk 4: Fixes Work on Dev Machine But Not User Machines
**Mitigation:** Test on clean Windows VM before declaring fixed

---

## Testing Checklist

Before declaring issues "fixed", ALL of these must pass:

### Build Tests
- [ ] `build.bat` completes without errors
- [ ] `dist/WeatherApp/WeatherApp.exe` exists
- [ ] `dist/WeatherApp/_internal/web/dist/index.html` exists
- [ ] `dist/WeatherApp/_internal/weather_app/resources/icons/weather-app.png` exists
- [ ] DuckDB extension files present in `_internal/duckdb/`

### Production Build Tests
- [ ] WeatherApp.exe launches without crash
- [ ] Process stays running (not immediate exit)
- [ ] Setup wizard appears on first launch
- [ ] After entering credentials, dashboard opens
- [ ] Dashboard shows correct content (not API JSON)
- [ ] API endpoints respond correctly
- [ ] System tray icon appears (or alternative UI works)
- [ ] Quit function terminates app cleanly

### Debug Build Tests
- [ ] WeatherApp_Debug.exe shows console window
- [ ] Console shows "DEBUG MODE" banner
- [ ] Console shows "Using test database: ..." message
- [ ] Test database path is different from production
- [ ] Dashboard shows test data (if test DB populated)
- [ ] All logging visible in console

### Clean Machine Tests
- [ ] Test on fresh Windows 11 VM (no dev tools)
- [ ] Test on fresh Windows 10 VM
- [ ] Test with no Python installed
- [ ] Test with no .env file (first-run scenario)
- [ ] Test uninstall and reinstall

### Regression Tests
- [ ] Development mode still works: `python launcher.py`
- [ ] CLI still works: `weather-app fetch`
- [ ] FastAPI still works: `uvicorn weather_app.web.app:create_app --factory`
- [ ] Frontend dev still works: `cd web && npm run dev`

---

## Next Steps

1. **Create diagnostic branch** ✅ (Done: bugfix/windows-installer-root-cause-analysis)
2. **Implement crash logging** - First implementation task
3. **Build and test with console=True** - Get real error messages
4. **Analyze crash.log and fix root causes** - Data-driven fixes
5. **Test on clean VM** - Verify fixes work on user machines
6. **Document verified solution** - Update installer docs with findings

---

## Lessons Learned

### What Went Wrong
1. **Insufficient diagnostics** - Fixed blind without seeing errors
2. **No verification testing** - Assumed builds worked without running them
3. **Reactive fixes** - Fixed symptoms, not root causes
4. **No test automation** - Relied on manual testing

### Process Improvements
1. **Diagnostic-first approach** - ALWAYS add logging before fixing
2. **Test on target platform** - Use VMs for clean testing
3. **Automate smoke tests** - Catch regressions early
4. **Document assumptions** - Write down WHY we think something will work

---

**Status:** Ready to implement Phase 1 (Diagnostic Instrumentation)
**Owner:** Development Team
**Priority:** P0 (Critical - Blocks user testing)
