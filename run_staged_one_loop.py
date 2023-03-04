import logging
import os
from random import shuffle

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import TelegramMessenger


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
    check()


if __name__ == '__main__':
    main()
