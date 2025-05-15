from PySide6.QtWidgets import QDialog, QFileDialog

class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Folder")
        self.setFixedSize(400, 200)  # Set the size of the dialog

        # Open the file explorer directly when the dialog is created
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        # Close the dialog immediately after folder selection
        self.accept() if self.folder_path else self.reject()

    def get_selected_folder(self):
        """Return the selected folder path."""
        return self.folder_path