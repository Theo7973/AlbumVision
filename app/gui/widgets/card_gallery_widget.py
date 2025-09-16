

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QGridLayout, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
import os

class ImageCard(QFrame):
    """Individual image card widget with hover effects."""
    
    clicked = Signal(str)  # Emits image path when clicked
    
    def __init__(self, image_path, category="Unknown", confidence=0.0, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.category = category
        self.confidence = confidence
        
        self.setup_ui()
        self.setup_styling()
    
    def setup_ui(self):
        """Setup the card UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 140)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Load and set image
        self.load_image()
        layout.addWidget(self.image_label)
        
        # Category label
        category_text = f"{self.category}"
        if self.confidence > 0:
            category_text += f" ({self.confidence:.0%})"
            
        self.category_label = QLabel(category_text)
        self.category_label.setAlignment(Qt.AlignCenter)
        self.category_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-weight: bold;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.category_label)
        
        # Filename label
        filename = os.path.basename(self.image_path)
        if len(filename) > 20:
            filename = filename[:17] + "..."
            
        self.filename_label = QLabel(filename)
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.filename_label)
    
    def setup_styling(self):
        """Setup card styling."""
        self.setStyleSheet("""
            ImageCard {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
            }
            ImageCard:hover {
                background-color: #3d3d3d;
                border: 2px solid #505050;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
    
    def load_image(self):
        """Load and display the image."""
        try:
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                # Crop to center square
                size = min(pixmap.width(), pixmap.height())
                x = (pixmap.width() - size) // 2
                y = (pixmap.height() - size) // 2
                cropped = pixmap.copy(x, y, size, size)
                
                # Scale to fit label
                scaled = cropped.scaled(
                    self.image_label.size(), 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
            else:
                self.image_label.setText("No Image")
        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")
            self.image_label.setText("Error")
    
    def mousePressEvent(self, event):
        """Handle mouse click."""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)


class CardGalleryWidget(QWidget):
    """Card-based gallery widget for PySide6."""
    
    image_clicked = Signal(str)  # Emits image path when card is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the gallery UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget for cards
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area.setWidget(self.container_widget)
        layout.addWidget(self.scroll_area)
        
        # Apply styling
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #232323;
            }
        """)
    
    def load_images(self, image_data_list):
        """Load images into card layout.
        
        Args:
            image_data_list: List of dicts with keys: 'path', 'category', 'confidence'
        """
        # Clear existing cards
        self.clear_cards()
        
        # Calculate grid layout
        cards_per_row = 4  # Adjust based on your preference
        
        # Create cards
        for i, img_data in enumerate(image_data_list):
            try:
                card = ImageCard(
                    img_data['path'],
                    img_data.get('category', 'Unknown'),
                    img_data.get('confidence', 0.0)
                )
                card.clicked.connect(self.image_clicked.emit)
                
                row = i // cards_per_row
                col = i % cards_per_row
                
                self.grid_layout.addWidget(card, row, col)
                self.cards.append(card)
                
            except Exception as e:
                print(f"Error creating card for {img_data.get('path', 'unknown')}: {e}")
    
    def clear_cards(self):
        """Clear all cards from the gallery."""
        for card in self.cards:
            card.setParent(None)
            card.deleteLater()
        self.cards.clear()
        
        # Clear grid layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)