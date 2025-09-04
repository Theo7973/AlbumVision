import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QCheckBox, QPushButton, QProgressBar, QMessageBox, QFrame, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# Fallback path settings if import fails
try:
    from app.utils.path_settings import PathSettings
except ImportError:
    class PathSettings:
        def __init__(self):
            self.settings = {}
        def get_output_path(self):
            return ""
        def set_output_path(self, path):
            self.settings["output_path"] = path
            return True

# Thread for calculating storage usage
class StorageCalculatorThread(QThread):
    finished = Signal(dict)
    def __init__(self, image_dir):
        super().__init__()
        self.image_dir = image_dir
    def run(self):
        try:
            if not self.image_dir or not os.path.exists(self.image_dir):
                self.finished.emit({"error": "No directory loaded"})
                return
            total_size = 0
            file_count = 0
            for root, dirs, files in os.walk(self.image_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                        try:
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
            if total_size < 1024:
                size_str = f"{total_size} B"
            elif total_size < 1024**2:
                size_str = f"{total_size/1024:.1f} KB"
            elif total_size < 1024**3:
                size_str = f"{total_size/(1024**2):.1f} MB"
            else:
                size_str = f"{total_size/(1024**3):.1f} GB"
            self.finished.emit({"total_size": total_size, "size_str": size_str, "file_count": file_count})
        except Exception as e:
            self.finished.emit({"error": str(e)})

# Main SettingsDialog
class SettingsDialog(QDialog):
    darkModeToggled = Signal(bool)  # Signal for dark mode changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(450, 550)
        self.parent_window = parent

        # Use parent's PathSettings if exists
        if hasattr(parent, 'path_settings'):
            self.path_settings = parent.path_settings
        else:
            self.path_settings = PathSettings()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title = QLabel("Album Vision+ Settings")
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Appearance group
        self.create_theme_group(layout)
        # Storage group
        self.create_storage_group(layout)
        # Auto-category group
        self.create_auto_category_group(layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Bottom buttons
        self.create_bottom_buttons(layout)

    def create_theme_group(self, parent_layout):
        group = QGroupBox("Appearance")
        v_layout = QVBoxLayout(group)
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Theme:"))

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Auto"])
        self.theme_combo.setCurrentText("Dark Theme")
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        h_layout.addWidget(self.theme_combo)
        h_layout.addStretch()
        v_layout.addLayout(h_layout)
        parent_layout.addWidget(group)

    def create_storage_group(self, parent_layout):
        group = QGroupBox("Storage Management")
        v_layout = QVBoxLayout(group)

        self.storage_label = QLabel("Calculating storage usage...")
        v_layout.addWidget(self.storage_label)

        self.storage_progress = QProgressBar()
        self.storage_progress.setRange(0, 0)
        v_layout.addWidget(self.storage_progress)

        # Output path row
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("Output Path:"))
        current_path = self.path_settings.get_output_path()
        self.output_path_label = QLabel(current_path if current_path else "Not set")
        path_row.addWidget(self.output_path_label)
        path_row.addStretch()

        change_btn = QPushButton("Change")
        change_btn.clicked.connect(self.change_output_path)
        change_btn.setMaximumWidth(80)
        path_row.addWidget(change_btn)

        v_layout.addLayout(path_row)
        parent_layout.addWidget(group)
        self.calculate_storage()

    def create_auto_category_group(self, parent_layout):
        group = QGroupBox("Auto-Categorization")
        v_layout = QVBoxLayout(group)

        self.auto_cb = QCheckBox("Enable automatic image categorization")
        self.auto_cb.setChecked(True)
        v_layout.addWidget(self.auto_cb)

        conf_row = QHBoxLayout()
        conf_row.addWidget(QLabel("Confidence threshold:"))
        self.confidence_combo = QComboBox()
        self.confidence_combo.addItems(["Low (0.3)", "Medium (0.5)", "High (0.7)"])
        self.confidence_combo.setCurrentText("Medium (0.5)")
        conf_row.addWidget(self.confidence_combo)
        conf_row.addStretch()
        v_layout.addLayout(conf_row)
        parent_layout.addWidget(group)

    def create_bottom_buttons(self, parent_layout):
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setDefault(True)
        h_layout.addWidget(reset_btn)
        h_layout.addWidget(cancel_btn)
        h_layout.addWidget(apply_btn)
        parent_layout.addLayout(h_layout)

    def calculate_storage(self):
        if hasattr(self.parent_window, 'image_dir') and self.parent_window.image_dir:
            self.thread = StorageCalculatorThread(self.parent_window.image_dir)
            self.thread.finished.connect(self.on_storage_calculated)
            self.thread.start()
        else:
            self.storage_label.setText("No directory loaded")
            self.storage_progress.hide()

    def on_storage_calculated(self, result):
        self.storage_progress.hide()
        if "error" in result:
            self.storage_label.setText(f"Storage: {result['error']}")
        else:
            self.storage_label.setText(f"Current folder: {result['size_str']} ({result['file_count']} images)")

    def change_output_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Directory", os.path.expanduser("~"))
        if folder:
            if self.path_settings.set_output_path(folder):
                self.output_path_label.setText(folder)
                QMessageBox.information(self, "Path Updated", f"Output path updated to:\n{folder}")

    def on_theme_changed(self, text):
        self.darkModeToggled.emit(text.lower().startswith("dark"))

    def reset_to_defaults(self):
        self.theme_combo.setCurrentText("Dark Theme")
        self.auto_cb.setChecked(True)
        self.confidence_combo.setCurrentText("Medium (0.5)")
        QMessageBox.information(self, "Settings Reset", "All settings have been reset to defaults.")

    def apply_settings(self):
        settings = {
            "theme": self.theme_combo.currentText(),
            "auto_categorization": self.auto_cb.isChecked(),
            "confidence": self.confidence_combo.currentText(),
            "output_path": self.path_settings.get_output_path()
        }
        print(f"Applying settings: {settings}")
        if self.parent_window and hasattr(self.parent_window, 'apply_theme'):
            self.parent_window.apply_theme(settings["theme"].lower())
        QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
        self.accept()
