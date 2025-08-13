'''
 # @ Create Time: 2025-05-09 10:10:00
 # @ Modified time: 2025-05-09 10:10:06
 # @ Description: convert long link into a short link to disguise the malicious link
 '''

import requests

long_url = "https://gist.githubusercontent.com/Wapiti08/191023b9a2e8dfe47339b8856c18c29e/raw/94555205262ecba7ee90edf9d83356452a0c3a0e/medusa_wins.py"

api_url = "http://tinyurl.com/api-create.php"

response = requests.get(api_url, params={"url": long_url})
if response.status_code == 200:
    short_url = response.text
    print("Shortened URL:", short_url)

else:
    print("Failed to shorten the URL. Status code:", response.status_code)



