
import os
import json
from datetime import datetime

from PySide6.QtWidgets import QFileDialog, QMessageBox

class PathSettings:
    def __init__(self):
        self.json_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "output_path")        
        os.makedirs(self.json_dir, exist_ok=True)
        self.settings_file = os.path.join(self.json_dir, 'settings.json')
        self.output_config_file = os.path.join(self.json_dir, 'output_config.json')
        
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        # Try to load from settings.json first
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    print(f"Loaded settings from: {self.settings_file}")
                    return settings
            except Exception as e:
                print(f"Error loading settings.json: {e}")
        
        # Try to load from output_config.json as fallback
        if os.path.exists(self.output_config_file):
            try:
                with open(self.output_config_file, 'r') as f:
                    config = json.load(f)
                    settings = {'output_path': config.get('output_path', '')}
                    print(f"Loaded output path from: {self.output_config_file}")
                    return settings
            except Exception as e:
                print(f"Error loading output_config.json: {e}")
        
        print("No existing settings found, creating new settings")
        return {}
    
    def save_settings(self):
        """Save settings to both JSON files for consistency"""
        try:
            # Save to settings.json
            self.settings['last_updated'] = datetime.now().isoformat()
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            
            # Also save to output_config.json for compatibility
            if 'output_path' in self.settings:
                output_config = {
                    "output_path": self.settings['output_path'],
                    "timestamp": datetime.now().isoformat(),
                    "created_by": "AlbumVision+",
                    "version": "1.0"
                }
                with open(self.output_config_file, 'w') as f:
                    json.dump(output_config, f, indent=4)
            
            print(f"Settings saved to: {self.settings_file}")
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_output_path(self):
        """Get the output path from settings"""
        path = self.settings.get('output_path', '')
        print(f"Getting output path: '{path}'")
        return path
    
    def set_output_path(self, path):
        """Set the output path in settings"""
        print(f"Setting output path to: '{path}'")
        self.settings['output_path'] = path
        success = self.save_settings()
        
        # Verify the path was saved correctly
        if success:
            # Reload settings to verify
            self.settings = self.load_settings()
            verified_path = self.settings.get('output_path', '')
            print(f"Verified saved path: '{verified_path}'")
        
        return success
    
    def validate_path(self, path):
        """Validate if a path exists and is writable"""
        if not path or not path.strip():
            return False, "Path is empty"
        
        if not os.path.exists(path):
            return False, "Path does not exist"
        
        if not os.path.isdir(path):
            return False, "Path is not a directory"
        
        if not os.access(path, os.W_OK):
            return False, "No write permission"
        
        return True, "Path is valid"
    
    def get_recent_paths(self, max_count=5):
        """Get list of recently used paths"""
        recent = self.settings.get('recent_paths', [])
        return recent[:max_count]
    
    def add_recent_path(self, path):
        """Add a path to recent paths list"""
        if not path:
            return
        
        recent = self.settings.get('recent_paths', [])
        
        # Remove if already exists
        if path in recent:
            recent.remove(path)
        
        # Add to beginning
        recent.insert(0, path)
        
        # Keep only first 10 items
        self.settings['recent_paths'] = recent[:10]
        self.save_settings()
    
    def clear_recent_paths(self):
        """Clear the recent paths list"""
        self.settings['recent_paths'] = []
        self.save_settings()


# Helper functions for main_window.py integration
def create_enhanced_output_path_dialog(parent):
    """Create an enhanced output path dialog using built-in Qt dialogs"""
    path_settings = PathSettings()
    current_path = path_settings.get_output_path()
    
    # Show folder selection dialog
    folder_path = QFileDialog.getExistingDirectory(
        parent, 
        "Select Output Directory",
        current_path or os.path.expanduser("~"),
        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    )
    
    if folder_path:
        # Validate the path
        is_valid, message = path_settings.validate_path(folder_path)
        
        if is_valid:
            # Save the path
            success = path_settings.set_output_path(folder_path)
            if success:
                path_settings.add_recent_path(folder_path)
                QMessageBox.information(
                    parent, 
                    "Path Set Successfully", 
                    f"Output path set to:\n{folder_path}"
                )
                return folder_path
            else:
                QMessageBox.warning(
                    parent, 
                    "Save Error", 
                    "Failed to save the output path settings."
                )
        else:
            QMessageBox.warning(
                parent, 
                "Invalid Path", 
                f"Selected path is not valid:\n{message}"
            )
    
    return None