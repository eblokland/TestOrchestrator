import time
from configparser import ConfigParser
from functools import singledispatchmethod

from simpleperf_utils import AdbHelper

from adb_helpers.actions import Actions
from adb_helpers.intent import Intent, Extra
from test_runner.test_runner import InstrumentedTest
from test_workloads.abstract_workload import AbstractWorkload
from config_strings import *

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'
ACTION = 'land.erikblok.action.START_BLUETOOTH'

#SCAN_PERIOD_MILLIS = "scan_period_millis"
#SCAN_ACTIVE_MILLIS = "scan_active_millis"
#RUNTIME = "runtime"
#TIMESTEP = "timestep"
#SLEEP_PROB = "sleep_prob"
#NUM_THREADS = "num_threads"
#TEST_RUNTIME = 'test_runtime'
#SHORT_RUNTIME = 'warmup_runtime'


class BluetoothWorkload(AbstractWorkload):
    @singledispatchmethod
    def __init__(self, arg):
        raise TypeError(f'Argument has unknown type {type(arg)}')

    @__init__.register
    def _init_from_cfg(self, file: str):
        cfg = ConfigParser()
        cfg.read(file)
        blue_conf = cfg['BLUETOOTH']

        self.adb = AdbHelper()
        self.scan_period_millis: int = blue_conf.getint(SCAN_PERIOD_MILLIS)
        self.scan_active_millis: int = blue_conf.getint(SCAN_ACTIVE_MILLIS)
        self.runtime: int = blue_conf.getint(RUNTIME)
       # self.test_runtime: int = blue_conf.getint(RUNTIME)
        self.short_runtime: int = blue_conf.getint(WARMUP_RUNTIME)
        self.timestep: int = blue_conf.getint(TIMESTEP)
        self.sleep_prob: float = blue_conf.getfloat(SLEEP_PROB)
        self.num_threads: int = blue_conf.getint(NUM_THREADS)

        if self.runtime is None or self.scan_active_millis is None or self.scan_period_millis is None:
            raise ValueError(f'Missing at least one mandatory config option')

    @__init__.register
    def _init_from_args(self, scan_period_millis: int, scan_active_millis: int, runtime: int = 0, timestep: int = 100,
                        sleep_prob: float = 0.0, num_threads: int = 0, dc_adb: bool = False):
        self.adb = AdbHelper()
        self.scan_period_millis: int = scan_period_millis
        self.scan_active_millis: int = scan_active_millis
        self.runtime: int = runtime
        self.timestep: int = timestep
        self.sleep_prob: float = sleep_prob
        self.num_threads: int = num_threads

    def pre_test(self):
        pass

    def warmup_workload(self):
        intent = self.get_start_intent()
        intent.remove_extra(RUNTIME)
        intent.send_intent()
        time.sleep(self.short_runtime)
        self.get_stop_intent().send_intent(self.adb)

    def start_test(self):
        intent = self.get_start_intent()
        intent.send_intent(self.adb)

    def wait_for_test(self):
        time.sleep(self.runtime + 1)

    def stop_test(self):
        self.get_stop_intent().send_intent(self.adb)

    def post_test(self):
        pass

    def get_start_intent(self) -> Intent:
        extras = [
            Extra(self.scan_period_millis, SCAN_PERIOD_MILLIS),
            Extra(self.scan_active_millis, SCAN_ACTIVE_MILLIS),
        ]

        def append_not_none(value, key):
            if value is not None:
                extras.append(Extra(value, key))

       # append_not_none(self.runtime, RUNTIME)
        append_not_none(self.timestep, TIMESTEP)
        append_not_none(self.num_threads, NUM_THREADS)
        append_not_none(self.sleep_prob, SLEEP_PROB)

        return Intent(PACKAGE, Actions.START_BLUETOOTH, extras=extras)


if __name__ == "__main__":
    test = InstrumentedTest(BluetoothWorkload('/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini'),
                            '/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini')

    test.runtest()
