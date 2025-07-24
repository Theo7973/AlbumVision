#!/usr/bin/env python3

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
        error_msg = f"Import Error: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        sys.exit(1)
        
    except Exception as e:
        import traceback
        error_msg = f"Application Error: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(error_msg)
        sys.exit(1)

# CRITICAL: Main guard
if __name__ == "__main__":
    main()
