"""
    Main interface GUI for user to interact with Album Vison+.
    # Need to update the Tool tips, image size control, and image metadata display. #
"""
import sys
import os
from PySide6.QtWidgets import QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QDialog, QPushButton
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

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
        self.resize(1200, 800)

        # Main container widget
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        # Create a vertical layout for the left-side widgets
        left_layout = QVBoxLayout()

        # Add a horizontal layout for the buttons (above the slider)
        button_layout = QHBoxLayout()
        self.button1 = QPushButton("Import", self)
        self.button2 = QPushButton("Arrange", self)
        self.button3 = QPushButton("Check Duplicate", self)
        self.button4 = QPushButton("Output Path", self)

        # Add buttons to the layout
        button_layout.addWidget(self.button1)
        button_layout.addWidget(self.button2)
        button_layout.addWidget(self.button3)
        button_layout.addWidget(self.button4)

        # Add the button layout to the left layout
        left_layout.addLayout(button_layout)

        # Add a slider bar below the buttons
        slider_layout = QHBoxLayout()  # Create a horizontal layout for the slider
        slider_layout.addStretch()  # Add stretch to push the slider to the right

        self.img_slider = QSlider(Qt.Horizontal, self)
        self.img_slider.setMinimum(0)
        self.img_slider.setMaximum(100)
        self.img_slider.setValue(50)  # Default value
        self.img_slider.setFixedWidth(200)  # Set the slider length to half of the current length
        self.img_slider.valueChanged.connect(self.update_image_sizes)  # Connect slider to function

        slider_layout.addWidget(self.img_slider)  # Add the slider to the layout
        left_layout.addLayout(slider_layout)  # Add the slider layout to the left layout

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
                image_label.setPixmap(pixmap)
                image_label.setScaledContents(True)
                image_label.setFixedSize(200, 200)  # Default size
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
        main_layout.addWidget(left_widget, 7)  # 70% width

        # Create a vertical layout for the right-side widgets
        right_layout = QVBoxLayout()

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
        main_layout.addWidget(right_widget, 3)  # 30% width

        # Set the main layout as the central widget
        self.setCentralWidget(main_widget)

    def update_image_sizes(self):
        """Update the size of the images based on the slider value."""
        slider_value = self.img_slider.value()
        # Map slider value (0-100) to image size (30-500)
        new_size = 30 + int((slider_value / 100) * (500 - 30))
        for image_label, pixmap in self.image_labels:
            scaled_pixmap = pixmap.scaled(new_size, new_size, Qt.KeepAspectRatio)
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
