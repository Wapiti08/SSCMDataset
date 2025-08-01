'''
 # @ Create Time: 2025-05-09 10:10:00
 # @ Modified time: 2025-05-09 10:10:06
 # @ Description: convert long link into a short link to disguise the malicious link
 '''

import requests

long_url = "https://gist.githubusercontent.com/Wapiti08/d2866a3d212e8f3a127ac86e30e87dc7/raw/99f52757f798ba15c70d6651d70d7045e86a6fe8/medusa_linux.py"
api_url = "http://tinyurl.com/api-create.php"

response = requests.get(api_url, params={"url": long_url})
if response.status_code == 200:
    short_url = response.text
    print("Shortened URL:", short_url)

else:
    print("Failed to shorten the URL. Status code:", response.status_code)


