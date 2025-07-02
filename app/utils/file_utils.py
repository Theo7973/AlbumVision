
"""
This module contains utility functions for file operations.
Import file, sort files, export files, set file path, fetch file metadata
"""

import os
import sys
import cv2
import numpy as np
import logging

COCO_TO_CUSTOM_TAG = {
    "fork": "Kitchenware",
    "spoon": "Kitchenware",
    "knife": "Kitchenware",
    "cup": "Kitchenware",
    "bowl": "Kitchenware",
    "wine glass": "Kitchenware",
    "dining table": "Kitchenware",
    "toaster": "Kitchenware",
    "microwave": "Kitchenware",
    "oven": "Kitchenware",
    "refrigerator": "Appliance",
    "tv": "Entertainment Device",
    "cell phone": "Appliance",
    "remote": "Entertainment Device",
    "laptop": "Appliance",
    "keyboard": "Appliance",
    "car": "Vehicle",
    "truck": "Vehicle",
    "bus": "Vehicle",
    "bicycle": "Vehicle",
    "motorcycle": "Vehicle",
    "train": "Vehicle",
    "airplane": "Vehicle",
    "boat": "Vehicle",
    "bird": "Animal",
    "horse": "Animal",
    "sheep": "Animal",
    "cow": "Animal",
    "elephant": "Animal",
    "bear": "Animal",
    "zebra": "Animal",
    "giraffe": "Animal",
    "cat": "Cat",
    "dog": "Dog",
    "person": "Person",
}

def map_coco_label_to_custom_tag(label):
    """Map a raw COCO label to a custom tag group."""
    return COCO_TO_CUSTOM_TAG.get(label.lower(), "Unknown")

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


def find_duplicate_images(input_image_path, folder_path):
    """
    Check for duplicate images in a folder compared to the input image.

    Args:
        input_image_path (str): Path to the input image.
        folder_path (str): Path to the folder containing images to compare.

    Returns:
        list: List of duplicate image paths.
    """
    # Load the input image
    input_image = cv2.imread(input_image_path)

    if input_image is None:
        raise ValueError("The input image path is invalid or the image could not be loaded.")

    duplicates = []

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip if the file is the input image itself or not an image
        if file_path == input_image_path or not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            continue

        # Load the current image
        current_image = cv2.imread(file_path)

        if current_image is None:
            continue

        # Check if the dimensions of the images are the same
        if input_image.shape != current_image.shape:
            continue

        # Compare the images pixel by pixel
        difference = cv2.subtract(input_image, current_image)
        if not np.any(difference):  # If no non-zero value in the difference, images are identical
            duplicates.append(file_path)

    return duplicates


def map_coco_label_to_custom_tag(coco_label: str) -> str:
    """Maps a COCO label to one of the 9 predefined categories."""
    label = coco_label.lower()

    mapping = {
        'animal': ['bear', 'bird', 'zebra', 'giraffe', 'elephant', 'sheep', 'cow', 'horse'],
        'cat': ['cat'],
        'dog': ['dog'],
        'person': ['person'],
        'vehicle': ['bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck', 'boat'],
        'kitchenware': ['fork', 'knife', 'spoon', 'bowl', 'cup', 'wine glass'],
        'appliance': ['microwave', 'oven', 'refrigerator', 'toaster', 'sink'],
        'entertainment device': ['tv', 'laptop', 'cell phone', 'remote', 'keyboard'],
    }

    for category, keywords in mapping.items():
        if label in keywords:
            return category

    return 'unknown'

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
