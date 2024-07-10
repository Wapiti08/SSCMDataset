'''
 # @ Create Time: 2024-07-09 14:12:01
 # @ Modified time: 2024-07-10 10:44:02
 # @ Description: 
 '''


from platform import platform
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
import time
from pathlib import Path

# define right path for driver
def load_driver():
    # driver_name = "chromedriver"
    # if os_type.startswith("mac"):
    #     driver_path = Path.cwd().joinpath("chromedriver-mac-arm64",driver_name)  
    # elif os_type.startswith("Linux"):
    #     driver_path = Path.cwd().joinpath("chromedriver-linux64",driver_name)  
    # elif os_type.startswith("Windows"):
    #     driver_path = Path.cwd().joinpath("chromedriver-win64",driver_name)
    # else:
    #     print(f"currently, we do not support {os_type}")
    #     exit

    # service = Service(executable_path = driver_path)
    # options = webdriver.ChromeOptions()
    # return webdriver.Chrome(service = service, options = driver_path)
    return webdriver.Chrome()


def enable_download_headless(driver, download_dir):

    pass

def website_access(driver,link):
    try:
        driver.get(link)
        time.sleep(3)
    finally:
        driver.quit()

if __name__ == "__main__":
    # print(os_type)
    driver = load_driver()
    website_access(driver, "https://www.google.com/")

