#!/bin/bash
#
# Build script for Weather App (macOS)
#
# This script:
# 1. Builds the React frontend
# 2. Packages the app with PyInstaller
# 3. Creates a distributable .app bundle
#
# Requirements:
# - Node.js and npm installed
# - Python 3.8+ with all dependencies installed
# - PyInstaller installed (pip install pyinstaller)

set -e  # Exit on error

echo "========================================"
echo "Weather App - macOS Build Script"
echo "========================================"
echo ""

# Step 1: Build frontend
echo "Step 1/2: Building React frontend..."
echo ""
cd ../../web

if [ ! -f "package.json" ]; then
    echo "ERROR: package.json not found in web/ directory"
    exit 1
fi

npm install
npm run build

echo ""
echo "Frontend built successfully!"
echo ""

# Step 2: Build executable
cd ../installer/macos
echo "Step 2/2: Building application bundle with PyInstaller..."
echo ""

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "ERROR: PyInstaller not installed"
    echo "Install with: pip install pyinstaller"
    exit 1
fi

# Run PyInstaller
pyinstaller weather_app.spec --clean --noconfirm

echo ""
echo "========================================"
echo "Build Complete!"
echo "========================================"
echo ""
echo "Application location: dist/WeatherApp.app"
echo ""
echo "To run: open dist/WeatherApp.app"
echo ""
echo "To create a DMG installer, run: ./create_dmg.sh"
echo ""
