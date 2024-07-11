'''
 # @ Create Time: 2024-07-09 14:06:43
 # @ Modified time: 2024-07-11 15:03:53
 # @ Description: simulate the behaviour of development
 '''

import os
import subprocess
import shutil

def create_code_files():
    project_name = "example_project"
    os.makedirs(project_name, exist_ok=True)
    with open(os.path.join(project_name, "main.py"), "w") as f:
        f.write("""
            def hello_world():
                print("Hello, World!")

            if __name__ == "__main__":
                hello_world()
            """)
    print(f"Created main.py in {project_name}")

def run_tests():
    try:
        result = subprocess.run(["python", "-m", "unittest", "discover"], check=True)
        print("Tests ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to run tests: {e}")

def deploy_application(source_dir, dest_dir):
    try:
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        print(f"Application deployed to {dest_dir}.")
    except Exception as e:
        print(f"Failed to deploy application: {e}")

if __name__ == "__main__":
    create_code_files()
    project_path = "example_project"
    run_tests()
    deployment_directory = "deployed_example_project"
    deploy_application(project_path, deployment_directory)