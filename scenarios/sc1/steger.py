
from stegano import lsb
from PIL import Image

# step1: read the python file content
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


# step2: hide content in an image
def hide_data_to_image(payload, input_img_path, output_img_path):
    # lsb technique to encode the content into the image
    sec_image = lsb.hide(input_img_path, payload)
    # save the image with embedded code
    sec_image.save(output_img_path)

if __name__ == "__main__":
    payload_file = 
    input_image_path = 
    output_image_path = 

    payload = read_file()

    hide_data_to_image(payload, input_image_path, output_image_path)


