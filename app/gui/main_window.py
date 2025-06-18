
import sys
import os
import shutil
from functools import partial

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.utils.Auto_Sort_Basic import model
from app.utils.file_utils import map_coco_label_to_custom_tag

from PySide6.QtWidgets import (QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame, QFileDialog,
                               QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSlider, QDialog, QPushButton, QCheckBox, QMessageBox)
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, Signal, QEvent, QSize
from pprint import pformat

# Import using absolute imports with error handling
try:
    # Create dummy modules if they don't exist
    class DummyModule:
        @staticmethod
        def get_all_files_in_directory(path):
            """Get all files in directory - fallback implementation"""
            if not os.path.exists(path):
                return []
            files = []
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    files.append(file_path)
            return files
        
        @staticmethod
        def get_image_metadata(path):
            """Get image metadata - fallback implementation"""
            try:
                return {
                    "filename": os.path.basename(path),
                    "size": os.path.getsize(path),
                    "path": path
                }
            except:
                return {"error": "Could not read metadata"}
        
        @staticmethod
        def find_duplicate_images(image_path, folder):
            """Find duplicate images - fallback implementation"""
            return []
    
    try:
        from app.utils import filter_non_image_files
    except ImportError:
        filter_non_image_files = DummyModule()
    
    try:
        from app.utils import get_all_files_in_directory
    except ImportError:
        get_all_files_in_directory = DummyModule()
    
    try:
        from app.utils import Get_MetaData
    except ImportError:
        Get_MetaData = DummyModule()
    
    try:
        from app.utils import file_utils
    except ImportError:
        file_utils = DummyModule()
    
    try:
        from app.utils.image_quality import check_image_quality
    except ImportError:
        def check_image_quality(image_path, threshold=150):
            """Fallback image quality check"""
            try:
                # Simple file size based quality check
                size = os.path.getsize(image_path)
                if size > 500000:  # 500KB
                    return "high", 85.0, (1920, 1080)
                else:
                    return "low", 45.0, (640, 480)
            except:
                return "error", 0, (0, 0)
    
    try:
        from app.utils.path_settings import PathSettings
    except ImportError:
        class PathSettings:
            def __init__(self):
                self.output_path = ""
            def get_output_path(self):
                return self.output_path
            def set_output_path(self, path):
                self.output_path = path
                return True
    
    try:
        from app.gui.dialogs import export_dialog
    except ImportError:
        # Create a dummy export dialog
        class DummyExportDialog:
            class ExportDialog(QDialog):
                def __init__(self, parent=None, source_directory=None):
                    super().__init__(parent)
                    self.setWindowTitle("Export Dialog")
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Export functionality not available"))
                    ok_button = QPushButton("OK")
                    ok_button.clicked.connect(self.accept)
                    layout.addWidget(ok_button)
                    self.setLayout(layout)
                def get_output_path(self):
                    return ""
        export_dialog = DummyExportDialog()
    
    try:
        from app.gui.dialogs import change_tag_dialog
    except ImportError:
        class DummyChangeTagDialog:
            class ChangeTagDialog(QDialog):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Change Tag Dialog")
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Change tag functionality not available"))
                    ok_button = QPushButton("OK")
                    ok_button.clicked.connect(self.accept)
                    layout.addWidget(ok_button)
                    self.setLayout(layout)
                def get_output_path(self):
                    return ""
        change_tag_dialog = DummyChangeTagDialog()
    
    try:
        from app.gui.dialogs import output_dialog
    except ImportError:
        class DummyOutputDialog:
            class OutputPathDialog(QDialog):
                def __init__(self, parent=None):
                    super().__init__(parent)
                    self.setWindowTitle("Output Path Dialog")
                    layout = QVBoxLayout()
                    layout.addWidget(QLabel("Output path functionality not available"))
                    ok_button = QPushButton("OK")
                    ok_button.clicked.connect(self.accept)
                    layout.addWidget(ok_button)
                    self.setLayout(layout)
                def get_output_path(self):
                    return ""
        output_dialog = DummyOutputDialog()
        
except ImportError as e:
    print(f"Some imports failed: {e}")
    print("Running with limited functionality")


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
                    print(f"Dropped folder: {folder_path}")
                    
                    # Get all files in the directory
                    try:
                        img_files = get_all_files_in_directory.get_all_files_in_directory(folder_path)
                        print(f"File list in folder: {len(img_files)} files")
                    except:
                        img_files = []
                        print("Could not get file list")
                    
                    # Update the parent window's image directory and refresh the grid
                    parent_window = self.parent()
                    while parent_window and not isinstance(parent_window, ImageWindow):
                        parent_window = parent_window.parent()
                    if parent_window:
                        parent_window.load_images_from_directory(folder_path)
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
        self.setWindowTitle("Album Vision+ - Smart Image Organization")
        self.setFixedSize(1200, 800)  # Set the window to a fixed size
        self.image_dir = image_dir
        self.path_settings = PathSettings()  # Initialize path settings

        # Initialize essential attributes early
        self.img_info = None
        self.tool_tips = None
        self.image_labels = []
        self.button_group = QButtonGroup(self)
        self.selection_mode = False
        self.selected_images = []
        

        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'ab_logo.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main container widget
        main_widget = QWidget(self)

        # Create the outer vertical layout
        outer_layout = QVBoxLayout(main_widget)

        # Create your main horizontal layout (for left/right panels)
        main_layout = QHBoxLayout()

        # Create a vertical layout for the left-side widgets
        left_layout = QVBoxLayout()

        # Add a horizontal layout for the buttons (top left)
        func_button_layout = QHBoxLayout()
        self.import_bnt = QPushButton("Import", self)
        self.export_bnt = QPushButton("Export", self)
        self.checkDup_bnt = QPushButton("Check Duplicate", self)
        self.changeTag_bnt = QPushButton("Change Tag", self)
        self.outputPath_bnt = QPushButton("Output Path", self)
        self.select_mode_btn = QPushButton("Select Images", self)
        self.select_mode_btn.setCheckable(True)
        self.select_mode_btn.clicked.connect(self.toggle_selection_mode)
       
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
        func_button_layout.addWidget(self.select_mode_btn)
        self.delete_selected_btn = QPushButton("Delete Selected", self)
        self.delete_selected_btn.clicked.connect(self.delete_selected_images)
        self.delete_selected_btn.setVisible(False)  # Only visible in selection mode
        left_layout.addWidget(self.delete_selected_btn)


        # Add the button layout to the left layout
        left_layout.addLayout(func_button_layout)

        # Create a QGroupBox for the tag buttons
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

        btn_name_list = ['Animal', 'Cat', 'Dog', 'Person', 'Vehicle', 'Kitchenware', 'Appliance', 'Entertainment\n Device']
        sorted_list = sorted(btn_name_list)  # Sorts alphabetically
        sorted_list.append('Unknown')
        for name in sorted_list:
            button = QRadioButton(f"{name}", self)
            button.setStyleSheet("font-size: 11px;")  # Set font size for the button
            self.button_group.addButton(button)  # Add the button to the group
            tab_btn_layout.addWidget(button)
            button.installEventFilter(self)  # Install event filter for the button
        
        self.button_group.buttonClicked.connect(self.handle_tag_button_click)    

        # Set the layout for the group box
        tag_btn_group_box.setLayout(tab_btn_layout)

        img_ctrl_layout.addWidget(tag_btn_group_box)  # Add the group box to the layout
        left_layout.addLayout(img_ctrl_layout)

        # Create another QGroupBox for the size control radio buttons
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

        # Load images from the initial directory
        self.load_images_from_directory(image_dir)

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


        # Create a vertical layout for the right-side widgets
        right_layout = QVBoxLayout()
        right_layout.addWidget(drag_drop_area)  # Align to the top

       

        # Create a vertical layout for the text views
        info_layout = QVBoxLayout()

        # Create the first QLabel for the text view
        self.img_info = QLabel(self)
        self.img_info.setText("Image Info and Metadata")  # Set the text to display
        self.img_info.setWordWrap(True)  # Enable word wrapping for long text
        info_layout.addWidget(self.img_info, 4)  # 80% height

    

        # Add the text view layout to the right layout
        text_view_widget = QWidget(self)
        text_view_widget.setLayout(info_layout)
        right_layout.addWidget(text_view_widget)

        # Add the right layout to the main layout
        right_widget = QWidget(self)
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(300)  # Set the width of the right widget
        main_layout.addWidget(right_widget)  # 30% width

        # Add the main_layout (left/right panels) to the outer_layout
        outer_layout.addLayout(main_layout)

        # --- Add the tool tip label at the bottom of the window ---
        self.tool_tips = QLabel(self)
        self.tool_tips.setText("Tool Tips")
        self.tool_tips.setWordWrap(True)
        outer_layout.addWidget(self.tool_tips)

        self.import_bnt.clicked.connect(self.open_import_dialog)
        self.export_bnt.clicked.connect(self.open_export_dialog)
        self.checkDup_bnt.clicked.connect(self.show_duplicates_dialog)
        self.changeTag_bnt.clicked.connect(self.open_change_tag_dialog)
        self.outputPath_bnt.clicked.connect(self.open_output_path_dialog)
    

        # Set the main widget as the central widget
        self.setCentralWidget(main_widget)
    
    def handle_tag_button_click(self, button):
        tag = button.text().strip().lower().replace("\n", " ")  # Normalize the tag name
        self.filter_images_by_tag(tag)    
        
    def toggle_selection_mode(self):
        """Enable or disable selection mode for deleting images."""
        self.selection_mode = self.select_mode_btn.isChecked()
        self.selected_images = []
        self.delete_selected_btn.setVisible(self.selection_mode)

        if self.selection_mode:
            self.select_mode_btn.setText("Exit Selection Mode")
            self.tool_tips.setText("Click the checkboxes below images to select them for deletion.")
        else:
            self.select_mode_btn.setText("Select Images")
            self.tool_tips.setText("Tool Tips")

        self.load_images_from_directory(self.image_dir)
        
    def update_selected_images(self, state):
        checkbox = self.sender()
        file_path = checkbox.property("file_path")

        if file_path is None:
            print("Checkbox missing file_path property")
            return

        if state == Qt.Checked:
            if file_path not in self.selected_images:
                self.selected_images.append(file_path)
        else:
            if file_path in self.selected_images:
                self.selected_images.remove(file_path) 
                

    def load_images_from_directory(self, directory):
        """Load images from a directory and populate the grid with optional checkboxes."""
        self.image_dir = directory

        # Clear existing images
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        self.image_labels.clear()

        # Load all image files from the directory
        row = 0
        col = 0
        image_count = 0

        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                    image_path = os.path.join(directory, file_name)
                    try:
                        image_widget = QWidget()
                        layout = QVBoxLayout(image_widget)
                        layout.setAlignment(Qt.AlignCenter)

                        image_label = ClickableLabel(self)
                        pixmap = QPixmap(image_path)

                        if not pixmap.isNull():
                            crop_center = self.crop_center(pixmap)
                            image_label.setPixmap(crop_center)
                            image_label.setScaledContents(True)
                            image_label.setFixedSize(260, 260)
                            layout.addWidget(image_label)

                            image_label.installEventFilter(self)
                            image_label.clicked.connect(lambda path=image_path: self.on_image_clicked(path))
                            image_label.doubleClicked.connect(lambda path=image_path: self.on_image_double_clicked(path))

                            # Get custom tag using the model
                            try:
                                results = model(image_path, verbose=False)
                                coco_tags = set(model.names[int(box.cls[0])] for box in results[0].boxes)
                                tag = map_coco_label_to_custom_tag(list(coco_tags)[0]) if coco_tags else "Unknown"
                            except:
                                tag = "Unknown"

                            # --- Add checkbox if selection mode is active ---
                            if self.selection_mode:
                                checkbox = QCheckBox("Select")
                                checkbox.setStyleSheet("margin-left: 5px; font-size: 10px;")
                                checkbox.setProperty("file_path", image_path)
                                checkbox.stateChanged.connect(self.update_selected_images)

                                if image_path in self.selected_images:
                                    checkbox.setChecked(True)

                                layout.addWidget(checkbox)
                                self.image_labels.append((image_label, pixmap, image_path, checkbox, tag))
                            else:
                                layout.addSpacing(20)
                                self.image_labels.append((image_label, pixmap, image_path, None, tag))

                            self.grid_layout.addWidget(image_widget, row, col)
                            col += 1
                            image_count += 1
                            if col == 3:
                                col = 0
                                row += 1
                    except Exception as e:
                        print(f"Error loading image {image_path}: {e}")

        # Update the tool tips
        if image_count > 0 and self.tool_tips:
            self.tool_tips.setText(f"Loaded {image_count} images from {os.path.basename(directory)}")
        elif self.tool_tips:
            self.tool_tips.setText("No images found in the selected directory")
            
          
                
    def delete_selected_images(self):
        """Delete all selected images from disk and refresh the grid."""
        if not self.selected_images:
            QMessageBox.information(self, "No Selection", "No images selected for deletion.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {len(self.selected_images)} selected image(s)?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if confirm == QMessageBox.Yes:
            deleted_count = 0
            for path in self.selected_images:
                try:
                    os.remove(path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {path}: {e}")

            self.selected_images = []
            self.load_images_from_directory(self.image_dir)

            QMessageBox.information(
                self, "Deleted", f"Deleted {deleted_count} image(s) successfully."
            )           

    def update_image_sizes(self, size):
        """Update the size of the images and grid layout based on the selected size."""
        if size == "Small":
            new_size = 160  # Small size
            max_columns = 5  # 5 columns
        elif size == "Medium":
            new_size = 260  # Medium size (default)
            max_columns = 3  # 3 columns
        elif size == "Large":
            new_size = 400  # Large size
            max_columns = 2  # 2 columns

        # Clear the current grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Re-add images to the grid layout with the new size and grid configuration
        row = 0
        col = 0
        for image_label, pixmap, image_path, checkbox in self.image_labels:
            cropped_pixmap = self.crop_center(pixmap)
            scaled_pixmap = cropped_pixmap.scaled(new_size, new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            image_label.setFixedSize(new_size, new_size)

            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setAlignment(Qt.AlignCenter)
            layout.addWidget(image_label)

            if self.selection_mode and checkbox:
                layout.addWidget(checkbox)

            self.grid_layout.addWidget(container, row, col)
            col += 1
            if col == max_columns:
                col = 0
                row += 1

    def on_image_clicked(self, image_path):
        """Handle the image click event with enhanced metadata, quality info, and simplified tags."""
        try:
            # Get basic metadata
            if hasattr(Get_MetaData, 'get_image_metadata'):
                metadata = Get_MetaData.get_image_metadata(image_path)
            else:
                metadata = {
                    "filename": os.path.basename(image_path),
                    "size": os.path.getsize(image_path),
                    "path": image_path
                }
            
            # Check image quality
            quality, score, dimensions = check_image_quality(image_path)

            # --- NEW PART: Run YOLOv8 and map to custom tags ---
            try:
                from ultralytics import YOLO
                model = YOLO("yolov8n.pt")

                def map_coco_label_to_custom_tag(label):
                    mapping = {
                        "person": "person",
                        "cat": "cat",
                        "dog": "dog",
                        "car": "vehicle",
                        "bus": "vehicle",
                        "truck": "vehicle",
                        "bicycle": "vehicle",
                        "motorcycle": "vehicle",
                        "airplane": "vehicle",
                        "train": "vehicle",
                        "knife": "kitchenware",
                        "fork": "kitchenware",
                        "spoon": "kitchenware",
                        "bowl": "kitchenware",
                        "refrigerator": "appliance",
                        "microwave": "appliance",
                        "oven": "appliance",
                        "toaster": "appliance",
                        "tv": "entertainment device",
                        "laptop": "entertainment device",
                        "cell phone": "entertainment device",
                        "mouse": "entertainment device",
                        "keyboard": "entertainment device",
                        "remote": "entertainment device",
                        "bear": "animal",
                        "zebra": "animal",
                        "elephant": "animal",
                        "sheep": "animal",
                        "cow": "animal",
                        "horse": "animal",
                        "bird": "animal",
                        "giraffe": "animal"
                    }
                    return mapping.get(label.lower(), "unknown")

                results = model(image_path, verbose=False)
                tags_detected = set()

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    coco_label = model.names[cls_id]
                    custom_tag = map_coco_label_to_custom_tag(coco_label)
                    tags_detected.add(custom_tag)

            except Exception as model_error:
                tags_detected = {"unknown"}
                print(f"YOLO model error: {model_error}")

            # -------------------------------------------------

            if isinstance(metadata, dict) and "error" in metadata:
                self.img_info.setText(f"Error reading metadata:\n{metadata['error']}")
            else:
                # Enhanced metadata display with quality information
                info_text = f"File: {os.path.basename(image_path)}\n\n"
                
                # Basic file info
                try:
                    file_size = os.path.getsize(image_path)
                    info_text += f"Size: {file_size:,} bytes\n"
                    info_text += f"Path: {image_path}\n\n"
                except:
                    pass
                
                # Quality analysis
                info_text += "Quality Analysis:\n"
                info_text += f"Quality: {quality.upper()}\n"
                info_text += f"Score: {score:.2f}\n"
                info_text += f"Dimensions: {dimensions[0]} x {dimensions[1]}\n\n"

                # Display simplified tags
                info_text += f"Detected Tags: {', '.join(tags_detected)}\n\n"
                
                # Additional metadata if available
                if isinstance(metadata, dict):
                    info_text += "Additional Metadata:\n"
                    for key, value in metadata.items():
                        info_text += f"{key}: {value}\n"
                
                self.img_info.setText(info_text)
        except Exception as e:
            self.img_info.setText(f"Error processing image:\n{str(e)}")

    def on_image_double_clicked(self, image_path):
        """Handle the image double-click event."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("Image Viewer")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            image_label = QLabel(dialog)
            pixmap = QPixmap(image_path)
            
            if not pixmap.isNull():
                # Scale the image to fit in a reasonable window size
                max_size = 800
                if pixmap.width() > max_size or pixmap.height() > max_size:
                    pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                image_label.setPixmap(pixmap)
                image_label.setAlignment(Qt.AlignCenter)
            else:
                image_label.setText("Could not load image")
                image_label.setAlignment(Qt.AlignCenter)
            
            layout.addWidget(image_label)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            
            dialog.setLayout(layout)
            dialog.resize(pixmap.width() + 50, pixmap.height() + 100)
            dialog.exec()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open image: {str(e)}")

    def crop_center(self, pixmap):
        """Crop the center of a QPixmap to create a square crop based on the smaller dimension."""
        if pixmap.isNull():
            return pixmap
            
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        crop_size = min(pixmap_width, pixmap_height)
        x = (pixmap_width - crop_size) // 2
        y = (pixmap_height - crop_size) // 2
        return pixmap.copy(x, y, crop_size, crop_size)

    def open_import_dialog(self):
        """Open a file explorer to select a folder and return the folder path."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder_path:  # If a folder is selected
            print(f"Selected folder: {folder_path}")
            
            # Load images from the selected folder
            self.load_images_from_directory(folder_path)
            
            # Update tool tips to show folder loaded
            if self.tool_tips:
                self.tool_tips.setText(f"Loaded folder: {os.path.basename(folder_path)}")
            
            return folder_path
        else:
            print("No folder selected.")
            return None

    def open_export_dialog(self):
        """Open the Export dialog with enhanced functionality."""
        try:
            # Check if output path is set
            output_path = self.path_settings.get_output_path()
            if not output_path:
                reply = QMessageBox.question(
                    self, 
                    "No Output Path", 
                    "No output path is set. Would you like to set one now?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.open_output_path_dialog()
                    return
                else:
                    return
                
            dialog = export_dialog.ExportDialog(self, self.image_dir)
            if dialog.exec():  # If the user clicks "OK"
                export_path = dialog.get_output_path()
                print(f"Images exported to: {export_path}")
                # Update status in the UI
                if self.tool_tips:
                    self.tool_tips.setText(f"Export completed to: {os.path.basename(export_path)}")
        except Exception as e:
            QMessageBox.information(self, "Export", f"Export functionality: {str(e)}")

    def open_change_tag_dialog(self):
        """Open the Change Tag dialog."""
        try:
            dialog = change_tag_dialog.ChangeTagDialog(self)
            if dialog.exec():  # If the user clicks "OK"
                output_path = dialog.get_output_path()
                if self.tool_tips:
                    self.tool_tips.setText("Tag changes applied")
        except Exception as e:
            QMessageBox.information(self, "Change Tag", f"Change tag functionality: {str(e)}")

    def open_output_path_dialog(self):
        """Open the Output Path dialog with enhanced functionality."""
        try:
            dialog = output_dialog.OutputPathDialog(self)
            if dialog.exec():  # If the user clicks "OK"
                output_path = dialog.get_output_path()
                print(f"Output path set to: {output_path}")
                # Update any UI elements that show the output path
                if self.tool_tips:
                    self.tool_tips.setText(f"Output path: {os.path.basename(output_path)}")
        except Exception as e:
            # Fallback - simple path selection
            folder_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if folder_path:
                self.path_settings.set_output_path(folder_path)
                if self.tool_tips:
                    self.tool_tips.setText(f"Output path: {os.path.basename(folder_path)}")

    def get_selected_tag(self):
        """Get the currently selected tag from radio buttons."""
        button = self.button_group.checkedButton()
        if button:
            return button.text().replace('\n', '_')  # Handle multi-line button text
        return "Unknown"  # Default if no tag is selected

    def process_images_with_quality_check(self, image_files, output_path):
        """
        Process images, check their quality, and move them to appropriate folders.
        
        Args:
            image_files (list): List of image file paths
            output_path (str): Base output path for sorted images
        """
        # Get selected tag
        tag = self.get_selected_tag()
        
        # Track stats
        processed = 0
        high_quality = 0
        low_quality = 0
        errors = 0
        
        # Process each image
        for img_path in image_files:
            try:
                # Check image quality
                quality, score, dimensions = check_image_quality(img_path)
                
                if quality == "error":
                    errors += 1
                    continue
                    
                # Determine target folder based on tag and quality
                if tag == "Unknown":
                    # If tag is unknown, use quality as the determining factor
                    if quality == "high":
                        target_folder = os.path.join(output_path, "High_Quality")
                        high_quality += 1
                    else:
                        target_folder = os.path.join(output_path, "Low_Quality")
                        low_quality += 1
                else:
                    # If tag is known, use both tag and quality
                    if quality == "high":
                        target_folder = os.path.join(output_path, tag, "High_Quality")
                        high_quality += 1
                    else:
                        target_folder = os.path.join(output_path, tag, "Low_Quality")
                        low_quality += 1
                
                # Create target folder if it doesn't exist
                os.makedirs(target_folder, exist_ok=True)
                
                # Copy the image to the target folder
                filename = os.path.basename(img_path)
                target_path = os.path.join(target_folder, filename)
                
                try:
                    # Copy the file (use shutil.move to move instead)
                    shutil.copy2(img_path, target_path)
                    processed += 1
                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                    errors += 1
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                errors += 1
        
        # Show results
        QMessageBox.information(
            self,
            "Processing Complete",
            f"Processed: {processed} images\n"
            f"High quality: {high_quality}\n"
            f"Low quality: {low_quality}\n"
            f"Errors: {errors}"
        )

    def refresh_image_grid(self):
        """Refresh the image grid after changes."""
        self.load_images_from_directory(self.image_dir)

    def eventFilter(self, obj, event):
        """Enhanced event filter with updated tool tips."""
        try:
            # Check if tool_tips exists before using it
            if not hasattr(self, 'tool_tips') or self.tool_tips is None:
                return super().eventFilter(obj, event)
                
            if event.type() == QEvent.Enter:
                if hasattr(self, 'import_bnt') and obj == self.import_bnt:
                    self.tool_tips.setText("Import images from a folder - supports drag and drop")
                elif hasattr(self, 'export_bnt') and obj == self.export_bnt:
                    self.tool_tips.setText("Export sorted images to category folders with quality filtering")
                elif hasattr(self, 'checkDup_bnt') and obj == self.checkDup_bnt:
                    self.tool_tips.setText("Check for duplicate images and remove them")
                elif hasattr(self, 'changeTag_bnt') and obj == self.changeTag_bnt:
                    self.tool_tips.setText("Change tags for selected images")
                elif hasattr(self, 'outputPath_bnt') and obj == self.outputPath_bnt:
                    try:
                        current_path = self.path_settings.get_output_path()
                        if current_path:
                            self.tool_tips.setText(f"Current output: {os.path.basename(current_path)} - Click to change")
                        else:
                            self.tool_tips.setText("Set the output path for sorted images")
                    except:
                        self.tool_tips.setText("Set the output path for sorted images")
                elif hasattr(self, 'small_size_btn') and obj == self.small_size_btn:
                    self.tool_tips.setText("Display images in small size (5x5 grid)")
                elif hasattr(self, 'medium_size_btn') and obj == self.medium_size_btn:
                    self.tool_tips.setText("Display images in medium size (3x3 grid)")
                elif hasattr(self, 'large_size_btn') and obj == self.large_size_btn:
                    self.tool_tips.setText("Display images in large size (2x2 grid)")
                elif isinstance(obj, QRadioButton):
                    self.tool_tips.setText(f"Filter images by {obj.text()} category")
                elif hasattr(self, 'image_labels') and any(obj == label for label, _, _ in self.image_labels):
                    self.tool_tips.setText("Click for metadata and quality info, double-click to view larger")
                elif isinstance(obj, DragDropArea):
                    self.tool_tips.setText("Drag and drop a folder here to import images")
            elif event.type() == QEvent.Leave:
                self.tool_tips.setText("Tool Tips")
        except Exception as e:
            print(f"Event filter error: {e}")
            
        return super().eventFilter(obj, event)
    
    def show_duplicates_dialog(self):
            """Launch a dialog to show and delete detected duplicate images with previews."""
            try:
                folder = self.image_dir

                all_files = get_all_files_in_directory.get_all_files_in_directory(folder)
                image_files = [f for f in all_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]

                if not image_files:
                    QMessageBox.information(self, "No Images", "No image files found in the current directory.")
                    return

                duplicates = {}
                seen_sizes = {}
                for img_path in image_files:
                    try:
                        size = os.path.getsize(img_path)
                        if size in seen_sizes:
                            orig = seen_sizes[size]
                            duplicates.setdefault(orig, []).append(img_path)
                        else:
                            seen_sizes[size] = img_path
                    except:
                        continue

                if not duplicates:
                    QMessageBox.information(self, "No Duplicates Found", "No duplicate images were found.")
                    return

                dialog = QDialog(self)
                dialog.setWindowTitle("Review and Delete Duplicates")
                dialog.resize(700, 500)

                main_layout = QVBoxLayout(dialog)
                main_layout.addWidget(QLabel(f"Found {len(duplicates)} sets of potential duplicates:"))

                scroll = QScrollArea()
                scroll_widget = QWidget()
                scroll_layout = QVBoxLayout(scroll_widget)

                self.dup_checkboxes = []

                for original, dup_list in duplicates.items():
                    scroll_layout.addWidget(QLabel(f"Original: {os.path.basename(original)}"))
                    orig_img = QLabel()
                    orig_img.setPixmap(QPixmap(original).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    scroll_layout.addWidget(orig_img)

                    for dup in dup_list:
                        dup_img = QLabel()
                        dup_img.setPixmap(QPixmap(dup).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                        scroll_layout.addWidget(dup_img)

                        cb = QCheckBox(f"Delete Duplicate: {os.path.basename(dup)}")
                        cb.setProperty("file_path", dup)
                        self.dup_checkboxes.append(cb)
                        scroll_layout.addWidget(cb)

                    scroll_layout.addSpacing(20)

                scroll.setWidget(scroll_widget)
                scroll.setWidgetResizable(True)
                main_layout.addWidget(scroll)

                btn_layout = QHBoxLayout()
                delete_btn = QPushButton("Delete Selected")
                cancel_btn = QPushButton("Cancel")
                delete_btn.clicked.connect(lambda: self.delete_selected_duplicates(dialog))
                cancel_btn.clicked.connect(dialog.reject)
                btn_layout.addWidget(cancel_btn)
                btn_layout.addWidget(delete_btn)
                main_layout.addLayout(btn_layout)

                dialog.setLayout(main_layout)
                dialog.exec()

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error checking for duplicates: {str(e)}")
    
    def delete_selected_duplicates(self, dialog):
        """Delete files selected in the duplicate review dialog."""
        deleted_count = 0
        error_count = 0

        for cb in self.dup_checkboxes:
            if cb.isChecked():
                path = cb.property("file_path")
                try:
                    os.remove(path)
                    deleted_count += 1
                    print(f"Deleted: {path}")
                except Exception as e:
                    error_count += 1
                    print(f"Failed to delete {path}: {e}")

        if deleted_count > 0:
            QMessageBox.information(
                self,
                "Deletion Complete",
                f"Deleted {deleted_count} duplicate file(s).\nErrors: {error_count}"
            )
            self.refresh_image_grid()
        else:
            QMessageBox.information(self, "No Action", "No files were selected for deletion.")

        dialog.accept()   
        
                 
    def map_coco_label_to_custom_tag(label):
        mapping = {
            "person": "person",
            "cat": "cat",
            "dog": "dog",
            "car": "vehicle",
            "bus": "vehicle",
            "truck": "vehicle",
            "bicycle": "vehicle",
            "motorcycle": "vehicle",
            "airplane": "vehicle",
            "train": "vehicle",
            "knife": "kitchenware",
            "fork": "kitchenware",
            "spoon": "kitchenware",
            "bowl": "kitchenware",
            "refrigerator": "appliance",
            "microwave": "appliance",
            "oven": "appliance",
            "toaster": "appliance",
            "tv": "entertainment device",
            "laptop": "entertainment device",
            "cell phone": "entertainment device",
            "mouse": "entertainment device",
            "keyboard": "entertainment device",
            "remote": "entertainment device",
            "bear": "animal",
            "zebra": "animal",
            "elephant": "animal",
            "sheep": "animal",
            "cow": "animal",
            "horse": "animal",
            "bird": "animal",
            "giraffe": "animal",
            "dog": "dog",
            "cat": "cat"
        }
        return mapping.get(label.lower(), "unknown")    
    
    
    def filter_images_by_tag(self, target_tag):
        """Filter and display images that match the selected custom tag."""
        # Clear current grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        row = 0
        col = 0
        match_count = 0

        for image_data in self.image_labels:
            # image_data format: (label, pixmap, path, checkbox, tag)
            if len(image_data) < 5:
                continue  # Skip malformed entries

            image_label, pixmap, image_path, checkbox, tag = image_data
            if tag == target_tag:
                try:
                    image_widget = QWidget()
                    layout = QVBoxLayout(image_widget)
                    layout.setAlignment(Qt.AlignCenter)

                    image_label = ClickableLabel(self)
                    image_label.setPixmap(pixmap)
                    image_label.setScaledContents(True)
                    image_label.setFixedSize(260, 260)
                    layout.addWidget(image_label)

                    image_label.clicked.connect(lambda path=image_path: self.on_image_clicked(path))
                    image_label.doubleClicked.connect(lambda path=image_path: self.on_image_double_clicked(path))

                    self.grid_layout.addWidget(image_widget, row, col)
                    col += 1
                    match_count += 1
                    if col == 3:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error displaying filtered image {image_path}: {e}")

        if self.tool_tips:
            self.tool_tips.setText(f"Filtered to {match_count} images under tag: {target_tag}")