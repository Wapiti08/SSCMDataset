'''
 # @ Author: Taylor Brierley
 # @ Create Time: 2024-09-16 09:48:58
 # @ Modified by: Taylor Brierley
 # @ Modified time: 2024-09-16 09:49:52
 # @ Description:
 '''


import os
import subprocess

def check_and_create_directory():
    start_menu_path = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
    system64_path = os.path.join(start_menu_path, 'System64')

    script_dir = os.path.dirname(os.path.abspath(__file__))


    if not os.path.exists(system64_path):
        try:
            os.makedirs(system64_path)
            print(f'Directory "System64" created at: {system64_path}')

            run_file(os.path.join(script_dir, 'batch.bat'))
 
        except Exception as e:
            print(f'An error occurred while creating the directory: {e}')
    else:
        print(f'Directory "System64" already exists at: {system64_path}')


        run_file(os.path.join(script_dir, 'batch.bat'))


def run_file(filepath):

    if  os.path.exists(filepath):
        print(f'Batch file correctly located')

        print(f'Running batch file')
        subprocess.run([filepath], check=True)

    else:
        print(f'Batch file not located')
        


if __name__ == "__main__":
    check_and_create_directory()