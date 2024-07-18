''' 
    according to system type to download compatible tools

'''
import platform
import subprocess
from pathlib import Path
import zipfile
import os

# configure git
def install_git(os_type):
    if os_type.startswith("Windows"):
        git_url = "https://github.com/git-for-windows/git/releases/download/v2.37.1.windows.1/Git-2.37.1-64-bit.exe"
        
        installer_path = Path.joinpath(Path.cwd(), 'Git-2.37.1-64-bit.exe')
        
        # Download the Git installer
        subprocess.run(["curl", "-L", git_url, "-o", installer_path], check=True)
        
        # Run the installer
        subprocess.run([installer_path, '/VERYSILENT'], check=True)
        print("Git installation executed successfully on Windows.")
    elif os_type.startswith("Linux"):
        try:
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "git"], check=True)
            print("Git installation executed successfully on Debian-based Linux.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Git on Debian-based Linux: {e}")
    elif os_type.startswith("mac"):
        try:
            # Ensure Homebrew is up-to-date
            subprocess.run(["brew", "update"], check=True)
            # Install Git
            subprocess.run(["brew", "install", "git"], check=True)
            print("Git installation executed successfully on macOS.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install Git on macOS: {e}")
    else:
        print(f"{os_type} is not supported currently")
        exit
    

if __name__ == "__main__":
    os_type = platform.platform()
    install_git(os_type)

