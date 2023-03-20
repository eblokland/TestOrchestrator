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


sensor_types: Dict[str, int] = {'accelerometer': 1}

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'


SAMP_RATE_HZ = "sample_rate_hz"
WORK_RATE_HZ = "work_rate_hz"
SENSOR_TYPE = "sensor_type"
USE_WAKEUP = "use_wakeup"
RUNTIME = "runtime"
WORK_AMOUNT = "work_amount"



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
        sensor_type_str = sensor_cfg.get('sensor_type').lower()
        if not sensor_type_str in sensor_types:
            raise ValueError(f'unknown sensor type string {sensor_type_str}')
        self.sensor_type: int = sensor_types[sensor_type_str]
        self.use_wakeup: bool = sensor_cfg.getboolean('use_wakeup')
        self.work_rate_hz: int = sensor_cfg.getint('work_rate_hz')
        self.samp_rate_hz: int = sensor_cfg.getint('samp_rate_hz')

        self.work_amount: Union[int, None] = sensor_cfg.getint('work_amount')
        self.runtime_secs: int = sensor_cfg.getint('runtime')




    def pre_test(self):
        pass

    def test_workload(self):
        extras = [
            Extra(self.sensor_type, SENSOR_TYPE),
            Extra(self.use_wakeup, USE_WAKEUP),
            Extra(self.work_rate_hz, WORK_RATE_HZ),
            Extra(self.samp_rate_hz, SAMP_RATE_HZ),
        ]
        if self.work_amount is not None:
            extras.append(Extra(self.work_amount, WORK_AMOUNT))

        intent = Intent(activity=PACKAGE, action=Actions.START_SENSOR, extras=extras)
        intent.send_intent(self.adb)

        time.sleep(self.runtime_secs + 1)

        self.get_stop_intent().send_intent(self.adb)



    def post_test(self):
        pass

if __name__ == "__main__":
    test = InstrumentedTest(SensorWorkload('config.ini'), 'config.ini')
    test.runtest()
