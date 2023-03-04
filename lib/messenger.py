import os
from urllib.parse import quote_plus

import requests


class Messenger:
    def send_message(self, body: str):
        raise NotImplementedError


class ConsoleMessenger(Messenger):
    def send_message(self, body: str):
        print(body)


class TelegramMessenger(Messenger):
    def send_message(self, body: str):
        token = os.environ['TELEGRAM_TOKEN']
        chat_id = os.environ['TELEGRAM_CHAT_ID']
        url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (token, chat_id, quote_plus(f'{body}'))
        _ = requests.get(url, timeout=10)


if __name__ == '__main__':
    tm = TelegramMessenger()
    tm.send_message("TEsT bOdY")
