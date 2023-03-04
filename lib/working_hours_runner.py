import datetime
import logging
import time
from dataclasses import dataclass
from random import random
from typing import Callable

import pytz
from pytimeparse.timeparse import timeparse

TIMEZONE = 'Europe/Warsaw'


@dataclass
class WorkingHours:
    begin_displace_from_midnight: str
    end_displace_from_midnight: str


@dataclass
class WorkingHoursRunner:
    sleep_interval: str
    sleep_interval_jitter: str
    working_hours: list[WorkingHours]

    def dt_now(self):
        return datetime.datetime.now(pytz.timezone(TIMEZONE))

    def random_sleep(self):
        return timeparse(self.sleep_interval) + (random() - 0.5) * timeparse(self.sleep_interval_jitter)

    def midnight_of_datetime(self, dt: datetime.datetime) -> datetime.datetime:
        return datetime.datetime.combine(dt, datetime.time.min)

    def in_working_hours(self, dt: datetime.datetime) -> bool:
        midnight = self.midnight_of_datetime(dt)
        for wh in self.working_hours:
            begin_dt = midnight + datetime.timedelta(seconds=timeparse(wh.begin_displace_from_midnight))
            end_dt = midnight + datetime.timedelta(seconds=timeparse(wh.end_displace_from_midnight))
            if begin_dt <= dt <= end_dt:
                return True
        return False

    def sleep_until(self, dt):
        seconds = (dt - datetime.datetime.now()).total_seconds()
        time.sleep(seconds)

    def run(self, func: Callable):
        while True:
            dt = datetime.datetime.now()
            logging.info(f'Start loop at {dt.strftime("%c")}')
            if self.in_working_hours(dt):
                func()
            dt2 = datetime.datetime.now()
            logging.info(f'End loop ({(dt2 - dt).total_seconds()}s) at {dt2.strftime("%c")}')
            next_run_at = dt2 + datetime.timedelta(seconds=self.random_sleep())
            logging.info(f'Sleep until {next_run_at.strftime("%c")}')
            self.sleep_until(next_run_at)
