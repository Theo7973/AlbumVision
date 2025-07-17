# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['album_vision_plus_launcher.py'],
    pathex=['app', 'app/gui', '.'],
    binaries=[],
    datas=[('app', 'app'), ('data', 'data'), ('resources', 'resources'), ('models', 'models'), ('user_data', 'user_data')],
    hiddenimports=['ultralytics', 'torch', 'torchvision', 'cv2', 'opencv-python', 'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'numpy', 'PIL', 'PIL.Image', 'sqlite3', 'aiosqlite', 'json', 'asyncio', 'shutil', 'functools', 'db_utils', 'app.gui.db_utils', 'app.gui.main_window', 'app.utils.Auto_Sort_Basic', 'app.utils.file_utils', 'app.utils.image_quality', 'app.utils.path_settings', 'app.gui.widgets.yolo_results_widget', 'app.gui.widgets.path_selection', 'app.export_widget', 'app.folder_preview_widget', 'app.gui.dialogs.change_tag_dialog', 'app.gui.dialogs.export_dialog', 'app.gui.dialogs.import_dialog', 'app.gui.dialogs.output_dialog', 'app.gui.dialogs.search_filter', 'app.gui.dialogs.stats_dashboard', 'app.categorizer.models', 'app.categorizer.processors', 'app.database', 'app.settings'],
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
    name='Album Vision+',
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
