# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app\\gui\\main_window.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/icons', 'resources/icons'), ('data/test_images', 'data/test_images'), ('resources/animations', 'resources/animations'), ('yolov8n.pt', '.')],
    hiddenimports=['PySide6', 'cv2', 'numpy', 'matplotlib', 'ultralytics'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AlbumVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\icons\\ab_logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AlbumVision',
)
