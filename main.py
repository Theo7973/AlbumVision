"""
Main entry point for the AlbumVision application.
This script initializes the application, shows the intro splash,
downloads models, then opens the main window.
"""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication

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

    # Create the Qt app ONCE
    app = QApplication(sys.argv)

    # Paths to assets next to this file (adjust if yours differ)
    project_root = Path(__file__).resolve().parent
    logo_path = project_root / "resources" / "images" / "albumvision_logo.png"
    gif_path  = project_root / "resources" / "animations" / "intro.gif"

    # Use the IntroSplash you defined in app.gui.main_window
    from app.gui.main_window import IntroSplash, ImageWindow

    # Intro splash (shows immediately)
    splash = IntroSplash(str(logo_path), str(gif_path) if gif_path.exists() else None)
    splash.start(2000)                 # keep visible for ~2 seconds
    QGuiApplication.processEvents()    # paint right away

    # Do your setup (models) while splash is up
    from app.utils.model_downloader import download_models
    download_models()

    # Create main window but don't show yet
    window = ImageWindow()
    window.setWindowTitle("Album Vision+")

    # Show main AFTER the splash duration, then finish the splash
    QTimer.singleShot(2000, lambda: (window.show(), splash.finish(window)))

    # Event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
