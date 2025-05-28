from PIL import Image
from PIL.ExifTags import TAGS
from ultralytics import YOLO

# Load YOLO model once globally
model_path = "yolov8n.pt" 
model = YOLO(model_path)

def get_image_metadata(image_path):
    metadata = {}

    try:
        with Image.open(image_path) as img:
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["size"] = img.size  # (width, height)

            # Extract EXIF metadata if available
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ["Make", "Model", "DateTime"]:
                        metadata[tag] = value

        # Set default values
        for tag in ["Make", "Model", "DateTime"]:
            if tag not in metadata:
                metadata[tag] = "Not Available"

    except Exception as e:
        metadata["error"] = f"EXIF error: {str(e)}"

    #COCO Tag Detection using YOLO
    try:
        results = model(image_path)  # Run inference
        tags = set()

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                tags.add(label)

        metadata["Tags"] = ', '.join(sorted(tags)) if tags else "None Detected"
    except Exception as e:
        metadata["Tags"] = f"Detection error: {str(e)}"

    return metadata