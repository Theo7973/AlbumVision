from app.utils.image_quality import check_image_quality

# Test with sample images (update paths to our actual images)
clear_image = "data/test_images/clear.jpg"
blurry_image = "data/test_images/blurry.jpg"

print("Testing clear image:")
quality, score = check_image_quality(clear_image)

print("\nTesting blurry image:")
quality, score = check_image_quality(blurry_image)