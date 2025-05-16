from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
from app.utils.folder_manager import create_output_folders
from app.utils.path_settings import PathSettings

class ExportWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.path_settings = PathSettings()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.path_label = QLabel("Output Path: Not selected")
        layout.addWidget(self.path_label)
        
        self.export_button = QPushButton("Export and Create Folders")
        self.export_button.clicked.connect(self.handle_export)
        layout.addWidget(self.export_button)
        
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def handle_export(self):
        # Get folder path from dialog
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        
        if folder_path:
            # Save the path
            self.path_settings.set_output_path(folder_path)
            self.path_label.setText(f"Output Path: {folder_path}")
            
            # Create category folders
            categories = [
                "Animals", "Appliances", "Cats", "Dogs", 
                "Entertainment_Devices", "Kitchenware", 
                "People", "Vehicles", "Unknown"
            ]
            
            folder_paths = create_output_folders(categories, folder_path)
            
            self.status_label.setText(f"Created {len(folder_paths)} folders!")
            print(f"Folders created at: {folder_path}")