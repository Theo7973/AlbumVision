"""
    Main entry point for the AlbumVision application.
    This script initializes the application, sets up the main window.
"""
import sys 
import os 
from pathlib import Path 
def ensure_directories(): 
    directories = [ 
        'data/test_images', 
        'models', 
        'user_data/thumbnails', 
        'user_data/cache', 
        'user_data/analytics', 
        'user_data/exports' 
    ] 
    for directory in directories: 
        Path(directory).mkdir(parents=True, exist_ok=True) 
def main(): 
    ensure_directories() 
    from app.utils.model_downloader import download_models 
    download_models() 
    try: 
        from PySide6.QtWidgets import QApplication 
        from app.gui.main_window import ImageWindow 
        image_directory = r".\data\test_images"  # Replace with your directory path
        app = QApplication(sys.argv) # Create the application instance
        window = ImageWindow(image_directory) # Create the main window instance
        window.setWindowTitle("Album Vision+")   # Set the window title
        window.show() 
        sys.exit(app.exec())  # Start the application event loop
    except ImportError: 
        pass 
if __name__ == "__main__": 
    main() 
