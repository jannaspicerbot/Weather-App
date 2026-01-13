"""
PyInstaller Runtime Hook for Production Build

This hook runs immediately after the Python interpreter is initialized
but before any application code runs. Use it to:
- Force production database configuration (immutable)
- Verify the bundled environment
- Set up necessary paths
- Log diagnostic information

This file is specified in the spec file with: runtime_hooks=['hooks/runtime_hook_production.py']
"""

import os
import sys
from pathlib import Path

# =============================================================================
# FORCE PRODUCTION CONFIGURATION
# =============================================================================
# CRITICAL: Production builds ALWAYS use the production database.
# This cannot be overridden by .env files or environment variables.
# Use the debug build (WeatherApp_Debug.exe) for testing with test database.
os.environ["USE_TEST_DB"] = "false"
os.environ.setdefault("LOG_LEVEL", "INFO")


def log_hook_message(message):
    """Log message from runtime hook"""
    # At this point, crash_logger isn't loaded yet
    # Write directly to a temp file
    try:
        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".local" / "share"

        log_dir = base / "WeatherApp" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / "runtime_hook.log"

        with open(log_file, "a", encoding="utf-8") as f:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        pass  # Silently fail - we're in startup hook


# Log that runtime hook is executing
log_hook_message("=" * 80)
log_hook_message("PyInstaller Runtime Hook - Production Build")
log_hook_message("=" * 80)

# Log frozen state
log_hook_message(f"sys.frozen: {getattr(sys, 'frozen', False)}")
log_hook_message(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'NOT SET')}")
log_hook_message(f"sys.executable: {sys.executable}")

# Log current working directory
log_hook_message(f"Current working directory: {os.getcwd()}")

# Log environment variables
log_hook_message("\nEnvironment Variables:")
for key in ["APPDATA", "LOCALAPPDATA", "TEMP", "PATH"]:
    value = os.getenv(key, "NOT SET")
    if key == "PATH":
        log_hook_message(f"  {key}:")
        for path_item in value.split(os.pathsep):
            log_hook_message(f"    - {path_item}")
    else:
        log_hook_message(f"  {key}: {value}")

# Verify _MEIPASS contents
if hasattr(sys, "_MEIPASS"):
    meipass = Path(sys._MEIPASS)
    log_hook_message(f"\nContents of _MEIPASS ({meipass}):")

    try:
        # List critical paths
        critical_paths = [
            "web/dist",
            "weather_app/resources/icons",
            "weather_app/launcher",
        ]

        for rel_path in critical_paths:
            full_path = meipass / rel_path
            if full_path.exists():
                log_hook_message(f"  ✓ {rel_path}")
                # List a few files in the directory
                if full_path.is_dir():
                    try:
                        files = list(full_path.iterdir())[:5]  # First 5 files
                        for f in files:
                            log_hook_message(f"      - {f.name}")
                        if len(list(full_path.iterdir())) > 5:
                            log_hook_message(f"      ... and more")
                    except Exception as e:
                        log_hook_message(f"      Error listing: {e}")
            else:
                log_hook_message(f"  ✗ MISSING: {rel_path}")

    except Exception as e:
        log_hook_message(f"  Error checking _MEIPASS: {e}")

# Check Python path
log_hook_message("\nPython Path (sys.path):")
for path in sys.path:
    log_hook_message(f"  - {path}")

log_hook_message("\nRuntime hook completed")
log_hook_message("=" * 80 + "\n")
