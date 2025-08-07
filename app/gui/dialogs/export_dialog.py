"""
Final Enhanced Export Dialog for Album Vision+
Includes folder preview, category management, and export functionality
FIXED to work with PathSettings properly
"""
from PySide6.QtWidgets import (QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, 
                              QSpacerItem, QSizePolicy, QMessageBox, QFileDialog, QProgressBar,
                              QGroupBox, QListWidget, QLineEdit, QCheckBox, QTextEdit)
from PySide6.QtCore import Qt, QThread, Signal
import sys
import os
import shutil
from ultralytics import YOLO
model = YOLO("yolov8n.pt")

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

try:
    from app.utils.folder_manager import create_output_folders
    from app.utils.path_settings import PathSettings
    from app.utils.image_quality import check_image_quality
    from app.utils import get_all_files_in_directory
except ImportError as e:
    print(f"Import error in export_dialog: {e}")
    # Create fallback functions
    def create_output_folders(categories, output_path):
        for category in categories:
            folder_path = os.path.join(output_path, category)
            os.makedirs(folder_path, exist_ok=True)
        return [os.path.join(output_path, cat) for cat in categories]
    
    
    class DummyGetAllFiles:
        @staticmethod
        def get_all_files_in_directory(path):
            if not os.path.exists(path):
                return []
            files = []
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    files.append(file_path)
            return files
    
    get_all_files_in_directory = DummyGetAllFiles()
    
    class PathSettings:
        def __init__(self):
            self.json_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            os.makedirs(self.json_dir, exist_ok=True)
            self.settings_file = os.path.join(self.json_dir, 'settings.json')
            self.output_path = ""
        def get_output_path(self):
            return self.output_path
        def set_output_path(self, path):
            self.output_path = path
            return True

import json
import shutil
from datetime import datetime

class FolderPreviewWidget(QGroupBox):
    """Widget for previewing and managing export categories"""
    def __init__(self, parent=None):
        super().__init__("Category Folders Preview", parent)
        # Match categories to the UI radio buttons
        self.categories = ["Animal", "Appliance", "Cat", "Dog", 
                          "Entertainment_Device", "Kitchenware", 
                          "Person", "Vehicle", "Unknown"]
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # List widget to show folders
        self.folder_list = QListWidget()
        self.folder_list.addItems(self.categories)
        self.folder_list.setMaximumHeight(150)
        layout.addWidget(self.folder_list)
        
        # Add category section
        add_layout = QHBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("New category name")
        add_layout.addWidget(self.category_input)
        
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_category)
        add_layout.addWidget(self.add_button)
        
        layout.addLayout(add_layout)
        
        # Remove category button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_category)
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
        self.setMaximumHeight(250)
    
    def add_category(self):
        """Add a new category to the list."""
        new_category = self.category_input.text().strip()
        if new_category and new_category not in self.categories:
            self.categories.append(new_category)
            self.folder_list.addItem(new_category)
            self.category_input.clear()
            print(f"Added category: {new_category}")
    
    def remove_category(self):
        """Remove the selected category from the list."""
        current_item = self.folder_list.currentItem()
        if current_item:
            category = current_item.text()
            self.categories.remove(category)
            self.folder_list.takeItem(self.folder_list.row(current_item))
            print(f"Removed category: {category}")
    
    def get_categories(self):
        """Return the list of categories."""
        return self.categories

class ExportWorker(QThread):
    """Worker thread for handling export operations"""
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, source_dir, output_path, categories):
        super().__init__()
        self.source_dir = source_dir
        self.output_path = output_path
        self.categories = categories


   
        
    def run(self):
        """Run the export process in a separate thread, sorting images by YOLO-detected category."""
        try:
            # Get all image files
            all_files = get_all_files_in_directory.get_all_files_in_directory(self.source_dir)
            image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]

            if not image_files:
                self.error.emit("No image files found in the source directory.")
                return

            self.status.emit(f"Found {len(image_files)} images to process...")

            # Mapping from YOLO/coco label to your custom category
            mapping = {
                "person": "Person",
                "cat": "Cat",
                "dog": "Dog",
                "car": "Vehicle",
                "bus": "Vehicle",
                "truck": "Vehicle",
                "bicycle": "Vehicle",
                "motorcycle": "Vehicle",
                "airplane": "Vehicle",
                "train": "Vehicle",
                "knife": "Kitchenware",
                "fork": "Kitchenware",
                "spoon": "Kitchenware",
                "bowl": "Kitchenware",
                "refrigerator": "Appliance",
                "microwave": "Appliance",
                "oven": "Appliance",
                "toaster": "Appliance",
                "tv": "Entertainment_Device",
                "laptop": "Entertainment_Device",
                "cell phone": "Entertainment_Device",
                "mouse": "Entertainment_Device",
                "keyboard": "Entertainment_Device",
                "remote": "Entertainment_Device",
                "bear": "Animal",
                "zebra": "Animal",
                "elephant": "Animal",
                "sheep": "Animal",
                "cow": "Animal",
                "horse": "Animal",
                "bird": "Animal",
                "giraffe": "Animal"
            }

            def map_coco_label_to_custom_tag(label):
                return mapping.get(label.lower(), "Unknown")

            stats = {
                'processed': 0,
                'errors': 0,
                'by_category': {}
            }

            for i, img_path in enumerate(image_files):
                self.status.emit(f"Processing {os.path.basename(img_path)}...")

                # --- YOLO detection ---
                try:
                    results = model(img_path, verbose=False)
                    detected_labels = []
                    if results and results[0].boxes:
                        for box in results[0].boxes:
                            cls_id = int(box.cls[0])
                            coco_label = model.names[cls_id]
                            mapped = map_coco_label_to_custom_tag(coco_label)
                            if mapped != "Unknown":
                                detected_labels.append(mapped)
                    # If more than one known item detected, use the first one (ignore Unknown)
                    if detected_labels:
                        target_category = detected_labels[0]
                    else:
                        target_category = "Unknown"
                except Exception as e:
                    print(f"YOLO error on {img_path}: {e}")
                    target_category = "Unknown"

                # Update category stats
                if target_category not in stats['by_category']:
                    stats['by_category'][target_category] = 0
                stats['by_category'][target_category] += 1

                # Create target folder if it doesn't exist
                target_folder = os.path.join(self.output_path, target_category)
                os.makedirs(target_folder, exist_ok=True)

                # Copy the image to the target folder
                filename = os.path.basename(img_path)
                target_path = os.path.join(target_folder, filename)

                try:
                    shutil.copy2(img_path, target_path)
                    stats['processed'] += 1
                except Exception as e:
                    print(f"Error copying {img_path}: {e}")
                    stats['errors'] += 1

                # Update progress
                progress_percent = int((i + 1) / len(image_files) * 100)
                self.progress.emit(progress_percent)

            self.finished.emit(stats)

        except Exception as e:
            self.error.emit(str(e))

class ExportDialog(QDialog):
    def __init__(self, parent=None, source_directory=None):
        super().__init__(parent)
        self.setWindowTitle("Export Images")
        self.setFixedSize(600, 650)
        
        # Initialize PathSettings - CRITICAL: Use the SAME class as main window
        print("=== EXPORT DIALOG INITIALIZATION ===")
        try:
            self.path_settings = PathSettings()
            current_path = self.path_settings.get_output_path()
            print(f"Export dialog PathSettings file: {getattr(self.path_settings, 'settings_file', 'Unknown')}")
            print(f"Export dialog loaded output path: '{current_path}'")
            self.output_path = current_path or ""
        except Exception as e:
            print(f"Error initializing PathSettings in export dialog: {e}")
            self.path_settings = None
            self.output_path = ""
        
        self.source_directory = source_directory or ""
        self.export_worker = None
        
        print(f"Export dialog initialized with:")
        print(f"  Source directory: '{self.source_directory}'")
        print(f"  Output path: '{self.output_path}'")
        print("=====================================")

        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Source directory display
        source_group = QGroupBox("Source Directory")
        source_layout = QVBoxLayout()
        self.source_label = QLabel(f"From: {self.source_directory if self.source_directory else 'No source selected'}")
        self.source_label.setWordWrap(True)
        source_layout.addWidget(self.source_label)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)

        # Output path section
        output_group = QGroupBox("Output Destination")
        output_layout = QVBoxLayout()
        
        self.path_label = QLabel("Export to: " + (self.output_path if self.output_path else "No output path set"))
        self.path_label.setWordWrap(True)
        output_layout.addWidget(self.path_label)
        
        browse_button = QPushButton("Browse Output Folder...")
        browse_button.clicked.connect(self.browse_output_path)
        output_layout.addWidget(browse_button)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Folder preview widget
        self.folder_preview = FolderPreviewWidget()
        layout.addWidget(self.folder_preview)
        

        # Progress section (initially hidden)
        self.progress_group = QGroupBox("Export Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setVisible(False)
        progress_layout.addWidget(self.status_label)
        
        self.progress_group.setLayout(progress_layout)
        self.progress_group.setVisible(False)
        layout.addWidget(self.progress_group)

        # Add spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons at the bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel", self)
        self.ok_button = QPushButton("Export", self)
        
        # Style the export button
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.start_export)
        self.cancel_button.clicked.connect(self.cancel_export)

    def set_output_path(self, path):
        """Method to set output path externally (called from main window)"""
        print(f"Export dialog: set_output_path called with '{path}'")
        self.output_path = path
        if hasattr(self, 'path_label'):
            self.path_label.setText(f"Export to: {path}")
        print(f"Export dialog output path updated to: '{self.output_path}'")

    def refresh_output_path(self):
        """Refresh output path from PathSettings"""
        if self.path_settings:
            try:
                # Reload settings to get latest data
                self.path_settings.settings = self.path_settings.load_settings()
                fresh_path = self.path_settings.get_output_path()
                print(f"Refreshed output path: '{fresh_path}'")
                if fresh_path:
                    self.set_output_path(fresh_path)
                return fresh_path
            except Exception as e:
                print(f"Error refreshing output path: {e}")
        return self.output_path

    def browse_output_path(self):
        """Open file dialog to select output directory"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        
        if folder_path:
            self.output_path = folder_path
            self.path_label.setText(f"Export to: {folder_path}")
            # Save the path immediately if path_settings is available
            if self.path_settings:
                success = self.path_settings.set_output_path(folder_path)
                print(f"Saved new output path via browse: {success}")

    def start_export(self):
        """Start the export process"""
        print("=== STARTING EXPORT ===")
        
        # Refresh output path one more time before validation
        current_path = self.refresh_output_path()
        print(f"Final output path check: '{current_path}'")
        
        # Validation
        if not self.source_directory:
            QMessageBox.warning(self, "No Source", "No source directory specified.")
            return
            
        if not self.output_path or self.output_path.strip() == "":
            QMessageBox.warning(self, "No Output Path", 
                               f"Please select an output directory.\nCurrent path: '{self.output_path}'")
            return
            
        if not os.path.exists(self.source_directory):
            QMessageBox.warning(self, "Invalid Source", "Source directory does not exist.")
            return

        # Show progress section
        self.progress_group.setVisible(True)
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Disable buttons during export
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Exporting...")

        # Get categories from preview widget
        categories = self.folder_preview.get_categories()
        
        print(f"Starting export with:")
        print(f"  Source: {self.source_directory}")
        print(f"  Output: {self.output_path}")
        print(f"  Categories: {categories}")
        
        # Start export worker thread
        self.export_worker = ExportWorker(
            self.source_directory,
            self.output_path,
            categories
        )
        
        # Connect worker signals
        self.export_worker.progress.connect(self.update_progress)
        self.export_worker.status.connect(self.update_status)
        self.export_worker.finished.connect(self.export_finished)
        self.export_worker.error.connect(self.export_error)
        
        # Start the worker
        self.export_worker.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def update_status(self, message):
        """Update status label"""
        self.status_label.setText(message)

    def export_finished(self, stats):
        """Handle successful export completion"""
        # Save export configuration
        self.save_export_config(stats)
        
        # Show completion message
        message = f"Export completed successfully!\n\n"
        message += f"Processed: {stats['processed']} images\n"
        if stats['errors'] > 0:
            message += f"Errors: {stats['errors']}\n"
        message += f"\nExported to: {self.output_path}"
        
        QMessageBox.information(self, "Export Complete", message)
        self.accept()

    def export_error(self, error_message):
        """Handle export errors"""
        QMessageBox.critical(self, "Export Error", f"Error during export:\n{error_message}")
        self.reset_ui()

    def cancel_export(self):
        """Cancel the export process"""
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "Cancel Export", 
                "Export is in progress. Are you sure you want to cancel?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.export_worker.terminate()
                self.export_worker.wait()
                self.reset_ui()
                self.reject()
        else:
            self.reject()

    def reset_ui(self):
        """Reset UI to initial state"""
        self.ok_button.setEnabled(True)
        self.ok_button.setText("Export")
        self.progress_group.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)

    def save_export_config(self, stats):
        """Save export configuration and statistics to JSON"""
        try:
            json_dir = os.path.join(os.path.expanduser("~"), "Desktop")
            os.makedirs(json_dir, exist_ok=True)
            config_path = os.path.join(json_dir, 'export_log.json')
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "source_directory": self.source_directory,
                "output_path": self.output_path,
                "categories": self.folder_preview.get_categories(),
                "statistics": stats
            }
            
            # Load existing log or create new one
            log_data = []
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        log_data = json.load(f)
                except:
                    log_data = []
            
            # Add new export entry
            log_data.append(export_data)
            
            # Keep only last 50 exports
            if len(log_data) > 50:
                log_data = log_data[-50:]
            
            with open(config_path, 'w') as f:
                json.dump(log_data, f, indent=4)
                
            print(f"Export log saved to: {config_path}")
        except Exception as e:
            print(f"Error saving export log: {e}")

    def get_output_path(self):
        """Return the output path"""
        return self.output_path

    def set_source_directory(self, directory):
        """Set the source directory"""
        self.source_directory = directory
        self.source_label.setText(f"From: {directory}")

    def showEvent(self, event):
        """Called when dialog is shown - refresh the output path"""
        super().showEvent(event)
        print("Export dialog shown - refreshing output path")
        self.refresh_output_path()

    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.export_worker and self.export_worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "Export in Progress", 
                "Export is still running. Close anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.export_worker.terminate()
                self.export_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()