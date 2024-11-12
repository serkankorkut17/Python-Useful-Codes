from rembg import remove
from PIL import Image

input_path = 'examples/car.jpg'
output_path = 'examples/car_no_bg.png'

input = Image.open(input_path)
output = remove(input)
output.save(output_path)