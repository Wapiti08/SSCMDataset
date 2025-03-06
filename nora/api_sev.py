import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os
import time

try:
    from openai import OpenAI
    from faker import Faker
    from dotenv import load_dotenv
except:
    os.system("pip3 install openai==1.65.4")
    os.system("pip3 install faker==26.0.0")
    os.system("pip3 install python-dotenv==1.0.1")

import json

from pathlib import Path
from utils import util
import random


random.seed(43)

dotenv_path = Path.cwd().parent.joinpath('.env').as_posix()
load_dotenv(dotenv_path)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"),)

fake = Faker("en_US")

def gpt_query(prompt, logger, max_retries=5):

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview", 
                messages=[
                    {"role": "system", "content": "you are a chatbox, talk to me"},
                    {'role': 'user', 'content': prompt}
                ]
                )
            logger.info(f"New prompt is {prompt}")
            logger.info(f"Response is {response.choices[0].message.content}")
            return response.choices[0].message.content
        except Exception as e:
            if "too many requests" in str(e).lower():
                wait_time = 2 ** attempt + random.uniform(0,1)
                logger.info(f"Rate limit hit. Retrying in {wait_time:.2f} seconds ...")
                time.sleep(wait_time)
            else:
                raise


def chat_with_gpt(logger):
    # define the times of query
    times = random.randint(1,10)
    for _ in range(times):
        logger.info("talking to gpt")
        gpt_query(fake.text(max_nb_chars=50), logger)
        time.sleep(10)
        

# if __name__ == "__main__":
#     chat_with_gpt()

