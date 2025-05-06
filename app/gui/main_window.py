from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from app.gui.widgets.path_selection import PathSelectionWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlbumVision")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Add path selection widget
        self.path_widget = PathSelectionWidget()
        layout.addWidget(self.path_widget)
        
        # We can add more widgets as needed here...
