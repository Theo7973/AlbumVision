# FIXED BUILD SCRIPT FOR ALBUM VISION+ WITH DB_UTILS
# Save this as: build_album_vision_plus_fixed.py

import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_proper_launcher():
    """Create a launcher that properly handles your app structure"""
    
    launcher_content = '''#!/usr/bin/env python3
"""
Album Vision+ Launcher
Entry point for Album Vision+ application
"""

import sys
import os

# Add the current directory, app directory, and app/gui directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
gui_dir = os.path.join(current_dir, 'app', 'gui')
sys.path.insert(0, current_dir)
sys.path.insert(0, app_dir)
sys.path.insert(0, gui_dir)

def main():
    """Main application entry point"""
    try:
        # Import your main window - this should now find db_utils
        from app.gui.main_window import ImageWindow
        from PySide6.QtWidgets import QApplication
        
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("Album Vision+")
        app.setApplicationDisplayName("Album Vision+ - Smart Image Organization") 
        
        # Set default image directory
        default_dir = os.path.join(current_dir, "data", "test_images")
        if not os.path.exists(default_dir):
            default_dir = os.path.expanduser("~/Pictures")
        
        # Create and show the main window
        window = ImageWindow(default_dir)
        window.setWindowTitle("Album Vision+ - Smart Image Organization")
        window.show()
        
        # Start the app
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Could not import the main window. Please check your app structure.")
        print("Current directory:", current_dir)
        print("App directory:", app_dir)
        input("Press Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open('album_vision_plus_launcher.py', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Created album_vision_plus_launcher.py")
    return 'album_vision_plus_launcher.py'

def build_album_vision_plus_fixed():
    """Build Album Vision+ with proper db_utils handling"""
    
    # Create the proper launcher
    main_file = create_proper_launcher()
    
    print(f"🚀 Building Album Vision+ from: {main_file}")
    
    # FIXED PyInstaller command with proper module handling
    cmd = [
        'pyinstaller',
        '--onefile',                      # Single executable
        '--windowed',                     # No console window
        '--name=Album Vision+',           # App name
        '--distpath=dist',                # Output directory
        '--workpath=build',               # Build directory
        '--clean',                        # Clean build
        
        # Add the entire app directory and its contents
        '--add-data=app;app',
        '--add-data=data;data',
        
        # Add other directories if they exist
        *(['--add-data=resources;resources'] if os.path.exists('resources') else []),
        *(['--add-data=models;models'] if os.path.exists('models') else []),
        *(['--add-data=user_data;user_data'] if os.path.exists('user_data') else []),
        
        # Essential hidden imports
        '--hidden-import=ultralytics',
        '--hidden-import=torch',
        '--hidden-import=torchvision',
        '--hidden-import=cv2',
        '--hidden-import=opencv-python',
        
        # PySide6 imports
        '--hidden-import=PySide6',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        
        # Other essential imports
        '--hidden-import=numpy',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=sqlite3',
        '--hidden-import=aiosqlite',
        '--hidden-import=json',
        '--hidden-import=asyncio',
        '--hidden-import=shutil',
        '--hidden-import=functools',
        
        # CRITICAL: Add db_utils explicitly with correct path
        '--hidden-import=db_utils',
        '--hidden-import=app.gui.db_utils',
        '--hidden-import=app.gui.main_window',
        '--hidden-import=app.utils.Auto_Sort_Basic',
        '--hidden-import=app.utils.file_utils',
        '--hidden-import=app.utils.image_quality',
        '--hidden-import=app.utils.path_settings',
        '--hidden-import=app.gui.widgets.yolo_results_widget',
        '--hidden-import=app.gui.widgets.path_selection',
        '--hidden-import=app.export_widget',
        '--hidden-import=app.folder_preview_widget',
        
        # Add all your dialog imports
        '--hidden-import=app.gui.dialogs.change_tag_dialog',
        '--hidden-import=app.gui.dialogs.export_dialog',
        '--hidden-import=app.gui.dialogs.import_dialog',
        '--hidden-import=app.gui.dialogs.output_dialog',
        '--hidden-import=app.gui.dialogs.search_filter',
        '--hidden-import=app.gui.dialogs.stats_dashboard',
        
        # Add categorizer imports
        '--hidden-import=app.categorizer.models',
        '--hidden-import=app.categorizer.processors',
        
        # Add database imports  
        '--hidden-import=app.database',
        
        # Add settings imports
        '--hidden-import=app.settings',
        
        # Icon if available
        *(['--icon=app/resources/icons/ab_logo.ico'] if os.path.exists('app/resources/icons/ab_logo.ico') else []),
        *(['--icon=resources/icons/ab_logo.ico'] if os.path.exists('resources/icons/ab_logo.ico') else []),
        
        # Add path for imports - include gui directory
        '--paths=app',
        '--paths=app/gui',
        '--paths=.',
        
        # Main script
        main_file
    ]
    
    print("📦 Running PyInstaller...")
    print("Command:", ' '.join(cmd))
    print("This may take 5-10 minutes...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print("STDOUT:", result.stdout[-500:])  # Show last 500 chars
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print("STDERR:", e.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout[-1000:])  # Show last 1000 chars
        return False

def verify_build():
    """Check if the build was successful"""
    exe_path = Path('dist/Album Vision+.exe')
    
    if not exe_path.exists():
        print("❌ Album Vision+.exe not found!")
        # Check if there's any .exe file in dist
        dist_path = Path('dist')
        if dist_path.exists():
            exe_files = list(dist_path.glob('*.exe'))
            if exe_files:
                print(f"Found other executables: {[f.name for f in exe_files]}")
        return False
    
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"✅ Album Vision+.exe created!")
    print(f"📁 Location: {exe_path.absolute()}")
    print(f"📏 Size: {size_mb:.1f} MB")
    return True

def main():
    """Main build process"""
    print("=" * 60)
    print("🎯 ALBUM VISION+ FIXED BUILDER (WITH DB_UTILS)")
    print("=" * 60)
    
    # Check if we're in the right directory and find db_utils
    if not os.path.exists('app'):
        print("❌ 'app' directory not found!")
        print("Please run this script from the AlbumVision root directory")
        return 1
    
    # Check for db_utils in the correct location (app/gui/)
    db_utils_path = 'app/gui/db_utils.py'
    if not os.path.exists(db_utils_path):
        print(f"❌ '{db_utils_path}' not found!")
        print("Looking for db_utils.py in other locations...")
        
        # Check other possible locations
        possible_paths = [
            'app/db_utils.py',
            'db_utils.py',
            'app/gui/db_utils.py'
        ]
        
        found = False
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ Found db_utils.py at: {path}")
                found = True
                break
        
        if not found:
            print("❌ db_utils.py not found anywhere!")
            return 1
    else:
        print(f"✅ Found db_utils.py at: {db_utils_path}")
    
    # Check Python and PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller available")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned dist directory")
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build directory")
    
    # Build the app
    if build_album_vision_plus_fixed():
        if verify_build():
            print("\n🎉 SUCCESS!")
            print("Your Album Vision+ app is ready!")
            print("Find it in: dist/Album Vision+.exe")
            print("\n💡 If you still get import errors, try:")
            print("1. Make sure all Python dependencies are installed")
            print("2. Check that db_utils.py has no syntax errors")
            print("3. Test the launcher script first: python album_vision_plus_launcher.py")
            return 0
        else:
            print("❌ Build verification failed")
            return 1
    else:
        print("❌ Build process failed")
        return 1

if __name__ == "__main__":
    exit(main())