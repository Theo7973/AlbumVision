import os
import json

class PathSettings:
    def __init__(self):
        self.settings_file = os.path.join('data', 'settings.json')
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from the settings file."""
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return {}
        return {}
    
    def save_settings(self):
        """Save settings to the settings file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_output_path(self):
        """Get the output path from settings."""
        return self.settings.get('output_path', '')
    
    def set_output_path(self, path):
        """Set the output path in settings."""
        self.settings['output_path'] = path
        return self.save_settings()