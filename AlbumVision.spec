# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('app', 'app'), ('data', 'data'), ('resources', 'resources'), ('models', 'models')],
    hiddenimports=['ultralytics', 'torch', 'torchvision', 'cv2', 'opencv-python', 'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'numpy', 'PIL', 'PIL.Image', 'sqlite3', 'aiosqlite', 'json', 'asyncio', 'app.utils.Auto_Sort_Basic', 'app.utils.file_utils', 'app.utils.image_quality', 'app.utils.path_settings', 'app.gui.widgets.yolo_results_widget'],
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
    a.binaries,
    a.datas,
    [],
    name='AlbumVision',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
