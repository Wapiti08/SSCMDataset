'''
 # @ Create Time: 2024-09-25 14:09:59
 # @ Modified time: 2024-09-25 16:53:52
 # @ Description: automatic scripts to start normal behaviour for office based device

simulated behaviours:
    - gpt usage (api service)
    - login
    - office
    - web_visit
    - download tools

 '''

from statemachine import api_sev, logins, office, web_visit
from utils import sche
import os
from core import config
import random

class OfficeVM:
    def __init__(self, login_url):
        self.web_username = os.environ.get("WEB_USERNAME")
        self.web_password = os.environ.get("WEB_PASSWORD")
        self.login_url = login_url

    def _API_CALL(self,):
        ''' simulate chatgpt call
        
        '''
        api_sev.chat_with_gpt()

    
    def _LOGIN(self,):
        ''' simulate website login behaviour
        
        '''
        logins.login_simu(
            self.login_url, 
            {
            "username": self.web_username ,
            "password": self.web_password
                }
        )

    
    def _OFFICE(self,):
        ''' simulate office work
        
        '''
        # document manipulations
        office.create_doc()
        office.modify_doc()
        office.delete_doc()

        # powerpoint manipulation
        office.create_ppt()
        office.modify_ppt()
        office.delete_ppt()

        # excel manipulation
        office.create_xls()
        office.modify_xls()
        office.delete_xls()

        # click event
        office.automate_gui()
    
    def _WebVisit(self,):
        ''' simulate web visit
        
        '''
        driver = web_visit.load_driver()
        url_list = config.web_sites
        url = random.choice(url_list)
        web_visit.website_access(driver, url)
    






