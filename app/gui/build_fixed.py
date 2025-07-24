#!/usr/bin/env python3
"""
COMPLETE FIXED BUILD SCRIPT FOR ALBUM VISION+
Addresses all dependency issues and background process problems
Save as: build_fixed.py
"""

import os
import sys
import subprocess
import shutil
import multiprocessing
from pathlib import Path

def create_safe_launcher():
    """Create a launcher that prevents multiple instances and background processes"""
    
    launcher_content = '''#!/usr/bin/env python3

import sys
import os
import multiprocessing

# CRITICAL: Prevent multiprocessing issues in PyInstaller
if __name__ == "__main__":
    # Freeze support for multiprocessing
    multiprocessing.freeze_support()
    
    # Set multiprocessing start method to spawn (safer for PyInstaller)
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Already set

def setup_paths():
    """Setup Python paths for imports"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add paths in correct order
    paths_to_add = [
        current_dir,
        os.path.join(current_dir, 'app'),
        os.path.join(current_dir, 'app', 'gui'),
        os.path.join(current_dir, 'app', 'utils'),
        os.path.join(current_dir, 'app', 'gui', 'widgets'),
        os.path.join(current_dir, 'app', 'gui', 'dialogs'),
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return current_dir

def check_single_instance():
    """Prevent multiple instances (simple file lock)"""
    import tempfile
    import atexit
    
    lock_file = os.path.join(tempfile.gettempdir(), 'album_vision_plus.lock')
    
    # Check if already running
    if os.path.exists(lock_file):
        try:
            with open(lock_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is still running (Windows)
            try:
                import psutil
                if psutil.pid_exists(pid):
                    print("Album Vision+ is already running!")
                    return False
            except ImportError:
                pass  # psutil not available, proceed
        except:
            pass  # Lock file corrupted, proceed
    
    # Create lock file
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
        
        # Register cleanup
        def cleanup():
            try:
                os.remove(lock_file)
            except:
                pass
        atexit.register(cleanup)
        
    except:
        pass  # Can't create lock, proceed anyway
    
    return True

def setup_environment():
    """Setup environment variables to prevent background processes"""
    
    # Prevent PyTorch from creating background processes
    os.environ['OMP_NUM_THREADS'] = '1'
    os.environ['MKL_NUM_THREADS'] = '1'
    os.environ['NUMEXPR_NUM_THREADS'] = '1'
    os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
    
    # Disable CUDA if not needed (reduces background processes)
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    
    # Qt environment
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    
    # Torch settings
    os.environ['TORCH_HOME'] = os.path.join(os.path.dirname(__file__), 'torch_cache')

def main():
    """Main application entry point with proper error handling"""
    
    # CRITICAL: Check if we're the main process
    if __name__ != "__main__":
        return
    
    try:
        # Setup environment first
        setup_environment()
        
        # Setup paths
        current_dir = setup_paths()
        
        # Check for single instance
        if not check_single_instance():
            return
        
        # Import after path setup
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        # Create application with proper settings
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(True)  # CRITICAL: Quit when last window closes
        
        # Try to set Qt attribute, skip if not available
        try:
            app.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
        except AttributeError:
            pass  # This attribute doesn't exist in this Qt version
        
        # Set application properties
        app.setApplicationName("Album Vision+")
        app.setApplicationDisplayName("Album Vision+ - Smart Image Organization")
        app.setApplicationVersion("1.0")
        
        # Import main window after QApplication creation
        from app.gui.main_window import ImageWindow
        
        # Set default directory
        default_dir = os.path.join(current_dir, "data", "test_images")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~/Pictures")
            if not os.path.exists(default_dir):
                default_dir = os.getcwd()
        
        # Create main window
        window = ImageWindow(default_dir)
        window.setWindowTitle("Album Vision+ - Smart Image Organization")
        
        # Show window
        window.show()
        
        # Start event loop
        exit_code = app.exec()
        
        # CRITICAL: Proper cleanup
        window.close()
        app.quit()
        
        # Force exit to prevent hanging
        sys.exit(exit_code)
        
    except ImportError as e:
        import traceback
        error_msg = f"Import Error: {e}\\n\\nTraceback:\\n{traceback.format_exc()}"
        print(error_msg)
        sys.exit(1)
        
    except Exception as e:
        import traceback
        error_msg = f"Application Error: {e}\\n\\nTraceback:\\n{traceback.format_exc()}"
        print(error_msg)
        sys.exit(1)

# CRITICAL: Main guard
if __name__ == "__main__":
    main()
'''
    
    with open('album_vision_safe_launcher.py', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Created safe launcher: album_vision_safe_launcher.py")
    return 'album_vision_safe_launcher.py'

def create_pyinstaller_spec():
    """Create a proper spec file with ALL dependencies"""
    
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-
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
'''
    
    with open('album_vision_fixed.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created spec file: album_vision_fixed.spec")
    return 'album_vision_fixed.spec'

def fix_main_window():
    """Add proper guards to main_window.py to prevent background processes"""
    
    main_window_path = 'app/gui/main_window.py'
    if not os.path.exists(main_window_path):
        print(f"❌ {main_window_path} not found!")
        return False
    
    # Read the current file
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it already has proper guards
    if 'multiprocessing.freeze_support()' in content:
        print("✅ main_window.py already has proper guards")
        return True
    
    # Add proper guards at the end
    if 'if __name__ == "__main__":' in content:
        # Replace the existing main block
        lines = content.split('\\n')
        new_lines = []
        in_main_block = False
        
        for line in lines:
            if line.strip().startswith('if __name__ == "__main__":'):
                in_main_block = True
                new_lines.extend([
                    '',
                    'if __name__ == "__main__":',
                    '    import multiprocessing',
                    '    multiprocessing.freeze_support()',
                    '    ',
                    '    # Prevent multiple processes',
                    '    import os',
                    '    os.environ["OMP_NUM_THREADS"] = "1"',
                    '    os.environ["MKL_NUM_THREADS"] = "1"',
                    '    ',
                ])
            elif in_main_block and line.startswith('    '):
                new_lines.append(line)
            elif in_main_block and not line.startswith('    ') and line.strip():
                # End of main block
                in_main_block = False
                new_lines.append(line)
            elif not in_main_block:
                new_lines.append(line)
        
        # Write back
        with open(main_window_path, 'w', encoding='utf-8') as f:
            f.write('\\n'.join(new_lines))
        
        print("✅ Added proper guards to main_window.py")
        return True
    
    return True

def install_all_dependencies():
    """Install all required dependencies"""
    
    print("📦 Installing ALL required dependencies...")
    
    # Complete list of all dependencies your app needs
    all_packages = [
        'psutil', 
        'pyinstaller',
        'aiomysql', 
        'pymysql',
        'python-dotenv',
        'aiosqlite',
        'ultralytics',
        'torch',
        'torchvision',
        'opencv-python',
        'numpy',
        'Pillow',
        'PySide6',
        'asyncio',
    ]
    
    successful_installs = 0
    failed_installs = []
    
    for package in all_packages:
        try:
            # Check if package is already installed
            if package == 'python-dotenv':
                import dotenv
            elif package == 'opencv-python':
                import cv2
            elif package == 'Pillow':
                import PIL
            else:
                __import__(package.replace('-', '_'))
            
            print(f"✅ {package} already installed")
            successful_installs += 1
            
        except ImportError:
            print(f"📥 Installing {package}...")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ Successfully installed {package}")
                    successful_installs += 1
                else:
                    print(f"⚠️ Warning: Could not install {package}")
                    print(f"   Error: {result.stderr[:200]}")
                    failed_installs.append(package)
                    
            except subprocess.TimeoutExpired:
                print(f"⚠️ Timeout installing {package}")
                failed_installs.append(package)
            except Exception as e:
                print(f"⚠️ Error installing {package}: {e}")
                failed_installs.append(package)
    
    print(f"\\n📊 Installation Summary:")
    print(f"✅ Successfully installed/verified: {successful_installs}")
    print(f"⚠️ Failed installations: {len(failed_installs)}")
    
    if failed_installs:
        print(f"Failed packages: {', '.join(failed_installs)}")
        print("\\n💡 You may need to install these manually")
    
    return len(failed_installs) == 0

def build_fixed_executable():
    """Build the executable with all fixes applied"""
    
    print("🔧 Applying fixes...")
    
    # Step 1: Create safe launcher
    launcher_file = create_safe_launcher()
    
    # Step 2: Create spec file
    spec_file = create_pyinstaller_spec()
    
    # Step 3: Fix main window
    fix_main_window()
    
    # Step 4: Install ALL dependencies
    if not install_all_dependencies():
        print("⚠️ Some dependencies failed to install, but continuing with build...")
    
    # Step 5: Clean previous builds
    for dir_name in ['build', 'dist', '__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 Cleaned {dir_name}")
    
    # Step 6: Build with spec file
    print("🚀 Building executable...")
    print("This may take 5-15 minutes...")
    
    cmd = [sys.executable, '-m', 'PyInstaller', '--clean', spec_file]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        
        # Verify the build
        exe_path = Path('dist/AlbumVisionPlus.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"📁 Executable: {exe_path.absolute()}")
            print(f"📏 Size: {size_mb:.1f} MB")
            return True
        else:
            print("❌ Executable not found after build!")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("Error:", e.stderr)
        return False

def create_user_guide():
    """Create a simple user guide with proper encoding"""
    
    guide_content = '''Album Vision+ - User Guide

INSTALLATION:
1. Extract all files to a folder
2. Double-click AlbumVisionPlus.exe to start

USAGE:
1. Click "Import" or drag & drop a folder with images
2. The AI will automatically categorize your images
3. Use tag buttons to filter by category
4. Click "Export" to save organized images

TROUBLESHOOTING:
- If the app doesn't start, try running as administrator
- If multiple instances appear, close all and restart
- For performance issues, close other applications

FEATURES:
- AI-powered image classification
- Duplicate image detection  
- Image quality analysis
- Batch operations
- Smart organization

For support, contact the developer.
'''
    
    try:
        # Create dist directory if it doesn't exist
        os.makedirs('dist', exist_ok=True)
        
        # Use UTF-8 encoding to handle special characters
        with open('dist/User_Guide.txt', 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        print("✅ Created User_Guide.txt")
        return True
    except Exception as e:
        print(f"⚠️ Could not create user guide: {e}")
        return False

def create_distribution_package():
    """Create a complete distribution package"""
    
    exe_path = Path('dist/AlbumVisionPlus.exe')
    if not exe_path.exists():
        return False
    
    print("📦 Creating distribution package...")
    
    # Create a readme for the executable
    readme_content = '''Album Vision+ - Smart Image Organization

QUICK START:
1. Double-click AlbumVisionPlus.exe to launch
2. No installation required - this is a standalone executable
3. Import images using the Import button or drag & drop

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- At least 4GB RAM recommended
- 1GB free disk space

FEATURES:
- AI-powered image classification using YOLO
- Automatic image organization by category
- Duplicate image detection
- Image quality analysis
- Batch processing capabilities

TROUBLESHOOTING:
- If Windows shows a security warning, click "More info" then "Run anyway"
- If the app fails to start, try running as administrator
- For best performance, close other heavy applications

Contact the developer for support or feature requests.
'''
    
    try:
        with open('dist/README.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Created README.txt")
    except Exception as e:
        print(f"⚠️ Could not create README: {e}")
    
    return True

def main():
    """Main build process"""
    print("=" * 60)
    print("🛠️  ALBUM VISION+ COMPLETE FIXED BUILDER")
    print("   (Includes ALL dependencies & prevents background processes)")
    print("=" * 60)
    
    # Check requirements
    if not os.path.exists('app'):
        print("❌ 'app' directory not found! Run from project root.")
        return 1
    
    if not os.path.exists('app/gui/main_window.py'):
        print("❌ main_window.py not found!")
        return 1
    
    print("✅ Found required project files")
    
    # Build the executable
    if build_fixed_executable():
        create_user_guide()
        create_distribution_package()
        
        print("\\n🎉 SUCCESS! Complete executable created!")
        print("\\n📋 SHARING CHECKLIST:")
        print("✅ AlbumVisionPlus.exe - Main executable")
        print("✅ User_Guide.txt - User instructions")
        print("✅ README.txt - Quick start guide")
        print("\\n💡 The complete version should:")
        print("- Include ALL required dependencies")
        print("- Not create multiple background processes")
        print("- Close properly when window is closed")
        print("- Prevent multiple instances")
        print("- Work on any Windows 10/11 computer")
        
        # Final size check
        exe_path = Path('dist/AlbumVisionPlus.exe')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\\n📏 Final executable size: {size_mb:.1f} MB")
            if size_mb > 500:
                print("⚠️ Large file size - consider using --onedir for faster startup")
        
        return 0
    else:
        print("\\n❌ Build failed! Check the errors above.")
        print("\\n🔧 Try these solutions:")
        print("1. Ensure you have a stable internet connection")
        print("2. Check if you have enough disk space (need ~3GB)")
        print("3. Try running as administrator")
        print("4. Install dependencies manually: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    # Prevent multiprocessing issues during build
    multiprocessing.freeze_support()
    exit(main())