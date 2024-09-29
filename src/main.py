'''
 # @ Create Time: 2024-07-11 14:38:47
 # @ Modified time: 2024-09-29 10:46:07
 # @ Description: decide scheduled tasks based on device function/type
 '''

import schedule
import time
from core import config
from datetime import datetime, timedelta
import random

random.seed(43)

schedule.every().minutes.do()

start_hour = 9
end_hour = 18


if __name__ == "__main__":
    # define the functions to simulate normal behaviour
    pass
