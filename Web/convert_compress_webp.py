from PIL import Image
import os

def convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4):
    with Image.open(input_image_path) as img:
        img.save(output_image_path, 'webp', quality=quality, lossless=lossless, method=effort)
    print(f"Successfully converted {input_image_path} to {output_image_path} with quality={quality}, lossless={lossless}, effort={effort}")
    
def convert_to_webp(input_path, output_path):
    # Open an image file
    with Image.open(input_path) as img:
        # Convert to WebP format
        img.save(output_path, 'webp')
    
if __name__ == '__main__':
    input_image_path = 'wall.jpg'
    output_image_path = 'wall-test.webp' 

    if not os.path.exists(input_image_path):
        print(f"Input file {input_image_path} does not exist.")
    else:
        convert_to_webp(input_image_path, output_image_path)
        convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4)
        print(f"Conversion complete. Output saved to {output_image_path}")
