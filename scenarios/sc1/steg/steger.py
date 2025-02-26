'''
 # @ Author: Newt Tan
 # @ Create Time: 2024-09-09 17:24:10
 # @ Modified by: Newt Tan
 # @ Modified time: 2024-09-16 10:20:48
 # @ Description:
 '''
from pathlib import Path
from stegano import lsb
from PIL import Image
import gzip
import base64

# step1: read the python file content
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def compress_file(code):
    compressed = gzip.compress(code.encode())
    return base64.b64encode(compressed).decode()


# step2: hide content in an image
def hide_data_to_image(payload, input_img_path, output_img_path):
    # lsb technique to encode the content into the image
    sec_image = lsb.hide(input_img_path, payload)
    # save the image with embedded code
    sec_image.save(output_img_path)

if __name__ == "__main__":
    cur_path = Path.cwd()
    
    payload_file = cur_path.joinpath("medusa_wins.py")
    input_image_path = cur_path.joinpath("largeimage.png")
    output_image_path = cur_path.joinpath("img.png")

    # payload = compress_file(read_file(payload_file))
    payload = read_file(payload_file)

    hide_data_to_image(payload, input_image_path, output_image_path)


