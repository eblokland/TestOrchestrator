import string
import time
from configparser import ConfigParser
from enum import Enum
from functools import singledispatchmethod
from typing import Dict, Union

from simpleperf_utils import AdbHelper

from adb_helpers.actions import Actions
from adb_helpers.intent import Extra, Intent
from test_runner.test_runner import InstrumentedTest
from test_workloads.abstract_workload import AbstractWorkload
from test_workloads.config_strings import *

sensor_types: Dict[str, int] = {'accelerometer': 1}

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'


class SensorWorkload(AbstractWorkload):

    @singledispatchmethod
    def __init__(self, arg):
        raise ValueError(f'unknown arg type {type(arg)}')

    @__init__.register
    def _init_from_file(self, file: str):
        self.adb = AdbHelper(enable_switch_to_root=False)
        self._read_file(file)

    def _read_file(self, file: str):
        cfg = ConfigParser()
        cfg.read(file)
        sensor_cfg = cfg['SENSORS']
        sensor_type_str = sensor_cfg.get(SENSOR_TYPE).lower()
        if not sensor_type_str in sensor_types:
            raise ValueError(f'unknown sensor type string {sensor_type_str}')
        self.sensor_type: int = sensor_types[sensor_type_str]
        self.use_wakeup: bool = sensor_cfg.getboolean(USE_WAKEUP)
        self.work_rate_hz: int = sensor_cfg.getint(WORK_RATE_HZ)
        self.samp_rate_hz: int = sensor_cfg.getint(SAMP_RATE_HZ)

        self.work_amount: Union[int, None] = sensor_cfg.getint(WORK_AMOUNT)
        self.runtime_secs: int = sensor_cfg.getint(RUNTIME)
        self.short_runtime: int = sensor_cfg.gentint(WARMUP_RUNTIME)

    def warmup_workload(self):
        intent = self.get_start_intent()
        intent.send_intent(self.adb)
        time.sleep(self.short_runtime)
        self.get_stop_intent().send_intent(self.adb)

    def pre_test(self):
        pass

    def test_workload(self):
        intent = self.get_start_intent()
        intent.send_intent(self.adb)

        time.sleep(self.runtime_secs + 1)

        self.get_stop_intent().send_intent(self.adb)



    def post_test(self):
        pass

    def get_start_intent(self) -> Intent:
        extras = [
            Extra(self.sensor_type, SENSOR_TYPE),
            Extra(self.use_wakeup, USE_WAKEUP),
            Extra(self.work_rate_hz, WORK_RATE_HZ),
            Extra(self.samp_rate_hz, SAMP_RATE_HZ),
        ]
        if self.work_amount is not None:
            extras.append(Extra(self.work_amount, WORK_AMOUNT))

        intent = Intent(activity=PACKAGE, action=Actions.START_SENSOR, extras=extras)
        return intent

if __name__ == "__main__":
    test = InstrumentedTest(SensorWorkload('config.ini'), 'config.ini')
    test.runtest()
