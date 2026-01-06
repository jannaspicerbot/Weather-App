# Weather App Installers

This directory contains build scripts and configurations for packaging the Weather App as standalone executables for Windows and macOS.

## Overview

The Weather App can be packaged as:
- **Windows**: `.exe` executable (with optional Inno Setup installer)
- **macOS**: `.app` application bundle (with optional `.dmg` installer)

## Prerequisites

### All Platforms
- Python 3.8 or higher
- All Python dependencies installed: `pip install -r requirements.txt`
- Node.js and npm installed
- Frontend built: `cd web && npm run build`

### Windows Specific
- PyInstaller: `pip install pyinstaller`
- (Optional) Inno Setup for creating installer: https://jrsoftware.org/isinfo.php

### macOS Specific
- PyInstaller: `pip install pyinstaller`
- (Optional) `create-dmg` for DMG creation: `npm install -g create-dmg`

## Building

### Windows

**Quick Build:**
```batch
cd installer\windows
build.bat
```

This will:
1. Build the React frontend
2. Package the app with PyInstaller
3. Create `dist\WeatherApp\WeatherApp.exe`

**Create Installer (Optional):**
1. Install Inno Setup
2. Run: `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss`
3. Installer created: `output\WeatherAppSetup.exe`

### macOS

**Quick Build:**
```bash
cd installer/macos
chmod +x build.sh
./build.sh
```

This will:
1. Build the React frontend
2. Package the app with PyInstaller
3. Create `dist/WeatherApp.app`

**Create DMG (Optional):**
```bash
chmod +x create_dmg.sh
./create_dmg.sh
```

## What Gets Packaged

The standalone executable includes:
- Complete Python runtime
- FastAPI web server
- APScheduler for automated data collection
- DuckDB database engine
- Pre-built React frontend (from `web/dist/`)
- System tray application
- First-launch setup wizard

**Not Included (User Data):**
- API credentials (`.env` file)
- Weather data database (`ambient_weather.duckdb`)
- User settings and logs

User data is stored in platform-specific locations:
- **Windows**: `%APPDATA%\WeatherApp\`
- **macOS**: `~/Library/Application Support/WeatherApp/`
- **Linux**: `~/.local/share/WeatherApp/`

## File Structure

```
installer/
├── README.md                    # This file
├── windows/
│   ├── weather_app.spec         # PyInstaller configuration
│   ├── build.bat                # Build script
│   ├── setup.iss                # Inno Setup installer script (optional)
│   └── dist/                    # Build output (generated)
│       └── WeatherApp/
│           └── WeatherApp.exe
└── macos/
    ├── weather_app.spec         # PyInstaller configuration
    ├── build.sh                 # Build script
    ├── create_dmg.sh            # DMG creation script (optional)
    └── dist/                    # Build output (generated)
        └── WeatherApp.app
```

## Testing

After building, test the executable on a clean machine or VM to ensure:
1. Setup wizard appears on first launch
2. API credentials can be entered and saved
3. System tray icon appears
4. Dashboard opens in browser
5. Data fetching works correctly
6. App can be restarted
7. Uninstall works cleanly (if using installer)

## Distribution

### GitHub Releases (Recommended)
1. Create a new release on GitHub
2. Upload the built executables as release assets:
   - `WeatherAppSetup.exe` (Windows installer)
   - `WeatherApp-Installer.dmg` (macOS installer)
   - Or the standalone executables if not using installers
3. Users download from GitHub Releases page

### Direct Download
- Host files on personal website or cloud storage (Dropbox, Google Drive, etc.)
- Provide download links in README

## Troubleshooting

### Build Fails
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Ensure frontend is built: `cd web && npm run build`
- Check Python version: `python --version` (must be 3.8+)

### App Won't Start
- Check if antivirus is blocking the executable
- Run from command line to see error messages:
  - Windows: `dist\WeatherApp\WeatherApp.exe`
  - macOS: `open -a dist/WeatherApp.app`

### Large File Size
- The executable is large (~150-200 MB) due to:
  - Bundled Python runtime
  - DuckDB binary extensions
  - Frontend assets
  - All Python dependencies
- This is normal for PyInstaller applications
- Consider using UPX compression (enabled by default)

### "Missing Dependencies" Error
- Check `hiddenimports` in the `.spec` file
- Add missing modules to the `hiddenimports` list
- Rebuild with: `pyinstaller weather_app.spec --clean`

## Future Improvements

- [ ] Add application icons (`.ico` for Windows, `.icns` for macOS)
- [ ] Code signing for security (requires developer certificates)
- [ ] Auto-update mechanism
- [ ] Reduce executable size with selective imports
- [ ] Linux packaging (AppImage, .deb, .rpm)
- [ ] Microsoft Store / Mac App Store distribution

## Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Inno Setup Documentation](https://jrsoftware.org/ishelp/)
- [create-dmg GitHub](https://github.com/create-dmg/create-dmg)
