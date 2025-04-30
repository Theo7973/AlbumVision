from PyQt6.QtWidgets import QMainWindow, QLabel 
 
class MainWindow(QMainWindow): 
    """Main application window.""" 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("AlbumVision") 
        self.setGeometry(100, 100, 800, 600) 
 
        # Placeholder label 
        label = QLabel("AlbumVision - Loading...") 
        self.setCentralWidget(label) 
