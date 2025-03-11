'''
 # @ Create Time: 2025-02-24 12:38:02
 # @ Modified time: 2025-02-24 12:38:12
 # @ Description: the full normal behaviour simulation

 '''

import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os
import random
import time
from datetime import datetime, timedelta
import multiprocessing
from nora import office, scopy, web_visit, sssh, update_call, download, dev, logins, api_sev
from core import config
import platform
from utils import util

try:
    import schedule

except:
    os.system("pip3 install schedule==1.2.2")

# list of available operations:
operations = ['web', 'ssh', 'copy', 'update_call', 'download', 'dev', 'gpt', 'login', 'office']

# define the operational time range (9 a.m to 7 p.m.)
START_HOUR = 9
END_HOUR = 19


def sche_random_operations(operation):
    ''' schedule a random operation at a random time within the day range
    
    '''
    try:
        log_path = Path.cwd().parent.joinpath("logs", f"{operation}")
        logger = util.create_logger(log_path)  # Initialize logger inside
        
        if operation == 'web':
            logger.info(f"Simulating website access or online search")
            # randomly decide action
            action = random.choice(["website", "search"])

            if action == "website":
                driver = web_visit.load_driver()
                url_list = config.web_sites
                url = random.choice(url_list)
                web_visit.website_access(driver, url, logger)

            elif action == "search":
                web_visit.search_simu(logger)
        
        elif operation == "office":
            logger.info(f"Simulating office related manipulations")
            action = random.choice(["doc", "ppt", "excel"])

            if action == "doc":
                # create file
                office.create_doc(logger)
                # wait for next action
                time.sleep(random.randint(10,100))
                # randomly choose action
                doc_act = random.choice(["del", "mod"])
                if doc_act == "del":
                    office.delete_doc(logger)
                else:
                    office.modify_doc(logger)

            elif action == "ppt":
                # create file
                office.create_ppt(logger)
                # wait for next action
                time.sleep(random.randint(10,100))
                # randomly choose action
                ppt_act = random.choice(["del", "mod"])
                if ppt_act == "del":
                    office.delete_ppt(logger)
                else:
                    office.modify_ppt(logger)

            elif action == "excel":
                # create file
                office.create_xls(logger)
                # wait for next action
                time.sleep(random.randint(10,100))
                # randomly choose action
                xls_act = random.choice(["del", "mod"])
                if xls_act == "del":
                    office.delete_xls(logger)
                else:
                    office.modify_xls(logger)


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
            logins.login_playwright("admin", "password", logger=logger)
            logger.info("Login operation completed.")

    except Exception as e:
        print(f"[Error] Operation {operation} failed: {e}")


def execute_operation(operation):
    logger = util.create_logger(Path.cwd().parent.joinpath("logs", "state"))  # Recreate logger
    logger.info(f"Executing: {operation}")

    # execute specific operation
    try:
        sche_random_operations(operation)
    except Exception as e:
        logger.error(f"Error executing operation {operation}: {e}")

    time.sleep(random.randint(1,3))


def sche_random_operation():
    now = datetime.now()
    if START_HOUR <= now.hour < END_HOUR:
        operation = random.choice(operations)
        # Start process
        process = multiprocessing.Process(target=execute_operation, args=(operation,))
        process.start()
        process.join()  # Ensure only one process runs at a time

            
def simu_norm():
    ''' schedule operations at random intervals during daytime
    
    '''
    for _ in range(15):
        # delay = random.randint(300, 3600)
        # for quick test
        delay = random.randint(30, 360)
        schedule.every(delay).seconds.do(sche_random_operation)  
    
    while True:
        schedule.run_pending()
        time.sleep(1)
    
if __name__ == "__main__":
    simu_norm()