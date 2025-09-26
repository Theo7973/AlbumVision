

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QSlider, QGroupBox, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon
from PIL import Image, ImageEnhance, ImageFilter
import os

class ImageEditor(QDialog):
    """Simple image editor with basic editing tools"""
    
    image_saved = Signal(str)  # Emitted when image is saved
    
    def __init__(self, parent, image_path):
        super().__init__(parent)
        self.original_image_path = image_path
        self.modified = False
        
        # Load original image
        try:
            self.original_image = Image.open(image_path)
            self.current_image = self.original_image.copy()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open image: {str(e)}")
            self.reject()
            return
        
        self.setup_ui()
        self.update_preview()
        self.apply_theme()
    
    def setup_ui(self):
        """Setup the editor UI"""
        self.setWindowTitle("Image Editor")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        main_layout = QHBoxLayout(self)
        
        # Left panel - controls
        self.create_controls_panel(main_layout)
        
        # Right panel - image preview
        self.create_preview_panel(main_layout)
    
    def create_controls_panel(self, parent_layout):
        """Create the editing controls panel"""
        controls_frame = QFrame()
        controls_frame.setFixedWidth(300)
        controls_layout = QVBoxLayout(controls_frame)
        
        # Title
        title = QLabel("Image Editor")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        controls_layout.addWidget(title)
        
        # Basic Adjustments
        basic_group = QGroupBox("Basic Adjustments")
        basic_layout = QVBoxLayout(basic_group)
        
        # Brightness
        basic_layout.addWidget(QLabel("Brightness:"))
        self.brightness_slider = self.create_slider(-50, 50, 0)
        self.brightness_slider.valueChanged.connect(self.on_adjustment_changed)
        basic_layout.addWidget(self.brightness_slider)
        
        # Contrast
        basic_layout.addWidget(QLabel("Contrast:"))
        self.contrast_slider = self.create_slider(-50, 50, 0)
        self.contrast_slider.valueChanged.connect(self.on_adjustment_changed)
        basic_layout.addWidget(self.contrast_slider)
        
        # Saturation
        basic_layout.addWidget(QLabel("Saturation:"))
        self.saturation_slider = self.create_slider(-50, 50, 0)
        self.saturation_slider.valueChanged.connect(self.on_adjustment_changed)
        basic_layout.addWidget(self.saturation_slider)
        
        # Sharpness
        basic_layout.addWidget(QLabel("Sharpness:"))
        self.sharpness_slider = self.create_slider(-50, 50, 0)
        self.sharpness_slider.valueChanged.connect(self.on_adjustment_changed)
        basic_layout.addWidget(self.sharpness_slider)
        
        controls_layout.addWidget(basic_group)
        
        # Filters
        filters_group = QGroupBox("Filters")
        filters_layout = QVBoxLayout(filters_group)
        
        filter_buttons = [
            ("Original", self.apply_original),
            ("Blur", self.apply_blur),
            ("Sharpen", self.apply_sharpen),
            ("Smooth", self.apply_smooth),
            ("Edge Enhance", self.apply_edge_enhance),
        ]
        
        for text, callback in filter_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            filters_layout.addWidget(btn)
        
        controls_layout.addWidget(filters_group)
        
        # Rotation
        rotation_group = QGroupBox("Rotation")
        rotation_layout = QVBoxLayout(rotation_group)
        
        rotation_buttons = [
            ("Rotate 90° Left", lambda: self.rotate(-90)),
            ("Rotate 90° Right", lambda: self.rotate(90)),
            ("Flip Horizontal", self.flip_horizontal),
            ("Flip Vertical", self.flip_vertical),
        ]
        
        for text, callback in rotation_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            rotation_layout.addWidget(btn)
        
        controls_layout.addWidget(rotation_group)
        
        # Reset and Save buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_image)
        button_layout.addWidget(reset_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_image)
        button_layout.addWidget(save_btn)
        
        save_as_btn = QPushButton("Save As...")
        save_as_btn.clicked.connect(self.save_image_as)
        button_layout.addWidget(save_as_btn)
        
        controls_layout.addLayout(button_layout)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        controls_layout.addWidget(close_btn)
        
        controls_layout.addStretch()
        parent_layout.addWidget(controls_frame)
    
    def create_preview_panel(self, parent_layout):
        """Create the image preview panel"""
        preview_frame = QFrame()
        preview_layout = QVBoxLayout(preview_frame)
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet("border: 1px solid #404040; background-color: #2b2b2b;")
        preview_layout.addWidget(self.preview_label)
        
        # Image info
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet("padding: 10px; font-size: 12px; color: #b0b0b0;")
        preview_layout.addWidget(self.info_label)
        
        parent_layout.addWidget(preview_frame)
    
    def create_slider(self, min_val, max_val, default_val):
        """Create a styled slider"""
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        return slider
    
    def on_adjustment_changed(self):
        """Apply adjustments when sliders change"""
        try:
            img = self.original_image.copy()
            
            # Apply brightness
            brightness = 1.0 + (self.brightness_slider.value() / 100.0)
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)
            
            # Apply contrast
            contrast = 1.0 + (self.contrast_slider.value() / 100.0)
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)
            
            # Apply saturation
            saturation = 1.0 + (self.saturation_slider.value() / 100.0)
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(saturation)
            
            # Apply sharpness
            sharpness = 1.0 + (self.sharpness_slider.value() / 100.0)
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpness)
            
            self.current_image = img
            self.update_preview()
            self.modified = True
            
        except Exception as e:
            print(f"Error applying adjustments: {e}")
    
    def apply_original(self):
        """Reset to original image"""
        self.reset_image()
    
    def apply_blur(self):
        """Apply blur filter"""
        try:
            self.current_image = self.current_image.filter(ImageFilter.BLUR)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error applying blur: {e}")
    
    def apply_sharpen(self):
        """Apply sharpen filter"""
        try:
            self.current_image = self.current_image.filter(ImageFilter.SHARPEN)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error applying sharpen: {e}")
    
    def apply_smooth(self):
        """Apply smooth filter"""
        try:
            self.current_image = self.current_image.filter(ImageFilter.SMOOTH)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error applying smooth: {e}")
    
    def apply_edge_enhance(self):
        """Apply edge enhance filter"""
        try:
            self.current_image = self.current_image.filter(ImageFilter.EDGE_ENHANCE)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error applying edge enhance: {e}")
    
    def rotate(self, degrees):
        """Rotate image by specified degrees"""
        try:
            self.current_image = self.current_image.rotate(degrees, expand=True)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error rotating image: {e}")
    
    def flip_horizontal(self):
        """Flip image horizontally"""
        try:
            self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error flipping horizontally: {e}")
    
    def flip_vertical(self):
        """Flip image vertically"""
        try:
            self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.update_preview()
            self.modified = True
        except Exception as e:
            print(f"Error flipping vertically: {e}")
    
    def reset_image(self):
        """Reset to original image"""
        self.current_image = self.original_image.copy()
        
        # Reset sliders
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.sharpness_slider.setValue(0)
        
        self.update_preview()
        self.modified = False
    
    def update_preview(self):
        """Update the preview image"""
        try:
            # Convert PIL image to QPixmap
            img_copy = self.current_image.copy()
            img_copy.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if img_copy.mode != 'RGB':
                img_copy = img_copy.convert('RGB')
            
            # Convert to QPixmap
            img_copy.save('/tmp/preview.png')  # Temporary save
            pixmap = QPixmap('/tmp/preview.png')
            
            self.preview_label.setPixmap(pixmap)
            
            # Update info
            width, height = self.current_image.size
            self.info_label.setText(f"Size: {width} x {height} pixels")
            
        except Exception as e:
            print(f"Error updating preview: {e}")
            self.preview_label.setText("Preview Error")
    
    def save_image(self):
        """Save image to original location"""
        try:
            self.current_image.save(self.original_image_path)
            self.modified = False
            self.image_saved.emit(self.original_image_path)
            QMessageBox.information(self, "Success", "Image saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def save_image_as(self):
        """Save image to new location"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Image As",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
            )
            
            if file_path:
                self.current_image.save(file_path)
                self.image_saved.emit(file_path)
                QMessageBox.information(self, "Success", f"Image saved as: {os.path.basename(file_path)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save image: {str(e)}")
    
    def apply_theme(self):
        """Apply dark theme to the editor"""
        # Import here to avoid circular imports
        try:
            from app.utils.theme_manager import ThemeManager
            self.setStyleSheet(ThemeManager.get_main_window_style())
        except ImportError:
            # Fallback styling
            self.setStyleSheet("""
                QDialog {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #2d2d2d;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 6px 12px;
                    color: #e0e0e0;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 6px;
                    color: #e0e0e0;
                    background-color: #2b2b2b;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #404040;
                    height: 6px;
                    background: #2b2b2b;
                    border-radius: 3px;
                }
                QSlider::handle:horizontal {
                    background: #0078d4;
                    border: 1px solid #404040;
                    width: 16px;
                    border-radius: 8px;
                    margin: -5px 0;
                }
            """)
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.modified:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_image()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()