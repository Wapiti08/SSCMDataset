'''
 # @ Create Time: 2025-02-24 10:38:23
 # @ Modified time: 2025-02-24 10:44:39
 # @ Description: simulate ssh service and basic operations
 '''
import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import paramiko
from core import config
from scp import SCPClient
import random
from utils import util
logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))


def create_ssh_client(hostname, port, username, password):
    ''' create and return a SSH client connected to the specified server
    
    '''
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port=port, username=username, password=password)
    return client


def random_operations(ssh_client):
    ''' simulate operations after successfully ssh
    
    '''
    commands = [
        "ls -l",
        "whoami",
        "uname -a",
        "df -h"
    ]

    command = random.choice(commands)
    logger.info(f"normal cmd executing: {command}")
    stdin, stdout, stderr = ssh_client.exec_command(command)
    logger.info('command output', stdout.read().decode())
    logger.info('command error', stderr.read().decode())
    

if __name__ == "__main__":

    try:
        ssh_client = create_ssh_client(config.ssh_hostname, config.ssh_port, config.ssh_username, config.ssh_password)
        random_operations(ssh_client)
    except Exception as e:
        logger.info(f"An error occurred: {e}")
    finally:
        ssh_client.close()