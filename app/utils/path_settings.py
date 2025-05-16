import json
import os
from pathlib import Path

class PathSettings:
    def __init__(self, config_file="user_data/settings.json"):
        self.config_file = config_file
        self.settings = self._load_settings()
    
    def _load_settings(self):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        # Load existing settings or create default
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return {"input_path": "", "output_path": ""}
        else:
            return {"input_path": "", "output_path": ""}
    
    def save_settings(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def set_input_path(self, path):
        self.settings["input_path"] = str(Path(path))
        self.save_settings()
        print(f"Input path set to: {path}")
    
    def set_output_path(self, path):
        self.settings["output_path"] = str(Path(path))
        self.save_settings()
        print(f"Output path set to: {path}")
    
    def get_input_path(self):
        return self.settings.get("input_path", "")
    
    def get_output_path(self):
        return self.settings.get("output_path", "")