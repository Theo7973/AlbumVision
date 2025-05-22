import cv2
import numpy as np

def check_image_quality(image_path, threshold=150):
    """
    Check if an image is blurry or low quality, considering image dimensions.
    
    Args:
        image_path (str): Path to the image file
        threshold (float): Base threshold for quality detection
        
    Returns:
        tuple: (quality, score, dimensions)
            - quality (str): "high", "low", or "error"
            - score (float): Quality score
            - dimensions (tuple): Image width and height
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return "error", 0, (0, 0)
            
        # Get image dimensions
        height, width = img.shape[:2]
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Adjust threshold based on image size
        # Smaller images need lower thresholds
        size_factor = min(width, height) / 1000
        adjusted_threshold = threshold * max(0.5, size_factor)
        
        # Calculate resolution score
        resolution_score = (height * width) / 1000000
        
        # Combine scores with size adjustment
        combined_score = (laplacian_var * 0.7 + resolution_score * 30) * size_factor
        
        quality = "high" if combined_score > adjusted_threshold else "low"
        
        print(f"Image: {image_path}")
        print(f"Dimensions: {width}x{height}")
        print(f"Quality: {quality}, Score: {combined_score:.2f}")
        print(f"Adjusted threshold: {adjusted_threshold:.2f}")
        
        return quality, combined_score, (width, height)
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return "error", 0, (0, 0)