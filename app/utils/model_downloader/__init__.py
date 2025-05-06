import os 
from pathlib import Path 
from ultralytics import YOLO 
def download_models(): 
    models_dir = Path('models') 
    models_dir.mkdir(exist_ok=True) 
    try: 
        model = YOLO("yolo11n.pt") 
    except Exception as e: 
        pass 
