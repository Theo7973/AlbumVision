import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from app.gui.export_widget import ExportWidget

# Create test application
app = QApplication(sys.argv)

# Create and show widget
widget = ExportWidget()
widget.show()

print("Export widget created. Click the button to test folder creation.")
sys.exit(app.exec())