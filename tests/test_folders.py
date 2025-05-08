import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.folder_manager import create_output_folders

# Create test category folders
categories = ["Landscapes", "Portraits", "Animals", "Food"]
folder_paths = create_output_folders(categories, "output")

# Verify folders were created
print("Checking created folders:")
for category, path in folder_paths.items():
    exists = os.path.exists(path)
    print(f"- {category}: {path} - {'Exists' if exists else 'MISSING'}")

# Check config file
config_path = "output/folder_config.json"
exists = os.path.exists(config_path)
print(f"\nConfig file: {config_path} - {'Exists' if exists else 'MISSING'}")