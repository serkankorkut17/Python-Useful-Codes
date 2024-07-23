from PIL import Image
import os

def convert_to_webp(input_path, output_path):
    # Open an image file
    with Image.open(input_path) as img:
        # Convert to WebP format
        img.save(output_path, 'webp')

if __name__ == '__main__':
    input_file = 'car.jpg'
    output_file = 'car.webp' 

    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist.")
    else:
        convert_to_webp(input_file, output_file)
        print(f"Conversion complete. Output saved to {output_file}")
