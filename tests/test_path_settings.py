import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.path_settings import PathSettings

# Initialize with a test config file
settings = PathSettings("user_data/test_settings.json")

# Test setting paths
test_output_path = os.path.abspath("output/test_directory")
settings.set_output_path(test_output_path)

# Verify path was saved
saved_path = settings.get_output_path()
print(f"Saved output path: {saved_path}")
print(f"Matches original: {saved_path == str(Path(test_output_path))}")

# Check that file was created
config_exists = os.path.exists("user_data/test_settings.json")
print(f"Settings file exists: {config_exists}")