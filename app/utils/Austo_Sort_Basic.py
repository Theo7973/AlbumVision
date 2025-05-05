import os
from collections import defaultdict
from ultralytics import YOLO

#YOLOv8 model
model = YOLO("yolov8n.pt")

#Set folder path
input_path = r"C:\Users\austi\OneDrive\Pictures\VISION FOLDERS\dogs"
image_extensions = [".jpg", ".jpeg", ".png", ".webp"]

#Store results
sorted_images = defaultdict(list)

def process_image(image_path):
    filename = os.path.basename(image_path)
    results = model(image_path, verbose=False)

    labels = set()
    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        labels.add(label)

    for label in labels:
        sorted_images[label].append(filename)

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