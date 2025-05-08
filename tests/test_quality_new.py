import sys
import os
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))


from app.utils.image_quality import check_image_quality

# Test with sample images
clear_image = "data/test_images/clear.jpg"
blurry_image = "data/test_images/blurry.jpg"

print("Testing clear image:")
quality, score = check_image_quality(clear_image)

print("\nTesting blurry image:")
quality, score = check_image_quality(blurry_image)