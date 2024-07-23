from PIL import Image

def convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4):
    with Image.open(input_image_path) as img:
        img.save(output_image_path, 'webp', quality=quality, lossless=lossless, method=effort)
    print(f"Successfully converted {input_image_path} to {output_image_path} with quality={quality}, lossless={lossless}, effort={effort}")
    
# Example usage
input_image_path = 'wall.jpg'
output_image_path = 'wall-test.webp'
convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4)
