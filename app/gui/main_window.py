import sys
import os
import shutil
import cv2 
import numpy as np
from functools import partial
import importlib

def do_something():
    from app.gui.main_window import ImageWindow

    class SettingsDialog:
        def __init__(self, parent=None):
            pass
        def exec(self):
            return False

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from app.gui.dialogs.statistics_dialog import StatisticsDialog
from app.utils.Auto_Sort_Basic import model
from app.utils.file_utils import map_coco_label_to_custom_tag
from app.utils.Auto_Sort_Basic import model
from app.utils.file_utils import map_coco_label_to_custom_tag
from app.gui.widgets.card_gallery_widget import CardGalleryWidget
from app.gui.widgets.swipe_viewer import SwipeImageViewer

from PySide6.QtWidgets import (QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame, QFileDialog,
                               QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSlider, QDialog, QPushButton, QCheckBox, QMessageBox, QSplashScreen, QGraphicsOpacityEffect)
from PySide6.QtGui import QPixmap, QIcon, QMovie, QGuiApplication, QPainter, QFont
from PySide6.QtCore import Qt, Signal, QEvent, QSize, QTimer, QPropertyAnimation, QCoreApplication
from pprint import pformat


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
class HistogramCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 2.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        # --- Set dark theme for the histogram initially ---
        self.fig.patch.set_facecolor('#232629')  # Figure background
        self.ax.set_facecolor('#232629')         # Axes background
        self.ax.tick_params(axis='both', colors='white', labelsize=6)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.set_title('RGB Histogram', fontsize=8)
        self.ax.set_xlabel('Pixel Value', fontsize=6)
        self.ax.set_ylabel('Frequency', fontsize=6)
        self.ax.grid(True, color='#444444')
        self.fig.tight_layout()
        self.fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.15)
        self.draw()
    def plot_rgb_histogram(self, image_path):
        # Load and convert image to RGB
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Clear previous plot
        self.ax.clear()

        # --- Set dark theme for the histogram (again, for redraw) ---
        self.fig.patch.set_facecolor('#232629')
        self.ax.set_facecolor('#232629')
        self.ax.tick_params(axis='both', colors='white', labelsize=6)
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        self.ax.set_title('RGB Histogram', fontsize=8)
        self.ax.set_xlabel('Pixel Value', fontsize=6)
        self.ax.set_ylabel('Frequency', fontsize=6)
        self.ax.grid(True, color='#444444')
        # -----------------------------------------------------------

        # Plot RGB channels
        colors = ('red', 'green', 'blue')
        for i, color in enumerate(colors):
            hist = cv2.calcHist([image_rgb], [i], None, [256], [0, 256])
            self.ax.plot(hist, color=color)
        self.fig.tight_layout()
        self.fig.subplots_adjust(left=0.18, right=0.98, top=0.9, bottom=0.15)
        self.draw()
        

class DragDropArea(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # Enable drag-and-drop
        self.setStyleSheet("""
    QDialog {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QGroupBox {
        font-weight: bold;
        border: 2px solid #555555;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 10px;
        background-color: #3d3d3d;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
        padding: 5px 0px;  /* INCREASED PADDING */
        margin: 3px 0px;   /* ADDED MARGIN */
        line-height: 20px; /* FIXED LINE HEIGHT */
    }
    QPushButton {
        background-color: #404040;
        border: 1px solid #606060;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #505050;
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
    def apply_modern_styling(self):
        """Apply refined, professional styling to the application"""
        app_style = """
        QMainWindow {
            background-color: #1a1a2e;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: normal;
            color: #e0e0e0;
            min-height: 18px;
        }
        
        QPushButton:hover {
            background-color: #383838;
            border-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #252525;
            border-color: #606060;
        }
        
        QPushButton:checked {
            background-color: #1e4d5b;
            border-color: #2b6a7a;
        }
        
        QGroupBox {
            font-weight: 500;
            font-size: 11px;
            border: 1px solid #404040;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 6px;
            color: #e0e0e0;
            background-color: #232323;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 6px 0 6px;
            color: #b0b0b0;
            background-color: #1a1a1a;
        }
        
        QRadioButton {
            color: #e0e0e0;
            font-size: 10px;
            spacing: 6px;
            padding: 3px;
        }
        
        QRadioButton::indicator {
            width: 12px;
            height: 12px;
            border-radius: 6px;
            border: 1px solid #606060;
            background-color: #2d2d2d;
        }
        
        QRadioButton::indicator:hover {
            border-color: #707070;
        }
        
        QRadioButton::indicator:checked {
            background-color: #4a7c59;
            border-color: #5a8c69;
        }
        
        QCheckBox {
            color: #e0e0e0;
            font-size: 9px;
            spacing: 4px;
        }
        
        QCheckBox::indicator {
            width: 12px;
            height: 12px;
            border: 1px solid #606060;
            border-radius: 2px;
            background-color: #2d2d2d;
        }
        
        QCheckBox::indicator:hover {
            border-color: #707070;
        }
        
        QCheckBox::indicator:checked {
            background-color: #4a7c59;
            border-color: #5a8c69;
        }
        
        QLabel {
            color: #e0e0e0;
            font-size: 11px;
        }
        
        QScrollArea {
            border: 1px solid #404040;
            border-radius: 3px;
            background-color: #232323;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #505050;
            border-radius: 5px;
            min-height: 15px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #606060;
        }
        
        QFrame#dragDropFrame {
            border: 2px dashed #505050;
            border-radius: 6px;
            background-color: #232323;
        }
        
        QFrame#dragDropFrame:hover {
            border-color: #707070;
            background-color: #282828;
        }
        """
        self.setStyleSheet(app_style)

    def __init__(self):  
        super().__init__()
        self.setWindowTitle("Album Vision+ - Smart Image Organization")
        self.setFixedSize(1200, 800)  # Set the window to a fixed size
        self.image_dir = ""
        self.path_settings = PathSettings()  # Initialize path settings

        # Initialize essential attributes early
        self.img_info = None
        self.tool_tips = None
        self.image_labels = []
        self.button_group = QButtonGroup(self)
        self.selection_mode = False
        self.selected_images = []
        self.TAG = "all"
        self.display_size = "Medium"
        self._import_splash = None
        self._import_total = 0  
        self.card_gallery = None
        self.current_view = "grid"  # "grid" or "card"
        self.current_images_data = []  
        # Set the window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'ab_logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Main container widget
        self.main_widget = QWidget(self)
        main_widget = self.main_widget

        # Create the outer vertical layout
        outer_layout = QVBoxLayout(main_widget)

        # Create your main horizontal layout (for left/right panels)
        main_layout = QHBoxLayout()

        # Create a vertical layout for the left-side widgets
        self.left_layout = QVBoxLayout()
        left_layout = self.left_layout

        # Add a horizontal layout for the buttons (top left)
        func_button_layout = QHBoxLayout()
        self.import_bnt = QPushButton("Import", self)
        self.export_bnt = QPushButton("Export", self)
        self.checkDup_bnt = QPushButton("Check Duplicate", self)
        self.outputPath_bnt = QPushButton("Output Path", self)
        self.select_mode_btn = QPushButton("Select Images", self)
        self.settings_btn = QPushButton("Settings", self)
        self.statistics_btn = QPushButton("Statistics", self)

        self.select_mode_btn.setCheckable(True)  # Make it a toggle button

        # install event filter on the buttons
        self.import_bnt.installEventFilter(self)
        self.export_bnt.installEventFilter(self)
        self.checkDup_bnt.installEventFilter(self)
        self.outputPath_bnt.installEventFilter(self)
        self.settings_btn.installEventFilter(self)
        self.statistics_btn.installEventFilter(self)  # Add event filter

        func_button_layout.addWidget(self.import_bnt)
        func_button_layout.addWidget(self.export_bnt)
        func_button_layout.addWidget(self.checkDup_bnt)
        func_button_layout.addWidget(self.outputPath_bnt)
        func_button_layout.addWidget(self.select_mode_btn)
        func_button_layout.addWidget(self.settings_btn)
        func_button_layout.addWidget(self.statistics_btn) 
        self.view_toggle_btn = QPushButton("Card View", self)
        self.view_toggle_btn.installEventFilter(self)
        func_button_layout.addWidget(self.view_toggle_btn)
        self.delete_selected_btn = QPushButton("Delete Selected", self)
        self.delete_selected_btn.setVisible(False)  # Only visible in selection mode

# Add the button layout to the left layout
        left_layout.addLayout(func_button_layout)
        left_layout.addWidget(self.delete_selected_btn)
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

        btn_name_list = ['All', 'Animal', 'Cat', 'Dog', 'Person', 'Vehicle', 'Kitchenware', 'Appliance', 'Entertainment\n Device']
        sorted_list = sorted(btn_name_list)  # Sorts alphabetically
        sorted_list.append('Unknown')
        for name in sorted_list:
            button = QRadioButton(f"{name}", self)
            button.setStyleSheet("font-size: 11px;")  # Set font size for the button
            self.button_group.addButton(button)  # Add the button to the group
            tab_btn_layout.addWidget(button)
            button.installEventFilter(self)  # Install event filter for the button
            if name.lower() == self.TAG.lower():
                button.setChecked(True)  # Set the default tag button to be checked
                

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

        # Create a QScrollArea and set the container widget as its widget
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.scroll_area, 1)
        
        left_widget = QWidget(self)
        left_widget.setLayout(self.left_layout)
        left_widget.setFixedWidth(900)
        main_layout.addWidget(left_widget)
        # main_layout.addWidget(left_widget)  # <-- REMOVE this duplicate line

        drag_drop_area = DragDropArea(self)
        drag_drop_area.installEventFilter(self)  # Install event filter for drag-and-drop area

        # Create a vertical layout for the right-side widgets
        right_layout = QVBoxLayout()
        right_layout.addWidget(drag_drop_area)  # Align to the top

        # Create a vertical layout for the text views
        info_layout = QVBoxLayout()

        # Histogram canvas for displaying RGB histogram
        self.canvas = HistogramCanvas(self)
        info_layout.addWidget(self.canvas)

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
        

# Set the main widget as the central widget
        self.setCentralWidget(main_widget)
        # Main widget setup
      

        self.import_bnt.clicked.connect(self.open_import_dialog)
        self.export_bnt.clicked.connect(self.open_export_dialog)
        self.checkDup_bnt.clicked.connect(self.show_duplicates_dialog)
        self.outputPath_bnt.clicked.connect(self.open_output_path_dialog)
        self.settings_btn.clicked.connect(self.open_settings_dialog)
        self.select_mode_btn.clicked.connect(self.toggle_selection_mode)
        self.delete_selected_btn.clicked.connect(self.delete_selected_images)
        self.statistics_btn.clicked.connect(self.open_statistics_dialog)  # ADD THIS LINE
        self.view_toggle_btn.clicked.connect(self.toggle_view_mode)
        # Connect tag button group and size buttons
        self.button_group.buttonClicked.connect(self.handle_tag_button_click)
        self.small_size_btn.toggled.connect(lambda: self.update_image_sizes("Small", self.TAG))
        self.medium_size_btn.toggled.connect(lambda: self.update_image_sizes("Medium", self.TAG))
        self.large_size_btn.toggled.connect(lambda: self.update_image_sizes("Large", self.TAG))
    def toggle_view_mode(self):
        """Toggle between grid and card view modes."""
        if self.current_view == "grid":
            self.switch_to_card_view()
        else:
            self.switch_to_grid_view()

    def switch_to_card_view(self):
        """Switch to card-based layout."""
        # Hide the current grid scroll area
        self.scroll_area.hide()
        
        # Create card gallery if it doesn't exist
        if not self.card_gallery:
            self.card_gallery = CardGalleryWidget(self)
            self.card_gallery.image_clicked.connect(self.open_swipe_viewer)
            
            # Insert card gallery into the left layout (replace scroll area position)
            layout_index = self.left_layout.indexOf(self.scroll_area)
            self.left_layout.insertWidget(layout_index + 1, self.card_gallery)
        
        # Prepare image data for card view
        self.prepare_image_data_for_cards()
        
        # Load images into card view
        if self.current_images_data:
            self.card_gallery.load_images(self.current_images_data)
        
        # Show card gallery
        self.card_gallery.show()
        
        # Update state and button
        self.current_view = "card"
        self.view_toggle_btn.setText("Grid View")
        
        if self.tool_tips:
            self.tool_tips.setText("Card view mode - Click any image to open swipe viewer")

    def switch_to_grid_view(self):
        """Switch back to grid-based layout."""
        # Hide card gallery
        if self.card_gallery:
            self.card_gallery.hide()
        
        # Show original grid scroll area
        self.scroll_area.show()
        
        # Update state and button
        self.current_view = "grid"
        self.view_toggle_btn.setText("Card View")
        
        if self.tool_tips:
            self.tool_tips.setText("Grid view mode")

    def prepare_image_data_for_cards(self):
        """Prepare image data structure for card and swipe viewers."""
        self.current_images_data = []
        
        # Get currently filtered images based on selected tag
        current_tag = self.TAG.lower()
        
        for image_data in self.image_labels:
            if len(image_data) < 5:
                continue
                
            image_label, pixmap, image_path, checkbox, tag = image_data
            
            # Apply current tag filter
            if current_tag == "all" or tag.lower() == current_tag:
                # Get YOLO classification with confidence
                category = tag if tag != "Unknown" else "Unknown"
                confidence = 0.0
                
                # Try to get confidence from YOLO if available
                try:
                    if hasattr(self, 'get_yolo_confidence'):
                        confidence = self.get_yolo_confidence(image_path, category)
                    else:
                        # Fallback: estimate confidence based on category certainty
                        confidence = 0.85 if category != "Unknown" else 0.0
                except:
                    confidence = 0.0
                
                self.current_images_data.append({
                    'path': image_path,
                    'category': category,
                    'confidence': confidence
                })

    def open_swipe_viewer(self, image_path):
        """Open the swipe viewer when an image is clicked."""
        try:
            # Get all image paths from current data
            image_paths = [img['path'] for img in self.current_images_data]
            
            # Find index of clicked image
            try:
                initial_index = image_paths.index(image_path)
            except ValueError:
                initial_index = 0
            
            # Create categories dict for swipe viewer
            categories = {}
            for img_data in self.current_images_data:
                categories[img_data['path']] = {
                    'category': img_data.get('category', 'Unknown'),
                    'confidence': img_data.get('confidence', 0.0)
                }
            
            # Open swipe viewer
            viewer = SwipeImageViewer(self, image_paths, initial_index, categories)
            viewer.exec()
            
        except Exception as e:
            print(f"Error opening swipe viewer: {e}")

    def get_selected_tag(self):
        """Get the currently selected tag from radio buttons."""
        button = self.button_group.checkedButton()
        if button:
            return button.text().replace('\n', '_')  # Handle multi-line button text
        return "Unknown"  # Default if no tag is selected

    def handle_tag_button_click(self, button):
        tag = button.text().strip().lower().replace("\n", " ")  # Normalize the tag name
        print(tag)
        self.filter_images_by_tag(tag)    
        
    def toggle_selection_mode(self):
        """Enable or disable selection mode for deleting images."""
        # Toggle the selection mode
        self.selection_mode = not self.selection_mode
        self.selected_images = []

        # Update button appearance and text
        if self.selection_mode:
            self.select_mode_btn.setText("Exit Selection")
            self.select_mode_btn.setChecked(True)
            self.delete_selected_btn.setVisible(True)
            if self.tool_tips:
                self.tool_tips.setText("Click checkboxes to select images for deletion.")
        else:
            self.select_mode_btn.setText("Select Images")
            self.select_mode_btn.setChecked(False)
            self.delete_selected_btn.setVisible(False)
            if self.tool_tips:
                self.tool_tips.setText("Tool Tips")

        # Reload the images to show/hide checkboxes
        if self.image_dir:
            self.load_images_from_directory(self.image_dir)
        
    def update_selected_images(self, state=None):
        self.selected_images.clear()
        for label_data in self.image_labels:
            if len(label_data) >= 4:
                checkbox = label_data[3]
                if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    file_path = checkbox.property("file_path")
                    if file_path:
                        self.selected_images.append(file_path)

        print(f"Selected images: {self.selected_images}") 
                
    def load_images_from_directory(self, directory, on_progress=None):
        """Load images from a directory and populate the grid with optional checkboxes."""
        self.image_dir = directory

        # Clear existing images
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)

        self.image_labels.clear()

        # Build file list
        files = []
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]
        total = len(files)

        row = col = image_count = 0

        for idx, file_name in enumerate(files, start=1):
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
                    except Exception:
                        tag = "Unknown"

                    # Checkbox if selection mode
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

                # report progress
                if callable(on_progress):
                    try:
                        on_progress(idx, total, file_name)
                    except Exception:
                        pass

            except Exception as e:
                print(f"Error loading image {image_path}: {e}")

        # Update the tool tips
        if image_count > 0 and self.tool_tips:
            self.tool_tips.setText(f"Loaded {image_count} images from {os.path.basename(directory)}")
        elif self.tool_tips:
            self.tool_tips.setText("No images found in the selected directory")
        if self.current_view == "card" and self.card_gallery:
            self.prepare_image_data_for_cards()
        if self.current_images_data:
            self.card_gallery.load_images(self.current_images_data)

                           
    def delete_selected_images(self):
        if not self.selected_images:
            QMessageBox.information(self, "No Selection", "No images selected for deletion.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete {len(self.selected_images)} selected image(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            deleted_count = 0
            for image_path in self.selected_images:
                try:
                    if os.path.exists(image_path):
                        os.remove(image_path)
                        deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {image_path}: {e}")

            # Clear the selection list
            self.selected_images.clear()

            # Reload grid
            self.load_images_from_directory(self.image_dir)

            # Show result
            QMessageBox.information(self, "Deleted", f"{deleted_count} image(s) deleted.")           

    def update_image_sizes(self, size, target_tag):
        """Update the size of the images and grid layout based on the selected size."""
        if size == "Small":
            new_size = 135  # Small size
            max_columns = 5  # 5 columns
            self.display_size = "Small"
        elif size == "Medium":
            new_size = 260  # Medium size (default)
            max_columns = 3  # 3 columns
            self.display_size = "Medium"
        elif size == "Large":
            new_size = 400  # Large size
            max_columns = 2  # 2 columns
            self.display_size = "Large"

        # Clear the current grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Re-add images to the grid layout with the new size and grid configuration
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
            if target_tag == "all":
                try:
                    image_widget = QWidget()
                    layout = QVBoxLayout(image_widget)
                    layout.setAlignment(Qt.AlignCenter)

                    image_label = ClickableLabel(self)
                    image_label.setPixmap(self.crop_center(pixmap))
                    image_label.setScaledContents(True)
                    image_label.setFixedSize(new_size, new_size)
                    layout.addWidget(image_label)

                    image_label.clicked.connect(lambda path=image_path: self.on_image_clicked(path))
                    image_label.doubleClicked.connect(lambda path=image_path: self.on_image_double_clicked(path))

                    self.grid_layout.addWidget(image_widget, row, col)
                    col += 1
                    match_count += 1
                    if col == max_columns:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error displaying filtered image {image_path}: {e}")
            elif tag == target_tag:
                try:
                    image_widget = QWidget()
                    layout = QVBoxLayout(image_widget)
                    layout.setAlignment(Qt.AlignCenter)

                    image_label = ClickableLabel(self)
                    image_label.setPixmap(self.crop_center(pixmap))
                    image_label.setScaledContents(True)
                    image_label.setFixedSize(new_size, new_size)
                    layout.addWidget(image_label)

                    image_label.clicked.connect(lambda path=image_path: self.on_image_clicked(path))
                    image_label.doubleClicked.connect(lambda path=image_path: self.on_image_double_clicked(path))

                    self.grid_layout.addWidget(image_widget, row, col)
                    col += 1
                    match_count += 1
                    if col == max_columns:
                        col = 0
                        row += 1
                except Exception as e:
                    print(f"Error displaying filtered image {image_path}: {e}")

        if self.tool_tips:
            self.tool_tips.setText(f"Filtered to {match_count} images under tag: {target_tag}")  

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

                # plot RGB histogram
                self.canvas.plot_rgb_histogram(image_path)

            except Exception as model_error:
                tags_detected = {"unknown"}
                print(f"YOLO model error: {model_error}")

            # -------------------------------------------------

            if isinstance(metadata, dict) and "error" in metadata:
                self.img_info.setText(f"Error reading metadata:<br>{metadata['error']}")
            else:
                # Enhanced metadata display with quality information
                info_text = '<p style="font-size: 14pt; font-weight: bold;">Info</p>'
                
                # Basic file info
                try:
                    file_size = os.path.getsize(image_path)
                    info_text += f"File size: {file_size:,} bytes<br>"
                    info_text += f"Path: {image_path}<br><br>"

                    info_text += "=" * 30 + "<br>"  # Separator
                except:
                    pass
                
                # Quality analysis
                info_text += '<p style="font-size: 14pt; font-weight: bold;">Quality Analysis</p>'
                info_text += f"Quality: {quality.upper()}<br>"
                # info_text += f"Score: {score:.2f}<br>"

                # Display simplified tags
                info_text += f"Detected Tags: {', '.join(tags_detected)}<br><br>"
                info_text += "=" * 30 + "<br>"  # Separator

                # Additional metadata if available
                if isinstance(metadata, dict):
                    info_text += '<p style="font-size: 14pt; font-weight: bold;">Additional Metadata</p>'
                    for key, value in metadata.items():
                        info_text += f"{key}: {value}<br>"
                self.img_info.setTextFormat(Qt.RichText)  # Enable HTML formatting
                self.img_info.setText(info_text)
        except Exception as e:
            self.img_info.setText(f"Error processing image:\n{str(e)}")

    def on_image_double_clicked(self, image_path):
        """Handle the image double-click event - opens swipe viewer."""
        try:
            # Prepare all images from current view for swiping
            all_images = []
            categories = {}
            
            # Get images based on current tag filter
            current_tag = self.TAG.lower()
            
            for image_data in self.image_labels:
                if len(image_data) < 5:
                    continue
                    
                image_label, pixmap, img_path, checkbox, tag = image_data
                
                # Apply current tag filter
                if current_tag == "all" or tag.lower() == current_tag:
                    all_images.append(img_path)
                    
                    # Add category info for swipe viewer
                    categories[img_path] = {
                        'category': tag if tag != "Unknown" else "Unknown",
                        'confidence': 0.85 if tag != "Unknown" else 0.0
                    }
            
            if not all_images:
                QMessageBox.information(self, "No Images", "No images available to view.")
                return
            
            # Find index of clicked image
            try:
                initial_index = all_images.index(image_path)
            except ValueError:
                initial_index = 0
            
            # Open the swipe viewer
            viewer = SwipeImageViewer(self, all_images, initial_index, categories)
            viewer.exec()
            
        except Exception as e:
            print(f"Error opening swipe viewer: {e}")
            # Fallback to simple dialog
            self.show_simple_image_dialog(image_path)

    def show_simple_image_dialog(self, image_path):
        """Fallback simple image dialog if swipe viewer fails."""
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
        """Open import dialog for selecting image folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder_path:
            print(f"Selected folder: {folder_path}")
            self.start_import_with_splash(folder_path)
            return folder_path
        else:
            print("No folder selected.")
            return None

    def open_settings_dialog(self):
        """Open the settings dialog"""
        print("Settings button clicked!")
        try:
            from app.gui.dialogs.settings_dialog import SettingsDialog
            print("SettingsDialog imported successfully")
            dialog = SettingsDialog(self)
            print("Dialog created successfully")
            result = dialog.exec()
            print(f"Dialog result: {result}")
            if result == QDialog.Accepted:
                if self.tool_tips:
                    self.tool_tips.setText("Settings applied successfully")
        except Exception as e:
            print(f"Settings dialog error: {e}")
            QMessageBox.information(self, "Settings Error", f"Settings: {str(e)}")
    def apply_dark_mode(self, enabled: bool):
        if enabled:
            self.setStyleSheet("QMainWindow { background-color: #121212; color: white; }")
    
    

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

    def start_import_with_splash(self, folder_path: str):
        """Import images with splash screen progress"""
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.warning(self, "Invalid path", "Invalid path provided. Make sure it's a directory.")
            return

        pm = _make_progress_splash(subtitle="Scanning and loading thumbnails…")
        self._import_splash = QSplashScreen(pm, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self._import_splash.setWindowFlag(Qt.Tool)
        self._import_splash.showMessage("Preparing…", Qt.AlignLeft | Qt.AlignBottom, Qt.darkGray)
        self._import_splash.show()
        QCoreApplication.processEvents()

        try:
            self.load_images_from_directory(folder_path, on_progress=self._update_import_progress)
        finally:
            if self._import_splash:
                self._import_splash.finish(self)
                self._import_splash = None
            if self.tool_tips:
                self.tool_tips.setText(f"Loaded folder: {os.path.basename(folder_path)}")

    def _update_import_progress(self, idx: int, total: int, filename: str | None):
        """Update import progress display"""
        self._import_total = total
        pct = 0 if total == 0 else int((idx / total) * 100)
        text = f"{pct}%  ({idx}/{total})"
        if filename:
            text += f" - {filename}"
        if self._import_splash:
            self._import_splash.showMessage(text, Qt.AlignLeft | Qt.AlignBottom, Qt.darkGray)
            QCoreApplication.processEvents()

    def refresh_image_grid(self):
        """Refresh the image grid after changes."""
        if self.image_dir:
            self.load_images_from_directory(self.image_dir)

    def eventFilter(self, obj, event):
        """Enhanced event filter with updated tool tips."""
        try:
            if not hasattr(self, 'tool_tips') or self.tool_tips is None:
                return super().eventFilter(obj, event)
            if event.type() == QEvent.Enter:
                if hasattr(self, 'import_bnt') and obj == self.import_bnt:
                    self.tool_tips.setText("Import images from a folder - supports drag and drop")
                elif hasattr(self, 'export_bnt') and obj == self.export_bnt:
                    self.tool_tips.setText("Export sorted images to category folders with quality filtering")
                elif hasattr(self, 'checkDup_bnt') and obj == self.checkDup_bnt:
                    self.tool_tips.setText("Check for duplicate images and remove them")
                elif hasattr(self, 'outputPath_bnt') and obj == self.outputPath_bnt:
                    try:
                        current_path = self.path_settings.get_output_path()
                        if current_path:
                            self.tool_tips.setText(f"Current output: {os.path.basename(current_path)} - Click to change")
                        else:
                            self.tool_tips.setText("Set the output path for sorted images")
                    except:
                        self.tool_tips.setText("Set the output path for sorted images")
                elif hasattr(self, 'settings_btn') and obj == self.settings_btn:
                    self.tool_tips.setText("Configure app settings: theme, storage, and auto-categorization")
                elif hasattr(self, 'statistics_btn') and obj == self.statistics_btn:
                    self.tool_tips.setText("View photo library statistics and analytics")
                elif hasattr(self, 'small_size_btn') and obj == self.small_size_btn:
                    self.tool_tips.setText("Display images in small size (5x5 grid)")
                elif hasattr(self, 'medium_size_btn') and obj == self.medium_size_btn:
                    self.tool_tips.setText("Display images in medium size (3x3 grid)")
                elif hasattr(self, 'large_size_btn') and obj == self.large_size_btn:
                    self.tool_tips.setText("Display images in large size (2x2 grid)")
                elif isinstance(obj, QRadioButton):
                    self.tool_tips.setText(f"Filter images by {obj.text()}")
                elif hasattr(self, 'image_labels') and any(obj == label[0] for label in self.image_labels if len(label) > 0):
                    self.tool_tips.setText("Click for metadata and quality info, double-click to view larger")
                elif isinstance(obj, DragDropArea):
                    self.tool_tips.setText("Drag and drop a folder here to import images")
                elif event.type() == QEvent.Leave:
                    self.tool_tips.setText("Tool Tips")
                elif hasattr(self, 'view_toggle_btn') and obj == self.view_toggle_btn:
                    if self.current_view == "grid":
                        self.tool_tips.setText("Switch to card layout with category labels")
                    else:
                         self.tool_tips.setText("Switch back to grid layout")
        except Exception as e:
            print(f"Event filter error: {e}")
        return super().eventFilter(obj, event)

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

    def map_coco_label_to_custom_tag(self, label):
        """Map COCO labels to custom tags"""
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
        """Filter and display images by tag"""
        self.TAG = target_tag
        self.update_image_sizes(self.display_size, target_tag)
        if self.current_view == "card" and self.card_gallery:
            self.prepare_image_data_for_cards()
        if self.current_images_data:
            self.card_gallery.load_images(self.current_images_data)

       
        #Statistics button to the toolbar
        self.stats_btn = QPushButton("Statistics", self)
        self.stats_btn.clicked.connect(self.open_statistics_dialog)
        self.toolbar.addWidget(self.stats_btn)
        self.left_layout.insertLayout(0, self.toolbar)
     

    def open_statistics_dialog(self):
        """Open the statistics dialog"""
        try:
            dialog = StatisticsDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"Statistics dialog error: {e}")
            QMessageBox.information(self, "Statistics", f"Statistics feature: {str(e)}")

    def apply_modern_styling(self):
        """Apply refined, professional styling to the application"""
        app_style = """
        QMainWindow {
            background-color: #1a1a2e;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        
        QPushButton {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 4px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: normal;
            color: #e0e0e0;
            min-height: 18px;
        }
        
        QPushButton:hover {
            background-color: #383838;
            border-color: #505050;
        }
        
        QPushButton:pressed {
            background-color: #252525;
            border-color: #606060;
        }
        
        QPushButton:checked {
            background-color: #1e4d5b;
            border-color: #2b6a7a;
        }
        
        QGroupBox {
            font-weight: 500;
            font-size: 11px;
            border: 1px solid #404040;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 6px;
            color: #e0e0e0;
            background-color: #232323;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 8px;
            padding: 0 6px 0 6px;
            color: #b0b0b0;
            background-color: #1a1a1a;
        }
        
        QRadioButton {
            color: #e0e0e0;
            font-size: 10px;
            spacing: 6px;
            padding: 3px;
        }
        
        QRadioButton::indicator {
            width: 12px;
            height: 12px;
            border-radius: 6px;
            border: 1px solid #606060;
            background-color: #2d2d2d;
        }
        
        QRadioButton::indicator:hover {
            border-color: #707070;
        }
        
        QRadioButton::indicator:checked {
            background-color: #4a7c59;
            border-color: #5a8c69;
        }
        
        QCheckBox {
            color: #e0e0e0;
            font-size: 9px;
            spacing: 4px;
        }
        
        QCheckBox::indicator {
            width: 12px;
            height: 12px;
            border: 1px solid #606060;
            border-radius: 2px;
            background-color: #2d2d2d;
        }
        
        QCheckBox::indicator:hover {
            border-color: #707070;
        }
        
        QCheckBox::indicator:checked {
            background-color: #4a7c59;
            border-color: #5a8c69;
        }
        
        QLabel {
            color: #e0e0e0;
            font-size: 11px;
        }
        
        QScrollArea {
            border: 1px solid #404040;
            border-radius: 3px;
            background-color: #232323;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #505050;
            border-radius: 5px;
            min-height: 15px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #606060;
        }
        
        QFrame#dragDropFrame {
            border: 2px dashed #505050;
            border-radius: 6px;
            background-color: #232323;
        }
        
        QFrame#dragDropFrame:hover {
            border-color: #707070;
            background-color: #282828;
        }
        """
        self.setStyleSheet(app_style)

    def create_professional_button_layout(self):
        """Create a professional button layout with proper spacing"""
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(8, 8, 8, 8)
        buttons = [
            self.import_bnt, self.export_bnt, self.checkDup_bnt,
            self.outputPath_bnt, self.select_mode_btn,
            self.settings_btn, self.statistics_btn
        ]
        for button in buttons:
            button.setMinimumHeight(32)
            button.setMinimumWidth(100)
            button_layout.addWidget(button)
        return button_container

    def enhance_drag_drop_area(self):
        """Enhance the drag-drop area with modern styling"""
        enhanced_style = """
            QFrame {
                border: 3px dashed #555555;
                border-radius: 12px;
                background-color: #2a2a2a;
                color: #cccccc;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #2d2d2d;
            }
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #cccccc;
                border: none;
            }
        """
        for widget in self.findChildren(DragDropArea):
            widget.setStyleSheet(enhanced_style)
            widget.setObjectName("dragDropFrame")

        # Set the main widget as the central widget
        self.setCentralWidget(self.main_widget)
def _make_progress_splash(width=560, height=220, title="Album Vision+", subtitle="Importing images…"):
    pm = QPixmap(width, height)
    pm.fill(Qt.white)
    p = QPainter(pm)
    try:
        f1 = QFont(); f1.setPointSize(18); f1.setBold(True)
        p.setFont(f1); p.setPen(Qt.black)
        p.drawText(24, 60, title)

        f2 = QFont(); f2.setPointSize(11)
        p.setFont(f2); p.setPen(Qt.darkGray)
        p.drawText(24, 96, subtitle)

        p.setPen(Qt.lightGray)
        p.drawRect(0, 0, width-1, height-1)
    finally:
        p.end()
    return pm
class IntroSplash(QSplashScreen):
    """
    Frameless splash screen with centered animated GIF and text.
    """
    def __init__(self, still_path: str, gif_path: str | None = None):
        # Just make an empty transparent pixmap as the "background"
        pm = QPixmap(560, 320)
        pm.fill(Qt.transparent)
        super().__init__(pm)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Use a vertical layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        self.title_lbl = QLabel("Album Vision+", self)
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet("QLabel { font-size: 22px; font-weight: bold; color: white; }")
        layout.addWidget(self.title_lbl)

        # GIF (centerpiece)
        self.movie_lbl = QLabel(self)
        self.movie_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.movie_lbl, alignment=Qt.AlignCenter)

        if gif_path and os.path.exists(gif_path):
            self.movie = QMovie(gif_path)
            self.movie_lbl.setMovie(self.movie)
            self.movie.start()

        # Subtitle
        self.subtitle_lbl = QLabel("Starting...", self)
        self.subtitle_lbl.setAlignment(Qt.AlignCenter)
        self.subtitle_lbl.setStyleSheet("QLabel { font-size: 12px; color: #CCCCCC; }")
        layout.addWidget(self.subtitle_lbl)

    def start(self, duration_ms: int = 1800):
        self.show()
        QGuiApplication.processEvents()
        QTimer.singleShot(duration_ms, self._fade_out)

    def _fade_out(self):
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(600)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(self.close)
        anim.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    #App Intro Execution
    logo_path = os.path.join(os.path.dirname(__file__),
                             "resources", "images", "albumvision_logo.png")
    gif_path  = os.path.join(os.path.dirname(__file__),
                             "resources", "animations", "intro.gif")
    splash = IntroSplash(logo_path, gif_path if os.path.exists(gif_path) else None)
    print("LOGO PATH:", logo_path)
    print("Exists?   ", os.path.exists(logo_path))
    splash.start(duration_ms=2400)   # show ~2.4 s total

    # Default test directory
    test_dir = os.path.join(os.getcwd(), "data", "test_images")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir, exist_ok=True)
        print(f"Created test directory: {test_dir}")
        print("Add some image files to this directory to test the application.")
    
    # Set application properties
    app.setApplicationName("Album Vision+")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("AlbumVision")
    
    # Main application style
    app_style = """
    QMainWindow {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }

    /* Button styling */
    QPushButton {
        background-color: #2d2d2d;
        border: 1px solid #404040;
        border-radius: 4px;
        padding: 6px 12px;
        font-size: 11px;
        font-weight: normal;
        color: #e0e0e0;
        min-height: 18px;
    }

    QPushButton:hover {
        background-color: #383838;
        border-color: #505050;
    }

    QPushButton:pressed {
        background-color: #252525;
        border-color: #606060;
    }

    QPushButton:checked {
        background-color: #1e4d5b;
        border-color: #2b6a7a;
    }

    /* GroupBox styling */
    QGroupBox {
        font-weight: 500;
        font-size: 11px;
        border: 1px solid #404040;
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 6px;
        color: #e0e0e0;
        background-color: #232323;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 8px;
        padding: 0 6px 0 6px;
        color: #b0b0b0;
        background-color: #1a1a1a;
    }

    /* Radio button styling */
    QRadioButton {
        color: #e0e0e0;
        font-size: 10px;
        spacing: 6px;
        padding: 3px;
    }

    QRadioButton::indicator {
        width: 12px;
        height: 12px;
        border-radius: 6px;
        border: 1px solid #606060;
        background-color: #2d2d2d;
    }

    QRadioButton::indicator:hover {
        border-color: #707070;
    }

    QRadioButton::indicator:checked {
        background-color: #4a7c59;
        border-color: #5a8c69;
    }

    /* Checkbox styling */
    QCheckBox {
        color: #e0e0e0;
        font-size: 9px;
        spacing: 4px;
    }

    QCheckBox::indicator {
        width: 12px;
        height: 12px;
        border: 1px solid #606060;
        border-radius: 2px;
        background-color: #2d2d2d;
    }

    QCheckBox::indicator:hover {
        border-color: #707070;
    }

    QCheckBox::indicator:checked {
        background-color: #4a7c59;
        border-color: #5a8c69;
    }

    /* Label styling */
    QLabel {
        color: #e0e0e0;
        font-size: 11px;
    }

    /* Scroll area styling */
    QScrollArea {
        border: 1px solid #404040;
        border-radius: 3px;
        background-color: #232323;
    }

    QScrollBar:vertical {
        background-color: #2d2d2d;
        width: 10px;
        border-radius: 5px;
    }

    QScrollBar::handle:vertical {
        background-color: #505050;
        border-radius: 5px;
        min-height: 15px;
    }

    QScrollBar::handle:vertical:hover {
        background-color: #606060;
    }

    /* Frame styling for drag-drop area */
    QFrame#dragDropFrame {
        border: 2px dashed #505050;
        border-radius: 6px;
        background-color: #232323;
    }

    QFrame#dragDropFrame:hover {
        border-color: #707070;
        background-color: #282828;
    }
    """
    app.setStyleSheet(app_style)
    try:
        window = ImageWindow()

        def show_main():
            window.show()
            splash.finish(window)
            splash.deleteLater()

        QTimer.singleShot(2400, show_main)  # Show main window after splash
        
        print("AlbumVision+ started successfully!")
        print(f"Test directory: {test_dir}")
        print("You can drag and drop folders containing images to import them.")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Startup Error", f"Failed to start AlbumVision+:\n{str(e)}")
        sys.exit(1)