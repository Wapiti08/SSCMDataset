import openai
import json
import time
from faker import Faker
import yaml
from pathlib import Path

yaml_file = Path.cwd().parent.joinpath("config.yaml")

with yaml_file.open("r") as file:
    config = yaml.safe_load(file)

openai.key = config["openai_key"]

content = """
            
                """

completion = openai.ChatCompletion.create(model="gpt-4-1106-preview", messages=[
    {"role": "system", "content": "you are a chatbox, talk to me"},
    {'role': 'user', 'content': content}])

print(json.dumps(completion, ensure_ascii=False, indent=4))