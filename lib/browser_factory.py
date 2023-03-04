import logging
import os

from selenium.webdriver.remote.remote_connection import LOGGER as webdriver_logger
from seleniumwire import webdriver
from seleniumwire.backend import log as seleniumwire_backend_logger
from seleniumwire.handler import log as seleniumwire_handler_logger
from seleniumwire.server import logger as seleniumwire_server_logger
from seleniumwire.storage import log as seleniumwire_storage_logger
from seleniumwire.utils import log as seleniumwire_utils_logger
from urllib3.connectionpool import log as urllib_logger


class BrowserFactory:
    def __init__(self, log_level=logging.WARNING):
        webdriver_logger.setLevel(log_level)
        urllib_logger.setLevel(log_level)
        seleniumwire_server_logger.setLevel(log_level)
        seleniumwire_storage_logger.setLevel(log_level)
        seleniumwire_backend_logger.setLevel(log_level)
        seleniumwire_handler_logger.setLevel(log_level)
        seleniumwire_utils_logger.setLevel(log_level)

    def create(self,
               maximized=False,
               window_size='1920,1080',
               service_log_path=None,
               proxy_server=None):

        options = webdriver.ChromeOptions()

        options.add_argument('--no-sandbox')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={window_size}')
        options.add_argument("--start-maximized") if maximized else None
        options.add_argument('--user-data-dir=' + os.environ.get('PROFILE_PATH', './.browser-profile'))
        options.add_experimental_option("excludeSwitches", ['enable-automation'])

        proxy_server = proxy_server or os.environ.get("PROXY_SERVER")
        seleniumwire_options = {'proxy': {}}
        if proxy_server:
            seleniumwire_options['proxy']['http'] = proxy_server
            seleniumwire_options['proxy']['https'] = proxy_server
            seleniumwire_options['proxy']['no_proxy'] = 'localhost,127.0.0.1'

        params = {
            'options': options,
            'seleniumwire_options': seleniumwire_options
        }
        if service_log_path is not None:
            params['service_log_path'] = service_log_path

        return webdriver.Chrome(**params)
