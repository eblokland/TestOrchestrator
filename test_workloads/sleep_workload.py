import time
from configparser import ConfigParser
from functools import singledispatchmethod

from simpleperf_utils import AdbHelper

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
        self.sleep_time: float = conf.getfloat(RUNTIME)
        self.adb: AdbHelper = AdbHelper()
        self.outfilename: str = cfg['CONFIG'].get('outfilename')
        self.outdirectory: str = cfg['SAMPLER'].get('samplerlogoutputpath')
        self.count: int = 1
        self._starting_battery: int = 0

    def pre_test(self):
        pass

    def start_test(self):
        pass

    def warmup_workload(self):
        pass

    def loop_pre_test(self):
        self._starting_battery = self._get_battery_level()

    def wait_for_test(self):
        time.sleep(self.sleep_time)

    def stop_test(self):
        pass

    def loop_post_test(self):
        end_level = self._get_battery_level()
        final_filename_string = f'{self.outdirectory}{self.outfilename}-battery_level-{self.count}.txt'
        with open(final_filename_string, 'w') as outfile:
            outfile.writelines([f'{self._starting_battery}\n', f'{end_level}'])
        self.count += 1
        
    def post_test(self):
        pass

    def get_start_intent(self) -> Intent:
        pass

    def _get_battery_level(self) -> int:
        (status, out) = self.adb.run_and_return_output(['shell', 'dumpsys', 'battery', '|', 'grep', 'level'])
        level = int(''.join(filter(str.isdigit, out))) if status else -1
        return level



if __name__ == "__main__":
    test = InstrumentedTest(SleepWorkload('/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini'),
                            '/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini')
    test.runtest()
