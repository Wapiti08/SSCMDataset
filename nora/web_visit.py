
import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import os
from platform import platform
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys

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

def search_simu(logger):
    ''' function to simulate searching and clicking results
    
    '''
    keywords = ["cybersecurity", "machine learning", "open-source projects", "data science", 
                "quantum computing", "AI advancements", "software vulnerabilities", 
                "supply chain security", "latest tech trends", "deep learning"]
    
    driver = load_driver()

    try:
        driver.get("https://www.google.com")
        time.sleep(2)

        search_box = driver.find_element(By.NAME, "q")
        keyword = random.choice(keywords)

        logger.info(f"Searching for: {keyword}")
        search_box.send_keys(keyword)
        # press enter
        search_box.send_keys(Keys.RETURN)

        # find search results -- lines shown on page
        results = driver.find_elements(By.XPATH, "//h3")

        if results:
            selected_result = random.choice(results)
            logger.info(f"Clicking on: {selected_result.text}")
            selected_result.click()

            time.sleep(random.randint(5,10))
    
    except Exception as e:
        logger.error(f"Search simulation failed: {e}")
    
    finally:
        driver.quit()


# if __name__ == "__main__":
#     # print(os_type)
#     driver = load_driver()
#     url_list = config.web_sites
#     url = random.choice(url_list)
#     website_access(driver, url)