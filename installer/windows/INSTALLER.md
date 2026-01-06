# Creating a Windows Installer with Inno Setup

This guide explains how to create a professional Windows installer for the Weather App using Inno Setup.

## Overview

The installer provides:
- ✅ Professional installation wizard
- ✅ Start Menu shortcuts
- ✅ Optional desktop shortcut
- ✅ Optional "Launch at startup"
- ✅ Proper uninstaller in Windows Settings
- ✅ Custom Weather App icon
- ✅ User data preservation on uninstall

---

## Prerequisites

### 1. Install Inno Setup

**Download:** https://jrsoftware.org/isinfo.php

**Recommended Version:** Inno Setup 6.x (latest stable)

**Installation:**
1. Download the installer (e.g., `innosetup-6.x.x.exe`)
2. Run the installer
3. Accept the license agreement
4. Choose default installation path: `C:\Program Files (x86)\Inno Setup 6\`
5. Complete installation

### 2. Build the Executable

The installer packages the PyInstaller build, so you need to create that first:

```bash
cd installer\windows
build.bat
```

This creates: `dist\WeatherApp\WeatherApp.exe`

---

## Building the Installer

### Quick Build

```bash
cd installer\windows
build_installer.bat
```

This will:
1. Verify `WeatherApp.exe` exists
2. Find Inno Setup installation
3. Compile the installer
4. Create `output\WeatherAppSetup.exe`

### Manual Build

If you prefer to build manually:

1. Open Inno Setup Compiler
2. File → Open → Select `setup.iss`
3. Build → Compile
4. Installer created in `output\` folder

### Command Line Build

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

---

## Installer Features

### Installation Options

**User chooses:**
- Installation directory (default: `C:\Program Files\Weather App\`)
- Create desktop shortcut (optional, unchecked by default)
- Launch at Windows startup (optional, unchecked by default)

**Automatic:**
- Start Menu shortcuts created
- Uninstaller registered in Windows Settings

### Files Installed

```
C:\Program Files\Weather App\
├── WeatherApp.exe           # Main application
└── _internal\               # Dependencies and resources
    ├── *.dll                # Python runtime and libraries
    ├── web\dist\            # React frontend
    └── ...                  # Other bundled files
```

### User Data Location

User data is stored separately and **NOT in Program Files**:

```
%APPDATA%\WeatherApp\
├── .env                     # API credentials
├── ambient_weather.duckdb   # Weather data
└── logs\                    # Application logs
```

**Why separate?**
- Preserved across upgrades
- Works without admin permissions
- Standard Windows practice

### Uninstallation

**Two ways to uninstall:**

1. **Windows Settings:**
   - Settings → Apps → Weather App → Uninstall

2. **Start Menu:**
   - Start → Weather App → Uninstall Weather App

**Uninstaller behavior:**
- Removes application files from `Program Files`
- Removes shortcuts (Start Menu, Desktop, Startup)
- **Asks user** if they want to keep their data
  - **Yes:** Preserves `%APPDATA%\WeatherApp\` (can reinstall later)
  - **No:** Deletes database and settings

---

## Customization

### Change App Version

Edit `setup.iss`:

```iss
#define MyAppVersion "1.0.0"
```

### Change App ID (for different variants)

The AppId uniquely identifies the app in Windows:

```iss
AppId={{8F3E9A2C-1B4D-4E5F-9C8A-7D6E5F4C3B2A}
```

**⚠️ Only change this if creating a completely different app!**

### Add License File

1. Create `LICENSE` file in project root
2. Uncomment in `setup.iss`:
   ```iss
   LicenseFile=..\..\LICENSE
   ```

### Add README Before Install

1. Uncomment in `setup.iss`:
   ```iss
   InfoBeforeFile=..\..\README.md
   ```

### Change Compression

Current: `lzma2/max` (best compression, slower build)

For faster builds, use:
```iss
Compression=lzma
```

### Disable Desktop Icon Option

Remove this task from `[Tasks]` section:
```iss
Name: "desktopicon"; ...
```

---

## Testing the Installer

### Test on Clean VM (Recommended)

1. **Create Windows VM** (VirtualBox, VMware, or Hyper-V)
2. **Copy installer:** `WeatherAppSetup.exe`
3. **Run installer** on clean Windows
4. **Test:**
   - Installation succeeds
   - App launches
   - Setup wizard appears (first launch)
   - Data collection works
   - Shortcuts work
5. **Test uninstall:**
   - Uninstaller runs
   - Data preservation dialog appears
   - Files removed properly

### Test on Current Machine

⚠️ **Warning:** This will install to your system!

```bash
cd installer\windows\output
WeatherAppSetup.exe
```

**Cleanup after testing:**
- Uninstall via Windows Settings
- Choose "No" when asked about keeping data (to fully clean up)

---

## Distribution

### GitHub Releases (Recommended)

1. Create a new release on GitHub
2. Tag version: `v1.0.0`
3. Upload `WeatherAppSetup.exe` as release asset
4. Users download from: https://github.com/jannaspicerbot/Weather-App/releases

### File Hosting

Alternative hosting options:
- Dropbox / Google Drive (public link)
- Your own website
- Cloud storage service

**Installer size:** ~100-120 MB (includes all dependencies)

---

## Code Signing (Optional - Future)

For production distribution, consider code signing:

**Benefits:**
- Removes "Unknown Publisher" warning
- Builds trust with users
- Required for Microsoft Store

**Requirements:**
- Code signing certificate ($100-300/year)
- From: DigiCert, Sectigo, or similar CA

**Process:**
1. Purchase certificate
2. Add to `setup.iss`:
   ```iss
   SignTool=signtool
   SignedUninstaller=yes
   ```
3. Configure SignTool path

**Not required for personal/testing use!**

---

## Troubleshooting

### "Inno Setup not found"

**Solution:** Install Inno Setup from https://jrsoftware.org/isinfo.php

### "WeatherApp.exe not found"

**Solution:** Run `build.bat` first to create the PyInstaller build

### "Access denied" during installation

**Solution:** Run installer as administrator (right-click → Run as administrator)

Or change `setup.iss`:
```iss
PrivilegesRequired=admin
```

### Installer won't run / SmartScreen warning

**Expected behavior** for unsigned installers.

**User must:**
1. Click "More info"
2. Click "Run anyway"

**To avoid:** Get code signing certificate (see above)

### Installation fails silently

**Check:** Inno Setup compiler output for errors

**Common issues:**
- Missing files in PyInstaller build
- Invalid icon path
- Syntax errors in `setup.iss`

---

## File Structure

```
installer/windows/
├── build.bat               # Build PyInstaller executable
├── build_installer.bat     # Build Inno Setup installer
├── setup.iss              # Inno Setup script
├── weather_app.spec       # PyInstaller configuration
├── INSTALLER.md           # This file
├── dist/                  # PyInstaller output (gitignored)
│   └── WeatherApp/
│       └── WeatherApp.exe
└── output/                # Installer output (gitignored)
    └── WeatherAppSetup.exe
```

---

## Resources

- **Inno Setup Documentation:** https://jrsoftware.org/ishelp/
- **Inno Setup Examples:** Check `Examples\` folder in Inno Setup installation
- **Script Reference:** https://jrsoftware.org/ishelp/index.php?topic=scriptintro

---

## Summary

**To create the installer:**

```bash
# 1. Install Inno Setup (one-time)
# Download from: https://jrsoftware.org/isinfo.php

# 2. Build the app
cd installer\windows
build.bat

# 3. Build the installer
build_installer.bat

# 4. Distribute
# Upload output\WeatherAppSetup.exe
```

**Users install with:**
- Double-click `WeatherAppSetup.exe`
- Follow wizard
- App appears in Start Menu
- Uninstall via Windows Settings

---

**Ready to build?** Install Inno Setup and run `build_installer.bat`!
