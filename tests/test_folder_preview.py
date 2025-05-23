import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from app.gui.folder_preview_widget import FolderPreviewWidget

# Create test application
app = QApplication(sys.argv)

# Create and show widget
widget = FolderPreviewWidget()
widget.setWindowTitle("Folder Preview Test")
widget.show()

print("Folder preview widget created. You can add/remove categories.")
sys.exit(app.exec())