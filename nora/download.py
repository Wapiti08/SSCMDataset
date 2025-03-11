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


def clone_repository(repo, logger):
    
    try:
        repo_name = Path(repo).stem
        destination = Path.cwd().parent.joinpath("install", repo_name).as_posix()
        if Path(destination).exists():
            logger.info(f"Repository already exists at {destination}")
            return
        
        logger.info(f"Cloning {repo} to {destination}...")

        result = subprocess.run(["git", "clone", repo, destination], 
                                capture_output=True, text=True, check=True)
        
        logger.info(f"Clone output: {result.stdout}")
        
        logger.info(f"Successfully cloned {repo}")
        logger.handlers[0].flush()

    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to clone {repo}: {e}")


# if __name__ == "__main__":
#     resp = random.choice(config.git_reps_list)
#     clone_repository(resp)