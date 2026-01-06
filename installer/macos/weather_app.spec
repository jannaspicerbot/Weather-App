# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Weather App (macOS)

Packages the Weather App as a standalone macOS application bundle with:
- System tray/menu bar application
- Embedded FastAPI server
- Pre-built React frontend
- DuckDB database engine

Build command:
    pyinstaller weather_app.spec --clean
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from pathlib import Path

# Project root directory
project_root = Path('..', '..').resolve()

# Collect all data files
datas = []

# Include frontend static files
frontend_dist = project_root / 'web' / 'dist'
if frontend_dist.exists():
    datas += [(str(frontend_dist), 'web/dist')]
else:
    print("WARNING: Frontend not built! Run 'npm run build' in web/ directory")

# Include DuckDB data files (binary extensions)
datas += collect_data_files('duckdb')

# Collect all weather_app submodules
hiddenimports = collect_submodules('weather_app')

# Add uvicorn hidden imports (required for FastAPI server)
hiddenimports += [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
]

# Add pystray and PIL dependencies
hiddenimports += [
    'pystray',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
]

a = Analysis(
    [str(project_root / 'launcher.py')],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Exclude if not needed to reduce size
        'scipy',       # Exclude if not needed
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WeatherApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WeatherApp',
)

app = BUNDLE(
    coll,
    name='WeatherApp.app',
    icon=str(project_root / 'weather_app' / 'resources' / 'icons' / 'weather-app.icns'),
    bundle_identifier='com.weatherapp.app',
    info_plist={
        'CFBundleName': 'Weather App',
        'CFBundleDisplayName': 'Weather App',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': 'True',
        'LSUIElement': '1',  # Run as menu bar app (no dock icon)
    },
)
