
import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os
from platform import platform
try:
    from selenium import webdriver
except:
    os.system("pip3 install selenium==4.22.0")

import time
from pathlib import Path
import random
from core import config
import time
from utils import util

# define right path for driver
def load_driver():
    return webdriver.Chrome()

def website_access(driver,link, logger):
    try:
        logger.info(f"visiting website {link}")
        driver.get(link)
        time.sleep(3)
    finally:
        driver.quit()

# if __name__ == "__main__":
#     # print(os_type)
#     driver = load_driver()
#     url_list = config.web_sites
#     url = random.choice(url_list)
#     website_access(driver, url)