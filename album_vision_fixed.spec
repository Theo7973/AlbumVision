# -*- mode: python ; coding: utf-8 -*-
import multiprocessing

# CRITICAL: Prevent multiprocessing issues
multiprocessing.freeze_support()

block_cipher = None

a = Analysis(
    ['album_vision_safe_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('app', 'app'),
        ('data', 'data'),
    ],
    hiddenimports=[
        # Core imports
        'multiprocessing',
        'psutil',
        
        # Qt imports
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        
        # AI/ML imports
        'ultralytics',
        'torch',
        'torchvision',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        
        # Database imports - COMPLETE LIST
        'sqlite3',
        'aiosqlite',
        'asyncio',
        'aiomysql',
        'pymysql',
        
        # Environment and config
        'dotenv',
        'python-dotenv',
        
        # App imports
        'app.gui.main_window',
        'app.gui.widgets.yolo_results_widget',
        'app.utils.Auto_Sort_Basic',
        'app.utils.file_utils',
        'app.utils.image_quality',
        'app.utils.path_settings',
        
        # All possible dialog imports
        'app.gui.dialogs',
        'app.gui.dialogs.change_tag_dialog',
        'app.gui.dialogs.export_dialog',
        'app.gui.dialogs.import_dialog',
        'app.gui.dialogs.output_dialog',
        'app.gui.dialogs.search_filter',
        'app.gui.dialogs.stats_dashboard',
        'app.gui.dialogs.resize_dialog',
        
        # Standard library
        'json',
        'shutil',
        'functools',
        'tempfile',
        'atexit',
        'pathlib',
        'datetime',
        'uuid',
        'hashlib',
        'base64',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'collections',
        'itertools',
        'operator',
        'weakref',
        
        # Additional potentially needed modules
        'logging',
        'threading',
        'queue',
        'time',
        'math',
        'random',
        'string',
        'pickle',
        'copy',
        'io',
        'struct',
        'zlib',
        'gzip',
        'tarfile',
        'zipfile',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Remove unnecessary modules to reduce size and conflicts
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'notebook',
        'sphinx',
        'pytest',
        'tensorflow',
        'bokeh',
        'plotly',
        'seaborn',
        'statsmodels',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AlbumVisionPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
