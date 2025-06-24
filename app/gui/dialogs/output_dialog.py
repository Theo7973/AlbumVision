from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox,
                             QGroupBox, QListWidget, QCheckBox, QTextEdit, QComboBox)
from PySide6.QtCore import Qt
from ...utils.path_settings import PathSettings
import os
import json
from datetime import datetime

class OutputPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Output Path")
        self.setFixedSize(700, 450)
        self.path_settings = PathSettings()
        
        # Get the current output path from settings
        self.current_path = self.path_settings.get_output_path() or ""
        self.path_history = self.load_path_history()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the complete UI for the output path dialog"""
        layout = QVBoxLayout(self)

        # Current path display section
        current_group = QGroupBox("Current Output Path")
        current_layout = QVBoxLayout()
        
        if self.current_path:
            self.current_label = QLabel(f"Currently set to: {self.current_path}")
            self.current_label.setWordWrap(True)
            self.current_label.setStyleSheet("font-weight: bold; color: #006400;")
        else:
            self.current_label = QLabel("No output path currently set")
            self.current_label.setStyleSheet("font-weight: bold; color: #CC0000;")
        
        current_layout.addWidget(self.current_label)
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)

        # Path selection section
        selection_group = QGroupBox("Select New Output Path")
        selection_layout = QVBoxLayout()

        # Path input with browse button
        path_input_layout = QHBoxLayout()
        self.path_label = QLabel("Enter the output path:", self)
        path_input_layout.addWidget(self.path_label)
        
        self.path_input = QLineEdit(self)
        self.path_input.setText(self.current_path)
        self.path_input.setPlaceholderText("Enter path or click Browse...")
        path_input_layout.addWidget(self.path_input)
        
        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.clicked.connect(self.open_folder_dialog)
        path_input_layout.addWidget(self.browse_button)
        
        selection_layout.addLayout(path_input_layout)

        # Quick access buttons for common locations
        quick_access_layout = QHBoxLayout()
        quick_access_layout.addWidget(QLabel("Quick Access:"))
        
        desktop_btn = QPushButton("Desktop")
        desktop_btn.clicked.connect(lambda: self.set_quick_path("Desktop"))
        quick_access_layout.addWidget(desktop_btn)
        
        documents_btn = QPushButton("Documents")
        documents_btn.clicked.connect(lambda: self.set_quick_path("Documents"))
        quick_access_layout.addWidget(documents_btn)
        
        pictures_btn = QPushButton("Pictures")
        pictures_btn.clicked.connect(lambda: self.set_quick_path("Pictures"))
        quick_access_layout.addWidget(pictures_btn)
        
        quick_access_layout.addStretch()
        selection_layout.addLayout(quick_access_layout)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Path history section
        if self.path_history:
            history_group = QGroupBox("Recent Paths")
            history_layout = QVBoxLayout()
            
            history_label = QLabel("Select from recently used paths:")
            history_layout.addWidget(history_label)
            
            self.history_list = QListWidget()
            self.history_list.setMaximumHeight(100)
            
            for path_entry in self.path_history[-10:]:  # Show last 10 entries
                display_text = f"{path_entry['path']} (used {path_entry['date']})"
                self.history_list.addItem(display_text)
            
            self.history_list.itemDoubleClicked.connect(self.select_from_history)
            history_layout.addWidget(self.history_list)
            
            history_group.setLayout(history_layout)
            layout.addWidget(history_group)

        # Path validation and options
        options_group = QGroupBox("Path Options")
        options_layout = QVBoxLayout()
        
        self.create_if_missing = QCheckBox("Create directory if it doesn't exist")
        self.create_if_missing.setChecked(True)
        options_layout.addWidget(self.create_if_missing)
        
        self.validate_writable = QCheckBox("Validate write permissions")
        self.validate_writable.setChecked(True)
        options_layout.addWidget(self.validate_writable)
        
        self.add_to_history = QCheckBox("Add to path history")
        self.add_to_history.setChecked(True)
        options_layout.addWidget(self.add_to_history)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Path info display
        self.info_group = QGroupBox("Path Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(80)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        self.info_group.setLayout(info_layout)
        layout.addWidget(self.info_group)

        # Connect path input to validation
        self.path_input.textChanged.connect(self.validate_path_realtime)

        # Add spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons at bottom
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_to_default)
        button_layout.addWidget(self.reset_button)
        
        # Clear history button
        if self.path_history:
            self.clear_history_button = QPushButton("Clear History")
            self.clear_history_button.clicked.connect(self.clear_path_history)
            button_layout.addWidget(self.clear_history_button)
        
        # Cancel and Save buttons
        self.cancel_button = QPushButton("Cancel")
        self.save_button = QPushButton("Save")
        
        # Style the save button
        self.save_button.setStyleSheet("""
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
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.save_button.clicked.connect(self.save_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        # Initial validation
        self.validate_path_realtime()

    def open_folder_dialog(self):
        """Open file dialog to select a folder"""
        # Start from current path if it exists, otherwise use home directory
        start_dir = self.current_path if os.path.exists(self.current_path) else os.path.expanduser("~")
        
        folder_path = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Directory",
            start_dir
        )
        
        if folder_path:
            self.path_input.setText(folder_path)

    def set_quick_path(self, location):
        """Set path to common system locations"""
        if location == "Desktop":
            path = os.path.join(os.path.expanduser("~"), "Desktop", "AlbumVision_Export")
        elif location == "Documents":
            path = os.path.join(os.path.expanduser("~"), "Documents", "AlbumVision_Export")
        elif location == "Pictures":
            path = os.path.join(os.path.expanduser("~"), "Pictures", "AlbumVision_Export")
        else:
            return
            
        self.path_input.setText(path)

    def select_from_history(self, item):
        """Select a path from the history list"""
        item_text = item.text()
        # Extract path from "path (used date)" format
        path = item_text.split(" (used ")[0]
        self.path_input.setText(path)

    def validate_path_realtime(self):
        """Validate the path as user types"""
        path = self.path_input.text().strip()
        info_text = ""
        
        if not path:
            info_text = "Please enter a path"
            self.save_button.setEnabled(False)
            self.info_text.setPlainText(info_text)
            return
        
        # Check if path exists
        if os.path.exists(path):
            if os.path.isdir(path):
                info_text += "✓ Directory exists\n"
                
                # Check write permissions
                if self.validate_writable.isChecked():
                    if os.access(path, os.W_OK):
                        info_text += "✓ Write permissions OK\n"
                    else:
                        info_text += "⚠ No write permissions\n"
                
                # Show disk space info
                try:
                    stat = os.statvfs(path) if hasattr(os, 'statvfs') else None
                    if stat:
                        free_space = stat.f_bavail * stat.f_frsize / (1024**3)  # GB
                        info_text += f"💾 Free space: {free_space:.1f} GB\n"
                except:
                    pass
                    
                self.save_button.setEnabled(True)
            else:
                info_text += "❌ Path exists but is not a directory\n"
                self.save_button.setEnabled(False)
        else:
            if self.create_if_missing.isChecked():
                info_text += "📁 Directory will be created\n"
                
                # Check if parent directory exists and is writable
                parent_dir = os.path.dirname(path)
                if os.path.exists(parent_dir) and os.access(parent_dir, os.W_OK):
                    info_text += "✓ Parent directory is writable\n"
                    self.save_button.setEnabled(True)
                else:
                    info_text += "❌ Cannot create directory (parent not writable)\n"
                    self.save_button.setEnabled(False)
            else:
                info_text += "❌ Directory does not exist\n"
                self.save_button.setEnabled(False)
        
        # Show path length warning
        if len(path) > 200:
            info_text += "⚠ Path is very long (may cause issues)\n"
        
        self.info_text.setPlainText(info_text.strip())

    def save_and_accept(self):
        """Save the output path and accept the dialog - Updated version"""
        output_path = self.path_input.text().strip()
        print(f"Attempting to save output path: '{output_path}'")
        
        if not output_path:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid Path", "Please enter or select an output path.")
            return
        
        # Create directory if it doesn't exist and option is checked
        if not os.path.exists(output_path):
            if self.create_if_missing.isChecked():
                try:
                    os.makedirs(output_path)
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Directory Created", 
                                          f"Created directory: {output_path}")
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(self, "Creation Error", 
                                       f"Could not create directory: {str(e)}")
                    return
            else:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Directory Missing", 
                                   "Directory does not exist and creation is disabled.")
                return
        
        # Validate write permissions
        if self.validate_writable.isChecked():
            if not os.access(output_path, os.W_OK):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Permission Error", 
                                   "No write permissions for the selected directory.")
                return
        
        # Save to settings - this is the crucial part
        try:
            success = self.path_settings.set_output_path(output_path)
            if not success:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Save Error", "Failed to save output path to settings.")
                return
                
            print(f"Output path successfully saved: {output_path}")
            
            # Add to history if option is checked
            if self.add_to_history.isChecked():
                self.add_to_path_history(output_path)
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Path Saved", 
                                   f"Output path successfully set to:\n{output_path}")
            self.accept()
            
        except Exception as e:
            print(f"Error saving output path: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Save Error", 
                               f"Error saving output path: {e}")