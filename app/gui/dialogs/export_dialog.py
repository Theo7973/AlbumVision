from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export")
        self.setFixedSize(400, 200)  # Set the size of the dialog

        # Create layout
        layout = QVBoxLayout(self)

        # Add vertical spacer to push label to center
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add label centered
        self.label = QLabel("The sorted image files will be\nExport to: \n", self)
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        # Add another vertical spacer to keep label centered
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add buttons at the bottom right
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Push buttons to the right
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)