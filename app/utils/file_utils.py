"""
This module contains utility functions for file operations.
Import file, sort files, export files, set file path, fetch file metadata
"""

import os
import sys
from collections import defaultdict
from ultralytics import YOLO
from PIL import Image
from PIL.ExifTags import TAGS
import time # For testing purposes

#-------------Austin's Code------------------
#YOLOv8 model
model = YOLO("yolov8n.pt")

#Set folder path
input_path = r"C:\Users\austi\OneDrive\Pictures\VISION FOLDERS\dogs"
image_extensions = [".jpg", ".jpeg", ".png", ".webp"]

#Store results
sorted_images = defaultdict(list)
#-----------------------------------------------

def filter_non_image_files(file_list):
    """
    Filters out strings that do not end with 'jpg', 'png', or 'webp'.
    Skips items that are not strings.

    Args:
        file_list (list): A list of items to check.

    Returns:
        tuple: A tuple containing:
            - A list of strings (original list without skipped items).
            - A list of strings that do not end with the specified extensions.
    """
    valid_extensions = ('jpg', 'png', 'webp')
    filtered_list = [file for file in file_list if isinstance(file, str)]
    non_image_files = [
        file for file in filtered_list 
        if not file.lower().endswith(valid_extensions)
    ]
    return filtered_list, non_image_files


def get_all_files_in_directory(directory):
    """
    Recursively finds all files in the given directory and its subfolders.

    Args:
        directory (str): The path to the directory.

    Returns:
        list: A list of file paths as strings.
    """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list


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


def get_image_metadata(image_path):
    metadata = {}

    try:
        with Image.open(image_path) as img:
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["size"] = img.size  #(width, height)

            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ["Make", "Model", "DateTime"]:
                        metadata[tag] = value

            #defaults if not found
            for tag in ["Make", "Model", "DateTime"]:
                if tag not in metadata:
                    metadata[tag] = "Not Available"

    except Exception as e:
        metadata["error"] = str(e)

    return metadata

def print_progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

# Only for testing purposes
# if __name__ == "__main__":
#     # Example usage
#     directory_path = r"D:\Full_Sail\Month_15\Project and Portfolio V\Testing"
#     all_files = get_all_files_in_directory(directory_path)
#     # print(all_files)  # Output: List of file paths in the directory and subfolders
#     print(f'Number of fles in dir: {len(all_files)}\n')  # Output: Number of files found

#     # Example usage
#     filtered_list, non_images = filter_non_image_files(all_files)
#     print(f'Image file list: {filtered_list}\n')
#     print(f'Non image file list: {non_images}')

#process_image test
    # Confirm that it is a folder
    # if os.path.isdir(input_path):
    #     for filename in os.listdir(input_path):
    #         if any(filename.lower().endswith(ext) for ext in image_extensions):
    #             full_path = os.path.join(input_path, filename)
    #             process_image(full_path)
    # else:
    #     print("Invalid path provided. Make sure it's a directory.")

    # #Print
    # for label, images in sorted_images.items():
    #     print(f"{label}: {images}")

#get_image_metadata test
    # test_image = r"C:\Users\austi\OneDrive\Desktop\Jeniffer stuff\Pictures from cruise\b09p 35874.jpg"
    
    # from pprint import pprint
    # metadata = get_image_metadata(test_image)
    # pprint(metadata)