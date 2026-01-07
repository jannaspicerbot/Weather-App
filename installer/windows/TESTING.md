# Windows Installer Testing Guide

This guide provides a systematic approach to testing Windows builds and identifying issues.

---

## Quick Start: Test Your Build

```bash
# 1. Build the installer
cd installer\windows
build.bat

# 2. Verify the build
python verify_build.py

# 3. Check the logs (if build succeeded)
# Production build logs:
%APPDATA%\WeatherApp\logs\

# 4. Test the executable
dist\WeatherApp\WeatherApp.exe
```

---

## Understanding the Build System

### Build Outputs

```
installer/windows/
├── dist/
│   ├── WeatherApp/              # Production build
│   │   ├── WeatherApp.exe       # Main executable (console=False)
│   │   └── _internal/           # Bundled resources
│   │       ├── web/dist/        # React frontend
│   │       ├── weather_app/     # Python modules
│   │       └── ...              # Dependencies
│   └── WeatherApp_Debug/        # Debug build
│       ├── WeatherApp_Debug.exe # Debug executable (console=True)
│       └── _internal/           # Same as production
└── build/                       # Build artifacts (can be deleted)
```

### Diagnostic Logs

All builds now include comprehensive logging:

**Production Build:**
- `%APPDATA%\WeatherApp\logs\startup_YYYYMMDD_HHMMSS.log` - Startup diagnostics
- `%APPDATA%\WeatherApp\logs\runtime_hook.log` - PyInstaller runtime verification

**Debug Build:**
- Console window shows real-time output
- Same log files as production
- `%APPDATA%\WeatherApp\logs\debug_runtime_hook.log` - Debug configuration

---

## Testing Checklist

### Phase 1: Build Verification (Before Running)

Run these checks BEFORE attempting to run the exe:

```bash
# Verify build completed correctly
python verify_build.py

# Check for common issues:
# ✓ Frontend built? (web/dist/index.html exists)
# ✓ Icons bundled? (weather_app/resources/icons/)
# ✓ DuckDB included? (search for *duckdb* files)
# ✓ Exe size reasonable? (100-200 MB typical)
```

**If verification fails:**
1. Check error messages - they tell you what's missing
2. Fix the issue (e.g., run `npm run build` for missing frontend)
3. Rebuild with `build.bat`
4. Verify again

### Phase 2: Startup Testing (Run the Exe)

**Test Production Build:**

```bash
# Run from command line to see any console output
cd dist\WeatherApp
WeatherApp.exe
```

**What should happen:**
1. Process starts (check Task Manager)
2. Setup wizard appears (first run)
3. After setup, browser opens with dashboard
4. System tray icon appears (may not work - known issue)

**If it crashes immediately:**
1. Check startup log: `%APPDATA%\WeatherApp\logs\startup_*.log`
2. Check runtime hook log: `%APPDATA%\WeatherApp\logs\runtime_hook.log`
3. Look for:
   - Import errors (missing dependencies)
   - Resource not found errors (bundling issue)
   - Exception traces (code bug)

**Test Debug Build:**

```bash
# Debug build shows console window
cd dist\WeatherApp_Debug
WeatherApp_Debug.exe
```

**What should see in console:**
```
================================================================================
WEATHER APP - DEBUG BUILD
================================================================================
Python: 3.12.x
Frozen: True
Bundle: C:\Users\...\AppData\Local\Temp\_MEIxxxxxx

Debug Configuration:
  USE_TEST_DB: true
  LOG_LEVEL: DEBUG
  DEBUG_MODE: true
================================================================================

[Timestamp] [INFO] Starting Weather App...
[Timestamp] [INFO] Using test database: C:\Users\...\AppData\Roaming\WeatherApp\ambient_weather_test.duckdb
...
```

**If console closes immediately:**
- Error occurred before console output
- Check log files in %APPDATA%\WeatherApp\logs\

### Phase 3: Functional Testing

Once the exe starts successfully, test functionality:

**Dashboard Access:**
- [ ] Dashboard opens in browser automatically
- [ ] Shows Weather App UI (not API JSON)
- [ ] API endpoints respond (check /api/health)

**System Tray Icon:**
- [ ] Icon appears in Windows system tray (bottom-right)
- [ ] Right-click shows menu
- [ ] "Open Dashboard" opens browser
- [ ] "Open Data Folder" opens Explorer
- [ ] "Quit" closes application

**⚠️ Known Issue:** System tray icon may not appear on Windows 11. If this happens:
- Dashboard still works (access via http://localhost:8000)
- Server still runs
- Use Start Menu shortcut or browser bookmark
- See "Tray Icon Troubleshooting" below

**Data Collection:**
- [ ] Setup wizard accepts API credentials
- [ ] Credentials saved to %APPDATA%\WeatherApp\.env
- [ ] Database created at %APPDATA%\WeatherApp\ambient_weather.duckdb
- [ ] Data fetching works (check dashboard for data)

**Debug Build Specific:**
- [ ] Uses test database (check console output)
- [ ] Log level is DEBUG (verbose logging)
- [ ] Can see all server startup messages

### Phase 4: Clean Machine Testing

⚠️ **CRITICAL:** Test on a machine without dev tools!

**Why:** Your dev machine has:
- Python installed
- All dependencies already installed
- Environment variables set
- Different permissions

**Users have:**
- No Python
- No dev tools
- Fresh Windows install
- May have antivirus/security software

**How to test cleanly:**

**Option 1: Windows VM (Recommended)**
```bash
# Create a clean Windows 11 VM (VirtualBox, VMware, or Hyper-V)
# Copy WeatherApp.exe to VM
# Double-click and test
# This is the TRUE user experience
```

**Option 2: Windows Sandbox (Quick)**
```bash
# Windows 10/11 Pro feature
# Start → Windows Sandbox
# Copy exe into sandbox
# Test (sandbox is reset after closing)
```

**Option 3: Fresh User Account**
```bash
# Create new Windows user account
# Log in as that user
# Test exe (no PATH, no Python)
```

**What to test:**
- [ ] Exe runs without Python installed
- [ ] No missing DLL errors
- [ ] Setup wizard works
- [ ] Dashboard displays correctly
- [ ] SmartScreen warning (expected for unsigned exe)

---

## Troubleshooting Guide

### Issue: Exe crashes immediately (no window)

**Diagnosis:**
```bash
# Check logs
dir %APPDATA%\WeatherApp\logs\

# Read startup log
type %APPDATA%\WeatherApp\logs\startup_*.log

# Read runtime hook log
type %APPDATA%\WeatherApp\logs\runtime_hook.log
```

**Common causes:**
1. **Missing resources** - Check "✗ MISSING" in runtime_hook.log
2. **Import error** - Check for "ImportError" in startup log
3. **DuckDB not bundled** - Check for duckdb in _internal/
4. **Frontend not built** - Check for web/dist/index.html

**Fixes:**
```bash
# Frontend missing:
cd ../../web
npm install
npm run build
cd ../installer/windows
build.bat

# Resources missing: Check spec file has correct datas=[]
# DuckDB missing: Check hiddenimports includes duckdb
# Rebuild: build.bat --clean
```

### Issue: Exe runs but shows blank/white screen

**Cause:** Frontend not loading or route conflict

**Check:**
1. Open browser dev tools (F12)
2. Look for 404 errors for static files
3. Check if http://localhost:8000/ shows API JSON (wrong route)
4. Check if http://localhost:8000/api shows API JSON (correct route)

**Fix:**
- Ensure app.py mounts StaticFiles at "/" with html=True
- Ensure API routes are at "/api" not "/"
- See PR #38 for route fix

### Issue: Setup wizard doesn't appear

**Cause:** Tkinter not bundled or .env already exists

**Check:**
```bash
# Check if .env already exists
dir %APPDATA%\WeatherApp\.env

# Check startup log for tkinter errors
type %APPDATA%\WeatherApp\logs\startup_*.log | findstr tkinter
```

**Fix:**
```bash
# Delete .env to trigger wizard again
del %APPDATA%\WeatherApp\.env

# If tkinter error: Rebuild, tkinter should be included on Windows
```

### Issue: System tray icon doesn't appear

**Status:** KNOWN ISSUE on Windows 11 (under investigation)

**Workarounds:**
1. Access dashboard via browser: http://localhost:8000
2. Create desktop shortcut to http://localhost:8000
3. Use Start Menu shortcut (if installed)
4. Dashboard auto-opens on startup

**Not a blocker:** App is fully functional without tray icon

**Investigation needed:**
- pystray Windows 11 compatibility
- Unsigned exe permissions
- Alternative tray libraries (infi.systray)

### Issue: "Windows protected your PC" (SmartScreen)

**Status:** EXPECTED for unsigned executables

**User action:**
1. Click "More info"
2. Click "Run anyway"

**To avoid:**
- Code sign the executable ($$$)
- Distribute via Microsoft Store (requires signing)
- Users must accept for first run

### Issue: Antivirus flags exe as suspicious

**Status:** EXPECTED for PyInstaller exes (false positive)

**Why:** PyInstaller bundles Python runtime, looks like packer to AV

**Solutions:**
- Submit exe to antivirus vendor (VirusTotal, etc.)
- Code sign the executable
- Add to AV exceptions (user decision)

**NOT malware:** Source code is public, build process is transparent

---

## Advanced Diagnostics

### Manual Resource Inspection

```bash
# Extract PyInstaller bundle (requires pyinstaller-extractor)
pip install pyinstaller-extractor

# Extract bundle
python -m pyinstaller_extractor dist\WeatherApp\WeatherApp.exe

# Inspect extracted files
dir WeatherApp.exe_extracted\
```

### Check Bundled Modules

```bash
# In Python console:
import sys
print(sys.path)
print(sys._MEIPASS)  # Where PyInstaller extracted files

# Check if module bundled:
import duckdb  # Should work
import weather_app.launcher.tray_app  # Should work
```

### Test Server Startup Directly

```bash
# Skip tray app, test server only
cd dist\WeatherApp\_internal

# Set PYTHONPATH
set PYTHONPATH=%CD%

# Try to start server
python -c "from weather_app.web.app import create_app; app = create_app(); print('Server created')"
```

### Debug Build vs Production Build

**Debug build advantages:**
- Console window shows all output
- Easier to see errors
- Runtime hook sets USE_TEST_DB

**Use debug build when:**
- Diagnosing startup issues
- Testing configuration changes
- Developing new features

**Use production build when:**
- Testing user experience
- Preparing for distribution
- Performance testing

---

## Build Automation Tests

### Pytest Tests

```bash
# Run build verification tests
pytest tests/test_installer_build.py -v

# These tests check:
# - Executables exist
# - Resources bundled
# - Configuration correct
# - Crash logger included
```

### CI/CD Integration

```yaml
# Future: Add to .github/workflows/
# - Build on PR to main
# - Run verification tests
# - Upload artifacts
# - Block merge if tests fail
```

---

## Success Criteria

### Before Declaring "Fixed"

**Production Build:**
- [ ] build.bat completes without errors
- [ ] verify_build.py passes with no errors
- [ ] WeatherApp.exe starts without crash
- [ ] Setup wizard appears and works
- [ ] Dashboard loads in browser
- [ ] API endpoints respond
- [ ] Logs show no critical errors
- [ ] Tested on clean Windows VM

**Debug Build:**
- [ ] Console shows debug banner
- [ ] Console shows "Using test database"
- [ ] USE_TEST_DB environment variable set
- [ ] All functionality works same as production

**Installer (if using Inno Setup):**
- [ ] WeatherAppSetup.exe creates
- [ ] Installer runs without errors
- [ ] Start Menu shortcut works
- [ ] Uninstaller works
- [ ] User data preserved on uninstall (if chosen)

---

## Next Steps After Testing

### If Tests Pass
1. Tag release: `git tag v1.0.0`
2. Push to GitHub: `git push origin v1.0.0`
3. Create GitHub release with installer
4. Update documentation with known issues

### If Tests Fail
1. Check logs (most important!)
2. Identify root cause from logs
3. Fix the specific issue
4. Rebuild: `build.bat --clean`
5. Re-test from Phase 1

### Ongoing Improvements
- [ ] Add CI/CD for automated testing
- [ ] Investigate tray icon Windows 11 fix
- [ ] Consider code signing
- [ ] Create video tutorial for users
- [ ] Document common user issues

---

## Resources

**Log Locations:**
- `%APPDATA%\WeatherApp\logs\startup_*.log` - Crash diagnostics
- `%APPDATA%\WeatherApp\logs\runtime_hook.log` - Build verification
- `%APPDATA%\WeatherApp\logs\debug_runtime_hook.log` - Debug config

**Build Scripts:**
- `build.bat` - Main build script
- `verify_build.py` - Build verification
- `weather_app.spec` - Production configuration
- `weather_app_debug.spec` - Debug configuration

**Documentation:**
- `INSTALLER.md` - Inno Setup guide
- `docs/testing/windows-installer-root-cause-analysis.md` - Deep analysis

**Support:**
- GitHub Issues: Report bugs with log files attached
- Include: Windows version, log files, steps to reproduce

---

**Last Updated:** January 6, 2026
**Status:** Testing framework implemented, awaiting build verification
