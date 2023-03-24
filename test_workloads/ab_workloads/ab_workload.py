from abc import abstractmethod
from configparser import ConfigParser
from functools import singledispatchmethod
from time import sleep
from typing import Union

from simpleperf_utils import AdbHelper

from adb_helpers.actions import Actions
from adb_helpers.commands import kill_app
from adb_helpers.intent import Extra, Intent
from adb_helpers.logcat_utils import get_logcat_for_aut, split_logcat, filter_logcat_str_for_tags
from test_workloads.ab_workloads.ab_workload_strings import AB_LOGCAT_TAG
from test_workloads.abstract_workload import AbstractWorkload
from config_strings import *

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'


class ABWorkload(AbstractWorkload):
    @singledispatchmethod
    def __init__(self, arg):
        raise ValueError(f'unknown arg type {type(arg)}')

    @__init__.register
    def _init_from_file(self, file: str):
        self.adb = AdbHelper(enable_switch_to_root=False)
        self._read_file_concrete(file)

    @__init__.register
    def _init_from_args(self, work_amount: int, use_fixed: bool, use_as_runtime: bool = False,
                        outer_loop_iterations: int = 1, time_guess: int = 2):
        self.adb = AdbHelper(enable_switch_to_root=False)
        self.use_fixed = use_fixed
        self.work_amount = work_amount
        self.use_as_runtime = use_as_runtime
        self.outer_loop_iterations = outer_loop_iterations
        self.time_guess = time_guess

    def test_workload(self):
        seconds = self.work_amount / 1000 if self.use_as_runtime else self.time_guess
        intent = self.get_start_intent()
        intent.send_intent(self.adb)
        sleep(seconds + 1)
        self.get_stop_intent().send_intent(self.adb)

    def warmup_workload(self):
        seconds = self.short_work_amount / 1000 if self.use_as_runtime else self.short_time_guess
        intent = self.get_short_start_intent()
        intent.send_intent(self.adb)
        sleep(seconds)
        self.get_stop_intent().send_intent(self.adb)
        print(f'Sleeping to allow JIT to compile')
        sleep(2)


    @abstractmethod
    def _read_file_concrete(self, file: str):
        pass

    def _read_file(self, file: str, cfg_section: str):
        config = ConfigParser()
        config.read(file)
        adb_conf = config['CONFIG']
        serial_no = adb_conf.get('adb_serial')
        if serial_no is not None:
            self.adb.serial_number = serial_no
        mim_conf = config[cfg_section]
        self.work_amount = mim_conf.getint(WORK_AMOUNT)
        self.short_work_amount = mim_conf.getint(SHORT_WORK_AMOUNT)
        self.use_as_runtime = mim_conf.getboolean(USE_AS_RUNTIME)
        self.use_fixed = mim_conf.getboolean(USE_FIXED)
        self.outer_loop_iterations = mim_conf.getint(OUTER_LOOP_ITERATIONS)
        self.time_guess = mim_conf.getint(TIME_GUESS)
        self.short_time_guess = mim_conf.getint(SHORT_TIME_GUESS)
        if self.short_time_guess is None:
            self.short_time_guess = 1
        if self.time_guess is None:
            self.time_guess = 2
        if self.work_amount is None or self.use_fixed is None or self.use_as_runtime is None:
            raise ValueError('Did not find all values in config file')

    def _get_start_intent(self, action: Actions):
        extras = [Extra(self.work_amount, WORK_AMOUNT),
                  Extra(self.use_fixed, USE_FIXED),
                  Extra(self.use_as_runtime, USE_AS_RUNTIME)]
        if self.outer_loop_iterations is not None:
            extras.append(Extra(self.outer_loop_iterations, OUTER_LOOP_ITERATIONS))

        return Intent(
            activity=PACKAGE,
            action=action,
            extras=extras
        )

    def _get_short_start_intent(self, action: Actions):
        extras = [
            Extra(self.short_work_amount, WORK_AMOUNT),
            Extra(self.use_fixed, USE_FIXED),
            Extra(self.use_as_runtime, USE_AS_RUNTIME)
        ]
        return Intent(
            activity=PACKAGE,
            action=action,
            extras=extras,
        )

    def post_test(self):
        if not self.use_as_runtime:
            print(f'end time = {self.get_stop_time()}')

    @abstractmethod
    def get_start_intent(self) -> Intent:
        pass

    @abstractmethod
    def get_short_start_intent(self) -> Intent:
        pass

    def get_stop_intent(self) -> Intent:
        return Intent(activity=PACKAGE, action=Actions.STOP_WORKER)

    def get_stop_time(self) -> Union[int, None]:
        logcat_str = get_logcat_for_aut('land.erikblok.busyworker', self.adb)
        if logcat_str is None:
            return None
        log_entries = split_logcat(logcat_str, latest_first=True)
        filtered = filter_logcat_str_for_tags(log_entries, AB_LOGCAT_TAG)
        if len(filtered) == 0:
            return None

        line_list = filtered[0].strip().split(' ')
        # final component should always be the end time
        return int(line_list[len(line_list) - 1])
