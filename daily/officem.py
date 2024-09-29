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


class OfficeVM:
    def __init__(self, login_url):
        self.web_username = os.environ.get("WEB_USERNAME")
        self.web_password = os.environ.get("WEB_PASSWORD")
        self.login_url = login_url

    def _API_CALL(self,):
        api_sev.chat_with_gpt()

    
    def _LOGIN(self,):
        logins.login_simu(
            self.login_url, {
                            "username": self.web_username ,
                            "password": self.web_password
                            }
        )

    
    def _OFFICE(self,):
        
    
    def _WebVisit(self,):
    
    






