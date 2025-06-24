
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QGroupBox, QGridLayout, QProgressBar, QTextEdit, QScrollArea,
                              QWidget, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

class StatsWorker(QThread):
    """Worker thread for calculating image statistics"""
    stats_ready = Signal(dict)
    progress = Signal(str)
    
    def __init__(self, image_directory):
        super().__init__()
        self.image_directory = image_directory
        
    def run(self):
        """Calculate comprehensive image statistics"""
        try:
            stats = {
                'total_images': 0,
                'total_size_mb': 0.0,
                'categories': defaultdict(int),
                'file_types': defaultdict(int),
                'size_distribution': {'small': 0, 'medium': 0, 'large': 0},
                'recent_files': [],
                'oldest_file': None,
                'newest_file': None,
                'average_size_mb': 0.0,
                'largest_file': {'name': '', 'size_mb': 0.0},
                'export_history': []
            }
            
            if not os.path.exists(self.image_directory):
                self.stats_ready.emit(stats)
                return
                
            self.progress.emit("Scanning image directory...")
            
            # Supported image extensions
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
            
            # Scan all files
            all_files = []
            for root, dirs, files in os.walk(self.image_directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            stats['total_images'] = len(all_files)
            
            if stats['total_images'] == 0:
                self.stats_ready.emit(stats)
                return
                
            self.progress.emit(f"Analyzing {stats['total_images']} images...")
            
            # Analyze each file
            file_info_list = []
            total_size_bytes = 0
            
            for i, file_path in enumerate(all_files):
                try:
                    file_stat = os.stat(file_path)
                    file_size_bytes = file_stat.st_size
                    file_size_mb = file_size_bytes / (1024 * 1024)
                    
                    total_size_bytes += file_size_bytes
                    
                    # File type
                    extension = os.path.splitext(file_path)[1].lower()
                    stats['file_types'][extension] += 1
                    
                    # Size distribution
                    if file_size_mb < 0.5:
                        stats['size_distribution']['small'] += 1
                    elif file_size_mb < 5.0:
                        stats['size_distribution']['medium'] += 1
                    else:
                        stats['size_distribution']['large'] += 1
                    
                    # Track largest file
                    if file_size_mb > stats['largest_file']['size_mb']:
                        stats['largest_file'] = {
                            'name': os.path.basename(file_path),
                            'size_mb': file_size_mb
                        }
                    
                    # File modification times
                    mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                    file_info = {
                        'path': file_path,
                        'name': os.path.basename(file_path),
                        'size_mb': file_size_mb,
                        'modified': mod_time
                    }
                    file_info_list.append(file_info)
                    
                    # Category detection (basic)
                    filename_lower = os.path.basename(file_path).lower()
                    category = self.detect_category_from_path(file_path)
                    stats['categories'][category] += 1
                    
                    # Progress update
                    if i % 50 == 0:  # Update every 50 files
                        self.progress.emit(f"Processed {i+1}/{stats['total_images']} images...")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
            
            # Calculate derived statistics
            stats['total_size_mb'] = total_size_bytes / (1024 * 1024)
            stats['average_size_mb'] = stats['total_size_mb'] / max(stats['total_images'], 1)
            
            # Sort by modification time for recent/oldest files
            if file_info_list:
                file_info_list.sort(key=lambda x: x['modified'], reverse=True)
                stats['recent_files'] = file_info_list[:10]  # Last 10 modified
                stats['newest_file'] = file_info_list[0]
                stats['oldest_file'] = file_info_list[-1]
            
            # Load export history if available
            self.progress.emit("Loading export history...")
            stats['export_history'] = self.load_export_history()
            
            self.progress.emit("Statistics ready!")
            self.stats_ready.emit(stats)
            
        except Exception as e:
            print(f"Error in stats calculation: {e}")
            self.stats_ready.emit(stats)
    
    def detect_category_from_path(self, file_path):
        """Simple category detection based on folder structure"""
        path_parts = file_path.lower().split(os.sep)
        
        # Common category keywords
        categories = {
            'animal': ['animal', 'pet', 'wildlife'],
            'person': ['person', 'people', 'human', 'portrait'],
            'vehicle': ['vehicle', 'car', 'truck', 'bike'],
            'cat': ['cat', 'kitten', 'feline'],
            'dog': ['dog', 'puppy', 'canine'],
            'appliance': ['appliance', 'device', 'electronics'],
            'kitchenware': ['kitchen', 'cooking', 'utensil'],
            'entertainment': ['tv', 'game', 'entertainment']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if any(keyword in part for part in path_parts):
                    return category.title()
        
        return 'Unknown'
    
    def load_export_history(self):
        """Load export history from JSON files"""
        try:
            history_file = os.path.join('data', 'output_path', 'export_log.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)[-5:]  # Last 5 exports
        except Exception as e:
            print(f"Error loading export history: {e}")
        return []


class StatsDashboardDialog(QDialog):
    """Image Statistics Dashboard Dialog"""
    
    def __init__(self, parent=None, image_directory=""):
        super().__init__(parent)
        self.setWindowTitle("Image Collection Statistics")
        self.setFixedSize(800, 600)
        self.image_directory = image_directory
        self.stats_worker = None
        
        self.setup_ui()
        self.start_stats_calculation()
        
    def setup_ui(self):
        """Setup the statistics dashboard UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(" Image Collection Statistics")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create scroll area for stats
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        
        # Progress indicator
        self.progress_label = QLabel("Loading statistics...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.progress_label)
        
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.clicked.connect(self.start_stats_calculation)
        button_layout.addWidget(self.refresh_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def start_stats_calculation(self):
        """Start the statistics calculation in a worker thread"""
        self.refresh_button.setEnabled(False)
        self.progress_label.setText("🔍 Scanning image directory...")
        
        # Clear existing stats
        self.clear_stats_display()
        
        # Start worker thread
        self.stats_worker = StatsWorker(self.image_directory)
        self.stats_worker.stats_ready.connect(self.display_stats)
        self.stats_worker.progress.connect(self.update_progress)
        self.stats_worker.start()
        
    def clear_stats_display(self):
        """Clear the current statistics display"""
        # Remove all widgets except progress label
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget() != self.progress_label:
                item.widget().setParent(None)
                
    def update_progress(self, message):
        """Update progress message"""
        self.progress_label.setText(message)
        
    def display_stats(self, stats):
        """Display the calculated statistics"""
        self.refresh_button.setEnabled(True)
        self.progress_label.setParent(None)  # Remove progress label
        
        # Overview Section
        overview_group = QGroupBox("📋 Overview")
        overview_layout = QGridLayout()
        
        overview_layout.addWidget(QLabel("Total Images:"), 0, 0)
        overview_layout.addWidget(QLabel(f"{stats['total_images']:,}"), 0, 1)
        
        overview_layout.addWidget(QLabel("Total Size:"), 1, 0)
        overview_layout.addWidget(QLabel(f"{stats['total_size_mb']:.1f} MB"), 1, 1)
        
        overview_layout.addWidget(QLabel("Average Size:"), 2, 0)
        overview_layout.addWidget(QLabel(f"{stats['average_size_mb']:.2f} MB"), 2, 1)
        
        if stats['largest_file']['name']:
            overview_layout.addWidget(QLabel("Largest File:"), 3, 0)
            overview_layout.addWidget(QLabel(f"{stats['largest_file']['name']} ({stats['largest_file']['size_mb']:.1f} MB)"), 3, 1)
        
        overview_group.setLayout(overview_layout)
        self.scroll_layout.addWidget(overview_group)
        
        # Categories Section
        if stats['categories']:
            categories_group = QGroupBox("🏷️ Categories")
            categories_layout = QGridLayout()
            
            row = 0
            for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_images']) * 100 if stats['total_images'] > 0 else 0
                categories_layout.addWidget(QLabel(f"{category}:"), row, 0)
                categories_layout.addWidget(QLabel(f"{count} ({percentage:.1f}%)"), row, 1)
                row += 1
                
            categories_group.setLayout(categories_layout)
            self.scroll_layout.addWidget(categories_group)
        
        # File Types Section
        if stats['file_types']:
            types_group = QGroupBox("📁 File Types")
            types_layout = QGridLayout()
            
            row = 0
            for file_type, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['total_images']) * 100 if stats['total_images'] > 0 else 0
                types_layout.addWidget(QLabel(f"{file_type.upper()}:"), row, 0)
                types_layout.addWidget(QLabel(f"{count} ({percentage:.1f}%)"), row, 1)
                row += 1
                
            types_group.setLayout(types_layout)
            self.scroll_layout.addWidget(types_group)
        
        # Size Distribution Section
        size_group = QGroupBox("📏 Size Distribution")
        size_layout = QGridLayout()
        
        size_layout.addWidget(QLabel("Small (< 0.5 MB):"), 0, 0)
        size_layout.addWidget(QLabel(f"{stats['size_distribution']['small']}"), 0, 1)
        
        size_layout.addWidget(QLabel("Medium (0.5-5 MB):"), 1, 0)
        size_layout.addWidget(QLabel(f"{stats['size_distribution']['medium']}"), 1, 1)
        
        size_layout.addWidget(QLabel("Large (> 5 MB):"), 2, 0)
        size_layout.addWidget(QLabel(f"{stats['size_distribution']['large']}"), 2, 1)
        
        size_group.setLayout(size_layout)
        self.scroll_layout.addWidget(size_group)
        
        # Recent Files Section
        if stats['recent_files']:
            recent_group = QGroupBox("🕒 Recently Modified")
            recent_layout = QVBoxLayout()
            
            for file_info in stats['recent_files'][:5]:  # Show top 5
                file_text = f"{file_info['name']} - {file_info['modified'].strftime('%Y-%m-%d %H:%M')}"
                recent_layout.addWidget(QLabel(file_text))
                
            recent_group.setLayout(recent_layout)
            self.scroll_layout.addWidget(recent_group)
        
        # Export History Section
        if stats['export_history']:
            export_group = QGroupBox(" Recent Exports")
            export_layout = QVBoxLayout()
            
            for export in stats['export_history']:
                timestamp = export.get('timestamp', 'Unknown time')
                if 'T' in timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
                        
                processed = export.get('statistics', {}).get('processed', 0)
                export_text = f"Exported {processed} images - {timestamp}"
                export_layout.addWidget(QLabel(export_text))
                
            export_group.setLayout(export_layout)
            self.scroll_layout.addWidget(export_group)
        
        # Add stretch to push everything to top
        self.scroll_layout.addStretch()
        
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.stats_worker and self.stats_worker.isRunning():
            self.stats_worker.terminate()
            self.stats_worker.wait()
        event.accept()