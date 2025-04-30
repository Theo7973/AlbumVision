# AlbumVision Main Application Entry Point 
import sys 
import os 
from pathlib import Path 
 
# Ensure all directories exist 
def ensure_directories(): 
    """Create necessary directories if they don't exist.""" 
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
    # Ensure all required directories exist 
    ensure_directories() 
 
    # Download models if needed 
    from app.utils.model_downloader import download_models 
    download_models() 
 
    # Import PyQt components here to avoid importing before model download 
    try: 
        from PyQt6.QtWidgets import QApplication 
        from app.gui.main_window import MainWindow 
 
        app = QApplication(sys.argv) 
        window = MainWindow() 
        window.show() 
        sys.exit(app.exec()) 
    except ImportError as e: 
        print(f"Failed to import GUI components: {e}") 
        print("Make sure PyQt6 is installed: pip install PyQt6") 
 
if __name__ == "__main__": 
    main() 
