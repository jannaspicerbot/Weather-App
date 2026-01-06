@echo off
REM Build script for Weather App (Windows)
REM
REM This script:
REM 1. Builds the React frontend
REM 2. Packages the app with PyInstaller
REM 3. Creates a distributable executable
REM
REM Requirements:
REM - Node.js and npm installed
REM - Python 3.8+ with all dependencies installed
REM - PyInstaller installed (pip install pyinstaller)

echo ========================================
echo Weather App - Windows Build Script
echo ========================================
echo.

REM Step 1: Build frontend
echo Step 1/2: Building React frontend...
echo.
cd ..\..\web
if not exist "package.json" (
    echo ERROR: package.json not found in web/ directory
    pause
    exit /b 1
)

call npm install
if errorlevel 1 (
    echo ERROR: npm install failed
    pause
    exit /b 1
)

call npm run build
if errorlevel 1 (
    echo ERROR: npm build failed
    pause
    exit /b 1
)

echo.
echo Frontend built successfully!
echo.

REM Step 2: Build executable
cd ..\installer\windows
echo Step 2/2: Building executable with PyInstaller...
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not installed
    echo Install with: pip install pyinstaller
    pause
    exit /b 1
)

REM Run PyInstaller
pyinstaller weather_app.spec --clean --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\WeatherApp\WeatherApp.exe
echo.
echo To run: cd dist\WeatherApp && WeatherApp.exe
echo.
echo To create an installer, run Inno Setup with setup.iss
echo.
pause
