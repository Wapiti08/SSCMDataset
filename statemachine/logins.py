'''
 # @ Create Time: 2024-07-05 14:47:20
 # @ Modified time: 2024-08-21 10:46:00
 # @ Description: simulate the login on host web service
'''
import sys
from pathlib import Path
sys.path.insert(0, Path(sys.path[0]).parent.as_posix())
import requests
import os
from bs4 import BeautifulSoup
import random
from urllib.parse import urlparse
from utils import util

logger = util.create_logger(Path.cwd().parent.joinpath("logs", Path(__file__).name))

def base_url_loc(page_url, soup):
    ''' locate the base url in order to reconstruct full path url
    
    '''
    base_tag = soup.find("base", href=True)

    if base_tag:
        base_url = base_tag["href"]
    
    else:
        parsed_url = urlparse(page_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}/"

    return base_url


def link_click_simu(page_url, response):
    ''' simulate the click behaviour inside a webpage
    :param page_url: the page url with login form
    :param response: the response page after loginning successful
    '''
    soup = BeautifulSoup(response.content, "html.parser")
    base_url = base_url_loc(page_url, soup)
    # get the links inside a tag
    links = soup.find_all('a', href=True)
    valid_links = [link['href'] for link in links if not link['href'].startswith("mailto:") \
                   and not link["href"].startswith("javascript:") ]

    if not valid_links:
        return

    # create a random number to decide how many times to click
    number = random.randint(1,10)
    # create a new session
    session = requests.Session()
    for _ in range(number):    
        random_link = random.choice(valid_links)

        # if the link is relative, construct the full URL
        if random_link.startswith("/"):
            random_link = base_url + random_link
        
        click_response = session.get(random_link)

        if click_response.status_code == 200:
            logger.info("successfully accessed: {random_link}")
        else:
            logger.info("Failed to access: {random_link}")


def login_simu(login_url, credential):
    '''
    :param login_url: the login webpage
    :param credential: the credential info, including username and password
    ''' 

    # start a session
    session = requests.Session()

    # send a post request to login
    response = session.post(login_url, data=credential)

    # check whether the login was successful
    if response.status_code == 200:
        print("Login successful!")
        # randomly click links
        link_click_simu(login_url, response)
    else:
        print("Login failed")


if __name__ == "__main__":
    login_url = 
    
    credential = {
        "username": os.environ.get("WEB_USERNAME"),
        "password": os.environ.get("WEB_PASSWORD")
    }

    login_simu(login_url, credential)