import logging
import os

from lib.browser_factory import BrowserFactory
from lib.checker import Checker
from lib.checker_config import CheckerConfig
from lib.messenger import ConsoleMessenger

if __name__ == '__main__':
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)

    browser = BrowserFactory().create(window_size='1200,800')
    messenger = ConsoleMessenger()

    config = CheckerConfig(
        email=os.environ['EMAIL'],
        password=os.environ['PASSWORD'],
        case_id=os.environ['CASE_ID'],
        messenger=messenger,
        browser=browser,
    )
    try:
        inpol = Checker(config)
        inpol.login()
        inpol.check_one_location(location_number=0)
    finally:
        config.browser.quit()
