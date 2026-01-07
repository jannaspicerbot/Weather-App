"""
PyInstaller Runtime Hook for Debug Build

This hook configures the debug environment:
- Forces USE_TEST_DB=true
- Sets LOG_LEVEL=DEBUG
- Adds debug-specific configuration
"""

import os
import sys

# Force debug configuration via environment variables
# These will be picked up by config.py when it loads
os.environ["USE_TEST_DB"] = "true"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["DEBUG_MODE"] = "true"

# Print debug banner to console (console=True in debug build)
print("=" * 80)
print("WEATHER APP - DEBUG BUILD")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Frozen: {getattr(sys, 'frozen', False)}")
if hasattr(sys, "_MEIPASS"):
    print(f"Bundle: {sys._MEIPASS}")
print("\nDebug Configuration:")
print(f"  USE_TEST_DB: {os.environ.get('USE_TEST_DB')}")
print(f"  LOG_LEVEL: {os.environ.get('LOG_LEVEL')}")
print(f"  DEBUG_MODE: {os.environ.get('DEBUG_MODE')}")
print("=" * 80)
print()

# Also log to file
from pathlib import Path
from datetime import datetime

try:
    if sys.platform == "win32":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home() / ".local" / "share"

    log_dir = base / "WeatherApp" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "debug_runtime_hook.log"

    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] Debug runtime hook executed\n")
        f.write(f"USE_TEST_DB: {os.environ.get('USE_TEST_DB')}\n")
        f.write(f"LOG_LEVEL: {os.environ.get('LOG_LEVEL')}\n")
        f.write(f"DEBUG_MODE: {os.environ.get('DEBUG_MODE')}\n")
except Exception as e:
    print(f"Warning: Could not write debug runtime hook log: {e}")
