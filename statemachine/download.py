'''
 # @ Create Time: 2024-07-05 14:48:08
 # @ Modified time: 2024-07-10 15:36:15
 # @ Description: simulate git download projects in dev environment
 '''
import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import subprocess
from utils import util
from pathlib import Path
from core import config
import random

logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))

def clone_repository(repo):
    try:
        repo_name = Path(repo).stem
        destination = Path.cwd().parent.joinpath("install", repo_name).as_posix()
        print(destination)
        logger.info(f"Cloning {repo}...")
        subprocess.run(["git", "clone", repo, destination], check=True)
        logger.info(f"Successfully cloned {repo}")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to clone {repo}: {e}")


if __name__ == "__main__":
    resp = random.choice(config.git_reps_list)
    clone_repository(resp)