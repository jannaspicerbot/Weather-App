#!/usr/bin/env python3
"""
Build Verification Script

Verifies that PyInstaller builds are complete and ready for distribution.
Run this after building but before testing or distributing.

Usage:
    python verify_build.py              # Check production build
    python verify_build.py --debug      # Check debug build
    python verify_build.py --all        # Check both builds
"""

import argparse
import sys
from pathlib import Path


def verify_build(build_name, build_dir, exe_name, is_debug=False):
    """
    Verify a single build.

    Args:
        build_name: Human-readable name (e.g., "Production")
        build_dir: Path to build directory
        exe_name: Executable filename
        is_debug: Whether this is a debug build

    Returns:
        tuple: (success: bool, errors: list, warnings: list)
    """
    errors = []
    warnings = []

    print(f"\n{'='*80}")
    print(f"Verifying {build_name} Build")
    print(f"{'='*80}\n")

    # Check if build exists
    if not build_dir.exists():
        errors.append(f"Build directory not found: {build_dir}")
        print(f"✗ Build directory not found")
        print(f"  Expected: {build_dir}")
        print(f"\n  To build:")
        if is_debug:
            print(f"    cd {build_dir.parent.parent}")
            print(f"    pyinstaller weather_app_debug.spec --clean")
        else:
            print(f"    cd {build_dir.parent.parent}")
            print(f"    build.bat")
        return False, errors, warnings

    print(f"✓ Build directory: {build_dir}")

    # Check executable
    exe_path = build_dir / exe_name
    if not exe_path.exists():
        errors.append(f"Executable not found: {exe_path}")
        print(f"✗ Executable not found: {exe_name}")
    else:
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✓ Executable: {exe_name} ({size_mb:.1f} MB)")

        if size_mb < 1:
            warnings.append(f"Executable suspiciously small: {size_mb:.1f} MB")
        elif size_mb > 500:
            warnings.append(f"Executable suspiciously large: {size_mb:.1f} MB")

    # Check _internal directory
    internal_dir = build_dir / "_internal"
    if not internal_dir.exists():
        errors.append("_internal directory not found")
        print(f"✗ _internal directory not found")
    else:
        print(f"✓ _internal directory exists")

    # Check critical resources
    print(f"\nCritical Resources:")

    resources = {
        "Frontend HTML": internal_dir / "web" / "dist" / "index.html",
        "Frontend Assets": internal_dir / "web" / "dist" / "assets",
        "PNG Icon": internal_dir
        / "weather_app"
        / "resources"
        / "icons"
        / "weather-app.png",
        "ICO Icon": internal_dir
        / "weather_app"
        / "resources"
        / "icons"
        / "weather-app.ico",
    }

    for name, path in resources.items():
        if path.exists():
            if path.is_dir():
                count = len(list(path.iterdir()))
                print(f"  ✓ {name} ({count} files)")
            else:
                size_kb = path.stat().st_size / 1024
                print(f"  ✓ {name} ({size_kb:.1f} KB)")
        else:
            errors.append(f"Missing {name}: {path}")
            print(f"  ✗ {name} - NOT FOUND")

            if "Frontend" in name:
                print(f"     → Run 'npm run build' in web/ directory first")

    # Check for DuckDB
    print(f"\nDependencies:")
    duckdb_files = list(internal_dir.rglob("*duckdb*"))
    if duckdb_files:
        print(f"  ✓ DuckDB ({len(duckdb_files)} files)")
        # Show a few examples
        for f in duckdb_files[:3]:
            rel_path = f.relative_to(internal_dir)
            print(f"      - {rel_path}")
        if len(duckdb_files) > 3:
            print(f"      ... and {len(duckdb_files) - 3} more")
    else:
        warnings.append("No DuckDB files found - database may not work")
        print(f"  ⚠ DuckDB files not found")

    # Check for PIL/Pillow
    pil_files = list(internal_dir.rglob("*PIL*")) + list(
        internal_dir.rglob("*Pillow*")
    )
    if pil_files:
        print(f"  ✓ PIL/Pillow ({len(pil_files)} files)")
    else:
        warnings.append("No PIL/Pillow files found - icons may not work")
        print(f"  ⚠ PIL/Pillow files not found")

    # Check for pystray
    pystray_files = list(internal_dir.rglob("*pystray*"))
    if pystray_files:
        print(f"  ✓ pystray ({len(pystray_files)} files)")
    else:
        warnings.append("No pystray files found - system tray may not work")
        print(f"  ⚠ pystray files not found")

    # Check for uvicorn
    uvicorn_files = list(internal_dir.rglob("*uvicorn*"))
    if uvicorn_files:
        print(f"  ✓ uvicorn ({len(uvicorn_files)} files)")
    else:
        errors.append("No uvicorn files found - server will not work")
        print(f"  ✗ uvicorn files not found")

    # Debug-specific checks
    if is_debug:
        print(f"\nDebug Configuration:")

        # Check runtime hook
        runtime_hook = build_dir.parent.parent / "hooks" / "runtime_hook_debug.py"
        if runtime_hook.exists():
            content = runtime_hook.read_text()
            if 'USE_TEST_DB' in content:
                print(f"  ✓ Runtime hook sets USE_TEST_DB")
            else:
                warnings.append("Runtime hook doesn't set USE_TEST_DB")
                print(f"  ⚠ Runtime hook missing USE_TEST_DB")
        else:
            warnings.append("Debug runtime hook not found")
            print(f"  ⚠ Runtime hook not found")

    # Summary
    print(f"\n{'='*80}")
    success = len(errors) == 0
    if success:
        print(f"✓ {build_name} build verification PASSED")
        if warnings:
            print(f"⚠ {len(warnings)} warning(s)")
    else:
        print(f"✗ {build_name} build verification FAILED")
        print(f"  {len(errors)} error(s), {len(warnings)} warning(s)")

    return success, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Verify PyInstaller builds")
    parser.add_argument(
        "--debug", action="store_true", help="Verify debug build instead of production"
    )
    parser.add_argument("--all", action="store_true", help="Verify both builds")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    results = []

    # Verify production build
    if not args.debug or args.all:
        prod_dir = script_dir / "dist" / "WeatherApp"
        success, errors, warnings = verify_build(
            "Production", prod_dir, "WeatherApp.exe", is_debug=False
        )
        results.append(("Production", success, errors, warnings))

    # Verify debug build
    if args.debug or args.all:
        debug_dir = script_dir / "dist" / "WeatherApp_Debug"
        success, errors, warnings = verify_build(
            "Debug", debug_dir, "WeatherApp_Debug.exe", is_debug=True
        )
        results.append(("Debug", success, errors, warnings))

    # Overall summary
    print(f"\n\n{'='*80}")
    print("OVERALL SUMMARY")
    print(f"{'='*80}\n")

    all_success = True
    for build_name, success, errors, warnings in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{build_name} Build: {status}")

        if errors:
            print(f"  Errors:")
            for error in errors:
                print(f"    - {error}")

        if warnings:
            print(f"  Warnings:")
            for warning in warnings:
                print(f"    - {warning}")

        if not success:
            all_success = False

    print(f"\n{'='*80}\n")

    if all_success:
        print("✓ All builds ready for testing/distribution")
        return 0
    else:
        print("✗ Fix errors before distributing")
        print("\nCommon fixes:")
        print("  - Frontend: cd web && npm run build")
        print("  - Icons: Ensure weather_app/resources/icons/ has .png and .ico files")
        print("  - Build: cd installer/windows && build.bat")
        return 1


if __name__ == "__main__":
    sys.exit(main())
