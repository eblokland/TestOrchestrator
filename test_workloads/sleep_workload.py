import time
from configparser import ConfigParser
from functools import singledispatchmethod

from adb_helpers.intent import Intent
from test_runner.test_runner import InstrumentedTest
from test_workloads.abstract_workload import AbstractWorkload
from config_strings import RUNTIME


class SleepWorkload(AbstractWorkload):

    @singledispatchmethod
    def __init__(self, args):
        raise TypeError(f'unknown arg type {type(args)}')

    @__init__.register
    def _init_from_file(self, filename: str):
        cfg = ConfigParser()
        cfg.read(filename)
        conf = cfg['SLEEP']
        self.sleep_time = conf.getfloat(RUNTIME)

    def pre_test(self):
        pass

    def start_test(self):
        pass

    def wait_for_test(self):
        time.sleep(self.sleep_time)

    def stop_test(self):
        pass

    def post_test(self):
        pass

    def get_start_intent(self) -> Intent:
        pass




if __name__ == "__main__":
    test = InstrumentedTest(SleepWorkload('/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini'),
                            '/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini')
    test.runtest()
