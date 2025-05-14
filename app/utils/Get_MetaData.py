from PIL import Image
from PIL.ExifTags import TAGS

def get_image_metadata(image_path):
    metadata = {}

    try:
        with Image.open(image_path) as img:
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["size"] = img.size  #(width, height)

            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ["Make", "Model", "DateTime"]:
                        metadata[tag] = value

            #defaults if not found
            for tag in ["Make", "Model", "DateTime"]:
                if tag not in metadata:
                    metadata[tag] = "Not Available"

    except Exception as e:
        metadata["error"] = str(e)

    return metadata

if __name__ == "__main__":
    test_image = r"C:\Users\austi\Downloads\sample_image.jpg"
    
    from pprint import pprint
    metadata = get_image_metadata(test_image)
    pprint(metadata)