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
        
    def network_info(self,):
        
    def disk_info(self,):

    def mem_info(self,):

    def env_info(self,):

    def _system_info(self, save_location):
        ''' the module to scan system info and export to somewhere
        
        '''
        system_info = {}



class SenInfoScanner:
    def __init__(self, ):

    def

    def

    def _sen_info(self, save_location):
        ''' the module to collect sensitive info from specific locations/files/extensions
        
        '''

