'''
 # @ Create Time: 2024-09-25 14:09:59
 # @ Modified time: 2024-09-25 16:53:52
 # @ Description: automatic scripts to start normal behaviour for dev machine

simulated behaviours:
    - copy 
    - dev
    - web_visit
    - update_call
    - rdp
    - download

 '''
from statemachine import (copy, dev, web_visit, api_sev, update_call, rdp, download)
import os
from core import config
import random
from pathlib import Path
import platform
from utils import util

logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))


class DevVM:
    def __init__(self, remote_host, local_file, remote_path):
        self.hostname = remote_host
        self.host_username = os.environ.get("HOST_USERNAME")
        self.host_password = os.environ.get("HOST_PASSWORD")
        # set default ssh port as 22
        self.ssh_port = 22

        self.remote_path = remote_path
        self.local_path = local_file


    def _API_CALL(self,):
        api_sev.chat_with_gpt()


    def _COPY(self,):
        ''' simulate scp for copy between two hosts
        
        '''
        copy.scp_copy_file(self.hostname, self.ssh_port, \
                           self.host_username, self.host_password, self.local_path, \
                            self.remote_path)

    # def _RDP(self,):
    #     ''' similar to scp
        
    #     '''
    #     pass


    def _DOWNLOAD(self,):
        
        download.clone_repository(random.choice(config.git_reps_list))

    def _DEV(self,):
        dev.create_code_files()
        project_path = Path.cwd().joinpath("example_project")
        dev.run_tests()
        deployment_directory = Path.cwd().joinpath("deployed_example_project")
        dev.deploy_application(project_path, deployment_directory)

    
    def _UPDATE_CALL(self,):
        os_type = platform.system()
        if os_type.startswith("Windows"):
            update_call.update_windows()
        
        elif os_type.startswith("Linux"):
            update_call.update_linux_debian()
        
        elif os_type.startswith("Darwin"):
            update_call.update_mac_brew()
        else:
            logger.info("The update call is not able on {os_type}")


    def _WebVisit(self,):
        driver = web_visit.load_driver()
        url_list = config.web_sites
        url = random.choice(url_list)
        web_visit.website_access(driver, url)
    






