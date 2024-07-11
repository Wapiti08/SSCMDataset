'''
 # @ Create Time: 2024-07-05 14:48:08
 # @ Modified time: 2024-07-10 15:36:15
 # @ Description: simulate git download projects in dev environment
 '''

import subprocess

def clone_repository(repo):
    try:
        print(f"Cloning {repo}...")
        subprocess.run(["git", "clone", repo], check=True)
        print(f"Successfully cloned {repo}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone {repo}: {e}")


