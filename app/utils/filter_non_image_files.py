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