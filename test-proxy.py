import logging
import os
import time

from lib.browser_factory import BrowserFactory


def test():
    browser = BrowserFactory().create(window_size='1200,800')
    try:
        browser.get('https://ifconfig.co')
        time.sleep(120)
    finally:
        browser.quit()


def main():
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(format='[%(levelname)s] %(message)s', level=log_level)
    test()


if __name__ == '__main__':
    main()
