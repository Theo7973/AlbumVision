"""
    Main interface GUI for user to interact with Album Vison+.
    # Need to update the Tool tips, image size control, and image metadata display. #
"""
import sys
import os
from PySide6.QtWidgets import QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame
from PySide6.QtWidgets import QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QDialog, QPushButton
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal

"""
Custom drag-and-drop area for importing image folders.
"""
class DragDropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Enable drag-and-drop
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed gray;
                border-radius: 5px;
                background-color: #f9f9f9;
                font: bold 12px;
                color: #555;
                text-align: center;
            }
        """)
        self.setFixedWidth(300)  # Set a fixed width for the drag-and-drop area
        self.setFixedHeight(100)  # Set a fixed height for the drag-and-drop area

        # Add a QLabel to display the text
        self.label = QLabel("Drop Image Folder", self)
        self.label.setAlignment(Qt.AlignCenter)  # Center the text
        self.label.setStyleSheet("font-size: 20px; color: #555;border: none;")  # Style the text

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
                    print(f"Dropped folder path: {folder_path}")
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

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'logo.svg')
        self.setWindowIcon(QIcon(icon_path))

        # Main container widget
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # Create a vertical layout for the left-side widgets
        left_layout = QVBoxLayout()

        # Add a horizontal layout for the buttons (top left)
        func_button_layout = QHBoxLayout()
        self.import_bnt = QPushButton("Import", self)
        self.arrange_bnt = QPushButton("Arrange", self)
        self.checkDup_bnt = QPushButton("Check Duplicate", self)
        self.changeTag_bnt = QPushButton("Change Tag", self)
        self.outputPath_bnt = QPushButton("Output Path", self)
        

        # Add buttons to the layout
        func_button_layout.addWidget(self.import_bnt)
        func_button_layout.addWidget(self.arrange_bnt)
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

        btn_name_list = ['Animal', 'Cat', 'Dog', 'Person', 'Vehicle', 'Kitchenware', 'Appliance', 'Entertainment\n Device', 'Unknown']
        sorted_list = sorted(btn_name_list)  # Sorts alphabetically
        for i in range(1, 9 + 1):  # Create buttons for each tag name
            name = sorted_list[i-1]  # Get the name from the sorted list
            button = QRadioButton(f"{name}", self)
            button.setStyleSheet("font-size: 11px;")  # Set font size for the button
            button_group.addButton(button)  # Add the button to the group
            tab_btn_layout.addWidget(button)


        # Set the layout for the group box
        tag_btn_group_box.setLayout(tab_btn_layout)

        img_ctrl_layout.addWidget(tag_btn_group_box)  # Add the group box to the layout
        # Add the group box to the left layout
        left_layout.addLayout(img_ctrl_layout)

        
        # Create another QGroupBox for the slider
        slider_group_box = QGroupBox("Image Size Control")
        slider_group_box.setStyleSheet("""
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
        # Add a horizontal layout for the slider (below the buttons)
        slider_layout = QHBoxLayout()

        self.img_slider = QSlider(Qt.Horizontal, self)
        self.img_slider.setMinimum(0)
        self.img_slider.setMaximum(100)
        self.img_slider.setValue(50)  # Default value
        self.img_slider.setFixedWidth(150)  # Set the slider length to half of the current length
        self.img_slider.valueChanged.connect(self.update_image_sizes)  # Connect slider to function

        # Add the slider to the layout
        slider_layout.addWidget(self.img_slider)  
        
        # Set the layout for the group box
        slider_group_box.setLayout(slider_layout)  
        
        # Add the slider group box to the left layout
        img_ctrl_layout.addWidget(slider_group_box)
        left_layout.addLayout(img_ctrl_layout)


        # Create a QWidget to hold multiple QLabel widgets
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
                image_label.setFixedSize(220, 220)  # Default size
                self.grid_layout.addWidget(image_label, row, col)
                self.image_labels.append((image_label, pixmap))  # Store label and pixmap

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

        # Add the scroll area below the slider in the left layout
        left_layout.addWidget(self.scroll_area, 1)  # Stretch factor for resizing

        # Add the left layout to the main layout
        left_widget = QWidget(self)
        left_widget.setLayout(left_layout)
        left_widget.setFixedWidth(900)  # Set the width of the left widget
        main_layout.addWidget(left_widget)  # 70% width


        # Create a vertical layout for the right-side widgets
        right_layout = QVBoxLayout()

        # Add the drag-and-drop area to the top of the right layout
        drag_drop_area = DragDropArea(self)
        right_layout.addWidget(drag_drop_area)

        # Create a vertical layout for the text views
        info_layout = QVBoxLayout()

        # Create the first QLabel for the text view
        self.img_info = QLabel(self)
        self.img_info.setText("Image Info and Metadata")  # Set the text to display
        self.img_info.setWordWrap(True)  # Enable word wrapping for long text
        info_layout.addWidget(self.img_info, 4)  # 80% height

        # Create the second QLabel for the text view
        self.tool_tips = QLabel(self)
        self.tool_tips.setText("Tool Tips")  # Set the text to display
        self.tool_tips.setWordWrap(True)  # Enable word wrapping for long text
        info_layout.addWidget(self.tool_tips, 1)  # 20% height

        # Add the text view layout to the right layout
        text_view_widget = QWidget(self)
        text_view_widget.setLayout(info_layout)
        right_layout.addWidget(text_view_widget)

        # Add the right layout to the main layout
        right_widget = QWidget(self)
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(300)  # Set the width of the right widget
        main_layout.addWidget(right_widget)  # 30% width

        # Set the main layout as the central widget
        self.setCentralWidget(main_widget)

    def update_image_sizes(self):
        """Update the size of the images based on the slider value."""
        slider_value = self.img_slider.value()
        # Map slider value (0-100) to image size (30-500)
        new_size = 30 + int((slider_value / 100) * (500 - 30))
        for image_label, pixmap in self.image_labels:
            # Reapply the crop_center function to maintain the square crop
            cropped_pixmap = self.crop_center(pixmap)
            # Scale the cropped image to the new size while maintaining the aspect ratio
            scaled_pixmap = cropped_pixmap.scaled(new_size, new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setFixedSize(new_size, new_size)

    def on_image_clicked(self, image_path):
        """Handle the image click event."""
        self.img_info.setText(f"Clicked on: {image_path}")  # Update the text view with the image path

    def on_image_double_clicked(self, image_path):
        """Handle the image double-click event."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Image Viewer - Double Click")
        # dialog.resize(800, 600)  # Default size for the pop-up window

        # Create a QLabel to display the image
        image_label = QLabel(dialog)
        pixmap = QPixmap(image_path)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)  # Scale the image to fit the dialog
        image_label.setFixedSize(pixmap.size()/3)  # Set the label size to the original image size

        # Create a layout for the dialog
        layout = QVBoxLayout(dialog)
        layout.addWidget(image_label)

        # Show the dialog
        dialog.exec()

    def crop_center(self, pixmap):
        """Crop the center of a QPixmap to create a square crop based on the larger dimension."""
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()

        # Determine the size of the square crop (use the larger dimension)
        crop_size = min(pixmap_width, pixmap_height)

        # Calculate the top-left corner of the cropping rectangle
        x = (pixmap_width - crop_size) // 2
        y = (pixmap_height - crop_size) // 2

        # Crop the image to a square
        return pixmap.copy(x, y, crop_size, crop_size)