@echo off
REM Build Inno Setup installer for Weather App
REM
REM Prerequisites:
REM - Inno Setup installed (https://jrsoftware.org/isinfo.php)
REM - WeatherApp.exe already built (run build.bat first)

echo ========================================
echo Weather App - Installer Builder
echo ========================================
echo.

REM Check if PyInstaller build exists
if not exist "dist\WeatherApp\WeatherApp.exe" (
    echo ERROR: WeatherApp.exe not found!
    echo.
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

echo Found WeatherApp.exe - Ready to build installer
echo.

REM Check for Inno Setup in common installation paths
set "INNO_PATH="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "INNO_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 5\ISCC.exe" set "INNO_PATH=C:\Program Files (x86)\Inno Setup 5\ISCC.exe"
if exist "C:\Program Files\Inno Setup 5\ISCC.exe" set "INNO_PATH=C:\Program Files\Inno Setup 5\ISCC.exe"

if "%INNO_PATH%"=="" (
    echo ERROR: Inno Setup not found!
    echo.
    echo Please install Inno Setup from:
    echo https://jrsoftware.org/isinfo.php
    echo.
    echo Default installation path:
    echo C:\Program Files (x86)\Inno Setup 6\
    echo.
    pause
    exit /b 1
)

echo Found Inno Setup: %INNO_PATH%
echo.
echo Building installer...
echo.

REM Create output directory
if not exist "output" mkdir output

REM Run Inno Setup compiler
"%INNO_PATH%" setup.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installer Build Complete!
echo ========================================
echo.
echo Installer location: output\WeatherAppSetup.exe
echo.
echo You can now distribute this installer to users.
echo.
echo To test: Run output\WeatherAppSetup.exe
echo.
pause
