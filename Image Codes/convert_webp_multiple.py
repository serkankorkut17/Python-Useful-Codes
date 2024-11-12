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


def __main__():
    input_image_folder_path = 'products'
    output_image_folder_path = 'webp_products'

    if not os.path.exists(input_image_folder_path):
        print(f"Input folder {input_image_folder_path} does not exist.")
    else:
        if not os.path.exists(output_image_folder_path):
            os.mkdir(output_image_folder_path)
        for file in os.listdir(input_image_folder_path):
            if file.endswith('.jpg'):
                input_image_path = os.path.join(input_image_folder_path, file)
                output_image_path = os.path.join(output_image_folder_path, file.replace('.jpg', '.webp'))
                # convert_to_webp(input_image_path, output_image_path)
                convert_compress_webp(input_image_path, output_image_path, quality=75, lossless=False, effort=4)
                print(f"Conversion complete. Output saved to {output_image_path}") 


if __name__ == '__main__':
    __main__()