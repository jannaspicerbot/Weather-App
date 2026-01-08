#!/usr/bin/env python3
"""
Generate PWA icons from the existing Weather App icon.

This script creates all necessary icon sizes for PWA/iOS support:
- icon-192.png (Android/Chrome)
- icon-512.png (Android/Chrome large)
- icon-maskable-512.png (Android maskable)
- apple-touch-icon.png (iOS home screen, 180x180)
- splash screens for iPad

Usage:
    python scripts/generate_pwa_icons.py
"""

from pathlib import Path
from PIL import Image

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_ICON = PROJECT_ROOT / "weather_app" / "resources" / "icons" / "icon.iconset" / "icon_512x512@2x.png"
OUTPUT_DIR = PROJECT_ROOT / "web" / "public" / "icons"

# Icon sizes needed for PWA
ICON_SIZES = {
    "icon-192.png": 192,
    "icon-512.png": 512,
    "icon-maskable-512.png": 512,
    "apple-touch-icon.png": 180,
}

# iPad splash screen sizes (width x height)
SPLASH_SIZES = {
    "splash-1024x1366.png": (1024, 1366),  # iPad Pro 10.5" portrait
    "splash-1536x2048.png": (1536, 2048),  # iPad Pro 12.9" portrait
}


def create_icon(source: Image.Image, output_path: Path, size: int) -> None:
    """Resize and save an icon."""
    resized = source.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(output_path, "PNG", optimize=True)
    print(f"  Created: {output_path.name} ({size}x{size})")


def create_maskable_icon(source: Image.Image, output_path: Path, size: int) -> None:
    """Create a maskable icon with padding for safe area."""
    # Maskable icons need 10% padding on each side (80% safe area)
    safe_size = int(size * 0.8)
    padding = (size - safe_size) // 2

    # Create new image with background color
    maskable = Image.new("RGBA", (size, size), (59, 130, 246, 255))  # Blue background (#3b82f6)

    # Resize source to safe area size
    resized = source.resize((safe_size, safe_size), Image.Resampling.LANCZOS)

    # Paste centered
    maskable.paste(resized, (padding, padding), resized if resized.mode == "RGBA" else None)
    maskable.save(output_path, "PNG", optimize=True)
    print(f"  Created: {output_path.name} ({size}x{size}, maskable)")


def create_splash_screen(source: Image.Image, output_path: Path, width: int, height: int) -> None:
    """Create a splash screen with centered icon."""
    # Create background with theme color
    splash = Image.new("RGBA", (width, height), (31, 41, 55, 255))  # Dark gray (#1f2937)

    # Icon should be about 20% of the smaller dimension
    icon_size = min(width, height) // 5
    icon = source.resize((icon_size, icon_size), Image.Resampling.LANCZOS)

    # Center the icon
    x = (width - icon_size) // 2
    y = (height - icon_size) // 2

    splash.paste(icon, (x, y), icon if icon.mode == "RGBA" else None)
    splash.save(output_path, "PNG", optimize=True)
    print(f"  Created: {output_path.name} ({width}x{height})")


def main() -> None:
    """Generate all PWA icons."""
    print("Generating PWA icons for Weather App...\n")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Check source icon exists
    if not SOURCE_ICON.exists():
        # Try alternate source
        alt_source = PROJECT_ROOT / "weather_app" / "resources" / "icons" / "icon.iconset" / "icon_512x512.png"
        if alt_source.exists():
            source_path = alt_source
        else:
            print(f"Error: Source icon not found at {SOURCE_ICON}")
            print("Please ensure the Weather App icons exist.")
            return
    else:
        source_path = SOURCE_ICON

    print(f"Source: {source_path}")
    print(f"Output: {OUTPUT_DIR}\n")

    # Load source image
    with Image.open(source_path) as source:
        # Convert to RGBA if needed
        if source.mode != "RGBA":
            source = source.convert("RGBA")

        print("Creating standard icons:")
        for filename, size in ICON_SIZES.items():
            output_path = OUTPUT_DIR / filename
            if "maskable" in filename:
                create_maskable_icon(source, output_path, size)
            else:
                create_icon(source, output_path, size)

        print("\nCreating splash screens:")
        for filename, (width, height) in SPLASH_SIZES.items():
            output_path = OUTPUT_DIR / filename
            create_splash_screen(source, output_path, width, height)

    print("\nDone! PWA icons generated successfully.")
    print(f"\nGenerated {len(ICON_SIZES) + len(SPLASH_SIZES)} files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
