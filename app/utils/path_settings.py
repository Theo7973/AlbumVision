# File: app/utils/path_settings.py
# Clean PathSettings class - NO GUI IMPORTS OR DIALOG REFERENCES

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
    
    def get_setting(self, key, default=None):
        """Get any setting by key"""
        return self.settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set any setting by key"""
        self.settings[key] = value
        return self.save_settings()
    
    def has_setting(self, key):
        """Check if a setting exists"""
        return key in self.settings
    
    def remove_setting(self, key):
        """Remove a setting"""
        if key in self.settings:
            del self.settings[key]
            return self.save_settings()
        return True
    
    def reset_settings(self):
        """Reset all settings to default"""
        self.settings = {}
        return self.save_settings()
    
    def debug_info(self):
        """Return debug information about settings"""
        return {
            'settings_file': self.settings_file,
            'settings_file_exists': os.path.exists(self.settings_file),
            'output_config_file': self.output_config_file,
            'output_config_file_exists': os.path.exists(self.output_config_file),
            'current_settings': self.settings,
            'json_dir': self.json_dir
        }