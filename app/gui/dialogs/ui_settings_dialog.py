from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QDialogButtonBox

class UISettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("UI Settings")

        layout = QVBoxLayout(self)

        # Theme selector
        layout.addWidget(QLabel("Choose Color Theme:"))
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark", "Blue", "High Contrast"])
        layout.addWidget(self.theme_selector)

        # Layout selector
        layout.addWidget(QLabel("Gallery Layout:"))
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(["Grid", "List", "Card-Based"])
        layout.addWidget(self.layout_selector)

        # OK / Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_values(self):
        return {
            "theme": self.theme_selector.currentText(),
            "layout": self.layout_selector.currentText()
        }
