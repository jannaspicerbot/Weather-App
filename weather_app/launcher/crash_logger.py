"""
Crash logger for Windows executable diagnostics

This module MUST be imported FIRST in launcher.py to capture all startup errors.
Logs to file even when console=False, enabling diagnostics for production builds.
"""

import sys
import traceback
from datetime import datetime
from pathlib import Path


def setup_crash_logger():
    """
    Set up crash logging that works in frozen executables.

    Creates log directory and configures exception logging.
    Must be called before any other imports that might fail.

    Returns:
        Path: Log file path
    """
    # Determine log directory based on frozen state
    if getattr(sys, "frozen", False):
        # Running as packaged executable - use APPDATA
        import os

        if sys.platform == "win32":
            base = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path.home() / ".local" / "share"

        log_dir = base / "WeatherApp" / "logs"
    else:
        # Development mode - use project directory
        log_dir = Path(__file__).parent.parent.parent / "logs"

    # Create log directory
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"startup_{timestamp}.log"

    return log_file


def log_startup_info(log_file):
    """Log system information at startup"""
    try:
        import platform

        with open(log_file, "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("Weather App Startup Log\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")

            f.write("System Information:\n")
            f.write(f"  Platform: {platform.platform()}\n")
            f.write(f"  Python: {platform.python_version()}\n")
            f.write(f"  Executable: {sys.executable}\n")
            f.write(f"  Frozen: {getattr(sys, 'frozen', False)}\n")

            if getattr(sys, "frozen", False):
                f.write(f"  _MEIPASS: {getattr(sys, '_MEIPASS', 'NOT SET')}\n")

            f.write("\nPython Path:\n")
            for path in sys.path:
                f.write(f"  {path}\n")

            f.write("\n" + "=" * 80 + "\n\n")

        return True
    except Exception as e:
        # If we can't even write startup info, we're in trouble
        print(f"CRITICAL: Failed to write startup log: {e}", file=sys.stderr)
        return False


def log_exception(log_file, exc_type, exc_value, exc_traceback):
    """Log uncaught exception to file"""
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write("UNCAUGHT EXCEPTION\n")
            f.write("=" * 80 + "\n")
            f.write(f"Type: {exc_type.__name__}\n")
            f.write(f"Message: {exc_value}\n")
            f.write("\nTraceback:\n")

            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            f.write("".join(tb_lines))

            f.write("\n" + "=" * 80 + "\n")
    except Exception as e:
        print(f"CRITICAL: Failed to log exception: {e}", file=sys.stderr)


def log_message(log_file, message, level="INFO"):
    """
    Log a message to the crash log.

    Args:
        log_file: Path to log file
        message: Message to log
        level: Log level (INFO, WARNING, ERROR, CRITICAL)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    except Exception:
        pass  # Silently fail - we're in crash logging, can't error here


def verify_bundled_resources(log_file):
    """
    Verify critical resources are bundled correctly.

    Returns:
        tuple: (success: bool, missing_resources: list)
    """
    missing = []

    try:
        # Determine base path for resources
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        else:
            base_path = Path(__file__).parent.parent.parent

        log_message(log_file, f"Resource base path: {base_path}")

        # Check critical resources
        critical_resources = [
            ("Frontend", base_path / "web" / "dist" / "index.html"),
            (
                "App Icon PNG",
                base_path / "weather_app" / "resources" / "icons" / "weather-app.png",
            ),
            (
                "App Icon ICO",
                base_path / "weather_app" / "resources" / "icons" / "weather-app.ico",
            ),
        ]

        for name, path in critical_resources:
            if path.exists():
                log_message(log_file, f"✓ Found {name}: {path}")
            else:
                log_message(log_file, f"✗ MISSING {name}: {path}", level="ERROR")
                missing.append((name, str(path)))

        # Check for DuckDB (try to import)
        try:
            import duckdb

            log_message(log_file, f"✓ DuckDB imported: {duckdb.__version__}")
        except ImportError as e:
            log_message(log_file, f"✗ DuckDB import failed: {e}", level="ERROR")
            missing.append(("DuckDB", str(e)))

        # Check for pystray and PIL
        try:
            import PIL

            log_message(log_file, f"✓ PIL imported: {PIL.__version__}")
        except ImportError as e:
            log_message(log_file, f"✗ PIL import failed: {e}", level="ERROR")
            missing.append(("PIL", str(e)))

        try:
            import pystray  # noqa: F401

            log_message(log_file, "✓ pystray imported")
        except ImportError as e:
            log_message(log_file, f"✗ pystray import failed: {e}", level="ERROR")
            missing.append(("pystray", str(e)))

        # Check for uvicorn
        try:
            import uvicorn

            log_message(log_file, f"✓ uvicorn imported: {uvicorn.__version__}")
        except ImportError as e:
            log_message(log_file, f"✗ uvicorn import failed: {e}", level="ERROR")
            missing.append(("uvicorn", str(e)))

        return len(missing) == 0, missing

    except Exception as e:
        log_message(
            log_file, f"Exception during resource verification: {e}", level="CRITICAL"
        )
        return False, [("Resource Verification", str(e))]


class CrashLogger:
    """Context manager for crash logging"""

    def __init__(self):
        self.log_file = setup_crash_logger()
        self.original_excepthook = None

    def __enter__(self):
        """Set up crash logging"""
        # Log startup info
        if not log_startup_info(self.log_file):
            # Failed to write log - continue anyway but warn
            print("WARNING: Could not initialize crash log", file=sys.stderr)

        log_message(self.log_file, "Starting Weather App...")

        # Install exception hook
        self.original_excepthook = sys.excepthook

        def crash_excepthook(exc_type, exc_value, exc_traceback):
            """Custom exception hook that logs to file"""
            log_exception(self.log_file, exc_type, exc_value, exc_traceback)

            # Also call original excepthook for console output (if console visible)
            if self.original_excepthook:
                self.original_excepthook(exc_type, exc_value, exc_traceback)

        sys.excepthook = crash_excepthook

        # Verify bundled resources
        log_message(self.log_file, "Verifying bundled resources...")
        success, missing = verify_bundled_resources(self.log_file)

        if not success:
            log_message(
                self.log_file,
                f"CRITICAL: Missing {len(missing)} resources",
                level="CRITICAL",
            )
            for name, path in missing:
                log_message(self.log_file, f"  - {name}: {path}", level="ERROR")

            # Don't abort - let app try to start, might work anyway
            # But log clearly that resources are missing

        log_message(self.log_file, "Crash logger initialized successfully")

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Clean up crash logging"""
        if exc_type is not None:
            # An exception occurred - log it
            log_exception(self.log_file, exc_type, exc_value, exc_traceback)
            log_message(self.log_file, "Application crashed", level="CRITICAL")
        else:
            log_message(self.log_file, "Application exited normally")

        # Restore original exception hook
        if self.original_excepthook:
            sys.excepthook = self.original_excepthook

        # Print log file location for user
        print(f"\nStartup log: {self.log_file}")

        return False  # Don't suppress exceptions

    def log(self, message, level="INFO"):
        """Log a message"""
        log_message(self.log_file, message, level)
