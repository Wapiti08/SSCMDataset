import openai
import json
import time
from faker import Faker

openai.api_key = "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"


content = """
            
                """

completion = openai.ChatCompletion.create(model="gpt-4-1106-preview", messages=[
    {"role": "system", "content": "you are a chatbox, talk to me"},
    {'role': 'user', 'content': content}])

print(json.dumps(completion, ensure_ascii=False, indent=4))