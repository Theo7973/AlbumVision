from PySide6.QtWidgets import QDialog, QGroupBox, QVBoxLayout, QCheckBox, QHBoxLayout, QPushButton

class ChangeTagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Image Tag")
        self.setFixedSize(400, 300)  # Adjusted size to accommodate buttons

        # Create layout
        layout = QVBoxLayout(self)

        # Create a QGroupBox for the checkboxes
        tag_btn_group_box = QGroupBox("Tag Name")
        tag_btn_group_box.setStyleSheet("""
            QGroupBox {
                font: bold 12px;
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 10px;
                padding: 3px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)

        # Create a vertical layout for the checkboxes
        tab_btn_layout = QVBoxLayout()

        # Create checkboxes for each tag name
        btn_name_list = ['Animal', 'Cat', 'Dog', 'Person', 'Vehicle', 'Kitchenware', 'Appliance', 'Entertainment Device']
        sorted_list = sorted(btn_name_list)  # Sorts alphabetically
        sorted_list.append('Unknown')
        self.checkboxes = []  # Store references to the checkboxes
        for name in sorted_list:  # Create checkboxes for each tag name
            checkbox = QCheckBox(f"{name}", self)
            checkbox.setStyleSheet("font-size: 11px;")  # Set font size for the checkbox
            tab_btn_layout.addWidget(checkbox)  # Add the checkbox to the vertical layout
            self.checkboxes.append(checkbox)  # Store the checkbox reference

        # Set the layout for the group box
        tag_btn_group_box.setLayout(tab_btn_layout)

        # Add the group box to the main layout
        layout.addWidget(tag_btn_group_box)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK", self)
        cancel_button = QPushButton("Cancel", self)

        # Connect buttons to dialog actions
        ok_button.clicked.connect(self.accept)  # Close dialog with accept
        cancel_button.clicked.connect(self.reject)  # Close dialog with reject

        # Add buttons to the layout
        button_layout.addStretch()  # Add stretch to align buttons to the right
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

    def get_selected_tags(self):
        """Return a list of selected tags."""
        selected_tags = [checkbox.text() for checkbox in self.checkboxes if checkbox.isChecked()]
        return selected_tags