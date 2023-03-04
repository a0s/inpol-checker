from dataclasses import dataclass

from selenium import webdriver

from lib.messenger import Messenger


@dataclass
class CheckerConfig:
    messenger: Messenger
    browser: webdriver.Chrome
    email: str
    password: str
    case_id: str
    page_load_timeout: int = 90
    count_of_locations: int = 3
