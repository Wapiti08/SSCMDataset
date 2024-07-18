import schedule
import time
from core import config
from datetime import datetime, timedelta
import random

random.seed(43)

schedule.every().minutes.do()

start_hour = 9
end_hour = 18

def schedule_random_tasks(task_function):
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

def run_scheduler():
    '''
    run scheduled tasks consistently
    '''
    while True:
        # schedule tasks for current day
        schedule_random_tasks()

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

if __name__ == "__main__":
    # define the functions to simulate normal behaviour
    
