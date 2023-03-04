import logging
import os
import time
from random import shuffle

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import ConsoleMessenger, TelegramMessenger
from lib.working_hours_runner import WorkingHours, WorkingHoursRunner


def check():
    browser = BrowserFactory().create(window_size='1300,800')
    if 'TELEGRAM_TOKEN' in os.environ and 'TELEGRAM_CHAT_ID' in os.environ:
        messenger = TelegramMessenger()
    else:
        messenger = ConsoleMessenger()

    try:
        config = CheckerConfig(
            email=os.environ['EMAIL'],
            password=os.environ['PASSWORD'],
            case_id=os.environ['CASE_ID'],
            messenger=messenger,
            browser=browser,
        )

        inpol = Checker(config)

        tries = 0
        while not inpol.login():
            if tries == 4:
                return
            tries += 1
            time.sleep(tries * 2)

        tries = 0
        while not inpol.open_case_page():
            if tries == 4:
                return
            tries += 1
            time.sleep(tries * 2)

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
        months_to_check = int(os.environ.get('MONTHS_TO_CHECK', '5'))
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
            inpol.day_checker_full(location=location, queue=queue, months_to_check=months_to_check)

            # prepare for next loop
            inpol.expand_locations()

        logging.debug('end')

    finally:
        browser.quit()


def main():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)

    WorkingHoursRunner(
        sleep_interval=os.environ.get('SLEEP_INTERVAL', '15m'),
        sleep_interval_jitter=os.environ.get('SLEEP_INTERVAL_JITTER', '3m'),
        working_hours=[
            WorkingHours(begin_displace_from_midnight='7h30m', end_displace_from_midnight='29h59m59s'),
            WorkingHours(begin_displace_from_midnight='0s', end_displace_from_midnight='57m')
        ]
    ).run(check)


if __name__ == '__main__':
    main()
