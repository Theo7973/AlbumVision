from PySide6.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from app.utils.path_settings import PathSettings

class PathSelectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.path_settings = PathSettings()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Input path section
        input_layout = QHBoxLayout()
        self.input_label = QLabel(f"Input Path: {self.path_settings.get_input_path()}")
        self.input_button = QPushButton("Select Input Directory")
        self.input_button.clicked.connect(self.select_input_path)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_button)
        
        # Output path section
        output_layout = QHBoxLayout()
        self.output_label = QLabel(f"Output Path: {self.path_settings.get_output_path()}")
        self.output_button = QPushButton("Select Output Directory")
        self.output_button.clicked.connect(self.select_output_path)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_button)
        
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        
        self.setLayout(layout)
    
    def select_input_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.path_settings.set_input_path(directory)
            self.input_label.setText(f"Input Path: {directory}")
    
    def select_output_path(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.path_settings.set_output_path(directory)
            self.output_label.setText(f"Output Path: {directory}")