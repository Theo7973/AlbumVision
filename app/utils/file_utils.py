"""
This module contains utility functions for file operations.
Import file, sort files, export files, set file path, fetch file metadata
"""

import os
import sys


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