import os

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