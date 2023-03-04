import logging
import os
import time
from datetime import datetime, timedelta
from random import random
from random import shuffle

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import TelegramMessenger

SLEEP_INTERVAL_MIN = 14 * 60  # 14min
SLEEP_INTERVAL_MAX = 16 * 60  # 16min


def check():
    browser = BrowserFactory().create(window_size='1200,800')
    messenger = TelegramMessenger()

    locations = list(range(CheckerConfig.count_of_locations))
    shuffle(locations)
    try:
        for location_number in locations:
            config = CheckerConfig(
                email=os.environ['EMAIL'],
                password=os.environ['PASSWORD'],
                case_id=os.environ['CASE_ID'],
                messenger=messenger,
                browser=browser
            )

            inpol = Checker(config)
            inpol.login()
            inpol.check_one_location(location_number=location_number)
    finally:
        browser.quit()


def main():
    while True:
        logging.info("Run new checking loop at %s" % (datetime.now().strftime("%c"),))
        loop_started_at = datetime.now()
        check()
        logging.info("Checking loop finished in %fs", (datetime.now() - loop_started_at).total_seconds())

        sleep_seconds = random() * (SLEEP_INTERVAL_MAX - SLEEP_INTERVAL_MIN) + SLEEP_INTERVAL_MIN
        logging.info("Next run at %s", (datetime.now() + timedelta(seconds=sleep_seconds)).strftime("%c"))
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)
    main()
