from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QGridLayout, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
import os

class ImageCard(QFrame):
    """Individual image card widget with hover effects and edit functionality."""
    
    clicked = Signal(str)  # Emits image path when clicked
    edit_requested = Signal(str)  # Emits image path when edit is requested
    
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
        layout.setSpacing(6)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setFixedSize(180, 140)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 1px solid #404040;
                border-radius: 4px;
                background-color: #232323;
            }
        """)
        
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
                padding: 2px;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.category_label)
        
        # Filename label
        filename = os.path.basename(self.image_path)
        if len(filename) > 22:
            filename = filename[:19] + "..."
            
        self.filename_label = QLabel(filename)
        self.filename_label.setAlignment(Qt.AlignCenter)
        self.filename_label.setStyleSheet("""
            QLabel {
                color: #e0e0e0;
                font-size: 10px;
                padding: 2px;
                background-color: transparent;
            }
        """)
        layout.addWidget(self.filename_label)
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 4, 0, 0)
        
        # View button
        view_btn = QPushButton("View")
        view_btn.setFixedHeight(24)
        view_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                border: 1px solid #106ebe;
                color: white;
                font-size: 9px;
                font-weight: bold;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #106ebe;
                border-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        view_btn.clicked.connect(self.on_view_clicked)
        button_layout.addWidget(view_btn)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedHeight(24)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                border: 1px solid #1e7e34;
                color: white;
                font-size: 9px;
                font-weight: bold;
                border-radius: 3px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
                border-color: #155724;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
        """)
        edit_btn.clicked.connect(self.on_edit_clicked)
        button_layout.addWidget(edit_btn)
        
        layout.addLayout(button_layout)
    
    def setup_styling(self):
        """Setup card styling with unified theme."""
        # Import theme colors
        try:
            from app.utils.theme_manager import ThemeManager
            colors = ThemeManager.COLORS
            bg_color = colors['background_tertiary']
            hover_color = colors['background_hover']
            border_color = colors['border_primary']
            hover_border = colors['border_accent']
        except ImportError:
            # Fallback colors
            bg_color = '#2d2d2d'
            hover_color = '#3d3d3d'
            border_color = '#404040'
            hover_border = '#505050'
        
        self.setStyleSheet(f"""
            ImageCard {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            ImageCard:hover {{
                background-color: {hover_color};
                border: 2px solid {hover_border};
            }}
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
                self.image_label.setStyleSheet("""
                    QLabel {
                        color: #888888;
                        font-size: 12px;
                        border: 1px dashed #404040;
                        border-radius: 4px;
                        background-color: #232323;
                    }
                """)
        except Exception as e:
            print(f"Error loading image {self.image_path}: {e}")
            self.image_label.setText("Error")
            self.image_label.setStyleSheet("""
                QLabel {
                    color: #ff6b6b;
                    font-size: 10px;
                    border: 1px solid #ff6b6b;
                    border-radius: 4px;
                    background-color: #232323;
                }
            """)
    
    def on_view_clicked(self):
        """Handle view button click."""
        self.clicked.emit(self.image_path)
    
    def on_edit_clicked(self):
        """Handle edit button click."""
        self.edit_requested.emit(self.image_path)
    
    def open_editor(self):
        """Open image editor for this card's image."""
        try:
            from .widgets.image_editor import ImageEditor
            
            editor = ImageEditor(self.parent(), self.image_path)
            editor.image_saved.connect(self.on_image_edited)
            editor.exec()
            
        except Exception as e:
            print(f"Error opening editor: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Editor Error", 
                f"Could not open image editor:\n{str(e)}"
            )
    
    def on_image_edited(self, image_path):
        """Refresh card after editing."""
        # Reload the image in this card
        self.load_image()
        print(f"Image {os.path.basename(image_path)} has been edited and reloaded")
    
    def mousePressEvent(self, event):
        """Handle mouse click on card background."""
        if event.button() == Qt.LeftButton:
            # Only emit click if not clicking on buttons
            self.clicked.emit(self.image_path)
        super().mousePressEvent(event)


class CardGalleryWidget(QWidget):
    """Card-based gallery widget for PySide6 with unified theming."""
    
    image_clicked = Signal(str)  # Emits image path when card is clicked
    edit_requested = Signal(str)  # Emits image path when edit is requested
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = []
        self.setup_ui()
        self.apply_theme()
    
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
    
    def apply_theme(self):
        """Apply unified dark theme."""
        try:
            from app.utils.theme_manager import ThemeManager
            colors = ThemeManager.COLORS
            
            style = f"""
            QScrollArea {{
                border: 1px solid {colors['border_primary']};
                border-radius: 5px;
                background-color: {colors['background_secondary']};
            }}
            QWidget {{
                background-color: {colors['background_primary']};
            }}
            """
            self.setStyleSheet(style)
        except ImportError:
            # Fallback styling
            self.setStyleSheet("""
            QScrollArea {
                border: 1px solid #404040;
                border-radius: 5px;
                background-color: #232323;
            }
            QWidget {
                background-color: #1a1a1a;
            }
            """)
    
    def load_images(self, image_data_list):
        """Load images into card layout.
        
        Args:
            image_data_list: List of dicts with keys: 'path', 'category', 'confidence'
        """
        # Clear existing cards
        self.clear_cards()
        
        if not image_data_list:
            # Show empty state
            self.show_empty_state()
            return
        
        # Calculate grid layout - responsive design
        self.container_widget.update()
        available_width = max(800, self.scroll_area.width() - 50)  # Account for scrollbars
        card_width = 200  # Approximate card width including margins
        cards_per_row = max(1, available_width // card_width)
        
        # Create cards
        for i, img_data in enumerate(image_data_list):
            try:
                card = ImageCard(
                    img_data['path'],
                    img_data.get('category', 'Unknown'),
                    img_data.get('confidence', 0.0)
                )
                
                # Connect signals
                card.clicked.connect(self.image_clicked.emit)
                card.edit_requested.connect(self.on_edit_requested)
                
                row = i // cards_per_row
                col = i % cards_per_row
                
                self.grid_layout.addWidget(card, row, col)
                self.cards.append(card)
                
            except Exception as e:
                print(f"Error creating card for {img_data.get('path', 'unknown')}: {e}")
        
        # Add stretch to push cards to top-left
        self.grid_layout.setRowStretch(len(image_data_list) // cards_per_row + 1, 1)
        self.grid_layout.setColumnStretch(cards_per_row, 1)
    
    def show_empty_state(self):
        """Show empty state when no images are loaded."""
        empty_label = QLabel("No images to display\n\nLoad a folder with images to see them here")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 14px;
                padding: 40px;
                background-color: transparent;
            }
        """)
        self.grid_layout.addWidget(empty_label, 0, 0, Qt.AlignCenter)
    
    def on_edit_requested(self, image_path):
        """Handle edit request from a card."""
        try:
            from app.gui.widgets.image_editor import ImageEditor
            
            # Find the parent window
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'setWindowTitle'):
                parent_window = parent_window.parent()
            
            editor = ImageEditor(parent_window or self, image_path)
            editor.image_saved.connect(lambda path: self.on_image_edited(path, image_path))
            editor.exec()
            
        except Exception as e:
            print(f"Error opening editor: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, 
                "Editor Error", 
                f"Could not open image editor:\n{str(e)}\n\nMake sure PIL (Pillow) is installed."
            )
    
    def on_image_edited(self, saved_path, original_path):
        """Handle image edit completion."""
        # Refresh the specific card that was edited
        for card in self.cards:
            if card.image_path == original_path:
                card.load_image()
                break
        
        # Emit signal for parent to handle
        self.edit_requested.emit(saved_path)
    
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
    
    def refresh_all_cards(self):
        """Refresh all cards (reload images)."""
        for card in self.cards:
            card.load_image()
    
    def resizeEvent(self, event):
        """Handle resize to adjust card layout."""
        super().resizeEvent(event)
     