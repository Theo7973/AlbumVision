#!/usr/bin/env python3
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
