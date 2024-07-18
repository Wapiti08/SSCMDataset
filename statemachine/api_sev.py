import openai
import json
from faker import Faker
import yaml
from pathlib import Path
from utils import util
import random

random.seed(43)
logger = util.create_logger(Path(__file__).name)

yaml_file = Path.cwd().parent.joinpath("config.yaml")

with yaml_file.open("r") as file:
    config = yaml.safe_load(file)

openai.api_key = config["openai_key"]

fake = Faker()

def chat_with_gpt():
    def gpt_query(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview", 
            messages=[
                {"role": "system", "content": "you are a chatbox, talk to me"},
                {'role': 'user', 'content': prompt}
            ]
            )
        return response.choices[0].message['content']
    
    # define the times of query
    times = random.randint(1,10)
    for _ in range(times):
        logger.info("talking to gpt")
        gpt_query(fake.text())
        

