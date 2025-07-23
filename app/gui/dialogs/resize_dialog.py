# app/gui/dialogs/resize_dialog.py
import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, 
                               QPushButton, QGroupBox, QRadioButton, QCheckBox, 
                               QSlider, QProgressBar, QTextEdit, QFileDialog,
                               QMessageBox, QButtonGroup, QGridLayout, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

try:
    from app.utils.image_resize import ImageResizer
except ImportError:
    # Fallback if import fails
    ImageResizer = None

class ResizeWorkerThread(QThread):
    """Worker thread for resizing images to keep UI responsive"""
    progress_updated = Signal(int, int)  # current, total
    finished = Signal(dict)  # results
    
    def __init__(self, image_paths, output_folder, resize_options):
        super().__init__()
        self.image_paths = image_paths
        self.output_folder = output_folder
        self.resize_options = resize_options
        self.resizer = ImageResizer() if ImageResizer else None
    
    def run(self):
        if not self.resizer:
            self.finished.emit({"error": "Image resizer not available"})
            return
            
        def progress_callback(current, total):
            self.progress_updated.emit(current, total)
        
        results = self.resizer.batch_resize(
            self.image_paths, 
            self.output_folder, 
            self.resize_options,
            progress_callback
        )
        self.finished.emit(results)

class ResizeDialog(QDialog):
    def __init__(self, parent=None, source_directory=None):
        super().__init__(parent)
        self.setWindowTitle("Resize Images")
        self.setModal(True)
        self.resize(800, 700)
        
        self.source_directory = source_directory
        self.output_folder = ""
        self.resize_thread = None
        
        # Check if ImageResizer is available
        if not ImageResizer:
            self.show_error("Image resize functionality requires PIL/Pillow library.")
            return
            
        self.resizer = ImageResizer()
        self.setup_ui()
        
        # Load images from source directory
        if source_directory:
            self.load_source_images()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Source and Output Selection
        source_group = QGroupBox("Source & Output")
        source_layout = QGridLayout(source_group)
        
        source_layout.addWidget(QLabel("Source Folder:"), 0, 0)
        self.source_label = QLabel(self.source_directory or "No folder selected")
        source_layout.addWidget(self.source_label, 0, 1)
        
        self.browse_source_btn = QPushButton("Browse Source")
        self.browse_source_btn.clicked.connect(self.browse_source_folder)
        source_layout.addWidget(self.browse_source_btn, 0, 2)
        
        source_layout.addWidget(QLabel("Output Folder:"), 1, 0)
        self.output_label = QLabel("Click 'Set Output Folder' to choose")
        source_layout.addWidget(self.output_label, 1, 1)
        
        self.browse_output_btn = QPushButton("Set Output Folder")
        self.browse_output_btn.clicked.connect(self.browse_output_folder)
        source_layout.addWidget(self.browse_output_btn, 1, 2)
        
        layout.addWidget(source_group)
        
        # Resize Method Selection
        method_group = QGroupBox("Resize Method")
        method_layout = QVBoxLayout(method_group)
        
        self.method_button_group = QButtonGroup(self)
        
        # Percentage resize
        self.percentage_radio = QRadioButton("Resize by Percentage")
        self.percentage_radio.setChecked(True)
        self.method_button_group.addButton(self.percentage_radio, 0)
        method_layout.addWidget(self.percentage_radio)
        
        percentage_layout = QHBoxLayout()
        percentage_layout.addWidget(QLabel("Percentage:"))
        self.percentage_spin = QSpinBox()
        self.percentage_spin.setRange(1, 500)
        self.percentage_spin.setValue(80)
        self.percentage_spin.setSuffix("%")
        percentage_layout.addWidget(self.percentage_spin)
        percentage_layout.addStretch()
        method_layout.addLayout(percentage_layout)
        
        # Fixed width
        self.width_radio = QRadioButton("Resize to Fixed Width")
        self.method_button_group.addButton(self.width_radio, 1)
        method_layout.addWidget(self.width_radio)
        
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        method_layout.addLayout(width_layout)
        
        # Fixed height
        self.height_radio = QRadioButton("Resize to Fixed Height")
        self.method_button_group.addButton(self.height_radio, 2)
        method_layout.addWidget(self.height_radio)
        
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")
        height_layout.addWidget(self.height_spin)
        height_layout.addStretch()
        method_layout.addLayout(height_layout)
        
        # Max dimension
        self.max_dim_radio = QRadioButton("Resize to Maximum Dimension")
        self.method_button_group.addButton(self.max_dim_radio, 3)
        method_layout.addWidget(self.max_dim_radio)
        
        max_dim_layout = QHBoxLayout()
        max_dim_layout.addWidget(QLabel("Max Dimension:"))
        self.max_dim_spin = QSpinBox()
        self.max_dim_spin.setRange(1, 10000)
        self.max_dim_spin.setValue(1920)
        self.max_dim_spin.setSuffix(" px")
        max_dim_layout.addWidget(self.max_dim_spin)
        max_dim_layout.addStretch()
        method_layout.addLayout(max_dim_layout)
        
        layout.addWidget(method_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)
        
        self.keep_aspect_checkbox = QCheckBox("Keep Aspect Ratio")
        self.keep_aspect_checkbox.setChecked(True)
        options_layout.addWidget(self.keep_aspect_checkbox)
        
        # Quality slider
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("JPEG Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        quality_layout.addWidget(self.quality_slider)
        self.quality_label = QLabel("90%")
        quality_layout.addWidget(self.quality_label)
        options_layout.addLayout(quality_layout)
        
        # File suffix
        suffix_layout = QHBoxLayout()
        suffix_layout.addWidget(QLabel("File Suffix:"))
        self.suffix_combo = QComboBox()
        self.suffix_combo.setEditable(True)
        self.suffix_combo.addItems(["_resized", "_small", "_compressed", "_thumb", ""])
        suffix_layout.addWidget(self.suffix_combo)
        suffix_layout.addStretch()
        options_layout.addLayout(suffix_layout)
        
        layout.addWidget(options_group)
        
        # Preview
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("Select source folder and resize options to see preview")
        self.preview_label.setMinimumHeight(80)
        self.preview_label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        preview_layout.addWidget(self.preview_label)
        layout.addWidget(preview_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log area
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        log_layout.addWidget(self.log_text)
        layout.addWidget(log_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.preview_btn = QPushButton("Update Preview")
        self.preview_btn.clicked.connect(self.update_preview)
        button_layout.addWidget(self.preview_btn)
        
        button_layout.addStretch()
        
        self.start_btn = QPushButton("Start Resize")
        self.start_btn.clicked.connect(self.start_resize)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.method_button_group.buttonClicked.connect(self.update_preview)
        self.percentage_spin.valueChanged.connect(self.update_preview)
        self.width_spin.valueChanged.connect(self.update_preview)
        self.height_spin.valueChanged.connect(self.update_preview)
        self.max_dim_spin.valueChanged.connect(self.update_preview)
        self.keep_aspect_checkbox.toggled.connect(self.update_preview)
    
    def show_error(self, message):
        """Show error message and close dialog"""
        QMessageBox.critical(self, "Error", message)
        self.reject()
    
    def update_quality_label(self, value):
        """Update quality label when slider changes"""
        self.quality_label.setText(f"{value}%")
    
    def browse_source_folder(self):
        """Browse for source folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.source_directory = folder
            self.source_label.setText(folder)
            self.load_source_images()
            self.update_preview()
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_label.setText(folder)
    
    def load_source_images(self):
        """Load images from source directory"""
        if not self.source_directory or not os.path.exists(self.source_directory):
            return
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.image_files = []
        
        for filename in os.listdir(self.source_directory):
            if any(filename.lower().endswith(ext) for ext in image_extensions):
                self.image_files.append(os.path.join(self.source_directory, filename))
        
        self.log_text.append(f"Found {len(self.image_files)} images in source folder")
    
    def get_resize_options(self):
        """Get current resize options from UI"""
        method_id = self.method_button_group.checkedId()
        
        if method_id == 0:  # Percentage
            method = "percentage"
            value = self.percentage_spin.value()
        elif method_id == 1:  # Fixed width
            method = "fixed_width"
            value = self.width_spin.value()
        elif method_id == 2:  # Fixed height
            method = "fixed_height"
            value = self.height_spin.value()
        elif method_id == 3:  # Max dimension
            method = "max_dimension"
            value = self.max_dim_spin.value()
        else:
            method = "percentage"
            value = 100
        
        return {
            "method": method,
            "value": value,
            "keep_aspect": self.keep_aspect_checkbox.isChecked(),
            "quality": self.quality_slider.value(),
            "suffix": self.suffix_combo.currentText()
        }
    
    def update_preview(self):
        """Update preview with current settings"""
        if not hasattr(self, 'image_files') or not self.image_files:
            self.preview_label.setText("No images found in source folder")
            return
        
        # Get first image for preview
        sample_image = self.image_files[0]
        try:
            info = self.resizer.get_image_info(sample_image)
            if "error" in info:
                self.preview_label.setText(f"Error reading sample image: {info['error']}")
                return
            
            options = self.get_resize_options()
            original_size = (info["width"], info["height"])
            new_size = self.resizer._calculate_new_size(original_size, options)
            
            # Calculate size reduction
            original_pixels = original_size[0] * original_size[1]
            new_pixels = new_size[0] * new_size[1]
            reduction = (1 - new_pixels/original_pixels) * 100
            
            preview_text = f"Sample: {os.path.basename(sample_image)}\n"
            preview_text += f"Original: {original_size[0]}×{original_size[1]} ({info['size_mb']:.1f} MB)\n"
            preview_text += f"New: {new_size[0]}×{new_size[1]} (est. {info['size_mb'] * (new_pixels/original_pixels):.1f} MB)\n"
            preview_text += f"Size reduction: {reduction:.1f}%\n"
            preview_text += f"Total images to process: {len(self.image_files)}"
            
            self.preview_label.setText(preview_text)
            
        except Exception as e:
            self.preview_label.setText(f"Preview error: {str(e)}")
    
    def start_resize(self):
        """Start the resize process"""
        if not hasattr(self, 'image_files') or not self.image_files:
            QMessageBox.warning(self, "No Images", "No images found to resize.")
            return
        
        if not self.output_folder:
            QMessageBox.warning(self, "No Output Folder", "Please select an output folder.")
            return
        
        if self.source_directory == self.output_folder:
            reply = QMessageBox.question(
                self, 
                "Same Folder", 
                "Source and output folders are the same. Files will be renamed with suffix. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Disable UI during processing
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.image_files))
        
        # Start resize thread
        options = self.get_resize_options()
        self.resize_thread = ResizeWorkerThread(self.image_files, self.output_folder, options)
        self.resize_thread.progress_updated.connect(self.update_progress)
        self.resize_thread.finished.connect(self.resize_finished)
        self.resize_thread.start()
        
        self.log_text.append(f"Starting resize of {len(self.image_files)} images...")
    
    def update_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        self.log_text.append(f"Processing image {current}/{total}")
    
    def resize_finished(self, results):
        """Handle resize completion"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if "error" in results:
            QMessageBox.critical(self, "Error", f"Resize failed: {results['error']}")
            return
        
        success_count = results["success_count"]
        error_count = results["error_count"]
        
        self.log_text.append(f"\nResize completed!")
        self.log_text.append(f"Successfully resized: {success_count} images")
        self.log_text.append(f"Errors: {error_count}")
        
        if results["errors"]:
            self.log_text.append("\nErrors:")
            for error in results["errors"][:10]:  # Show first 10 errors
                self.log_text.append(f"  - {error}")
        
        QMessageBox.information(
            self, 
            "Resize Complete", 
            f"Resize completed!\n\nSuccess: {success_count}\nErrors: {error_count}\n\nOutput folder: {self.output_folder}"
        )
    
    def get_output_folder(self):
        """Return the selected output folder"""
        return self.output_folder