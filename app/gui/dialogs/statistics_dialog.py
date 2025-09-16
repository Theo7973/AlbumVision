import os
from datetime import datetime, timedelta
from collections import defaultdict

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QWidget, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# Safe matplotlib import
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')  # Set dark theme for charts
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not available. Statistics will show text-based data only.")
    MATPLOTLIB_AVAILABLE = False


class StatsCalculatorThread(QThread):
    """Thread to calculate statistics without blocking UI"""
    finished = Signal(dict)
    
    def __init__(self, image_dir, image_labels):
        super().__init__()
        self.image_dir = image_dir
        self.image_labels = image_labels
        
    def run(self):
        try:
            if not self.image_dir or not os.path.exists(self.image_dir):
                self.finished.emit({"error": "No directory loaded"})
                return
                
            stats = self.calculate_statistics()
            self.finished.emit(stats)
            
        except Exception as e:
            self.finished.emit({"error": str(e)})
    
    def calculate_statistics(self):
        """Calculate comprehensive photo statistics"""
        stats = {
            "total_photos": 0,
            "categories": defaultdict(int),
            "file_sizes": [],
            "recent_uploads": defaultdict(int),
            "quality_distribution": {"high": 0, "medium": 0, "low": 0},
            "storage_usage": 0
        }
        
        # Get current time for recent uploads calculation
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Analyze files in directory
        for root, dirs, files in os.walk(self.image_dir):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
                    file_path = os.path.join(root, file)
                    try:
                        # Basic stats
                        stats["total_photos"] += 1
                        file_size = os.path.getsize(file_path)
                        stats["file_sizes"].append(file_size)
                        stats["storage_usage"] += file_size
                        
                        # File modification time for recent uploads
                        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if mod_time >= week_ago:
                            stats["recent_uploads"]["This Week"] += 1
                        elif mod_time >= month_ago:
                            stats["recent_uploads"]["This Month"] += 1
                        else:
                            stats["recent_uploads"]["Older"] += 1
                        
                        # Quality estimation based on file size
                        if file_size > 2000000:  # > 2MB
                            stats["quality_distribution"]["high"] += 1
                        elif file_size > 500000:  # > 500KB
                            stats["quality_distribution"]["medium"] += 1
                        else:
                            stats["quality_distribution"]["low"] += 1
                            
                    except:
                        continue
        
        # Analyze categories from loaded image labels
        if self.image_labels:
            for image_data in self.image_labels:
                if len(image_data) >= 5:  # Has tag information
                    tag = image_data[4]  # Tag is at index 4
                    if tag and tag != "Unknown":
                        stats["categories"][tag.title()] += 1
                    else:
                        stats["categories"]["Unknown"] += 1
        
        # Convert storage to readable format
        storage_bytes = stats["storage_usage"]
        if storage_bytes < 1024**2:
            stats["storage_display"] = f"{storage_bytes/1024:.1f} KB"
        elif storage_bytes < 1024**3:
            stats["storage_display"] = f"{storage_bytes/(1024**2):.1f} MB"
        else:
            stats["storage_display"] = f"{storage_bytes/(1024**3):.1f} GB"
            
        return stats


class StatisticsDialog(QDialog):
    """Professional statistics dashboard for photo library analysis"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Photo Library Statistics")
        self.setMinimumSize(700, 600)
        self.parent_window = parent
        
        # Apply professional dark theme
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
                padding: 3px 0px;  /* KEY FIX: Add vertical padding */
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
        
        self.init_ui()
        self.calculate_stats()
        
    def init_ui(self):
        """Initialize the statistics UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Photo Library Analytics")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.content_layout = QVBoxLayout(scroll_widget)
        self.content_layout.setSpacing(12)  # KEY FIX: Add spacing between sections
        
        # Loading message
        self.loading_label = QLabel("Calculating statistics...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("font-size: 14px; color: #cccccc; padding: 20px;")
        self.content_layout.addWidget(self.loading_label)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn)
        
    def calculate_stats(self):
        """Start statistics calculation in background thread"""
        if hasattr(self.parent_window, 'image_dir') and self.parent_window.image_dir:
            image_labels = getattr(self.parent_window, 'image_labels', [])
            self.stats_thread = StatsCalculatorThread(self.parent_window.image_dir, image_labels)
            self.stats_thread.finished.connect(self.on_stats_calculated)
            self.stats_thread.start()
        else:
            self.show_error("No photo directory loaded")
            
    def on_stats_calculated(self, stats):
        """Display calculated statistics"""
        # Clear loading message
        self.loading_label.hide()
        
        if "error" in stats:
            self.show_error(stats["error"])
            return
            
        self.display_statistics(stats)
        
    def show_error(self, error_msg):
        """Display error message"""
        error_label = QLabel(f"Error: {error_msg}")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setStyleSheet("color: #ff6b6b; font-size: 14px; padding: 20px;")
        self.content_layout.addWidget(error_label)
        
    def display_statistics(self, stats):
        """Display comprehensive statistics with proper spacing"""
        
        # Overview section
        overview_group = QGroupBox("Library Overview")
        overview_layout = QVBoxLayout(overview_group)
        overview_layout.setSpacing(8)  # KEY FIX: Proper spacing
        overview_layout.setContentsMargins(15, 20, 15, 15)  # KEY FIX: Proper margins
        
        overview_layout.addWidget(self.create_stat_label(f"Total Photos: {stats['total_photos']:,}"))
        overview_layout.addWidget(self.create_stat_label(f"Storage Used: {stats['storage_display']}"))
        
        if stats['file_sizes']:
            avg_size = sum(stats['file_sizes']) / len(stats['file_sizes'])
            avg_size_mb = avg_size / (1024**2)
            overview_layout.addWidget(self.create_stat_label(f"Average File Size: {avg_size_mb:.1f} MB"))
        
        self.content_layout.addWidget(overview_group)
        
        # Categories section with fixed spacing
        if stats['categories']:
            categories_group = QGroupBox("Photo Categories")
            categories_layout = QVBoxLayout(categories_group)
            categories_layout.setSpacing(6)  # KEY FIX: Consistent spacing
            categories_layout.setContentsMargins(15, 20, 15, 15)  # KEY FIX: Proper margins
            
            # Text summary
            total_categorized = sum(stats['categories'].values())
            categories_layout.addWidget(self.create_stat_label(f"Categorized Photos: {total_categorized:,}"))
            
            # Add spacing after summary
            categories_layout.addSpacing(5)
            
            # Top categories with individual labels for proper spacing
            sorted_categories = sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True)
            for category, count in sorted_categories[:10]:  # Show more categories
                percentage = (count / total_categorized * 100) if total_categorized > 0 else 0
                category_label = self.create_stat_label(f"  {category}: {count} ({percentage:.1f}%)")
                category_label.setContentsMargins(10, 0, 0, 0)  # Indent subcategories
                categories_layout.addWidget(category_label)
            
            # Chart if matplotlib available
            if MATPLOTLIB_AVAILABLE and stats['categories']:
                try:
                    categories_chart = self.create_pie_chart(stats['categories'], "Photo Categories")
                    categories_layout.addWidget(categories_chart)
                except Exception as e:
                    print(f"Chart error: {e}")
            
            self.content_layout.addWidget(categories_group)
        
        # Upload activity section
        if stats['recent_uploads']:
            uploads_group = QGroupBox("Upload Activity")
            uploads_layout = QVBoxLayout(uploads_group)
            uploads_layout.setSpacing(6)  # KEY FIX: Consistent spacing
            uploads_layout.setContentsMargins(15, 20, 15, 15)
            
            for period, count in stats['recent_uploads'].items():
                uploads_layout.addWidget(self.create_stat_label(f"{period}: {count} photos"))
            
            # Chart if matplotlib available
            if MATPLOTLIB_AVAILABLE:
                try:
                    uploads_chart = self.create_bar_chart(stats['recent_uploads'], "Recent Upload Activity")
                    uploads_layout.addWidget(uploads_chart)
                except Exception as e:
                    print(f"Chart error: {e}")
            
            self.content_layout.addWidget(uploads_group)
        
        # Quality distribution section
        if stats['quality_distribution']:
            quality_group = QGroupBox("Image Quality Distribution")
            quality_layout = QVBoxLayout(quality_group)
            quality_layout.setSpacing(6)  # KEY FIX: Consistent spacing
            quality_layout.setContentsMargins(15, 20, 15, 15)
            
            total_quality = sum(stats['quality_distribution'].values())
            for quality, count in stats['quality_distribution'].items():
                percentage = (count / total_quality * 100) if total_quality > 0 else 0
                quality_layout.addWidget(self.create_stat_label(f"{quality.title()} Quality: {count} ({percentage:.1f}%)"))
            
            self.content_layout.addWidget(quality_group)
    
    def create_stat_label(self, text):
        """Create a properly styled statistics label with consistent spacing"""
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                padding: 6px 0px;     /* INCREASED padding */
                margin: 4px 0px;      /* INCREASED margin */
                line-height: 18px;    /* FIXED line height in pixels */
                min-height: 20px;     /* MINIMUM height to prevent overlap */
            }
        """)
        return label
    def create_pie_chart(self, data, title):
        """Create a professional pie chart"""
        if not MATPLOTLIB_AVAILABLE:
            return QLabel("Charts not available")
            
        fig = Figure(figsize=(6, 4), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        
        # Professional color scheme
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#34495e', '#e67e22', '#95a5a6']
        
        wedges, texts, autotexts = ax.pie(
            data.values(), 
            labels=data.keys(),
            autopct='%1.1f%%',
            colors=colors[:len(data)],
            textprops={'color': 'white', 'fontsize': 10}
        )
        
        ax.set_title(title, color='white', fontsize=12, fontweight='bold')
        fig.tight_layout()
        
        canvas = FigureCanvas(fig)
        canvas.setMaximumHeight(300)
        return canvas
    
    def create_bar_chart(self, data, title):
        """Create a professional bar chart"""
        if not MATPLOTLIB_AVAILABLE:
            return QLabel("Charts not available")
            
        fig = Figure(figsize=(6, 3), dpi=100)
        fig.patch.set_facecolor('#2b2b2b')
        ax = fig.add_subplot(111)
        ax.set_facecolor('#2b2b2b')
        
        bars = ax.bar(data.keys(), data.values(), color='#3498db')
        
        ax.set_title(title, color='white', fontsize=12, fontweight='bold')
        ax.tick_params(colors='white', labelsize=9)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{int(height)}', ha='center', va='bottom', color='white', fontsize=9)
        
        fig.tight_layout()
        
        canvas = FigureCanvas(fig)
        canvas.setMaximumHeight(250)
        return canvas