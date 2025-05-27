# File: app/utils/path_settings.py
# Updated PathSettings class to ensure consistent path storage and retrieval

import os
import json
from datetime import datetime

class PathSettings:
    def __init__(self):
        # Use the specific directory you want for JSON files
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

# Update your main_window.py methods to use consistent PathSettings

def open_output_path_dialog(self):
    """Open the Output Path dialog with enhanced functionality."""
    try:
        dialog = output_dialog.OutputPathDialog(self)
        if dialog.exec():  # If the user clicks "OK"
            output_path = dialog.get_output_path()
            print(f"Dialog returned output path: '{output_path}'")
            
            if output_path:
                # Save the path using PathSettings
                success = self.path_settings.set_output_path(output_path)
                if success:
                    print(f"Successfully saved output path: {output_path}")
                    # Update any UI elements that show the output path
                    if hasattr(self, 'tool_tips') and self.tool_tips:
                        self.tool_tips.setText(f"Output path: {os.path.basename(output_path)}")
                else:
                    print("Failed to save output path")
            else:
                print("No output path provided by dialog")
    except Exception as e:
        print(f"Error in output path dialog: {e}")
        # Fallback - simple path selection
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if folder_path:
            success = self.path_settings.set_output_path(folder_path)
            if success and hasattr(self, 'tool_tips') and self.tool_tips:
                self.tool_tips.setText(f"Output path: {os.path.basename(folder_path)}")

def open_export_dialog(self):
    """Open the Export dialog with enhanced functionality."""
    try:
        # Refresh path settings to get the latest saved path
        self.path_settings.settings = self.path_settings.load_settings()
        output_path = self.path_settings.get_output_path()
        
        print(f"Checking output path for export: '{output_path}'")
        
        if not output_path or output_path.strip() == "":
            print("No output path found, prompting user")
            reply = QMessageBox.question(
                self, 
                "No Output Path", 
                "No output path is set. Would you like to set one now?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.open_output_path_dialog()
                # Check again after setting path
                output_path = self.path_settings.get_output_path()
                if not output_path or output_path.strip() == "":
                    print("Still no output path after dialog")
                    return
            else:
                return
        
        print(f"Using output path for export: '{output_path}'")
        dialog = export_dialog.ExportDialog(self, self.image_dir)
        if dialog.exec():  # If the user clicks "OK"
            export_path = dialog.get_output_path()
            print(f"Images exported to: {export_path}")
            # Update status in the UI
            if hasattr(self, 'tool_tips') and self.tool_tips:
                self.tool_tips.setText(f"Export completed to: {os.path.basename(export_path)}")
    except Exception as e:
        print(f"Error in export dialog: {e}")
        QMessageBox.information(self, "Export", f"Export functionality error: {str(e)}")

# Updated output_dialog.py save method
def save_and_accept(self):
    """Save the output path and accept the dialog - Updated version"""
    output_path = self.path_input.text().strip()
    print(f"Attempting to save output path: '{output_path}'")
    
    if not output_path:
        QMessageBox.warning(self, "Invalid Path", "Please enter or select an output path.")
        return
    
    # Create directory if it doesn't exist and option is checked
    if not os.path.exists(output_path):
        if self.create_if_missing.isChecked():
            try:
                os.makedirs(output_path)
                QMessageBox.information(self, "Directory Created", 
                                      f"Created directory: {output_path}")
            except Exception as e:
                QMessageBox.critical(self, "Creation Error", 
                                   f"Could not create directory: {str(e)}")
                return
        else:
            QMessageBox.warning(self, "Directory Missing", 
                               "Directory does not exist and creation is disabled.")
            return
    
    # Validate write permissions
    if self.validate_writable.isChecked():
        if not os.access(output_path, os.W_OK):
            QMessageBox.warning(self, "Permission Error", 
                               "No write permissions for the selected directory.")
            return
    
    # Save to settings - this is the crucial part
    try:
        success = self.path_settings.set_output_path(output_path)
        if not success:
            QMessageBox.critical(self, "Save Error", "Failed to save output path to settings.")
            return
            
        print(f"Output path successfully saved: {output_path}")
        
        # Add to history if option is checked
        if self.add_to_history.isChecked():
            self.add_to_path_history(output_path)
        
        QMessageBox.information(self, "Path Saved", 
                               f"Output path successfully set to:\n{output_path}")
        self.accept()
        
    except Exception as e:
        print(f"Error saving output path: {e}")
        QMessageBox.critical(self, "Save Error", 
                           f"Error saving output path: {str(e)}")

# Debug function to check current settings
def debug_path_settings(self):
    """Debug function to check current path settings"""
    print("\n=== DEBUG PATH SETTINGS ===")
    print(f"Settings file: {self.path_settings.settings_file}")
    print(f"Settings exist: {os.path.exists(self.path_settings.settings_file)}")
    print(f"Current settings: {self.path_settings.settings}")
    print(f"Output path: '{self.path_settings.get_output_path()}'")
    
    # Check if files exist
    if os.path.exists(self.path_settings.settings_file):
        try:
            with open(self.path_settings.settings_file, 'r') as f:
                content = f.read()
                print(f"Settings file content: {content}")
        except Exception as e:
            print(f"Error reading settings file: {e}")
    
    print("=== END DEBUG ===\n")

# Add this to your main_window.py to test
def test_path_settings(self):
    """Test function to verify path settings work"""
    print("Testing path settings...")
    
    # Test setting a path
    test_path = r"C:\Users\Theo-\Desktop\TestOutput"
    print(f"Setting test path: {test_path}")
    success = self.path_settings.set_output_path(test_path)
    print(f"Set result: {success}")
    
    # Test getting the path
    retrieved_path = self.path_settings.get_output_path()
    print(f"Retrieved path: '{retrieved_path}'")
    
    # Test with fresh instance
    fresh_settings = PathSettings()
    fresh_path = fresh_settings.get_output_path()
    print(f"Fresh instance path: '{fresh_path}'")
    
    if test_path == retrieved_path == fresh_path:
        print("✓ Path settings working correctly!")
    else:
        print("✗ Path settings not working correctly!")