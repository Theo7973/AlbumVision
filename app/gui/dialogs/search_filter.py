
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                              QLineEdit, QListWidget, QGroupBox, QComboBox, QCheckBox,
                              QGridLayout, QSpacerItem, QSizePolicy, QListWidgetItem,
                              QTextEdit, QSplitter, QWidget, QScrollArea)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap
import os
import json
from datetime import datetime, timedelta
import fnmatch

class SearchWorker(QThread):
    """Worker thread for searching and filtering images"""
    results_ready = Signal(list)
    progress = Signal(str)
    
    def __init__(self, image_directory, search_params):
        super().__init__()
        self.image_directory = image_directory
        self.search_params = search_params
        
    def run(self):
        """Perform search based on parameters"""
        try:
            results = []
            
            if not os.path.exists(self.image_directory):
                self.results_ready.emit(results)
                return
                
            self.progress.emit("Searching images...")
            
            # Supported image extensions
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
            
            # Get all image files
            all_files = []
            for root, dirs, files in os.walk(self.image_directory):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in image_extensions):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            self.progress.emit(f"Filtering {len(all_files)} images...")
            
            # Apply filters
            for i, file_path in enumerate(all_files):
                try:
                    if self.matches_criteria(file_path):
                        file_info = self.get_file_info(file_path)
                        results.append(file_info)
                    
                    # Progress update
                    if i % 100 == 0:
                        self.progress.emit(f"Processed {i+1}/{len(all_files)} images...")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
            
            # Sort results based on sort criteria
            sort_by = self.search_params.get('sort_by', 'name')
            reverse = self.search_params.get('sort_reverse', False)
            
            if sort_by == 'name':
                results.sort(key=lambda x: x['name'], reverse=reverse)
            elif sort_by == 'size':
                results.sort(key=lambda x: x['size_mb'], reverse=reverse)
            elif sort_by == 'date':
                results.sort(key=lambda x: x['modified'], reverse=reverse)
            
            self.progress.emit(f"Found {len(results)} matching images")
            self.results_ready.emit(results)
            
        except Exception as e:
            print(f"Error in search: {e}")
            self.results_ready.emit([])
    
    def matches_criteria(self, file_path):
        """Check if file matches search criteria"""
        params = self.search_params
        
        try:
            # File name filter
            filename = os.path.basename(file_path).lower()
            if params.get('filename_filter'):
                search_text = params['filename_filter'].lower()
                if params.get('exact_match', False):
                    if search_text not in filename:
                        return False
                else:
                    # Use wildcard matching
                    if not fnmatch.fnmatch(filename, f"*{search_text}*"):
                        return False
            
            # File size filter
            if params.get('size_filter') != 'all':
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                size_filter = params['size_filter']
                
                if size_filter == 'small' and file_size_mb >= 0.5:
                    return False
                elif size_filter == 'medium' and (file_size_mb < 0.5 or file_size_mb >= 5.0):
                    return False
                elif size_filter == 'large' and file_size_mb < 5.0:
                    return False
            
            # Date filter
            if params.get('date_filter') != 'all':
                file_stat = os.stat(file_path)
                file_date = datetime.fromtimestamp(file_stat.st_mtime)
                now = datetime.now()
                
                date_filter = params['date_filter']
                if date_filter == 'today' and file_date.date() != now.date():
                    return False
                elif date_filter == 'week' and file_date < now - timedelta(days=7):
                    return False
                elif date_filter == 'month' and file_date < now - timedelta(days=30):
                    return False
                elif date_filter == 'year' and file_date < now - timedelta(days=365):
                    return False
            
            # File type filter
            if params.get('type_filter') != 'all':
                file_ext = os.path.splitext(file_path)[1].lower()
                type_filter = params['type_filter']
                
                if type_filter == 'jpg' and file_ext not in ['.jpg', '.jpeg']:
                    return False
                elif type_filter == 'png' and file_ext != '.png':
                    return False
                elif type_filter == 'other' and file_ext in ['.jpg', '.jpeg', '.png']:
                    return False
            
            # Category filter (basic path-based detection)
            if params.get('category_filter') != 'all':
                detected_category = self.detect_category(file_path)
                if detected_category.lower() != params['category_filter'].lower():
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error checking criteria for {file_path}: {e}")
            return False
    
    def detect_category(self, file_path):
        """Simple category detection based on folder structure"""
        path_parts = file_path.lower().split(os.sep)
        
        categories = {
            'animal': ['animal', 'pet', 'wildlife'],
            'person': ['person', 'people', 'human'],
            'vehicle': ['vehicle', 'car', 'truck'],
            'cat': ['cat', 'kitten'],
            'dog': ['dog', 'puppy']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if any(keyword in part for part in path_parts):
                    return category
        
        return 'unknown'
    
    def get_file_info(self, file_path):
        """Get comprehensive file information"""
        try:
            file_stat = os.stat(file_path)
            size_mb = file_stat.st_size / (1024 * 1024)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size_mb': size_mb,
                'size_bytes': file_stat.st_size,
                'modified': datetime.fromtimestamp(file_stat.st_mtime),
                'extension': os.path.splitext(file_path)[1].lower(),
                'directory': os.path.dirname(file_path),
                'category': self.detect_category(file_path)
            }
        except Exception as e:
            print(f"Error getting file info for {file_path}: {e}")
            return None


class SearchFilterDialog(QDialog):
    """Quick Search & Filter System Dialog"""
    
    def __init__(self, parent=None, image_directory=""):
        super().__init__(parent)
        self.setWindowTitle("🔍 Search & Filter Images")
        self.setFixedSize(900, 700)
        self.image_directory = image_directory
        self.search_worker = None
        self.search_history = self.load_search_history()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the search and filter UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🔍 Search & Filter Images")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Create splitter for filters and results
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Search filters
        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)
        
        # Search by filename
        filename_group = QGroupBox("📝 Filename Search")
        filename_layout = QVBoxLayout()
        
        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("Enter filename to search...")
        self.filename_input.textChanged.connect(self.on_search_text_changed)
        filename_layout.addWidget(self.filename_input)
        
        self.exact_match_cb = QCheckBox("Exact match")
        filename_layout.addWidget(self.exact_match_cb)
        
        filename_group.setLayout(filename_layout)
        filter_layout.addWidget(filename_group)
        
        # Quick search history
        history_group = QGroupBox(" Recent Searches")
        history_layout = QVBoxLayout()
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(100)
        self.history_list.itemClicked.connect(self.use_history_search)
        self.populate_search_history()
        history_layout.addWidget(self.history_list)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_search_history)
        history_layout.addWidget(clear_history_btn)
        
        history_group.setLayout(history_layout)
        filter_layout.addWidget(history_group)
        
        # Filter options
        filters_group = QGroupBox(" Filters")
        filters_layout = QGridLayout()
        
        # Size filter
        filters_layout.addWidget(QLabel("File Size:"), 0, 0)
        self.size_filter = QComboBox()
        self.size_filter.addItems(["All Sizes", "Small (< 0.5MB)", "Medium (0.5-5MB)", "Large (> 5MB)"])
        filters_layout.addWidget(self.size_filter, 0, 1)
        
        # Date filter
        filters_layout.addWidget(QLabel("Date Modified:"), 1, 0)
        self.date_filter = QComboBox()
        self.date_filter.addItems(["Any Time", "Today", "This Week", "This Month", "This Year"])
        filters_layout.addWidget(self.date_filter, 1, 1)
        
        # File type filter
        filters_layout.addWidget(QLabel("File Type:"), 2, 0)
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "JPG/JPEG", "PNG", "Other"])
        filters_layout.addWidget(self.type_filter, 2, 1)
        
        # Category filter
        filters_layout.addWidget(QLabel("Category:"), 3, 0)
        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Animal", "Person", "Vehicle", "Cat", "Dog", "Unknown"])
        filters_layout.addWidget(self.category_filter, 3, 1)
        
        filters_group.setLayout(filters_layout)
        filter_layout.addWidget(filters_group)
        
        # Sort options
        sort_group = QGroupBox(" Sort Results")
        sort_layout = QGridLayout()
        
        sort_layout.addWidget(QLabel("Sort by:"), 0, 0)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Size", "Date Modified"])
        sort_layout.addWidget(self.sort_combo, 0, 1)
        
        self.sort_reverse_cb = QCheckBox("Descending order")
        sort_layout.addWidget(self.sort_reverse_cb, 1, 0, 1, 2)
        
        sort_group.setLayout(sort_layout)
        filter_layout.addWidget(sort_group)
        
        # Search button
        self.search_button = QPushButton("🔍 Search")
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #007ACC;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        filter_layout.addWidget(self.search_button)
        
        filter_layout.addStretch()
        
        # Right side - Results
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Results header
        self.results_label = QLabel("Search results will appear here")
        self.results_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(self.results_label)
        
        # Progress indicator
        self.progress_label = QLabel("")
        results_layout.addWidget(self.progress_label)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.open_file_location)
        results_layout.addWidget(self.results_list)
        
        # Results info
        self.results_info = QTextEdit()
        self.results_info.setMaximumHeight(150)
        self.results_info.setReadOnly(True)
        results_layout.addWidget(self.results_info)
        
        # Add widgets to splitter
        splitter.addWidget(filter_widget)
        splitter.addWidget(results_widget)
        splitter.setSizes([300, 600])  # Give more space to results
        
        layout.addWidget(splitter)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.export_results_btn = QPushButton(" Export Results")
        self.export_results_btn.clicked.connect(self.export_search_results)
        self.export_results_btn.setEnabled(False)
        button_layout.addWidget(self.export_results_btn)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
    def on_search_text_changed(self):
        """Auto-search when text changes (with delay)"""
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_timer.start(500)  # 500ms delay
        
    def perform_search(self):
        """Perform the search with current parameters"""
        search_text = self.filename_input.text().strip()
        
        # Build search parameters
        search_params = {
            'filename_filter': search_text,
            'exact_match': self.exact_match_cb.isChecked(),
            'size_filter': ['all', 'small', 'medium', 'large'][self.size_filter.currentIndex()],
            'date_filter': ['all', 'today', 'week', 'month', 'year'][self.date_filter.currentIndex()],
            'type_filter': ['all', 'jpg', 'png', 'other'][self.type_filter.currentIndex()],
            'category_filter': ['all', 'animal', 'person', 'vehicle', 'cat', 'dog', 'unknown'][self.category_filter.currentIndex()],
            'sort_by': ['name', 'size', 'date'][self.sort_combo.currentIndex()],
            'sort_reverse': self.sort_reverse_cb.isChecked()
        }
        
        # Save search to history if there's text
        if search_text:
            self.add_to_search_history(search_text)
        
        # Clear current results
        self.results_list.clear()
        self.results_info.clear()
        self.export_results_btn.setEnabled(False)
        
        # Update UI
        self.search_button.setEnabled(False)
        self.progress_label.setText("🔍 Searching...")
        
        # Start search worker
        self.search_worker = SearchWorker(self.image_directory, search_params)
        self.search_worker.results_ready.connect(self.display_results)
        self.search_worker.progress.connect(self.update_progress)
        self.search_worker.start()
        
    def update_progress(self, message):
        """Update progress message"""
        self.progress_label.setText(message)
        
    def display_results(self, results):
        """Display search results"""
        self.search_button.setEnabled(True)
        self.progress_label.setText("")
        
        if not results:
            self.results_label.setText("No images found matching criteria")
            self.results_info.setText("Try adjusting your search parameters.")
            return
        
        self.results_label.setText(f"Found {len(results)} matching images")
        self.export_results_btn.setEnabled(True)
        
        # Populate results list
        for result in results:
            item_text = f"{result['name']} ({result['size_mb']:.1f} MB) - {result['modified'].strftime('%Y-%m-%d')}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, result)  # Store full result data
            self.results_list.addItem(item)
        
        # Show summary info
        total_size = sum(r['size_mb'] for r in results)
        avg_size = total_size / len(results) if results else 0
        
        info_text = f"""Search Summary:
• Found: {len(results)} images
• Total size: {total_size:.1f} MB
• Average size: {avg_size:.2f} MB
• Date range: {min(r['modified'] for r in results).strftime('%Y-%m-%d')} to {max(r['modified'] for r in results).strftime('%Y-%m-%d')}

Double-click any result to open its folder location."""
        
        self.results_info.setText(info_text)
        
    def open_file_location(self, item):
        """Open the file location in system file explorer"""
        result = item.data(Qt.UserRole)
        if result:
            file_path = result['path']
            folder_path = os.path.dirname(file_path)
            
            # Open folder in system file explorer
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':  # macOS and Linux
                    os.system(f'open "{folder_path}"')  # macOS
                    # os.system(f'xdg-open "{folder_path}"')  # Linux
            except Exception as e:
                print(f"Error opening folder: {e}")
                
    def populate_search_history(self):
        """Populate the search history list"""
        self.history_list.clear()
        for search in self.search_history[-10:]:  # Show last 10
            self.history_list.addItem(search)
            
    def use_history_search(self, item):
        """Use a search from history"""
        search_text = item.text()
        self.filename_input.setText(search_text)
        
    def add_to_search_history(self, search_text):
        """Add search to history"""
        if search_text and search_text not in self.search_history:
            self.search_history.append(search_text)
            if len(self.search_history) > 20:  # Keep last 20
                self.search_history = self.search_history[-20:]
            self.save_search_history()
            self.populate_search_history()
            
    def clear_search_history(self):
        """Clear search history"""
        self.search_history = []
        self.save_search_history()
        self.populate_search_history()
        
    def load_search_history(self):
        """Load search history from file"""
        try:
            history_file = os.path.join('data', 'search_history.json')
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading search history: {e}")
        return []
        
    def save_search_history(self):
        """Save search history to file"""
        try:
            os.makedirs('data', exist_ok=True)
            history_file = os.path.join('data', 'search_history.json')
            with open(history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving search history: {e}")
            
    def export_search_results(self):
        """Export search results to text file"""
        try:
            results = []
            for i in range(self.results_list.count()):
                item = self.results_list.item(i)
                result = item.data(Qt.UserRole)
                if result:
                    results.append(result)
            
            if not results:
                return
                
            # Create export text
            export_text = f"Search Results Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            export_text += f"Found {len(results)} images\n\n"
            
            for result in results:
                export_text += f"File: {result['name']}\n"
                export_text += f"Path: {result['path']}\n"
                export_text += f"Size: {result['size_mb']:.1f} MB\n"
                export_text += f"Modified: {result['modified'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                export_text += f"Category: {result['category']}\n\n"
            
            # Save to file
            os.makedirs('data', exist_ok=True)
            export_file = os.path.join('data', f'search_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
            with open(export_file, 'w') as f:
                f.write(export_text)
                
            self.results_info.append(f"\n✅ Results exported to: {export_file}")
            
        except Exception as e:
            print(f"Error exporting results: {e}")
            self.results_info.append(f"\n❌ Export failed: {str(e)}")
            
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
        event.accept()