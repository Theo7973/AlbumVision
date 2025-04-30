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
        from app.gui.main_window import MainWindow 
        app = QApplication(sys.argv) 
        window = MainWindow() 
        window.show() 
        sys.exit(app.exec()) 
    except ImportError: 
        pass 
if __name__ == "__main__": 
    main() 
