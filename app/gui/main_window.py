from PySide6.QtWidgets import QMainWindow, QLabel 
class MainWindow(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("AlbumVision") 
        self.setGeometry(100, 100, 800, 600) 
        label = QLabel("AlbumVision - Loading...") 
        self.setCentralWidget(label) 
