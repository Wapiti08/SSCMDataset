'''
 # @ Create Time: 2025-02-24 12:38:02
 # @ Modified time: 2025-02-24 12:38:12
 # @ Description: entrypoint to simulate:
    web visit, remote ssh, scp manipulation, open software,
    downlaod resp, automatic development

 '''

import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.parent.as_posix())
import random
import time
import schedule
from datetime import datetime, timedelta
from statemachine import web_visit, sssh, copy, update_call, download, dev
from core import config
import platform

# list of available operations:
operations = ['web', 'ssh', 'copy', 'update_call', 'download', 'dev']

# define the operational time range (9 a.m to 7 p.m.)
START_HOUR = 9
END_HOUR = 19


def sche_random_operations():
    ''' schedule a random operation at a random time within the day range
    
    '''
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        operation = random.choice(operations)
        if operation == 'web':
            driver = web_visit.load_driver()
            url_list = config.web_sites
            url = random.choice(url_list)
            web_visit.website_access(driver, url)

        elif operation == 'ssh':
            try:
                ssh_client = sssh.create_ssh_client(config.ssh_hostname, config.ssh_port, \
                                       config.ssh_username, config.ssh_password)
                sssh.random_operations(ssh_client)
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                ssh_client.close()

        elif operation == 'copy':
            local_file = random.choice(config.local_file_list)
            remote_path = random.choice(config.remote_path_list)
            copy.scp_copy_file(config.scp_hostname, config.scp_port, config.scp_username, \
                  config.scp_password, local_file, remote_path)

        elif operation == 'update_call':
            os_name = platform.system()
            if os_name == "Darwin":
                update_call.update_mac_brew()

            elif os_name == "Linux":
                update_call.update_linux_debian()

            elif os_name == "Windows":
                update_call.update_windows()

        elif operation == 'download':
            resp = random.choice(config.git_reps_list)
            download.clone_repository(resp)

        elif operation == 'dev':
            dev.create_code_files()
            project_path = Path.cwd().joinpath("example_project")
            dev.run_tests()
            deployment_directory = Path.cwd().joinpath("deployed_example_project")
            dev.deploy_application(project_path, deployment_directory)


def simu_norm():
    ''' schedule operations at random intervals during daytime
    
    '''
    for _ in range(15):
        delay = random.randint(300, 3600)
        schedule.every(delay).seconds.do(sche_random_operations)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == "__main__":
    simu_norm()