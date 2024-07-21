import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
from openai import OpenAI
import json
from faker import Faker
from pathlib import Path
from utils import util
import random
import os
from dotenv import load_dotenv

random.seed(43)
logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))

dotenv_path = Path.cwd().parent.joinpath('.env').as_posix()
load_dotenv(dotenv_path)

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

fake = Faker()
def chat_with_gpt():
    def gpt_query(prompt):
        response = client.chat.completions.create(
            model="gpt-4-1106-preview", 
            messages=[
                {"role": "system", "content": "you are a chatbox, talk to me"},
                {'role': 'user', 'content': prompt}
            ]
            )
        return response.choices[0].message.content
    
    # define the times of query
    times = random.randint(1,10)
    for _ in range(times):
        logger.info("talking to gpt")
        gpt_query(fake.text())

if __name__ == "__main__":
    chat_with_gpt()

