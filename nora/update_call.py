import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import subprocess
from utils import util
from pathlib import Path


def update_windows(logger):
    try:
        subprocess.run(["wuauclt", "/updatenow"], check=True)
        logger.info("Windows update command executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to execute Windows update: {e}")
        

def update_linux_debian(logger):
    try:
        # Update package list and upgrade all packages
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)
        logger.info("Linux (Debian-based) update executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to execute Debian-based Linux update: {e}")


def update_mac_brew(logger):
    try:
        # Update Homebrew and all installed packages
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "upgrade"], check=True)
        logger.info("Homebrew update executed successfully.")
    except subprocess.CalledProcessError as e:
        logger.info(f"Failed to execute Homebrew update: {e}")

# if __name__ == "__main__":
#     update_windows()