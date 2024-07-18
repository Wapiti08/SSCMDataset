'''
 # @ Create Time: 2024-07-05 14:48:08
 # @ Modified time: 2024-07-10 15:36:15
 # @ Description: simulate git download projects in dev environment
 '''

import subprocess
from utils import util
from pathlib import Path

logger = util.create_logger(Path(__file__).name)

def clone_repository(repo):
    try:
        logger.info(f"Cloning {repo}...")
        subprocess.run(["git", "clone", repo], check=True)
        logger.info(f"Successfully cloned {repo}")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to clone {repo}: {e}")


