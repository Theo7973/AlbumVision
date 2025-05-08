import cv2
import numpy as np

def check_image_quality(image_path, threshold=150):
    """
    Check if an image is blurry or low quality.
    
    Args:
        image_path: Path to the image file
        threshold: Laplacian variance threshold (lower means blurrier)
        
    Returns:
        quality: String indicating "low" or "high" quality
        score: Numerical score of image quality
    """
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not read image at {image_path}")
            return "error", 0
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (measure of focus/blur)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Check image resolution
        height, width = img.shape[:2]
        resolution_score = (height * width) / 1000000  # Normalized by megapixels
        
        # Combine scores (we can adjust weights as needed later here)
        combined_score = laplacian_var * 0.7 + resolution_score * 30
        
        quality = "high" if combined_score > threshold else "low"
        
        print(f"Image: {image_path}, Quality: {quality}, Score: {combined_score:.2f}")
        return quality, combined_score
        
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return "error", 0