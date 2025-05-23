from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                              QPushButton, QLineEdit, QLabel)
from PySide6.QtCore import Qt

class FolderPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Match categories to the UI radio buttons
        self.categories = ["Animal", "Appliance", "Cat", "Dog", 
                          "Entertainment_Device", "Kitchenware", 
                          "Person", "Vehicle", "Unknown"]
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Category Folders Preview")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # List widget to show folders
        self.folder_list = QListWidget()
        self.folder_list.addItems(self.categories)
        layout.addWidget(self.folder_list)
        
        # Add category section
        add_layout = QHBoxLayout()
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("New category name")
        add_layout.addWidget(self.category_input)
        
        self.add_button = QPushButton("Add Category")
        self.add_button.clicked.connect(self.add_category)
        add_layout.addWidget(self.add_button)
        
        layout.addLayout(add_layout)
        
        # Remove category button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_category)
        layout.addWidget(self.remove_button)
        
        self.setLayout(layout)
    
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