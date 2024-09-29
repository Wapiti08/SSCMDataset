'''
 # @ Create Time: 2024-09-29 10:43:12
 # @ Modified time: 2024-09-29 10:43:45
 # @ Description: functions to schedule tasks
 '''


import schedule
import time
from core import config
from datetime import datetime, timedelta
import random

def schedule_random_task(start_hour, end_hour, task_function):
    '''
    schedule random tasks within the working hours
    '''
    now = datetime.now()
    current_time = now.hour

    # ensure the scheduled tasks are within in working hours
    if start_hour <= current_time <= end_hour:
        # get the left time before end of working hours
        minutes_left = (end_hour - current_time) * 60 - now.minute

        # schedule the next task at a random time
        random_minute = random.randint(0, minutes_left)
        schedule_time = now + timedelta(minutes=random_minute)

        # schedule the task
        schedule.every().day.at(schedule_time.strftime("%H:%M")).do(task_function)

def run_scheduler(start_hour, end_hour, task_function_list):
    '''
    run scheduled tasks consistently
    '''
    while True:
        for task_function in task_function_list:
            # schedule tasks for current day
            schedule_random_task(start_hour, end_hour,task_function)

            # run pending tasks
            while True:
                now = datetime.now()
                if now.hour >= end_hour:
                    break
                schedule.run_pending()
                time.sleep(1)

            now = datetime.now()
            if now.hour >= end_hour:
                next_start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
                sleep_time = (next_start_time - now).total_seconds()
                time.sleep(sleep_time)
