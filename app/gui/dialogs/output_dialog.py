from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QFileDialog

class OutputPathDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Output Path")
        self.setFixedSize(600, 100)

        # Main vertical layout
        layout = QVBoxLayout(self)

        # Add vertical spacer to push content to center
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Create an HBoxLayout for label, line edit, and browse button
        path_layout = QHBoxLayout()
        self.label = QLabel("Enter the output path:", self)
        self.path_input = QLineEdit(self)
        self.browse_button = QPushButton("Browse...", self)
        self.browse_button.clicked.connect(self.open_folder_dialog)
        path_layout.addWidget(self.label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)
        layout.addLayout(path_layout)

        # Add another vertical spacer to keep content centered
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add OK and Cancel buttons at the bottom right
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

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.path_input.setText(folder_path)

    def get_output_path(self):
        """Return the text entered in the input field."""
        return self.path_input.text()