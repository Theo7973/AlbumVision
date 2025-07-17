#!/usr/bin/env python3
"""
Album Vision+ Main Launcher
Entry point for the Album Vision+ application
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the main application
try:
    from app.gui.widgets.main_window import ImageWindow
    from PySide6.QtWidgets import QApplication
    
    def main():
        """Main application entry point"""
        # Create the application instance
        app = QApplication(sys.argv)
        
        # Set application properties
        app.setApplicationName("Album Vision+")
        app.setApplicationDisplayName("Album Vision+ - Smart Image Organization")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("AlbumVision Team")
        
        # Create the main window instance with default directory
        default_image_directory = os.path.join(os.path.dirname(__file__), "data", "test_images")
        if not os.path.exists(default_image_directory):
            default_image_directory = os.path.expanduser("~/Pictures")  # Fallback to user Pictures
        
        window = ImageWindow(default_image_directory)
        
        # Set the window title
        window.setWindowTitle("Album Vision+ - Smart Image Organization")
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec())

    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)
except Exception as e:
    print(f"Application error: {e}")
    sys.exit(1)
