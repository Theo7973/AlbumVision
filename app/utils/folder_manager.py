import os
import json
from app.utils.folder_manager import create_output_folders

def create_output_folders(folder_names, base_directory="output"):
    """
    Create output folders for organized images.
    
    Args:
        folder_names: List of folder names to create
        base_directory: Base directory where folders should be created
        
    Returns:
        Dictionary mapping folder names to their full paths
    """
    # Create base directory if it doesn't exist
    os.makedirs(base_directory, exist_ok=True)
    
    # Create each folder and store paths
    folder_paths = {}
    for folder_name in folder_names:
        # Sanitize folder name
        safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in folder_name).strip()
        if not safe_name:
            continue
            
        folder_path = os.path.join(base_directory, safe_name)
        os.makedirs(folder_path, exist_ok=True)
        folder_paths[folder_name] = folder_path
        print(f"Created folder: {folder_path}")
    
    # Save folder structure to a config file
    config_path = os.path.join(base_directory, "folder_config.json")
    with open(config_path, "w") as f:
        json.dump(folder_paths, f, indent=4)
    
    return folder_paths

folder_names = ["processed", "thumbnails", "exports"]
folder_paths = create_output_folders(folder_names)
print(folder_paths)