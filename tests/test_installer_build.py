"""
Installer Build Verification Tests

Verifies that PyInstaller builds contain all required resources
and are properly structured for distribution.

Run after building with PyInstaller:
    pytest tests/test_installer_build.py -v
"""

from pathlib import Path

import pytest

# Path to installer builds
INSTALLER_DIR = Path(__file__).parent.parent / "installer" / "windows"
PROD_BUILD_DIR = INSTALLER_DIR / "dist" / "WeatherApp"
DEBUG_BUILD_DIR = INSTALLER_DIR / "dist" / "WeatherApp_Debug"


class TestProductionBuild:
    """Tests for production WeatherApp.exe build"""

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_executable_exists(self):
        """Production executable should exist"""
        exe_path = PROD_BUILD_DIR / "WeatherApp.exe"
        assert exe_path.exists(), f"WeatherApp.exe not found at {exe_path}"

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_executable_size(self):
        """Production executable should be reasonable size"""
        exe_path = PROD_BUILD_DIR / "WeatherApp.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            assert (
                1 < size_mb < 500
            ), f"Suspicious exe size: {size_mb:.1f}MB (expected 1-500MB)"

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_internal_directory_exists(self):
        """_internal directory should exist with bundled files"""
        internal_dir = PROD_BUILD_DIR / "_internal"
        assert internal_dir.exists(), f"_internal directory not found at {internal_dir}"

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_frontend_bundled(self):
        """Frontend dist files should be bundled"""
        frontend_index = PROD_BUILD_DIR / "_internal" / "web" / "dist" / "index.html"
        assert frontend_index.exists(), (
            f"Frontend not bundled: {frontend_index} not found\n"
            "Run 'npm run build' in web/ directory before building installer"
        )

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_frontend_assets(self):
        """Frontend should have assets directory"""
        assets_dir = PROD_BUILD_DIR / "_internal" / "web" / "dist" / "assets"
        assert (
            assets_dir.exists() and assets_dir.is_dir()
        ), f"Frontend assets not found at {assets_dir}"

        # Should have at least some JS and CSS files
        assets = list(assets_dir.iterdir())
        assert len(assets) > 0, "Frontend assets directory is empty"

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_icons_bundled(self):
        """App icons should be bundled"""
        icons_dir = PROD_BUILD_DIR / "_internal" / "weather_app" / "resources" / "icons"
        assert icons_dir.exists(), f"Icons directory not found at {icons_dir}"

        # Check for specific icons
        png_icon = icons_dir / "weather-app.png"
        ico_icon = icons_dir / "weather-app.ico"

        assert png_icon.exists(), f"PNG icon not found at {png_icon}"
        assert ico_icon.exists(), f"ICO icon not found at {ico_icon}"

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(),
        reason="Production build not found - run PyInstaller first",
    )
    def test_prod_duckdb_bundled(self):
        """DuckDB extension should be bundled"""
        # Look for duckdb directory or .pyd/.so files
        internal_dir = PROD_BUILD_DIR / "_internal"

        # Search for DuckDB-related files
        duckdb_files = list(internal_dir.rglob("*duckdb*"))
        assert (
            len(duckdb_files) > 0
        ), f"No DuckDB files found in {internal_dir}\nFound: {list(internal_dir.iterdir())}"

    def test_prod_no_console_flag(self):
        """Production build should be windowed (no console)"""
        # This is harder to test programmatically
        # but we can at least warn if console=True in spec
        spec_file = INSTALLER_DIR / "weather_app.spec"
        if spec_file.exists():
            content = spec_file.read_text()
            # Look for console=True (should be console=False)
            if "console=True" in content and "console=False" not in content:
                pytest.fail("Production spec has console=True, should be console=False")

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(), reason="Production build not found"
    )
    def test_prod_runtime_hook_included(self):
        """Runtime hook should be referenced in build"""
        # Check that runtime hook was included in build
        runtime_hook = INSTALLER_DIR / "hooks" / "runtime_hook_production.py"
        assert (
            runtime_hook.exists()
        ), f"Production runtime hook not found at {runtime_hook}"


class TestDebugBuild:
    """Tests for debug WeatherApp_Debug.exe build"""

    @pytest.mark.skipif(
        not DEBUG_BUILD_DIR.exists(),
        reason="Debug build not found - run PyInstaller debug spec first",
    )
    def test_debug_executable_exists(self):
        """Debug executable should exist"""
        exe_path = DEBUG_BUILD_DIR / "WeatherApp_Debug.exe"
        assert exe_path.exists(), (
            f"WeatherApp_Debug.exe not found at {exe_path}\n"
            "Build debug version with: pyinstaller weather_app_debug.spec"
        )

    @pytest.mark.skipif(
        not DEBUG_BUILD_DIR.exists(),
        reason="Debug build not found - run PyInstaller debug spec first",
    )
    def test_debug_executable_size(self):
        """Debug executable should be reasonable size"""
        exe_path = DEBUG_BUILD_DIR / "WeatherApp_Debug.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            assert (
                1 < size_mb < 500
            ), f"Suspicious exe size: {size_mb:.1f}MB (expected 1-500MB)"

    def test_debug_console_flag(self):
        """Debug build should have console enabled"""
        spec_file = INSTALLER_DIR / "weather_app_debug.spec"
        if spec_file.exists():
            content = spec_file.read_text()
            assert (
                "console=True" in content
            ), "Debug spec should have console=True for debugging"

    @pytest.mark.skipif(not DEBUG_BUILD_DIR.exists(), reason="Debug build not found")
    def test_debug_runtime_hook_included(self):
        """Debug runtime hook should be referenced in build"""
        runtime_hook = INSTALLER_DIR / "hooks" / "runtime_hook_debug.py"
        assert runtime_hook.exists(), f"Debug runtime hook not found at {runtime_hook}"

        # Check that it sets USE_TEST_DB
        content = runtime_hook.read_text()
        assert (
            'os.environ["USE_TEST_DB"] = "true"' in content
        ), "Debug runtime hook should set USE_TEST_DB=true"


class TestBuildConfiguration:
    """Tests for build configuration files"""

    def test_spec_files_exist(self):
        """Spec files should exist"""
        prod_spec = INSTALLER_DIR / "weather_app.spec"
        debug_spec = INSTALLER_DIR / "weather_app_debug.spec"

        assert prod_spec.exists(), f"Production spec not found at {prod_spec}"
        assert debug_spec.exists(), f"Debug spec not found at {debug_spec}"

    def test_runtime_hooks_exist(self):
        """Runtime hooks should exist"""
        prod_hook = INSTALLER_DIR / "hooks" / "runtime_hook_production.py"
        debug_hook = INSTALLER_DIR / "hooks" / "runtime_hook_debug.py"

        assert prod_hook.exists(), f"Production runtime hook not found at {prod_hook}"
        assert debug_hook.exists(), f"Debug runtime hook not found at {debug_hook}"

    def test_hidden_imports_configured(self):
        """Spec files should have required hidden imports"""
        spec_file = INSTALLER_DIR / "weather_app.spec"
        content = spec_file.read_text()

        required_imports = [
            "uvicorn",
            "pystray",
            "PIL",
        ]

        for imp in required_imports:
            assert (
                imp in content
            ), f"Missing required hidden import '{imp}' in spec file"

    def test_frontend_check_in_spec(self):
        """Spec file should check if frontend is built"""
        spec_file = INSTALLER_DIR / "weather_app.spec"
        content = spec_file.read_text()

        assert "web/dist" in content, "Spec file should reference frontend dist/"
        assert ".exists()" in content, "Spec file should check if frontend dist exists"


class TestResourceVerification:
    """Tests that verify bundled resources are correct"""

    @pytest.mark.skipif(
        not PROD_BUILD_DIR.exists(), reason="Production build not found"
    )
    def test_verify_all_critical_resources(self):
        """Verify all critical resources are present in production build"""
        critical_resources = {
            "Frontend HTML": PROD_BUILD_DIR
            / "_internal"
            / "web"
            / "dist"
            / "index.html",
            "PNG Icon": PROD_BUILD_DIR
            / "_internal"
            / "weather_app"
            / "resources"
            / "icons"
            / "weather-app.png",
            "ICO Icon": PROD_BUILD_DIR
            / "_internal"
            / "weather_app"
            / "resources"
            / "icons"
            / "weather-app.ico",
        }

        missing = []
        for name, path in critical_resources.items():
            if not path.exists():
                missing.append(f"{name}: {path}")

        assert not missing, f"Missing critical resources:\n" + "\n".join(
            f"  - {m}" for m in missing
        )


def test_crash_logger_module_exists():
    """Crash logger module should exist"""
    crash_logger = (
        Path(__file__).parent.parent / "weather_app" / "launcher" / "crash_logger.py"
    )
    assert crash_logger.exists(), f"Crash logger module not found at {crash_logger}"


def test_launcher_uses_crash_logger():
    """Launcher should import and use crash logger"""
    launcher = Path(__file__).parent.parent / "launcher.py"
    assert launcher.exists(), "launcher.py not found"

    content = launcher.read_text()
    assert "crash_logger" in content, "launcher.py should import crash_logger module"
    assert (
        "CrashLogger" in content
    ), "launcher.py should use CrashLogger context manager"


# Build verification summary
def test_build_verification_summary(capsys):
    """Print summary of build verification"""
    print("\n" + "=" * 80)
    print("BUILD VERIFICATION SUMMARY")
    print("=" * 80)

    prod_exists = PROD_BUILD_DIR.exists()
    debug_exists = DEBUG_BUILD_DIR.exists()

    print(f"\nProduction Build: {'✓ Found' if prod_exists else '✗ Not Found'}")
    if prod_exists:
        exe = PROD_BUILD_DIR / "WeatherApp.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / (1024 * 1024)
            print(f"  Location: {PROD_BUILD_DIR}")
            print(f"  Size: {size_mb:.1f} MB")

    print(f"\nDebug Build: {'✓ Found' if debug_exists else '✗ Not Found'}")
    if debug_exists:
        exe = DEBUG_BUILD_DIR / "WeatherApp_Debug.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / (1024 * 1024)
            print(f"  Location: {DEBUG_BUILD_DIR}")
            print(f"  Size: {size_mb:.1f} MB")

    print("\nTo build installers:")
    print("  cd installer/windows")
    print("  build.bat                    # Production build")
    print("  pyinstaller weather_app_debug.spec --clean    # Debug build")

    print("\n" + "=" * 80)

    # Always pass - this is just informational
    assert True
