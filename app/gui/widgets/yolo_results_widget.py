# File: app/gui/widgets/yolo_results_widget.py
# CORRECT YOLO Results Display Widget

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QScrollArea, QGroupBox, QProgressBar, QTextEdit,
                               QListWidget, QListWidgetItem, QPushButton, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QPixmap
import os
import json
from datetime import datetime

class YOLOResultsWidget(QWidget):
    """Widget to display YOLO detection results and statistics"""
    
    # Signal to notify when user wants to view an image
    image_view_requested = Signal(str)  # Emits image path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(350)  # Fixed width for right panel
        self.current_results = {}
        self.total_processed = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the YOLO results display UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🧠 YOLO Detection Results")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #007ACC; padding: 5px;")
        layout.addWidget(title)
        
        # Processing status section
        status_group = QGroupBox("Processing Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Ready to process images")
        self.status_label.setWordWrap(True)
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        self.processed_count_label = QLabel("Processed: 0 images")
        status_layout.addWidget(self.processed_count_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Category summary section
        summary_group = QGroupBox("Category Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setMaximumHeight(120)
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlainText("No classifications yet...")
        summary_layout.addWidget(self.summary_text)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Recent detections section
        recent_group = QGroupBox("Recent Detections")
        recent_layout = QVBoxLayout()
        
        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        self.recent_list.itemDoubleClicked.connect(self.on_recent_item_clicked)
        recent_layout.addWidget(self.recent_list)
        
        # Clear recent button
        clear_btn = QPushButton("Clear Recent")
        clear_btn.clicked.connect(self.clear_recent_detections)
        clear_btn.setMaximumWidth(100)
        recent_layout.addWidget(clear_btn)
        
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        # Statistics section
        stats_group = QGroupBox("Classification Stats")
        stats_layout = QVBoxLayout()
        
        self.confidence_label = QLabel("Avg Confidence: N/A")
        stats_layout.addWidget(self.confidence_label)
        
        self.accuracy_label = QLabel("High Confidence: N/A")
        stats_layout.addWidget(self.accuracy_label)
        
        self.last_updated_label = QLabel("Last Updated: Never")
        self.last_updated_label.setStyleSheet("color: #666; font-size: 10px;")
        stats_layout.addWidget(self.last_updated_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    def start_processing(self, total_images):
        """Start processing indicator"""
        self.total_processed = 0
        self.progress_bar.setMaximum(total_images)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Processing {total_images} images with YOLO...")
        self.update_processed_count()
        
    def add_detection_result(self, image_path, predicted_class, confidence):
        """Add a new YOLO detection result"""
        try:
            filename = os.path.basename(image_path)
            
            # Update progress
            self.total_processed += 1
            self.progress_bar.setValue(self.total_processed)
            self.update_processed_count()
            
            # Store result
            self.current_results[image_path] = {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'filename': filename
            }
            
            # Add to recent detections (keep last 10)
            confidence_str = f"{confidence:.1%}" if confidence > 0 else "N/A"
            item_text = f"{filename} → {predicted_class.title()} ({confidence_str})"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, image_path)  # Store full path
            
            self.recent_list.insertItem(0, item)  # Add to top
            
            # Keep only last 10 items
            while self.recent_list.count() > 10:
                self.recent_list.takeItem(self.recent_list.count() - 1)
            
            # Update summary and stats
            self.update_summary()
            self.update_statistics()
        except Exception as e:
            print(f"Error adding detection result: {e}")
        
    def finish_processing(self):
        """Called when processing is complete"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"✅ Processing complete! Classified {self.total_processed} images")
        self.last_updated_label.setText(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        
    def update_processed_count(self):
        """Update processed count display"""
        self.processed_count_label.setText(f"Processed: {self.total_processed} images")
        
    def update_summary(self):
        """Update category summary"""
        try:
            if not self.current_results:
                self.summary_text.setPlainText("No classifications yet...")
                return
                
            # Count by category
            category_counts = {}
            for result in self.current_results.values():
                category = result['predicted_class']
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Create summary text
            summary_lines = ["Category Distribution:"]
            total = len(self.current_results)
            
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total) * 100
                summary_lines.append(f"• {category.title()}: {count} ({percentage:.1f}%)")
            
            self.summary_text.setPlainText("\n".join(summary_lines))
        except Exception as e:
            print(f"Error updating summary: {e}")
        
    def update_statistics(self):
        """Update statistics display"""
        try:
            if not self.current_results:
                self.confidence_label.setText("Avg Confidence: N/A")
                self.accuracy_label.setText("High Confidence: N/A")
                return
                
            # Calculate average confidence (exclude unknowns)
            confidences = [r['confidence'] for r in self.current_results.values() if r['confidence'] > 0]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                self.confidence_label.setText(f"Avg Confidence: {avg_confidence:.1%}")
                
                # Count high confidence detections
                high_conf_count = sum(1 for c in confidences if c > 0.7)
                high_conf_percentage = (high_conf_count / len(confidences)) * 100
                self.accuracy_label.setText(f"High Confidence: {high_conf_count}/{len(confidences)} ({high_conf_percentage:.1f}%)")
            else:
                self.confidence_label.setText("Avg Confidence: N/A")
                self.accuracy_label.setText("High Confidence: N/A")
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def clear_recent_detections(self):
        """Clear the recent detections list"""
        self.recent_list.clear()
        
    def on_recent_item_clicked(self, item):
        """Handle clicking on a recent detection item"""
        image_path = item.data(Qt.UserRole)
        if image_path:
            self.image_view_requested.emit(image_path)
            
    def clear_all_results(self):
        """Clear all results and reset the widget"""
        self.current_results = {}
        self.total_processed = 0
        self.recent_list.clear()
        self.status_label.setText("Ready to process images")
        self.processed_count_label.setText("Processed: 0 images")
        self.summary_text.setPlainText("No classifications yet...")
        self.confidence_label.setText("Avg Confidence: N/A")
        self.accuracy_label.setText("High Confidence: N/A")
        self.last_updated_label.setText("Last Updated: Never")
        self.progress_bar.setVisible(False)
        
    def get_classification_summary(self):
        """Get a summary of all classifications for export"""
        return {
            'total_processed': self.total_processed,
            'results': self.current_results,
            'timestamp': datetime.now().isoformat()
        }