'''
 # @ Create Time: 2025-02-24 12:38:02
 # @ Modified time: 2025-02-24 12:38:12
 # @ Description: entrypoint to simulate:
    web visit, remote ssh, scp manipulation, open software,
    downlaod resp, automatic development

 '''

import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os
import random
import time
from datetime import datetime, timedelta
import multiprocessing
from nora import scopy, web_visit, sssh, update_call, download, dev, logins, api_sev
from core import config
import platform
from utils import util

try:
    import schedule

except:
    os.system("pip3 install schedule==1.2.2")

# list of available operations:
operations = ['web', 'ssh', 'copy', 'update_call', 'download', 'dev', 'gpt', 'login']

# define the operational time range (9 a.m to 7 p.m.)
START_HOUR = 9
END_HOUR = 19


def sche_random_operations(operation):
    ''' schedule a random operation at a random time within the day range
    
    '''
    try:
        logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))

        if operation == 'web':
            driver = web_visit.load_driver()
            url_list = config.web_sites
            url = random.choice(url_list)
            web_visit.website_access(driver, url, logger)
            logger.info(f"Visited {url}")

        elif operation == 'ssh':
            try:
                ssh_client = sssh.create_ssh_client(config.ssh_hostname, config.ssh_port, \
                                    config.ssh_username, config.ssh_password)
                sssh.random_operations(ssh_client, logger)
            except Exception as e:
                logger.info(f"An error occurred when processing ssh: {e}")
            finally:
                ssh_client.close()

        elif operation == 'copy':
            # Select a random index
            index = random.randint(0, len(config.local_file_list) - 1)

            # Use the same index for both lists
            local_file = config.local_file_list[index]
            remote_path = config.remote_path_list[index]
            scopy.scp_copy_file(config.scp_hostname, config.scp_port, config.scp_username, \
                config.scp_password, local_file, remote_path, logger)
            logger.info(f"Copied {local_file} to {remote_path}")

        elif operation == 'update_call':
            os_name = platform.system()
            if os_name == "Darwin":
                update_call.update_mac_brew(logger)

            elif os_name == "Linux":
                update_call.update_linux_debian(logger)

            elif os_name == "Windows":
                update_call.update_windows(logger)
            
            logger.info(f"Updated system on {os_name}")

        elif operation == 'download':
            resp = random.choice(config.git_reps_list)
            download.clone_repository(resp,logger)
            logger.info(f"Cloned repository {resp}")

        elif operation == 'dev':
            dev.create_code_files(logger)
            project_path = Path.cwd().joinpath("example_project")
            dev.run_tests(logger)
            deployment_directory = Path.cwd().joinpath("deployed_example_project")
            dev.deploy_application(project_path, deployment_directory,logger)
            logger.info("Development operation completed")

        elif operation == 'gpt':
            api_sev.chat_with_gpt(logger)
            logger.info("Completed GPT chat operation.")
        
        elif operation == "login":
            logins.login_playwright("admin", "password")
            logger.info("Login operation completed.")

    except Exception as e:
        print(f"[Error] Operation {operation} failed: {e}")

def execute_operation(operation, logger):
    logger.info(f"Executing: {operation}")
    time.sleep(random.randint(1,3))

def sche_random_operation():
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        operation = random.choice(operations)
        logger = util.create_logger(operation)
        # Start process
        process = multiprocessing.Process(target=execute_operation, args=(operation, logger))
        process.start()
        process.join()  # Ensure only one process runs at a time

            
def simu_norm():
    ''' schedule operations at random intervals during daytime
    
    '''
    for _ in range(15):
        # delay = random.randint(300, 3600)
        # for quick test
        delay = random.randint(30, 360)
        schedule.every(delay).seconds.do(sche_random_operation)  # FIXED: Removed parentheses
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == "__main__":
    simu_norm()