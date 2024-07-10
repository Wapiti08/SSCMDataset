
from platform import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path
import random
from core import config
import time

# define right path for driver
def load_driver():
    return webdriver.Chrome()

def website_access(driver,link):
    try:
        driver.get(link)
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    # print(os_type)
    driver = load_driver()
    url_list = config.web_sites
    url = random.choice(url_list)
    website_access(driver, url)