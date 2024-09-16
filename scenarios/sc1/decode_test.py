'''
 # @ Author: Newt Tan
 # @ Create Time: 2024-09-16 11:40:51
 # @ Modified by: Newt Tan
 # @ Modified time: 2024-09-16 11:42:41
 # @ Description:
 '''
from pathlib import Path
from stegeno import lsb

# load the image with hidden payload
cur_path = Path.cwd()
image_path = cur_path.joinpath("img.jpeg")

# extract hidden message from image
hide_msg= lsb.reveal(image_path)

if hide_msg:
    print("the hidden payload is:", hide_msg)
else:
    print("there is no hidden payload")