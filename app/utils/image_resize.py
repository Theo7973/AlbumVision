# app/utils/image_resize.py
import os
import shutil
from PIL import Image, ImageOps
from typing import List, Tuple, Optional

class ImageResizer:
    """Utility class for resizing images with various options"""
    
    def __init__(self):
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
    
    def get_image_info(self, image_path: str) -> dict:
        """Get basic information about an image"""
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                    "size_mb": os.path.getsize(image_path) / (1024 * 1024)
                }
        except Exception as e:
            return {"error": str(e)}
    
    def resize_image(self, input_path: str, output_path: str, resize_options: dict) -> bool:
        """
        Resize a single image based on options
        
        resize_options format:
        {
            "method": "percentage" | "fixed_width" | "fixed_height" | "fixed_dimensions" | "max_dimension",
            "value": int or tuple,
            "keep_aspect": bool,
            "quality": int (1-100),
            "format": str (optional)
        }
        """
        try:
            with Image.open(input_path) as img:
                # Convert RGBA to RGB if saving as JPEG
                if resize_options.get("format", "").upper() == "JPEG" and img.mode == "RGBA":
                    img = img.convert("RGB")
                
                original_size = img.size
                new_size = self._calculate_new_size(original_size, resize_options)
                
                if new_size == original_size:
                    # No resize needed, just copy with quality adjustment
                    if resize_options.get("quality", 95) < 95:
                        img.save(output_path, quality=resize_options.get("quality", 95), optimize=True)
                    else:
                        shutil.copy2(input_path, output_path)
                else:
                    # Resize the image
                    if resize_options.get("keep_aspect", True):
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    else:
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Save with specified quality
                    save_kwargs = {
                        "quality": resize_options.get("quality", 95),
                        "optimize": True
                    }
                    
                    img.save(output_path, **save_kwargs)
                
                return True
                
        except Exception as e:
            print(f"Error resizing {input_path}: {e}")
            return False
    
    def _calculate_new_size(self, original_size: Tuple[int, int], options: dict) -> Tuple[int, int]:
        """Calculate new dimensions based on resize method"""
        width, height = original_size
        method = options.get("method", "percentage")
        value = options.get("value", 100)
        keep_aspect = options.get("keep_aspect", True)
        
        if method == "percentage":
            new_width = int(width * (value / 100))
            new_height = int(height * (value / 100))
            
        elif method == "fixed_width":
            new_width = value
            if keep_aspect:
                ratio = new_width / width
                new_height = int(height * ratio)
            else:
                new_height = height
                
        elif method == "fixed_height":
            new_height = value
            if keep_aspect:
                ratio = new_height / height
                new_width = int(width * ratio)
            else:
                new_width = width
                
        elif method == "fixed_dimensions":
            new_width, new_height = value  # value should be a tuple (width, height)
            
        elif method == "max_dimension":
            # Resize so the largest dimension becomes the specified value
            if width > height:
                new_width = value
                ratio = new_width / width
                new_height = int(height * ratio)
            else:
                new_height = value
                ratio = new_height / height
                new_width = int(width * ratio)
        else:
            return original_size
            
        return (max(1, new_width), max(1, new_height))
    
    def batch_resize(self, image_paths: List[str], output_folder: str, resize_options: dict, 
                    progress_callback=None) -> dict:
        """
        Resize multiple images
        
        Returns:
        {
            "success_count": int,
            "error_count": int,
            "errors": list of error messages,
            "output_paths": list of successfully created files
        }
        """
        results = {
            "success_count": 0,
            "error_count": 0,
            "errors": [],
            "output_paths": []
        }
        
        # Ensure output folder exists
        os.makedirs(output_folder, exist_ok=True)
        
        total_images = len(image_paths)
        
        for i, image_path in enumerate(image_paths):
            try:
                if not self._is_supported_image(image_path):
                    results["errors"].append(f"Unsupported format: {os.path.basename(image_path)}")
                    results["error_count"] += 1
                    continue
                
                # Generate output filename
                filename = os.path.basename(image_path)
                name, ext = os.path.splitext(filename)
                
                # Add suffix to avoid overwriting
                suffix = resize_options.get("suffix", "_resized")
                new_filename = f"{name}{suffix}{ext}"
                output_path = os.path.join(output_folder, new_filename)
                
                # Handle filename conflicts
                counter = 1
                while os.path.exists(output_path):
                    new_filename = f"{name}{suffix}_{counter}{ext}"
                    output_path = os.path.join(output_folder, new_filename)
                    counter += 1
                
                # Resize the image
                if self.resize_image(image_path, output_path, resize_options):
                    results["success_count"] += 1
                    results["output_paths"].append(output_path)
                else:
                    results["error_count"] += 1
                    results["errors"].append(f"Failed to resize: {os.path.basename(image_path)}")
                
                # Update progress
                if progress_callback:
                    progress_callback(i + 1, total_images)
                    
            except Exception as e:
                results["error_count"] += 1
                results["errors"].append(f"Error processing {os.path.basename(image_path)}: {str(e)}")
        
        return results
    
    def _is_supported_image(self, image_path: str) -> bool:
        """Check if the image format is supported"""
        ext = os.path.splitext(image_path)[1].lower()
        return ext in self.supported_formats
    
    def get_optimal_quality_for_size(self, target_size_mb: float, current_size_mb: float) -> int:
        """Suggest optimal quality setting to achieve target file size"""
        if current_size_mb <= target_size_mb:
            return 95  # High quality if already small enough
        
        # Simple estimation - adjust quality based on size ratio
        ratio = target_size_mb / current_size_mb
        if ratio >= 0.8:
            return 90
        elif ratio >= 0.6:
            return 80
        elif ratio >= 0.4:
            return 70
        elif ratio >= 0.2:
            return 60
        else:
            return 50