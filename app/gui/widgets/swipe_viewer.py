from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QWidget, QGraphicsOpacityEffect)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QKeySequence, QShortcut, QWheelEvent
import os

class SwipeImageViewer(QDialog):
    """Full-screen image viewer with smooth fade animations for PySide6."""
    
    def __init__(self, parent, images, initial_index=0, categories=None):
        super().__init__(parent)
        self.images = images  # List of image paths
        self.categories = categories or {}  # Dict mapping path to category info
        self.current_index = initial_index
        self.is_transitioning = False
        
        # Animation attributes
        self.opacity_effect = None
        self.fade_animation = None
        
        self.setup_window()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_current_image_direct()  # Initial load without animation
    
    def setup_window(self):
        """Configure the viewer window."""
        self.setWindowTitle("Image Viewer")
        self.setModal(True)
        
        # Make it fullscreen-like
        self.showMaximized()
        
        # Dark styling
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
                color: #e0e0e0;
            }
        """)
    
    def setup_ui(self):
        """Setup the viewer UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top toolbar
        self.create_toolbar(main_layout)
        
        # Main image area
        self.create_image_area(main_layout)
        
        # Bottom info panel
        self.create_info_panel(main_layout)
    
    def create_toolbar(self, parent_layout):
        """Create top toolbar."""
        toolbar = QFrame()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-bottom: 1px solid #404040;
            }
        """)
        
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QLabel("Image Viewer")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #e0e0e0;
            }
        """)
        toolbar_layout.addWidget(title_label)
        
        toolbar_layout.addStretch()
        
        # Counter
        self.counter_label = QLabel("")
        self.counter_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #b0b0b0;
            }
        """)
        toolbar_layout.addWidget(self.counter_label)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        close_btn.clicked.connect(self.close)
        toolbar_layout.addWidget(close_btn)
        
        parent_layout.addWidget(toolbar)
    
    def create_image_area(self, parent_layout):
        """Create main image display area."""
        image_container = QFrame()
        image_container.setStyleSheet("QFrame { background-color: #000000; }")
        
        image_layout = QHBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)
        
        # Previous button
        self.prev_btn = QPushButton("‹")
        self.prev_btn.setFixedSize(50, 100)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 45, 180);
                color: #e0e0e0;
                border: none;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(61, 61, 61, 200);
            }
            QPushButton:disabled {
                background-color: rgba(26, 26, 26, 120);
                color: #555555;
            }
        """)
        self.prev_btn.clicked.connect(self.prev_image)
        image_layout.addWidget(self.prev_btn, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Image display area
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("QLabel { background-color: #000000; }")
        self.image_label.setMinimumSize(400, 300)
        image_layout.addWidget(self.image_label, 1)
        
        # Next button
        self.next_btn = QPushButton("›")
        self.next_btn.setFixedSize(50, 100)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(45, 45, 45, 180);
                color: #e0e0e0;
                border: none;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(61, 61, 61, 200);
            }
            QPushButton:disabled {
                background-color: rgba(26, 26, 26, 120);
                color: #555555;
            }
        """)
        self.next_btn.clicked.connect(self.next_image)
        image_layout.addWidget(self.next_btn, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        parent_layout.addWidget(image_container, 1)
    
    def create_info_panel(self, parent_layout):
        """Create bottom info panel."""
        info_panel = QFrame()
        info_panel.setFixedHeight(80)
        info_panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-top: 1px solid #404040;
            }
        """)
        
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(20, 10, 20, 10)
        
        # Filename
        self.filename_label = QLabel("")
        self.filename_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #e0e0e0;
            }
        """)
        info_layout.addWidget(self.filename_label)
        
        # Category info
        self.category_label = QLabel("")
        self.category_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #0078d4;
            }
        """)
        info_layout.addWidget(self.category_label)
        
        parent_layout.addWidget(info_panel)
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Arrow keys and space for navigation
        QShortcut(QKeySequence(Qt.Key_Right), self, self.next_image)
        QShortcut(QKeySequence(Qt.Key_Left), self, self.prev_image)
        QShortcut(QKeySequence(Qt.Key_Space), self, self.next_image)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self.close)
    
    def load_current_image_animated(self):
        """Load current image with smooth fade animation."""
        if not self.images or self.is_transitioning:
            return
        
        self.is_transitioning = True
        
        # If no image is currently loaded, load directly without animation
        if not hasattr(self, 'current_photo') or not self.image_label.pixmap():
            self.load_current_image_direct()
            return
        
        # Start fade out animation
        self.fade_out_current_image()
    
    def fade_out_current_image(self):
        """Fade out the current image."""
        # Create opacity effect if it doesn't exist
        if not self.opacity_effect:
            self.opacity_effect = QGraphicsOpacityEffect()
            self.image_label.setGraphicsEffect(self.opacity_effect)
        
        # Create fade out animation
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)  # 200ms - quick and smooth
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.3)  # Don't go fully transparent
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # When fade out completes, load new image
        self.fade_animation.finished.connect(self.load_new_image_and_fade_in)
        self.fade_animation.start()
    
    def load_new_image_and_fade_in(self):
        """Load new image and fade it in."""
        try:
            current_path = self.images[self.current_index]
            
            # Update info labels first
            self.update_info_labels(current_path)
            
            # Load new image
            pixmap = QPixmap(current_path)
            
            if not pixmap.isNull():
                # Get display size
                available_width = self.image_label.width() - 20
                available_height = self.image_label.height() - 20
                
                if available_width <= 1 or available_height <= 1:
                    available_width, available_height = 800, 600
                
                # Scale image maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    available_width, available_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.current_photo = scaled_pixmap
                self.image_label.setPixmap(self.current_photo)
                
            else:
                self.image_label.setText("Could not load image")
            
            # Update navigation buttons
            self.update_navigation_buttons()
            
            # Now fade in the new image
            self.fade_in_new_image()
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label.setText(f"Error loading image")
            self.fade_in_new_image()  # Still fade in to complete the transition
    
    def fade_in_new_image(self):
        """Fade in the newly loaded image."""
        if not self.opacity_effect:
            self.opacity_effect = QGraphicsOpacityEffect()
            self.image_label.setGraphicsEffect(self.opacity_effect)
        
        # Create fade in animation
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0.3)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        # When animation completes, clear the transitioning flag
        self.fade_animation.finished.connect(self.animation_completed)
        self.fade_animation.start()
    
    def animation_completed(self):
        """Called when animation is complete."""
        self.is_transitioning = False
    
    def load_current_image_direct(self):
        """Load image directly without animation (for first load)."""
        if not self.images:
            return
        
        try:
            current_path = self.images[self.current_index]
            
            # Update info labels
            self.update_info_labels(current_path)
            
            # Load image
            pixmap = QPixmap(current_path)
            
            if not pixmap.isNull():
                # Get available space for image
                available_width = self.image_label.width() - 20
                available_height = self.image_label.height() - 20
                
                if available_width <= 0 or available_height <= 0:
                    # Fallback dimensions
                    available_width, available_height = 800, 600
                
                # Scale image maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    available_width, available_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.current_photo = scaled_pixmap
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("Could not load image")
            
            # Update navigation buttons
            self.update_navigation_buttons()
            
        except Exception as e:
            print(f"Error loading image: {e}")
            self.image_label.setText(f"Error loading image:\n{str(e)}")
        
        finally:
            self.is_transitioning = False
    
    def update_info_labels(self, image_path):
        """Update the information labels."""
        filename = os.path.basename(image_path)
        self.filename_label.setText(filename)
        
        # Update counter
        counter_text = f"{self.current_index + 1} of {len(self.images)}"
        self.counter_label.setText(counter_text)
        
        # Update category info
        if image_path in self.categories:
            category_info = self.categories[image_path]
            category_text = f"Category: {category_info.get('category', 'Unknown')}"
            if 'confidence' in category_info and category_info['confidence'] > 0:
                category_text += f" (Confidence: {category_info['confidence']:.0%})"
            self.category_label.setText(category_text)
        else:
            self.category_label.setText("Category: Unknown")
    
    def update_navigation_buttons(self):
        """Update navigation button states."""
        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.images) - 1)
    
    def next_image(self):
        """Navigate to next image with smooth animation."""
        if self.current_index < len(self.images) - 1 and not self.is_transitioning:
            self.current_index += 1
            self.load_current_image_animated()
    
    def prev_image(self):
        """Navigate to previous image with smooth animation."""
        if self.current_index > 0 and not self.is_transitioning:
            self.current_index -= 1
            self.load_current_image_animated()
    
    def mousePressEvent(self, event):
        """Handle mouse clicks for navigation."""
        if event.button() == Qt.LeftButton:
            # Click on right side = next, left side = previous
            if event.x() > self.width() // 2:
                self.next_image()
            else:
                self.prev_image()
        super().mousePressEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel navigation."""
        if event.angleDelta().y() > 0:
            self.prev_image()
        else:
            self.next_image()
        event.accept()
    
    def resizeEvent(self, event):
        """Handle window resize."""
        super().resizeEvent(event)
        # Reload current image with new dimensions after a short delay
        if not self.is_transitioning:
            QTimer.singleShot(100, self.load_current_image_direct)