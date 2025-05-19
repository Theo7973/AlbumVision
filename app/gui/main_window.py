"""
    Main interface GUI for user to interact with Album Vison+.
    # Need to update the Tool tips, image size control, and image metadata display. #
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame, QFileDialog
from PySide6.QtWidgets import QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QDialog, QPushButton
from PySide6.QtWidgets import (QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame, QMainWindow,
                               QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, QVBoxLayout, QSlider,
                               QDialog, QPushButton, QCheckBox, QMessageBox)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QEvent
from pprint import pformat
from ..utils import filter_non_image_files  # Import the filter_non_image_files function
from ..utils import get_all_files_in_directory  # Import the get_all_files_in_directory function
from ..utils import Get_MetaData  # Import the Get_MetaData class
from ..utils import file_utils  # Import the file_utils module

from .dialogs import export_dialog
from .dialogs import change_tag_dialog
from .dialogs import output_dialog


class DragDropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Enable drag-and-drop
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed gray;
                border-radius: 5px;
                background-color: none;
                font: bold 12px;
                color: #555;
                text-align: center;
            }
        """)
        self.setFixedWidth(291)  # Set a fixed width for the drag-and-drop area
        self.setFixedHeight(100)  # Set a fixed height for the drag-and-drop area

        # Add a QLabel to display the text
        self.label = QLabel("Drag and Drop Folder Here", self)
        self.label.setAlignment(Qt.AlignCenter)  # Center the text
        self.label.setStyleSheet("font-size: 20px; color: #e0e0e0;border: none;")  # Style the text

        # Use a layout to center the label inside the frame
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setAlignment(Qt.AlignCenter)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()  # Accept the drag event if it contains URLs
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            folder_found = False
            for url in event.mimeData().urls():
                folder_path = url.toLocalFile()
                if os.path.isdir(folder_path):  # Check if the dropped item is a folder

                    img_files = get_all_files_in_directory.get_all_files_in_directory(folder_path)  # Call the function to get all files in the directory

                    print(f"File list in folder: {img_files}")
                    folder_found = True
                    break
            if not folder_found:
                print("Please import a folder")  # Print message if no folder is found
            event.accept()
        else:
            print("Please import a folder")  # Print message if the dropped item is invalid
            event.ignore()

class ClickableLabel(QLabel):
    clicked = Signal()  # Define a custom signal
    doubleClicked = Signal()  # Define a custom signal for double click

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()  # Emit the signal when the label is clicked

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        self.doubleClicked.emit()  # Emit the signal when the label is double-clicked

class ImageWindow(QMainWindow):
    def __init__(self, image_dir):
        super().__init__()
        self.setWindowTitle("Image Viewer with Scroll Area, Text Views, and Slider")
        self.setFixedSize(1200, 800)  # Set the window to a fixed size
        self.image_dir = image_dir

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'ab_logo.svg')
        self.setWindowIcon(QIcon(icon_path))

        # Main container widget
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # Create a vertical layout for the left-side widgets
        left_layout = QVBoxLayout()

        # Add a horizontal layout for the buttons (top left)
        func_button_layout = QHBoxLayout()
        self.import_bnt = QPushButton("Import", self)
        self.export_bnt = QPushButton("Export", self)
        self.checkDup_bnt = QPushButton("Check Duplicate", self)
        self.changeTag_bnt = QPushButton("Change Tag", self)
        self.outputPath_bnt = QPushButton("Output Path", self)

         # install event filter on the import button
        self.import_bnt.installEventFilter(self)
        self.export_bnt.installEventFilter(self)
        self.checkDup_bnt.installEventFilter(self)
        self.changeTag_bnt.installEventFilter(self)
        self.outputPath_bnt.installEventFilter(self)
    

        # Add buttons to the layout
        func_button_layout.addWidget(self.import_bnt)
        func_button_layout.addWidget(self.export_bnt)
        func_button_layout.addWidget(self.checkDup_bnt)
        func_button_layout.addWidget(self.changeTag_bnt)
        func_button_layout.addWidget(self.outputPath_bnt)

        # Add the button layout to the left layout
        left_layout.addLayout(func_button_layout)

        # Create a QGroupBox for the buttons
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

        # Add a horizontal layout for the image control widgets (above image area)
        img_ctrl_layout = QHBoxLayout()

        tab_btn_layout = QHBoxLayout()
        # Create a button group to ensure only one button can be selected
        button_group = QButtonGroup(self)

        btn_name_list = ['Animal', 'Cat', 'Dog', 'Person', 'Vehicle', 'Kitchenware', 'Appliance', 'Entertainment\n Device']
        sorted_list = sorted(btn_name_list)  # Sorts alphabetically
        sorted_list.append('Unknown')
        for name in sorted_list:
            button = QRadioButton(f"{name}", self)
            button.setStyleSheet("font-size: 11px;")  # Set font size for the button
            button_group.addButton(button)  # Add the button to the group
            tab_btn_layout.addWidget(button)
            button.installEventFilter(self)  # Install event filter for the button


        # Set the layout for the group box
        tag_btn_group_box.setLayout(tab_btn_layout)

        img_ctrl_layout.addWidget(tag_btn_group_box)  # Add the group box to the layout
        left_layout.addLayout(img_ctrl_layout)

        
        # Create another QGroupBox for the radio buttons
        size_group_box = QGroupBox("Image Size Control")
        size_group_box.setStyleSheet("""
            QGroupBox {
                font: bold 12px;
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 10px;
                padding: 1px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
        """)

        slider_layout = QHBoxLayout()


        # Add a horizontal layout for the radio buttons
        size_layout = QHBoxLayout()

        # Create radio buttons for Small, Medium, and Large sizes
        self.small_size_btn = QRadioButton("Small", self)
        self.medium_size_btn = QRadioButton("Medium", self)
        self.large_size_btn = QRadioButton("Large", self)

        # Install event filter for each size button
        self.small_size_btn.installEventFilter(self)
        self.medium_size_btn.installEventFilter(self)
        self.large_size_btn.installEventFilter(self)

        # Set default selection to Medium
        self.medium_size_btn.setChecked(True)

        # Connect the radio buttons to the update_image_sizes function
        self.small_size_btn.toggled.connect(lambda: self.update_image_sizes("Small"))
        self.medium_size_btn.toggled.connect(lambda: self.update_image_sizes("Medium"))
        self.large_size_btn.toggled.connect(lambda: self.update_image_sizes("Large"))

        # Add the radio buttons to the layout
        size_layout.addWidget(self.small_size_btn)
        size_layout.addWidget(self.medium_size_btn)
        size_layout.addWidget(self.large_size_btn)

        # Set the layout for the group box
        size_group_box.setLayout(size_layout)

        # Add the size group box to the left layout
        img_ctrl_layout.addWidget(size_group_box)
        left_layout.addLayout(img_ctrl_layout)

        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)

        # Load all image files from the directory
        self.image_labels = []  # Store references to image labels
        row = 0
        col = 0
        for file_name in os.listdir(image_dir):
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(image_dir, file_name)
                image_label = ClickableLabel(self)
                pixmap = QPixmap(image_path)
                crop_center = self.crop_center(pixmap)  # Crop the image to 200x200
                image_label.setPixmap(crop_center)
                image_label.setScaledContents(True)
                image_label.setFixedSize(260, 260)  # Default size
                self.grid_layout.addWidget(image_label, row, col)
                self.image_labels.append((image_label, pixmap))  # Store label and pixmap
                image_label.installEventFilter(self)

                # Connect the clicked signal to a custom slot
                image_label.clicked.connect(lambda path=image_path: self.on_image_clicked(path))

                # Connect the doubleClicked signal to a custom slot
                image_label.doubleClicked.connect(lambda path=image_path: self.on_image_double_clicked(path))

                # Update column and row for the next image
                col += 1
                if col == 3:  # Move to the next row after 3 columns
                    col = 0
                    row += 1

        # Create a QScrollArea and set the container widget as its widget
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.scroll_area, 1)

        left_widget = QWidget(self)
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(900)
        main_layout.addWidget(left_widget)

        right_layout = QVBoxLayout()
        drag_drop_area = DragDropArea(self)
        drag_drop_area.installEventFilter(self)  # Install event filter for drag-and-drop area
        right_layout.addWidget(drag_drop_area)

        info_layout = QVBoxLayout()
        self.img_info = QLabel(self)
        self.img_info.setText("Image Info and Metadata")
        self.img_info.setWordWrap(True)
        info_layout.addWidget(self.img_info, 4)

        self.tool_tips = QLabel(self)
        self.tool_tips.setText("Tool Tips")
        self.tool_tips.setWordWrap(True)
        info_layout.addWidget(self.tool_tips, 1)

        text_view_widget = QWidget(self)
        text_view_widget.setLayout(info_layout)
        right_layout.addWidget(text_view_widget)

        right_widget = QWidget(self)
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(300)
        main_layout.addWidget(right_widget)


        # Connect the "Output Path" button to open the pop-up window
        self.import_bnt.clicked.connect(self.open_import_dialog)
        self.export_bnt.clicked.connect(self.open_export_dialog)
        self.checkDup_bnt.clicked.connect(self.show_duplicates_dialog)
        self.changeTag_bnt.clicked.connect(self.open_change_tag_dialog)
        self.outputPath_bnt.clicked.connect(self.open_output_path_dialog)

        # Set the main layout as the central widget
        self.setCentralWidget(main_widget)

    def update_image_sizes(self, size):
        """Update the size of the images and grid layout based on the selected size."""
        if size == "Small":
            new_size = 160  # Small size
            max_columns = 5  # 5x5 grid
        elif size == "Medium":
            new_size = 260  # Medium size (default)
            max_columns = 3  # 3x3 grid
        elif size == "Large":
            new_size = 400  # Large size
            max_columns = 2  # 2x2 grid

        # Clear the current grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Re-add images to the grid layout with the new size and grid configuration
        row = 0
        col = 0
        for image_label, pixmap in self.image_labels:
            cropped_pixmap = self.crop_center(pixmap)
            scaled_pixmap = cropped_pixmap.scaled(new_size, new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setFixedSize(new_size, new_size)

            # Add the image label to the grid layout
            self.grid_layout.addWidget(image_label, row, col)

            # Update column and row for the next image
            col += 1
            if col == max_columns:  # Move to the next row after reaching max columns
                col = 0
                row += 1


    def on_image_clicked(self, image_path):
        """Handle the image click event."""
        metadata = Get_MetaData.get_image_metadata(image_path)
        if "error" in metadata:
            self.img_info.setText(f"Error reading metadata:\n{metadata['error']}")
        else:
            from pprint import pformat
            pretty_metadata = pformat(metadata, indent=2)
            self.img_info.setText(f"Metadata for:\n{image_path}\n\n{pretty_metadata}")


    def on_image_double_clicked(self, image_path):
        """Handle the image double-click event."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Viewer - Double Click")
        image_label = QLabel(dialog)
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setFixedSize(pixmap.size() / 3)
        layout = QVBoxLayout(dialog)
        layout.addWidget(image_label)
        dialog.exec()


    def crop_center(self, pixmap):
        """Crop the center of a QPixmap to create a square crop based on the larger dimension."""
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        crop_size = min(pixmap_width, pixmap_height)
        x = (pixmap_width - crop_size) // 2
        y = (pixmap_height - crop_size) // 2
        return pixmap.copy(x, y, crop_size, crop_size)

        # Crop the image to a square
        return pixmap.copy(x, y, crop_size, crop_size)
    

    def open_import_dialog(self):
        """Open a file explorer to select a folder and return the folder path."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:  # If a folder is selected
            file_list = get_all_files_in_directory.get_all_files_in_directory(folder_path)  # Call the function to get all files in the directory
            print(f"Files in folder: {file_list}")  # Print the selected folder path
            return folder_path
        else:
            print("No folder selected.")  # Print a message if no folder is selected
            return None


    def open_export_dialog(self):
        """Open the Import  pop-up dialog."""
        dialog = export_dialog.ExportDialog(self)
        if dialog.exec():  # If the user clicks "OK"
            output_path = dialog.get_output_path()


    def open_change_tag_dialog(self):
        """Open the Import  pop-up dialog."""
        dialog = change_tag_dialog.ChangeTagDialog(self)
        if dialog.exec():  # If the user clicks "OK"
            output_path = dialog.get_output_path()


    def open_output_path_dialog(self):
        """Open the Output Path pop-up dialog."""
        dialog = output_dialog.OutputPathDialog(self)
        if dialog.exec():  # If the user clicks "OK"
            output_path = dialog.get_output_path()
            print(f"Output path set to: {output_path}")  # Handle the output path (e.g., save it)


    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            if obj == self.import_bnt:
                self.tool_tips.setText("Import images from a folder")
            elif obj == self.export_bnt:
                self.tool_tips.setText("Export sorted images")
            elif obj == self.checkDup_bnt:
                self.tool_tips.setText("Check for duplicate images")
            elif obj == self.changeTag_bnt:
                self.tool_tips.setText("Change tags for selected images")
            elif obj == self.outputPath_bnt:
                self.tool_tips.setText("Set the output path for exports")
            elif obj == self.small_size_btn:
                self.tool_tips.setText("Display images in small size (5x5 grid)")
            elif obj == self.medium_size_btn:
                self.tool_tips.setText("Display images in medium size (3x3 grid)")
            elif obj == self.large_size_btn:
                self.tool_tips.setText("Display images in large size (2x2 grid)")
            elif isinstance(obj, QRadioButton):
                self.tool_tips.setText("Display images in the selected tag category")
            elif any(obj == label for label, _ in self.image_labels):
                self.tool_tips.setText("Hovering over image")
            elif isinstance(obj, DragDropArea):
                self.tool_tips.setText("Drag and drop a folder here to import images")
        elif event.type() == QEvent.Leave:
            self.tool_tips.setText("Tool Tips")
        return super().eventFilter(obj, event)
    

    def show_duplicates_dialog(self):
        """Launch a dialog to show and delete detected duplicate images."""
        folder = self.image_dir
        all_files = get_all_files_in_directory.get_all_files_in_directory(folder)
        image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        duplicates = {}
        for i, img_path in enumerate(image_files):
            dups = file_utils.find_duplicate_images(img_path, folder)
            if dups:
                duplicates[img_path] = dups
        if not duplicates:
            QMessageBox.information(self, "No Duplicates Found", "No duplicate images were found.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Review and Delete Duplicates")
        dialog.resize(600, 400)
        layout = QVBoxLayout(dialog)
        self.dup_checkboxes = []
        for original, dup_list in duplicates.items():
            layout.addWidget(QLabel(f"Original: {os.path.basename(original)}"))
            for dup in dup_list:
                checkbox = QCheckBox(f"Delete Duplicate: {os.path.basename(dup)}")
                checkbox.setProperty("file_path", dup)
                self.dup_checkboxes.append(checkbox)
                layout.addWidget(checkbox)
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(lambda: self.delete_selected_duplicates(dialog))
        layout.addWidget(delete_btn)
        dialog.setLayout(layout)
        dialog.exec()

    def delete_selected_duplicates(self, dialog):
        """Delete files selected in the duplicate review dialog."""
        for cb in self.dup_checkboxes:
            if cb.isChecked():
                path = cb.property("file_path")
                try:
                    os.remove(path)
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")
        QMessageBox.information(self, "Deleted", "Selected duplicates have been deleted.")
        dialog.accept()
        self.refresh_image_grid()
