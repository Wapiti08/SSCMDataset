import schedule
import time
from core import config

schedule.every().minutes.do()


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)