import subprocess


def update_windows():
    try:
        subprocess.run(["wuauclt", "/updatenow"], check=True)
        print("Windows update command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Windows update: {e}")
        

def update_linux_debian():
    try:
        # Update package list and upgrade all packages
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)
        print("Linux (Debian-based) update executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Debian-based Linux update: {e}")


def update_mac_brew():
    try:
        # Update Homebrew and all installed packages
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "upgrade"], check=True)
        print("Homebrew update executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute Homebrew update: {e}")

if __name__ == "__main__":
    update_windows()