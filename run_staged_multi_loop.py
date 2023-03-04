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

    try:
        config = CheckerConfig(
            email=os.environ['EMAIL'],
            password=os.environ['PASSWORD'],
            case_id=os.environ['CASE_ID'],
            messenger=messenger,
            browser=browser,
        )

        inpol = Checker(config)
        inpol.login()
        inpol.open_case_page()
        inpol.expand_appointment_panel()
        inpol.expand_locations()
        locations = inpol.get_locations()

        if len(locations) != CheckerConfig.count_of_locations:
            msg = f'wrong list of locations {locations}'
            logging.warning(msg)
            messenger.send_message(msg)
            if len(locations) == 0:
                return

        shuffle(locations)
        for location in locations:
            inpol.select_location(location)
            inpol.expand_queues()
            queues = inpol.get_queues()

            if len(queues) != 1:
                msg = f'wrong list of queues {queues} for location "{location}"'
                logging.warning(msg)
                messenger.send_message(msg)
                if len(queues) == 0:
                    inpol.expand_locations()
                    continue
            queue = queues[0]

            inpol.select_queue(queue)
            inpol.day_checker_full(location=location, queue=queue)

            # prepare for next loop
            inpol.expand_locations()

        logging.debug('end')

    finally:
        browser.quit()


def main():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)

    while True:
        logging.info("Run new checking loop at %s" % (datetime.now().strftime("%c"),))
        loop_started_at = datetime.now()
        check()
        logging.info("Checking loop finished in %fs", (datetime.now() - loop_started_at).total_seconds())

        sleep_seconds = random() * (SLEEP_INTERVAL_MAX - SLEEP_INTERVAL_MIN) + SLEEP_INTERVAL_MIN
        logging.info("Next run at %s", (datetime.now() + timedelta(seconds=sleep_seconds)).strftime("%c"))
        time.sleep(sleep_seconds)


if __name__ == '__main__':
    main()
