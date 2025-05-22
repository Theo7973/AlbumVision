"""
Enhanced Export Dialog for Album Vision+
Includes folder preview, category management, and export functionality
"""
from PySide6.QtWidgets import (QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, 
                              QSpacerItem, QSizePolicy, QMessageBox, QFileDialog, QProgressBar,
                              QGroupBox, QListWidget, QLineEdit, QCheckBox, QTextEdit)
from PySide6.QtCore import Qt, QThread, Signal
import sys
import os

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
    
    def __init__(self, source_dir, output_path, categories, quality_check=True):
        super().__init__()
        self.source_dir = source_dir
        self.output_path = output_path
        self.categories = categories
        self.quality_check = quality_check
        
    def run(self):
        """Run the export process in a separate thread"""
        try:
            # Get all image files
            all_files = get_all_files_in_directory.get_all_files_in_directory(self.source_dir)
            image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]
            
            if not image_files:
                self.error.emit("No image files found in the source directory.")
                return
            
            self.status.emit(f"Found {len(image_files)} images to process...")
            
            # Create category folders
            folder_paths = create_output_folders(self.categories, self.output_path)
            self.status.emit(f"Created {len(folder_paths)} category folders...")
            
            # Process images
            stats = {
                'processed': 0,
                'high_quality': 0,
                'low_quality': 0,
                'errors': 0,
                'by_category': {}
            }
            
            for i, img_path in enumerate(image_files):
                self.status.emit(f"Processing {os.path.basename(img_path)}...")
                
                # Check image quality if enabled
                if self.quality_check:
                    quality, score, dimensions = check_image_quality(img_path)
                    if quality == "error":
                        stats['errors'] += 1
                        continue
                else:
                    quality = "high"  # Default to high if not checking
                
                # Determine target folder (for now, use Unknown category)
                # In a full implementation, this would use YOLO11 detection
                target_category = "Unknown"
                
                # Create subfolder structure: Category/Quality
                if quality == "high":
                    target_folder = os.path.join(self.output_path, target_category, "High_Quality")
                    stats['high_quality'] += 1
                else:
                    target_folder = os.path.join(self.output_path, target_category, "Low_Quality")
                    stats['low_quality'] += 1
                
                # Update category stats
                if target_category not in stats['by_category']:
                    stats['by_category'][target_category] = 0
                stats['by_category'][target_category] += 1
                
                # Create target folder if it doesn't exist
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
        try:
            self.path_settings = PathSettings()
        except:
            self.path_settings = None
        self.output_path = ""
        if self.path_settings:
            self.output_path = self.path_settings.get_output_path() or ""
        self.source_directory = source_directory or ""
        self.export_worker = None

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
        
        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout()
        
        self.quality_check = QCheckBox("Enable quality filtering")
        self.quality_check.setChecked(True)
        self.quality_check.setToolTip("Separate images into High_Quality and Low_Quality subfolders")
        options_layout.addWidget(self.quality_check)
        
        self.create_subfolders = QCheckBox("Create quality subfolders")
        self.create_subfolders.setChecked(True)
        self.create_subfolders.setToolTip("Create High_Quality and Low_Quality subfolders within each category")
        options_layout.addWidget(self.create_subfolders)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

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

    def browse_output_path(self):
        """Open file dialog to select output directory"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        
        if folder_path:
            self.output_path = folder_path
            self.path_label.setText(f"Export to: {folder_path}")
            # Save the path immediately if path_settings is available
            if self.path_settings:
                self.path_settings.set_output_path(folder_path)

    def start_export(self):
        """Start the export process"""
        # Validation
        if not self.source_directory:
            QMessageBox.warning(self, "No Source", "No source directory specified.")
            return
            
        if not self.output_path:
            QMessageBox.warning(self, "No Output Path", "Please select an output directory.")
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
        
        # Start export worker thread
        self.export_worker = ExportWorker(
            self.source_directory,
            self.output_path,
            categories,
            self.quality_check.isChecked()
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
        message += f"High quality: {stats['high_quality']}\n"
        message += f"Low quality: {stats['low_quality']}\n"
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
            config_path = os.path.join('data', 'export_log.json')
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "source_directory": self.source_directory,
                "output_path": self.output_path,
                "categories": self.folder_preview.get_categories(),
                "quality_check_enabled": self.quality_check.isChecked(),
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
        except Exception as e:
            print(f"Error saving export log: {e}")

    def get_output_path(self):
        """Return the output path"""
        return self.output_path

    def set_source_directory(self, directory):
        """Set the source directory"""
        self.source_directory = directory
        self.source_label.setText(f"From: {directory}")

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