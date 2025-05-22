import os
import json

def create_output_folders(categories, output_path):
    """
    Create category folders at the specified output path.
    
    Args:
        categories (list): List of category names to create folders for
        output_path (str): Path where folders should be created
        
    Returns:
        list: List of created folder paths
    """
    folder_paths = []
    
    # Create the base output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    # Create a folder for each category
    for category in categories:
        folder_path = os.path.join(output_path, category)
        
        # Skip if folder already exists
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            
        folder_paths.append(folder_path)
    
    # Save folder configuration to a JSON file in the data directory
    config_file = os.path.join('data', 'folder_config.json')
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    config_data = {
        'categories': categories,
        'output_path': output_path
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=4)
    
    return folder_paths