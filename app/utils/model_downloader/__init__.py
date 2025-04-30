# Model Downloader Package 
import os 
from pathlib import Path 
from ultralytics import YOLO 
 
def download_models(): 
    """Download required YOLO models if they don't exist.""" 
    models_dir = Path('models') 
    models_dir.mkdir(exist_ok=True) 
 
    # Download YOLOv11 models 
    try: 
        print("Downloading YOLOv11 model...") 
        model = YOLO("yolo11n.pt") 
        print(f"YOLOv11 model downloaded successfully!") 
    except Exception as e: 
        print(f"Error downloading YOLOv11 model: {e}") 
        print("You may need to download it manually.") 
