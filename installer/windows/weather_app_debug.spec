# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller DEBUG spec file for Weather App (Windows)

This version has console=True to show error messages during debugging.

Build command:
    pyinstaller weather_app_debug.spec --clean
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

# Include icon resources
icons_dir = project_root / 'weather_app' / 'resources' / 'icons'
if icons_dir.exists():
    datas += [(str(icons_dir), 'weather_app/resources/icons')]
else:
    print("WARNING: Icons directory not found!")

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
    runtime_hooks=['hooks/runtime_hook_debug.py'],  # Debug configuration + diagnostics
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
    name='WeatherApp_Debug',
    debug=True,  # Enable debug mode
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # SHOW CONSOLE for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'weather_app' / 'resources' / 'icons' / 'weather-app.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WeatherApp_Debug',
)
