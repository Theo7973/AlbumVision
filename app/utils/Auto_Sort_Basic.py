import os
from collections import defaultdict
from ultralytics import YOLO
from file_utils import map_coco_label_to_custom_tag

def map_coco_label_to_custom_tag(label):
    mapping = {
        "person": "person",
        "cat": "cat",
        "dog": "dog",
        "car": "vehicle",
        "bus": "vehicle",
        "truck": "vehicle",
        "bicycle": "vehicle",
        "motorcycle": "vehicle",
        "airplane": "vehicle",
        "train": "vehicle",
        "knife": "kitchenware",
        "fork": "kitchenware",
        "spoon": "kitchenware",
        "bowl": "kitchenware",
        "refrigerator": "appliance",
        "microwave": "appliance",
        "oven": "appliance",
        "toaster": "appliance",
        "tv": "entertainment device",
        "laptop": "entertainment device",
        "cell phone": "entertainment device",
        "mouse": "entertainment device",
        "keyboard": "entertainment device",
        "remote": "entertainment device",
        "bear": "animal",
        "zebra": "animal",
        "elephant": "animal",
        "sheep": "animal",
        "cow": "animal",
        "horse": "animal",
        "bird": "animal",
        "giraffe": "animal",
        "dog": "dog",
        "cat": "cat"
    }
    return mapping.get(label.lower(), "unknown")

#YOLOv8 model
model = YOLO("yolov8n.pt")

#Set folder path
input_path = r"C:\Users\austi\OneDrive\Desktop\REPO\AlbumVision\data\test_images"
image_extensions = [".jpg", ".jpeg", ".png", ".webp"]

#Store results
sorted_images = defaultdict(list)

def process_image(image_path):
    filename = os.path.basename(image_path)
    results = model(image_path, verbose=False)

    custom_labels = set()
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        coco_label = model.names[cls_id]
        custom_tag = map_coco_label_to_custom_tag(coco_label)
        custom_labels.add(custom_tag)

    for tag in custom_labels:
        sorted_images[tag].append(filename)

#Confirm that it is a folder
if os.path.isdir(input_path):
    for filename in os.listdir(input_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            full_path = os.path.join(input_path, filename)
            process_image(full_path)
else:
    print("Invalid path provided. Make sure it's a directory.")

#Print
for label, images in sorted_images.items():
    print(f"{label}: {images}")
    
