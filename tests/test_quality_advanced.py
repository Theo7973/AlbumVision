import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.image_quality import check_image_quality

# Test with different sized images
test_images = [
    "data/test_images/clear.jpg",
    "data/test_images/blurry.jpg"
]

print("Testing enhanced quality detection with size adjustment:")
for image in test_images:
    quality, score, dimensions = check_image_quality(image)
    print(f"Result: {quality}, Dimensions: {dimensions[0]}x{dimensions[1]}\n")