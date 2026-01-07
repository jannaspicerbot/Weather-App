# Troubleshooting: WeatherApp.exe Launch Failure

**Date:** January 6, 2026 (Updated: January 7, 2026)
**Issue:** WeatherApp.exe fails to launch after installation
**Status:** ✅ RESOLVED

**Resolution:** The production exe crash was caused by uvicorn's logging configuration attempting to access `sys.stdout.isatty()` when `sys.stdout` is `None` in frozen executables with `console=False`. Fixed by disabling uvicorn's log config.

---

## Problem Description

After building and installing the Weather App Windows installer (`WeatherAppSetup.exe`), the application executable (`WeatherApp.exe`) would not launch when double-clicked or run from the Start Menu. No error messages were visible to the user since the app was configured as a GUI application (`console=False` in PyInstaller spec).

### Symptoms

- Double-clicking `WeatherApp.exe` shows no response
- No system tray icon appears
- No error messages displayed
- Application appears to fail silently

---

## Root Causes

Two critical issues were preventing the app from launching:

### Issue 1: Missing Dependencies in setup.py

**Problem:** The `setup.py` file was missing several critical dependencies that were present in `requirements.txt` but not included in the package installation requirements.

**Missing packages:**
- `pystray>=0.19.0` - Required for system tray functionality
- `Pillow>=10.0.0` - Required for icon image rendering
- `duckdb>=0.10.0` - Database engine
- `apscheduler>=3.10.0` - Scheduled task management
- `structlog>=24.1.0` - Structured logging

**Impact:** When the PyInstaller executable tried to import these modules, Python couldn't find them, causing the application to crash immediately on startup.

### Issue 2: Incompatible pystray MenuItem Callback Signature

**Problem:** The `quit_app()` method in `weather_app/launcher/tray_app.py` had a default parameter (`restart=False`) that made its signature incompatible with pystray's expected callback format.

**Error:**
```python
ValueError: <bound method WeatherTrayApp.quit_app of <...>>
```

**Impact:** Even after fixing the dependencies, pystray would reject the callback and raise a ValueError, preventing the system tray menu from being created.

---

### Issue 3: Uvicorn Logging Fails When sys.stdout is None (ROOT CAUSE)

**Problem:** When PyInstaller packages with `console=False` (no console window), `sys.stdout` is set to `None`. Uvicorn's default logging formatter tries to call `sys.stdout.isatty()`, which raises `AttributeError: 'NoneType' object has no attribute 'isatty'`.

**Error (from crash log):**
```
UNCAUGHT EXCEPTION
Type: SystemExit
Message: 1

Traceback:
  File "uvicorn\logging.py", line 42, in __init__
  AttributeError: 'NoneType' object has no attribute 'isatty'

  File "weather_app\launcher\tray_app.py", line 40, in start_server
  File "uvicorn\config.py", line 278, in __init__
  ValueError: Unable to configure formatter 'default'
```

**Impact:** Server startup fails immediately, app exits with code 1, no visible error because console is hidden.

**Why we didn't see it before:** Without crash logging infrastructure, the error was completely invisible.

---

### Issue 4: Setup Wizard Blocks Startup (console=False builds)

**Problem:** When running the production exe (console=False), if the `.env` file doesn't exist in `%APPDATA%\WeatherApp\`, the setup wizard launches a tkinter GUI window. However, with console=False, this window may not display properly, causing the app to appear frozen or non-responsive.

**Impact:** Users double-clicking the exe see nothing happen because the invisible setup wizard is waiting for input.

**Solution:** Copy the .env file to the user data directory before running:
```bash
# Windows
mkdir %APPDATA%\WeatherApp
copy .env %APPDATA%\WeatherApp\.env

# Then run the exe
```

Alternatively, use the debug version (`WeatherApp_Debug.exe`) which has console=True and will show the setup wizard properly.

---

### Issue 5: Frontend Not Served (API JSON displayed instead)

**Problem:** When accessing `http://localhost:8000` in the browser, the API root endpoint was being served instead of the React frontend dashboard. This caused users to see JSON API information instead of the actual web interface.

**Root Cause:** The API routes had a `@app.get("/")` endpoint defined, which took precedence over the FastAPI static file mount for the React frontend. Even though the frontend files were bundled and the static mount was registered last, explicitly defined routes have higher priority than mounted static files.

**Impact:** Users could not access the web dashboard - they only saw API metadata JSON when visiting the root URL.

**Solution:** Move the API root endpoint from `/` to `/api` to free up the root path for the frontend.

---

## Solution

### Fix 1: Update setup.py Dependencies

Added all missing dependencies to `setup.py`:

```python
install_requires=[
    "requests>=2.31.0",
    "pandas>=2.0.0",
    "plotly>=5.18.0",
    "numpy>=1.24.0",
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "click>=8.1.0",
    "duckdb>=0.10.0",
    "apscheduler>=3.10.0",
    "structlog>=24.1.0",
    # Launcher/GUI dependencies
    "pystray>=0.19.0",
    "Pillow>=10.0.0",
],
```

**Files changed:**
- [`setup.py`](../../setup.py)

### Fix 2: Refactor pystray Callbacks

Refactored the quit/restart methods to separate the callback interface from the implementation:

**Before:**
```python
def quit_app(self, icon=None, item=None, restart=False):
    """Quit application"""
    # Implementation with default parameter
```

**After:**
```python
def quit_app(self, icon=None, item=None):
    """Quit application (menu callback)"""
    self._do_quit(restart=False)

def restart_app(self, icon=None, item=None):
    """Restart the application"""
    self._do_quit(restart=True)

def _do_quit(self, restart=False):
    """Internal quit implementation"""
    # Actual implementation
```

**Files changed:**
- [`weather_app/launcher/tray_app.py`](../../weather_app/launcher/tray_app.py)

### Fix 3: Disable Uvicorn Logging Config (CRITICAL FIX)

Disabled uvicorn's default logging configuration to prevent the `sys.stdout.isatty()` error in frozen executables.

**Before:**
```python
config = uvicorn.Config(
    app,
    host="127.0.0.1",
    port=PORT,
    log_level="info",
    access_log=False,
)
```

**After:**
```python
config = uvicorn.Config(
    app,
    host="127.0.0.1",
    port=PORT,
    log_level="info",
    access_log=False,
    log_config=None,  # CRITICAL: Disable uvicorn logging config when frozen
)
```

**Why this works:**
- `log_config=None` disables uvicorn's logging configuration entirely
- The application's own logging (structured logging to files) handles all logging
- No dependency on `sys.stdout.isatty()` which fails when `sys.stdout` is `None`

**Files changed:**
- [`weather_app/launcher/tray_app.py`](../../weather_app/launcher/tray_app.py)

**Commit:** `93a2518` - Fix: Disable uvicorn logging config when running as frozen exe

### Fix 4: Move API Root Route to /api

Changed the API information endpoint from `/` to `/api` to allow the frontend to be served at the root path.

**Before:**
```python
@app.get("/")
def read_root():
    """Root endpoint with API information"""
    return {"message": "Weather API", ...}
```

**After:**
```python
@app.get("/api")
def read_root():
    """API information endpoint"""
    return {"message": "Weather API", ...}
```

**Files changed:**
- [`weather_app/web/routes.py`](../../weather_app/web/routes.py)

**Result:**
- Frontend dashboard served at `http://localhost:8000/`
- API information available at `http://localhost:8000/api`
- All API endpoints prefixed with `/api` or legacy `/weather` paths

### Fix 5: Add Tray Icon Fallback

Added error handling to prevent the app from crashing if the system tray icon fails to create (known issue with pystray on some Windows systems).

**Changes:**
- Start server before attempting to create tray icon
- Wrap tray icon creation in try-except block
- Keep server running even if tray fails
- Added infinite loop to prevent exit when running without tray

**Files changed:**
- [`weather_app/launcher/tray_app.py`](../../weather_app/launcher/tray_app.py)

**Result:**
- App no longer crashes when tray icon fails
- Server remains accessible even without tray
- Dashboard can still be accessed at `http://localhost:8000`

---

## How to Apply the Fix

### For Developers

1. **Update dependencies:**
   ```bash
   cd "C:/GitHub Repos/Weather-App"
   pip install -e .  # Reinstall with updated dependencies
   ```

2. **Rebuild the executable:**
   ```bash
   cd installer/windows
   python -m PyInstaller weather_app.spec --clean --noconfirm
   ```

3. **Test the executable:**
   ```bash
   cd dist/WeatherApp
   ./WeatherApp.exe
   ```

   You should see:
   - System tray icon appears
   - FastAPI server starts
   - Dashboard opens in browser

### For Users

1. **Uninstall the old version:**
   - Go to Settings → Apps → Weather App
   - Click Uninstall
   - Choose to keep or delete your data

2. **Install the updated version:**
   - Download the new `WeatherAppSetup.exe`
   - Run the installer
   - Launch the application

---

## Debugging Tips

If you encounter similar issues in the future, use the debug launcher to capture detailed error logs:

### Create a Debug Launcher

File: `debug_launcher.py`

```python
"""
Debug launcher to test the Weather App with console output and error logging
"""
import sys
import logging
import traceback
from pathlib import Path

# Setup comprehensive logging
log_file = Path.home() / "weather_app_debug.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

try:
    from weather_app.launcher.tray_app import main
    main()
except Exception as e:
    logger.error(f"Error: {e}")
    logger.error(f"Traceback:\n{traceback.format_exc()}")
    input("\nPress Enter to exit...")
```

### Run Debug Launcher

```bash
python debug_launcher.py
```

Check `~/weather_app_debug.log` for detailed error information.

---

## Testing Checklist

After applying the fixes, verify:

**Debug exe (WeatherApp_Debug.exe with console=True):**
- [x] `pip show weather-app` shows all required packages as dependencies
- [x] PyInstaller build completes without errors
- [x] Debug exe launches successfully
- [ ] System tray icon appears (may not work on all systems - known Windows 11 issue)
- [x] FastAPI server starts on `http://localhost:8000`
- [x] Frontend dashboard served at root path (not API JSON)
- [x] Dashboard opens in browser
- [x] Scheduler starts and logs initialization

**Production exe (WeatherApp.exe with console=False):**
- [x] PyInstaller build completes without errors
- [x] Production exe launches successfully (fixed with `log_config=None`)
- [x] FastAPI server starts and responds to requests
- [x] Dashboard accessible at http://localhost:8000
- [ ] System tray icon appears (known Windows 11 issue - not blocking)

---

## Known Issues & Future Work

### Production Exe Launch Failure (console=False) - ✅ RESOLVED

**Status:** Fixed in commit `93a2518`

**Root Cause:** Uvicorn's logging configuration called `sys.stdout.isatty()` when `sys.stdout` was `None` in frozen executables with `console=False`.

**Solution:** Added `log_config=None` to uvicorn.Config() to disable uvicorn's logging configuration.

**Diagnostic Infrastructure Added:**
- Crash logging to `%APPDATA%\WeatherApp\logs\startup_*.log`
- Runtime hooks to verify bundled resources
- Build verification scripts (`installer/windows/verify_build.py`)

### System Tray Icon Not Appearing (Windows 11)

**Status:** Known issue - not blocking

**Problem:** The system tray icon doesn't appear on some Windows 11 systems, even though pystray loads and runs without errors.

**Possible Causes:**
1. pystray compatibility with Windows 11
2. Unsigned executable restrictions
3. Windows notification area settings

**Workarounds:**
- Dashboard auto-opens in browser on startup
- Access via http://localhost:8000
- Use browser bookmark
- App remains fully functional without tray icon

**Future Investigation:**
- Test on Windows 10 to confirm OS-specific
- Investigate alternative tray libraries (infi.systray, win10toast-click)
- Consider code signing

---

## Prevention

To prevent similar issues:

1. **Keep setup.py and requirements.txt synchronized**
   - Always add new dependencies to both files
   - Consider using `setup.py` as the single source of truth
   - Use `pip install -e .` instead of `pip install -r requirements.txt`

2. **Test with PyInstaller regularly**
   - Build and test the exe after adding new dependencies
   - Use the debug launcher for development testing

3. **Follow pystray callback conventions**
   - Menu item callbacks should accept `(icon, item)` parameters only
   - No default parameters in callback methods
   - Use wrapper methods for callbacks that need additional logic

4. **Monitor dependency compatibility**
   - Check PyInstaller hooks for new packages
   - Test hidden imports in `.spec` file
   - Review PyInstaller build warnings

---

## Related Issues

- Initial implementation: [launcher.py](../../launcher.py)
- PyInstaller spec: [installer/windows/weather_app.spec](../../installer/windows/weather_app.spec)
- Tray app implementation: [weather_app/launcher/tray_app.py](../../weather_app/launcher/tray_app.py)

---

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [pystray Documentation](https://pystray.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
