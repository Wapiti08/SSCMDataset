'''
 # @ Create Time: 2024-08-21 10:11:33
 # @ Modified time: 2025-02-24 11:24:56
 # @ Description: simulate scp copy behavior
 '''


import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os

try:
    import paramiko
    from scp import SCPClient
except:
    os.system("pip3 install paramiko==3.4.1")
    os.system("pip3 install scp==0.15.0")

from utils import util
from core import config

def create_ssh_client(hostname, port, username, password):
    ''' create and return a SSH client connected to the specified server
    
    '''
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    return client


def scp_copy_file(hostname, port, username, password, local_file, remote_path):
    ''' simulate the scp action to copy data between hosts with python script
    
    '''
    try:
        # Create the SSH client
        ssh_client = create_ssh_client(hostname, port, username, password)
        
        # Create an SCP client from the SSH connection
        with SCPClient(ssh_client.get_transport()) as scp:
            # Copy the file
            scp.put(local_file, remote_path)
            print(f"File '{local_file}' successfully copied to '{remote_path}' on '{hostname}'")
        
    except Exception as e:
        print(f"An error occurred while copying the file: {e}")
    
    finally:
        # Close the SSH connection
        ssh_client.close()

if __name__ == "__main__":

    local_file = '/path/to/local/file.txt'
    remote_path = '/path/to/remote/destination/'

    scp_copy_file(config.scp_hostname, config.scp_port, config.scp_username, \
                  config.scp_password, local_file, remote_path)