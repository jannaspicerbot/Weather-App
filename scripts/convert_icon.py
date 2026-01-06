"""
Convert PNG icon to platform-specific formats (.ico and .icns)

Usage: python scripts/convert_icon.py
"""

from PIL import Image
from pathlib import Path
import sys

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def convert_to_ico(png_path: Path, ico_path: Path):
    """Convert PNG to Windows .ico format with multiple sizes"""
    print(f"Converting {png_path} to {ico_path}...")

    img = Image.open(png_path)

    # Windows icon sizes: 16, 32, 48, 64, 128, 256
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]

    img.save(
        ico_path,
        format='ICO',
        sizes=icon_sizes
    )

    print(f"✅ Created {ico_path}")

def convert_to_icns(png_path: Path, icns_path: Path):
    """Convert PNG to macOS .icns format"""
    print(f"Converting {png_path} to {icns_path}...")

    # For .icns, we need to create a temporary iconset directory
    # and use macOS tools (iconutil) which only works on macOS
    # For now, we'll create the required PNG sizes that can be packaged

    img = Image.open(png_path)

    # macOS icon sizes for .icns
    iconset_dir = icns_path.parent / "icon.iconset"
    iconset_dir.mkdir(exist_ok=True)

    sizes = [
        (16, "icon_16x16.png"),
        (32, "icon_16x16@2x.png"),
        (32, "icon_32x32.png"),
        (64, "icon_32x32@2x.png"),
        (128, "icon_128x128.png"),
        (256, "icon_128x128@2x.png"),
        (256, "icon_256x256.png"),
        (512, "icon_256x256@2x.png"),
        (512, "icon_512x512.png"),
        (1024, "icon_512x512@2x.png"),
    ]

    for size, filename in sizes:
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(iconset_dir / filename)

    print(f"✅ Created iconset at {iconset_dir}")
    print(f"   On macOS, run: iconutil -c icns {iconset_dir} -o {icns_path}")

    # Note: .icns creation requires macOS 'iconutil' command
    # PyInstaller on macOS can also use the PNG directly with --icon flag

def main():
    # Paths
    project_root = Path(__file__).parent.parent
    png_path = project_root / "docs" / "design" / "icons" / "weather-app-icon-soft-trust.png"

    # Output to weather_app/resources/icons/ (bundled with app)
    resources_dir = project_root / "weather_app" / "resources" / "icons"
    windows_ico = resources_dir / "weather-app.ico"
    macos_icns = resources_dir / "weather-app.icns"
    fallback_png = resources_dir / "weather-app.png"

    # Verify source exists
    if not png_path.exists():
        print(f"❌ Error: Icon not found at {png_path}")
        sys.exit(1)

    # Create output directory
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Convert to platform-specific formats
    convert_to_ico(png_path, windows_ico)
    convert_to_icns(png_path, macos_icns)

    # Copy PNG for Linux/fallback use
    import shutil
    shutil.copy(png_path, fallback_png)
    print(f"✅ Copied fallback PNG to {fallback_png}")

    print("\n✅ Icon conversion complete!")
    print(f"   Windows:  {windows_ico}")
    print(f"   macOS:    {macos_icns} (requires macOS iconutil)")
    print(f"   Fallback: {fallback_png}")

if __name__ == "__main__":
    main()
