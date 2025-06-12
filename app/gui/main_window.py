# File: app/gui/widgets/main_window.py
# Enhanced main window with modern UI, AI integration, and performance optimization

import sys
import os
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import (QApplication, QRadioButton, QButtonGroup, QGroupBox, QFrame, QFileDialog,
                               QMainWindow, QLabel, QScrollArea, QGridLayout, QWidget, QHBoxLayout, 
                               QVBoxLayout, QSlider, QDialog, QPushButton, QCheckBox, QMessageBox,
                               QProgressBar, QLineEdit, QComboBox, QSplitter, QToolBar, QStatusBar,
                               QMenuBar, QMenu, QToolButton, QTextEdit)
from PySide6.QtGui import (QPixmap, QIcon, QPalette, QColor, QFont, QPainter, QBrush, 
                          QLinearGradient, QAction, QShortcut, QKeySequence)
from PySide6.QtCore import (Qt, Signal, QEvent, QTimer, QThread, QPropertyAnimation, 
                           QEasingCurve, QRect, QSize, QEventLoop)

# Import enhanced modules
try:
    from app.utils.image_quality import EnhancedImageQualityChecker
    # Try to import YOLOImageAnalyzer, fallback if not available
    try:
        from app.services.yolo_service import YOLOImageAnalyzer as AIImageAnalyzer
    except ImportError:
        class AIImageAnalyzer:
            async def analyze_image(self, path):
                return {'category': 'Unknown', 'confidence': 0.0}
    from app.utils.cache_manager import CacheManager, get_cache_manager
    from app.utils.path_settings import PathSettings, create_enhanced_output_path_dialog
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f"Some enhanced features not available: {e}")
    AI_FEATURES_AVAILABLE = False
    
    # Fallback imports
    class EnhancedImageQualityChecker:
        async def analyze_image_comprehensive(self, path, threshold=150):
            return type('Result', (), {
                'quality': 'medium', 'score': 75.0, 'dimensions': (1920, 1080),
                'ai_category': 'Unknown', 'faces_detected': 0
            })()
    
    class AIImageAnalyzer:
        async def analyze_image(self, path):
            return {'category': 'Unknown', 'confidence': 0.0}
    
    class CacheManager:
        def get_thumbnail(self, path, size): return None
        def put_thumbnail(self, path, size, pixmap): return True
        def get_comprehensive_stats(self): return {}

# Modern UI Styles
MODERN_STYLE = """
/* Modern Glassmorphism Theme */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
        stop:0 #667eea, stop:1 #764ba2);
    color: #ffffff;
}

QWidget {
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    color: #ffffff;
}

/* Glass effect panels */
QGroupBox {
    font-weight: bold;
    font-size: 13px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 15px;
    margin-top: 12px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 8px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    color: #ffffff;
}

/* Modern buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.3),
        stop:1 rgba(255, 255, 255, 0.1));
    border: 1px solid rgba(255, 255, 255, 0.4);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 12px;
    color: #ffffff;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.4),
        stop:1 rgba(255, 255, 255, 0.2));
    border: 1px solid rgba(255, 255, 255, 0.6);
    transform: translateY(-1px);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(255, 255, 255, 0.2),
        stop:1 rgba(255, 255, 255, 0.1));
    transform: translateY(1px);
}

/* AI-enhanced button */
QPushButton#ai_button {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ff6b6b, stop:1 #feca57);
    border: 2px solid rgba(255, 255, 255, 0.3);
}

QPushButton#ai_button:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ff5252, stop:1 #ffca28);
}

/* Radio buttons */
QRadioButton {
    font-size: 11px;
    color: #ffffff;
    spacing: 8px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid rgba(255, 255, 255, 0.5);
    background: rgba(255, 255, 255, 0.1);
}

QRadioButton::indicator:checked {
    background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
        stop:0 #4facfe, stop:1 #00f2fe);
    border: 2px solid rgba(255, 255, 255, 0.8);
}

/* Scroll areas */
QScrollArea {
    border: none;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
}

QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.1);
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.5);
}

/* Progress bar */
QProgressBar {
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    text-align: center;
    font-weight: bold;
    background: rgba(255, 255, 255, 0.1);
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4facfe, stop:1 #00f2fe);
    border-radius: 6px;
}

/* Status bar */
QStatusBar {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
    border-top: 1px solid rgba(255, 255, 255, 0.2);
}

/* Tool tips */
QToolTip {
    background: rgba(0, 0, 0, 0.8);
    color: #ffffff;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 6px;
    padding: 6px;
    font-size: 11px;
}

/* Search box */
QLineEdit {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 8px;
    padding: 8px;
    font-size: 12px;
    color: #ffffff;
}

QLineEdit:focus {
    border: 2px solid rgba(79, 172, 254, 0.8);
    background: rgba(255, 255, 255, 0.25);
}

QLineEdit::placeholder {
    color: rgba(255, 255, 255, 0.6);
}
"""

DARK_THEME_STYLE = """
/* Dark Theme */
QMainWindow {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
        stop:0 #2c3e50, stop:1 #34495e);
    color: #ecf0f1;
}

QWidget {
    background-color: rgba(44, 62, 80, 0.7);
    border-radius: 8px;
    color: #ecf0f1;
}

QGroupBox {
    border: 2px solid #7f8c8d;
    background: rgba(44, 62, 80, 0.9);
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3498db, stop:1 #2980b9);
    border: none;
    color: white;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #5dade2, stop:1 #3498db);
}
"""

class ImageAnalysisWorker(QThread):
    """Background worker for AI image analysis"""
    analysis_complete = Signal(str, dict)  # image_path, analysis_result
    progress_updated = Signal(int, int, str)  # current, total, current_file
    
    def __init__(self, image_paths: List[str]):
        super().__init__()
        self.image_paths = image_paths
        self.ai_analyzer = AIImageAnalyzer()
        self.quality_checker = EnhancedImageQualityChecker()
        
    def run(self):
        """Run analysis on all images"""
        total = len(self.image_paths)
        
        for i, image_path in enumerate(self.image_paths):
            try:
                # Run comprehensive analysis
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                quality_result = loop.run_until_complete(
                    self.quality_checker.analyze_image_comprehensive(image_path)
                )
                
                ai_result = loop.run_until_complete(
                    self.ai_analyzer.analyze_image(image_path)
                )
                
                # Combine results
                combined_result = {
                    'quality': quality_result.quality,
                    'score': quality_result.score,
                    'dimensions': quality_result.dimensions,
                    'ai_category': ai_result.get('category', 'Unknown'),
                    'ai_confidence': ai_result.get('confidence', 0.0),
                    'faces': ai_result.get('faces', 0),
                    'tags': ai_result.get('tags', []),
                    'aesthetic_score': ai_result.get('aesthetic_score', 0.5)
                }
                
                self.analysis_complete.emit(image_path, combined_result)
                self.progress_updated.emit(i + 1, total, os.path.basename(image_path))
                
                loop.close()
                
            except Exception as e:
                logging.error(f"Analysis failed for {image_path}: {e}")

class SmartSearchWidget(QWidget):
    """AI-powered search widget with natural language support"""
    search_requested = Signal(str, dict)  # query, filters
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search images: 'sunset with people' or 'high quality cats'...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        # Quick filters
        self.quality_filter = QComboBox()
        self.quality_filter.addItems(["All Quality", "Excellent", "High", "Medium", "Low"])
        
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "People", "Animals", "Nature", "Vehicles", "Buildings"])
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.perform_search)
        
        layout.addWidget(self.search_input, 3)
        layout.addWidget(self.quality_filter, 1)
        layout.addWidget(self.category_filter, 1)
        layout.addWidget(search_btn)
        
    def perform_search(self):
        """Perform smart search with AI assistance"""
        query = self.search_input.text().strip()
        
        filters = {
            'quality': self.quality_filter.currentText(),
            'category': self.category_filter.currentText(),
            'use_ai': True
        }
        
        self.search_requested.emit(query, filters)

class EnhancedDragDropArea(QFrame):
    """Enhanced drag and drop area with modern styling and AI preview"""
    files_dropped = Signal(list)  # List of file paths
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed rgba(255, 255, 255, 0.4);
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(10px);
            }
            
            QFrame:hover {
                border: 3px dashed rgba(79, 172, 254, 0.8);
                background: rgba(79, 172, 254, 0.1);
            }
        """)
        
        self.setFixedSize(300, 120)
        
        layout = QVBoxLayout(self)
        
        # Icon and text
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 32px; border: none;")
        
        text_label = QLabel("Drop folders or images here")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff; border: none;")
        
        subtitle_label = QLabel("AI analysis included")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 11px; color: rgba(255, 255, 255, 0.7); border: none;")
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addWidget(subtitle_label)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
            
    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.exists(path):
                    file_paths.append(path)
            
            if file_paths:
                self.files_dropped.emit(file_paths)
                
        event.accept()

class ModernImageLabel(QLabel):
    """Enhanced image label with hover effects and AI info"""
    clicked = Signal(str)  # image_path
    right_clicked = Signal(str)  # image_path
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.ai_info = {}
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QLabel {
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.05);
                padding: 4px;
            }
            
            QLabel:hover {
                border: 2px solid rgba(79, 172, 254, 0.8);
                background: rgba(79, 172, 254, 0.1);
                transform: scale(1.02);
            }
        """)
        
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        
    def set_ai_info(self, ai_info: Dict):
        """Set AI analysis information"""
        self.ai_info = ai_info
        
        # Update tooltip with AI info
        tooltip_text = f"Path: {os.path.basename(self.image_path)}\n"
        if ai_info:
            tooltip_text += f"Category: {ai_info.get('ai_category', 'Unknown')}\n"
            tooltip_text += f"Quality: {ai_info.get('quality', 'Unknown')}\n"
            tooltip_text += f"Faces: {ai_info.get('faces', 0)}\n"
            if ai_info.get('tags'):
                tooltip_text += f"Tags: {', '.join(ai_info['tags'][:3])}"
                
        self.setToolTip(tooltip_text)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.image_path)
        elif event.button() == Qt.RightButton:
            self.right_clicked.emit(self.image_path)
        super().mousePressEvent(event)

class EnhancedImageWindow(QMainWindow):
    """Enhanced main window with modern UI and AI features"""
    
    def __init__(self, image_dir: str):
        super().__init__()
        self.image_dir = image_dir
        self.current_theme = "modern"
        
        # Initialize services
        self.cache_manager = get_cache_manager()
        self.path_settings = PathSettings()
        self.ai_analyzer = AIImageAnalyzer() if AI_FEATURES_AVAILABLE else None
        self.quality_checker = EnhancedImageQualityChecker() if AI_FEATURES_AVAILABLE else None
        
        # UI state
        self.image_widgets = []  # List of (widget, image_path, ai_info)
        self.current_filter = {}
        self.analysis_results = {}  # Store AI analysis results
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        self.apply_modern_theme()
        self.load_images_from_directory(image_dir)
        
        # Setup async event loop for AI features
        if AI_FEATURES_AVAILABLE:
            self.setup_ai_features()
    
    def setup_ui(self):
        """Setup the enhanced user interface"""
        self.setWindowTitle("Album Vision+ Pro - AI-Powered Photo Organization")
        self.setFixedSize(1400, 900)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'icons', 'ab_logo.svg')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Setup menu bar and toolbar
        self.setup_menu_bar()
        self.setup_toolbar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        central_layout = QHBoxLayout(central_widget)
        central_layout.addWidget(main_splitter)
        
        # Left panel
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        main_splitter.setSizes([1000, 400])
        
        # Setup status bar
        self.setup_status_bar()
        
        # Connect signals
        self.connect_signals()
    
    def setup_menu_bar(self):
        """Setup modern menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        import_action = QAction("Import Folder", self)
        import_action.setShortcut(QKeySequence("Ctrl+O"))
        import_action.triggered.connect(self.open_import_dialog)
        file_menu.addAction(import_action)
        
        export_action = QAction("Export Organized", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.open_export_dialog)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        # AI menu
        ai_menu = menubar.addMenu("AI Analysis")
        
        analyze_all_action = QAction("Analyze All Images", self)
        analyze_all_action.triggered.connect(self.start_ai_analysis)
        ai_menu.addAction(analyze_all_action)
        
        clear_cache_action = QAction("Clear AI Cache", self)
        clear_cache_action.triggered.connect(self.clear_ai_cache)
        ai_menu.addAction(clear_cache_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_action = QAction("Toggle Theme", self)
        theme_action.setShortcut(QKeySequence("Ctrl+T"))
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        stats_action = QAction("Cache Statistics", self)
        stats_action.triggered.connect(self.show_cache_stats)
        view_menu.addAction(stats_action)
    
    def setup_toolbar(self):
        """Setup modern toolbar"""
        toolbar = self.addToolBar("Main")
        toolbar.setMovable(False)
        
        # Import button
        import_btn = QToolButton()
        import_btn.setText("📁 Import")
        import_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        import_btn.clicked.connect(self.open_import_dialog)
        toolbar.addWidget(import_btn)
        
        toolbar.addSeparator()
        
        # AI analysis button
        ai_btn = QToolButton()
        ai_btn.setText("🤖 AI Analysis")
        ai_btn.setObjectName("ai_button")
        ai_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        ai_btn.clicked.connect(self.start_ai_analysis)
        ai_btn.setEnabled(AI_FEATURES_AVAILABLE)
        toolbar.addWidget(ai_btn)
        
        toolbar.addSeparator()
        
        # Export button
        export_btn = QToolButton()
        export_btn.setText("📤 Export")
        export_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        export_btn.clicked.connect(self.open_export_dialog)
        toolbar.addWidget(export_btn)
        
        # Stretch
        spacer = QWidget()
        spacer.setSizePolicy(QWidget.Expanding, QWidget.Preferred)
        toolbar.addWidget(spacer)
        
        # Theme toggle
        theme_btn = QToolButton()
        theme_btn.setText("🎨")
        theme_btn.setToolTip("Toggle Theme")
        theme_btn.clicked.connect(self.toggle_theme)
        toolbar.addWidget(theme_btn)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with controls and image grid"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Smart search widget
        self.search_widget = SmartSearchWidget()
        self.search_widget.search_requested.connect(self.perform_smart_search)
        left_layout.addWidget(self.search_widget)
        
        # Function buttons
        func_layout = QHBoxLayout()
        
        self.import_btn = QPushButton("📁 Import")
        self.export_btn = QPushButton("📤 Export")
        self.ai_analyze_btn = QPushButton("🤖 AI Analyze")
        self.organize_btn = QPushButton("📂 Auto-Organize")
        
        self.ai_analyze_btn.setEnabled(AI_FEATURES_AVAILABLE)
        
        func_layout.addWidget(self.import_btn)
        func_layout.addWidget(self.export_btn)
        func_layout.addWidget(self.ai_analyze_btn)
        func_layout.addWidget(self.organize_btn)
        
        left_layout.addLayout(func_layout)
        
        # Category filters with AI enhancement
        category_group = QGroupBox("🏷️ Smart Categories")
        category_layout = QHBoxLayout(category_group)
        
        self.category_buttons = QButtonGroup()
        categories = ['All', 'People', 'Animals', 'Nature', 'Vehicles', 'Buildings', 'Documents', 'Unknown']
        
        for category in categories:
            btn = QRadioButton(category)
            self.category_buttons.addButton(btn)
            category_layout.addWidget(btn)
            btn.toggled.connect(lambda checked, cat=category: self.filter_by_category(cat) if checked else None)
        
        # Set "All" as default
        self.category_buttons.buttons()[0].setChecked(True)
        left_layout.addWidget(category_group)
        
        # Quality filter
        quality_group = QGroupBox("⭐ Quality Filter")
        quality_layout = QHBoxLayout(quality_group)
        
        self.quality_buttons = QButtonGroup()
        qualities = ['All', 'Excellent', 'High', 'Medium', 'Low']
        
        for quality in qualities:
            btn = QRadioButton(quality)
            self.quality_buttons.addButton(btn)
            quality_layout.addWidget(btn)
            btn.toggled.connect(lambda checked, qual=quality: self.filter_by_quality(qual) if checked else None)
        
        self.quality_buttons.buttons()[0].setChecked(True)
        left_layout.addWidget(quality_group)
        
        # Size controls
        size_group = QGroupBox("🖼️ View Size")
        size_layout = QHBoxLayout(size_group)
        
        self.size_buttons = QButtonGroup()
        sizes = [('Small', 160), ('Medium', 220), ('Large', 300)]
        
        for size_name, size_px in sizes:
            btn = QRadioButton(size_name)
            self.size_buttons.addButton(btn)
            size_layout.addWidget(btn)
            btn.toggled.connect(lambda checked, s=size_px: self.update_image_sizes(s) if checked else None)
        
        # Set Medium as default
        self.size_buttons.buttons()[1].setChecked(True)
        left_layout.addWidget(size_group)
        
        # Progress bar for AI analysis
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)
        
        # Scroll area for images
        self.scroll_area = QScrollArea()
        self.container_widget = QWidget()
        self.grid_layout = QGridLayout(self.container_widget)
        
        self.scroll_area.setWidget(self.container_widget)
        self.scroll_area.setWidgetResizable(True)
        left_layout.addWidget(self.scroll_area, 1)
        
        return left_widget
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with drag-drop and info"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Enhanced drag-drop area
        self.drop_area = EnhancedDragDropArea()
        self.drop_area.files_dropped.connect(self.handle_dropped_files)
        right_layout.addWidget(self.drop_area)
        
        # AI Analysis results
        ai_group = QGroupBox("🤖 AI Analysis")
        ai_layout = QVBoxLayout(ai_group)
        
        self.ai_info_text = QTextEdit()
        self.ai_info_text.setMaximumHeight(200)
        self.ai_info_text.setPlainText("Select an image to see AI analysis...")
        ai_layout.addWidget(self.ai_info_text)
        
        right_layout.addWidget(ai_group)
        
        # Image metadata
        meta_group = QGroupBox("📊 Image Details")
        meta_layout = QVBoxLayout(meta_group)
        
        self.meta_info_text = QTextEdit()
        self.meta_info_text.setMaximumHeight(200)
        self.meta_info_text.setPlainText("No image selected...")
        meta_layout.addWidget(self.meta_info_text)
        
        right_layout.addWidget(meta_group)
        
        # Cache statistics
        cache_group = QGroupBox("💾 Performance")
        cache_layout = QVBoxLayout(cache_group)
        
        self.cache_info_text = QTextEdit()
        self.cache_info_text.setMaximumHeight(150)
        self.update_cache_info()
        cache_layout.addWidget(self.cache_info_text)
        
        right_layout.addWidget(cache_group)
        
        # Stretch
        right_layout.addStretch()
        
        return right_widget
    
    def setup_status_bar(self):
        """Setup enhanced status bar"""
        status_bar = self.statusBar()
        
        # Image count label
        self.image_count_label = QLabel("Images: 0")
        status_bar.addWidget(self.image_count_label)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # AI status label
        self.ai_status_label = QLabel("AI: Ready" if AI_FEATURES_AVAILABLE else "AI: Unavailable")
        status_bar.addPermanentWidget(self.ai_status_label)
        
        status_bar.addPermanentWidget(QLabel("|"))
        
        # Cache status
        self.cache_status_label = QLabel("Cache: OK")
        status_bar.addPermanentWidget(self.cache_status_label)
    
    def connect_signals(self):
        """Connect UI signals"""
        self.import_btn.clicked.connect(self.open_import_dialog)
        self.export_btn.clicked.connect(self.open_export_dialog)
        self.ai_analyze_btn.clicked.connect(self.start_ai_analysis)
        self.organize_btn.clicked.connect(self.auto_organize_images)
    
    def apply_modern_theme(self):
        """Apply modern glassmorphism theme"""
        if self.current_theme == "modern":
            self.setStyleSheet(MODERN_STYLE)
        else:
            self.setStyleSheet(DARK_THEME_STYLE)
    
    def toggle_theme(self):
        """Toggle between modern and dark themes"""
        self.current_theme = "dark" if self.current_theme == "modern" else "modern"
        self.apply_modern_theme()
    
    def load_images_from_directory(self, directory: str):
        """Load images with enhanced caching and AI analysis"""
        self.image_dir = directory
        self.clear_image_grid()
        
        # Get image files
        image_files = self.get_image_files(directory)
        
        if not image_files:
            self.image_count_label.setText("Images: 0")
            return
        
        # Load images with caching
        self.load_images_with_cache(image_files)
        
        # Update UI
        self.image_count_label.setText(f"Images: {len(image_files)}")
        
        # Auto-start AI analysis if enabled
        if AI_FEATURES_AVAILABLE and len(image_files) < 100:  # Only auto-analyze small sets
            QTimer.singleShot(1000, self.start_ai_analysis)
    
    def get_image_files(self, directory: str) -> List[str]:
        """Get list of image files from directory"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
        image_files = []
        
        try:
            for file_name in os.listdir(directory):
                if os.path.splitext(file_name.lower())[1] in image_extensions:
                    full_path = os.path.join(directory, file_name)
                    if os.path.isfile(full_path):
                        image_files.append(full_path)
        except Exception as e:
            self.logger.error(f"Error reading directory {directory}: {e}")
        
        return sorted(image_files)
    
    def load_images_with_cache(self, image_files: List[str]):
        """Load images using cache for performance"""
        row, col = 0, 0
        max_cols = 4
        thumbnail_size = (220, 220)
        
        for image_path in image_files:
            try:
                # Try to get cached thumbnail
                cached_pixmap = self.cache_manager.get_thumbnail(image_path, thumbnail_size)
                
                if cached_pixmap is None:
                    # Create thumbnail
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        # Crop to square and scale
                        squared_pixmap = self.crop_center(pixmap)
                        thumbnail = squared_pixmap.scaled(
                            thumbnail_size[0], thumbnail_size[1], 
                            Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                        
                        # Cache the thumbnail
                        self.cache_manager.put_thumbnail(image_path, thumbnail_size, thumbnail)
                        cached_pixmap = thumbnail
                
                if cached_pixmap:
                    # Create enhanced image widget
                    image_widget = ModernImageLabel(image_path)
                    image_widget.setPixmap(cached_pixmap)
                    image_widget.setFixedSize(thumbnail_size[0], thumbnail_size[1])
                    
                    # Connect signals
                    image_widget.clicked.connect(self.on_image_clicked)
                    image_widget.right_clicked.connect(self.on_image_right_clicked)
                    
                    # Add to grid
                    self.grid_layout.addWidget(image_widget, row, col)
                    self.image_widgets.append((image_widget, image_path, {}))
                    
                    # Update grid position
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1
                        
            except Exception as e:
                self.logger.error(f"Error loading image {image_path}: {e}")
    
    def crop_center(self, pixmap: QPixmap) -> QPixmap:
        """Crop pixmap to center square"""
        if pixmap.isNull():
            return pixmap
        
        width, height = pixmap.width(), pixmap.height()
        crop_size = min(width, height)
        x = (width - crop_size) // 2
        y = (height - crop_size) // 2
        
        return pixmap.copy(x, y, crop_size, crop_size)
    
    def clear_image_grid(self):
        """Clear the image grid"""
        for widget, _, _ in self.image_widgets:
            widget.setParent(None)
        
        self.image_widgets.clear()
        self.analysis_results.clear()
    
    def start_ai_analysis(self):
        """Start AI analysis of all visible images"""
        if not AI_FEATURES_AVAILABLE:
            QMessageBox.information(self, "AI Unavailable", "AI features are not available. Please install required dependencies.")
            return
        
        if not self.image_widgets:
            QMessageBox.information(self, "No Images", "No images to analyze.")
            return
        
        # Get image paths
        image_paths = [path for _, path, _ in self.image_widgets]
        
        # Setup progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(image_paths))
        self.progress_bar.setValue(0)
        self.ai_status_label.setText("AI: Analyzing...")
        
        # Start worker thread
        self.analysis_worker = ImageAnalysisWorker(image_paths)
        self.analysis_worker.analysis_complete.connect(self.on_analysis_complete)
        self.analysis_worker.progress_updated.connect(self.on_analysis_progress)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.start()
    
    def on_analysis_complete(self, image_path: str, analysis: Dict):
        """Handle completed AI analysis for single image"""
        self.analysis_results[image_path] = analysis
        
        # Update image widget with AI info
        for widget, path, _ in self.image_widgets:
            if path == image_path:
                widget.set_ai_info(analysis)
                break
    
    def on_analysis_progress(self, current: int, total: int, filename: str):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        self.ai_status_label.setText(f"AI: Analyzing {filename} ({current}/{total})")
    
    def on_analysis_finished(self):
        """AI analysis completed"""
        self.progress_bar.setVisible(False)
        self.ai_status_label.setText(f"AI: Complete ({len(self.analysis_results)} analyzed)")
        
        # Show summary
        categories = {}
        qualities = {}
        
        for analysis in self.analysis_results.values():
            cat = analysis.get('ai_category', 'Unknown')
            qual = analysis.get('quality', 'unknown')
            
            categories[cat] = categories.get(cat, 0) + 1
            qualities[qual] = qualities.get(qual, 0) + 1
        
        summary = f"Analysis Complete!\n\nCategories found:\n"
        for cat, count in sorted(categories.items()):
            summary += f"  {cat}: {count}\n"
        
        summary += f"\nQuality distribution:\n"
        for qual, count in sorted(qualities.items()):
            summary += f"  {qual.title()}: {count}\n"
        
        QMessageBox.information(self, "AI Analysis Complete", summary)
    
    def on_image_clicked(self, image_path: str):
        """Handle image click - show detailed info"""
        # Update metadata display
        self.show_image_details(image_path)
        
        # Update AI info if available
        if image_path in self.analysis_results:
            analysis = self.analysis_results[image_path]
            ai_text = f"Category: {analysis.get('ai_category', 'Unknown')}\n"
            ai_text += f"Confidence: {analysis.get('ai_confidence', 0.0):.2f}\n"
            ai_text += f"Quality: {analysis.get('quality', 'Unknown')} (Score: {analysis.get('score', 0):.1f})\n"
            ai_text += f"Faces detected: {analysis.get('faces', 0)}\n"
            ai_text += f"Aesthetic score: {analysis.get('aesthetic_score', 0.5):.2f}\n"
            
            if analysis.get('tags'):
                ai_text += f"Tags: {', '.join(analysis['tags'][:5])}\n"
            
            self.ai_info_text.setPlainText(ai_text)
        else:
            self.ai_info_text.setPlainText("No AI analysis available for this image.\nClick 'AI Analyze' to analyze all images.")
    
    def on_image_right_clicked(self, image_path: str):
        """Handle right-click on image - show context menu"""
        # Could implement context menu here
        pass
    
    def show_image_details(self, image_path: str):
        """Show detailed image information"""
        try:
            stat = os.stat(image_path)
            pixmap = QPixmap(image_path)
            
            details = f"File: {os.path.basename(image_path)}\n"
            details += f"Path: {image_path}\n"
            details += f"Size: {stat.st_size / 1024 / 1024:.2f} MB\n"
            details += f"Dimensions: {pixmap.width()} x {pixmap.height()}\n"
            details += f"Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            self.meta_info_text.setPlainText(details)
            
        except Exception as e:
            self.meta_info_text.setPlainText(f"Error reading file details: {e}")
    
    def update_cache_info(self):
        """Update cache information display"""
        try:
            stats = self.cache_manager.get_comprehensive_stats()
            
            cache_text = f"Memory Cache: {stats.get('memory_cache', {}).get('items', 0)} items\n"
            cache_text += f"Thumbnail Cache: {stats.get('thumbnail_cache', {}).get('items', 0)} items\n"
            cache_text += f"Total Size: {stats.get('total_cache_size_mb', 0):.1f} MB\n"
            cache_text += f"Hit Rate: {stats.get('memory_cache', {}).get('hit_rate', 0):.1f}%\n"
            
            self.cache_info_text.setPlainText(cache_text)
            
        except Exception as e:
            self.cache_info_text.setPlainText(f"Cache info unavailable: {e}")
    
    def filter_by_category(self, category: str):
        """Filter images by AI-detected category"""
        self.current_filter['category'] = category
        self.apply_current_filters()
    
    def filter_by_quality(self, quality: str):
        """Filter images by quality level"""
        self.current_filter['quality'] = quality
        self.apply_current_filters()
    
    def apply_current_filters(self):
        """Apply current filters to image display"""
        category_filter = self.current_filter.get('category', 'All')
        quality_filter = self.current_filter.get('quality', 'All')
        
        visible_count = 0
        
        for widget, image_path, _ in self.image_widgets:
            show_widget = True
            
            # Apply category filter
            if category_filter != 'All':
                analysis = self.analysis_results.get(image_path, {})
                image_category = analysis.get('ai_category', 'Unknown')
                if image_category.lower() != category_filter.lower():
                    show_widget = False
            
            # Apply quality filter
            if quality_filter != 'All':
                analysis = self.analysis_results.get(image_path, {})
                image_quality = analysis.get('quality', 'unknown')
                if image_quality.lower() != quality_filter.lower():
                    show_widget = False
            
            # Show/hide widget
            widget.setVisible(show_widget)
            if show_widget:
                visible_count += 1
        
        # Update status
        self.image_count_label.setText(f"Images: {visible_count} (filtered)")
    
    def perform_smart_search(self, query: str, filters: Dict):
        """Perform AI-powered smart search"""
        if not query.strip():
            # Clear filters if no query
            self.current_filter = {}
            self.apply_current_filters()
            return
        
        # Simple keyword matching for now
        # In a full implementation, this would use AI to understand natural language
        query_lower = query.lower()
        visible_count = 0
        
        for widget, image_path, _ in self.image_widgets:
            show_widget = False
            
            # Check filename
            if query_lower in os.path.basename(image_path).lower():
                show_widget = True
            
            # Check AI analysis results
            analysis = self.analysis_results.get(image_path, {})
            if analysis:
                # Check category
                if query_lower in analysis.get('ai_category', '').lower():
                    show_widget = True
                
                # Check tags
                tags = analysis.get('tags', [])
                if any(query_lower in tag.lower() for tag in tags):
                    show_widget = True
            
            widget.setVisible(show_widget)
            if show_widget:
                visible_count += 1
        
        self.image_count_label.setText(f"Images: {visible_count} (search: '{query}')")
    
    def update_image_sizes(self, size: int):
        """Update image display size"""
        for widget, _, _ in self.image_widgets:
            widget.setFixedSize(size, size)
    
    def handle_dropped_files(self, file_paths: List[str]):
        """Handle dropped files/folders"""
        for path in file_paths:
            if os.path.isdir(path):
                self.load_images_from_directory(path)
                break
    
    # Dialog methods (simplified versions)
    def open_import_dialog(self):
        """Open import dialog"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Image Folder")
        if folder_path:
            self.load_images_from_directory(folder_path)
    
    def open_export_dialog(self):
        """Open export dialog"""
        if not self.analysis_results:
            QMessageBox.information(self, "No Analysis", "Please run AI analysis first to enable smart export.")
            return
        
        # Simplified export - in real implementation would use enhanced export widget
        QMessageBox.information(self, "Export", "Enhanced export functionality will be available in the full version.")
    
    def auto_organize_images(self):
        """Auto-organize images based on AI analysis"""
        if not self.analysis_results:
            QMessageBox.information(self, "No Analysis", "Please run AI analysis first.")
            return
        
        # Show preview of organization
        categories = {}
        for path, analysis in self.analysis_results.items():
            cat = analysis.get('ai_category', 'Unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(os.path.basename(path))
        
        preview = "Auto-organization preview:\n\n"
        for cat, files in categories.items():
            preview += f"{cat} ({len(files)} files):\n"
            for file in files[:3]:  # Show first 3
                preview += f"  • {file}\n"
            if len(files) > 3:
                preview += f"  • ... and {len(files) - 3} more\n"
            preview += "\n"
        
        QMessageBox.information(self, "Auto-Organization Preview", preview)
    
    def open_settings(self):
        """Open settings dialog"""
        QMessageBox.information(self, "Settings", "Settings dialog will be implemented in the full version.")
    
    def clear_ai_cache(self):
        """Clear AI analysis cache"""
        self.cache_manager.clear_all_caches()
        self.update_cache_info()
        QMessageBox.information(self, "Cache Cleared", "AI analysis cache has been cleared.")
    
    def show_cache_stats(self):
        """Show detailed cache statistics"""
        stats = self.cache_manager.get_comprehensive_stats()
        
        stats_text = "Cache Statistics:\n\n"
        stats_text += f"Memory Cache: {stats.get('memory_cache', {}).get('items', 0)} items, "
        stats_text += f"{stats.get('memory_cache', {}).get('size_mb', 0):.1f} MB\n"
        stats_text += f"Thumbnail Cache: {stats.get('thumbnail_cache', {}).get('items', 0)} items, "
        stats_text += f"{stats.get('thumbnail_cache', {}).get('size_mb', 0):.1f} MB\n"
        stats_text += f"AI Cache: {stats.get('ai_analysis_cache', {}).get('items', 0)} items, "
        stats_text += f"{stats.get('ai_analysis_cache', {}).get('size_mb', 0):.1f} MB\n"
        stats_text += f"\nTotal Cache Size: {stats.get('total_cache_size_mb', 0):.1f} MB\n"
        stats_text += f"Cache Directory: {stats.get('cache_directory', 'Unknown')}\n"
        
        QMessageBox.information(self, "Cache Statistics", stats_text)
    
    def setup_ai_features(self):
        """Setup AI-specific features"""
        # Timer to periodically update cache info
        self.cache_timer = QTimer()
        self.cache_timer.timeout.connect(self.update_cache_info)
        self.cache_timer.start(5000)  # Update every 5 seconds

# Main execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Album Vision+ Pro")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AlbumVision")
    
    # Default test directory
    test_dir = os.path.join(os.getcwd(), "data", "test_images")
    if not os.path.exists(test_dir):
        os.makedirs(test_dir, exist_ok=True)
        print(f"Created test directory: {test_dir}")
    
    try:
        window = EnhancedImageWindow(test_dir)
        window.show()
        
        print("Album Vision+ Pro started successfully!")
        print(f"AI Features: {'Available' if AI_FEATURES_AVAILABLE else 'Unavailable'}")
        print(f"Test directory: {test_dir}")
        
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Startup Error", f"Failed to start Album Vision+ Pro:\n{str(e)}")
        sys.exit(1)