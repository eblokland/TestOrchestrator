import csv
import time
from configparser import ConfigParser
from functools import singledispatchmethod

from simpleperf_utils import AdbHelper

from adb_helpers.intent import Intent, Actions, Extra, ExtraTypes
from test_runner.test_runner import InstrumentedTest
from test_workloads.abstract_workload import AbstractWorkload
from adb_helpers.logcat_utils import get_logcat_for_aut
from config_strings import *

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'

#TIMESTEP = "timestep"
#RUNTIME = "runtime"
#SLEEP_PROB = "sleep_prob"
#NUM_THREADS = "num_threads"
#WORKER_ID = "worker_id"
#NUM_CLASSES = "num_classes"


workload_runtime_csv_header = ['Classname', 'Runtime (ns)', 'proportion of total', 'proportion of active']


class RandomWorkloadRuntime(object):
    def __init__(self, cut_string: str):
        split = cut_string.split(', ')
        self.classname = split[0]
        self.runtime = int(split[1])
        self.prop = 0.0
        self.runprop = 0.0

    def set_prop(self, total_time: int) -> float:
        self.prop = float(self.runtime) / float(total_time)
        return self.prop

    def set_run_prop(self, run_time: int):
        self.runprop = float(self.runtime) / float(run_time)
        return self.runprop

    def to_arr(self):
        return [self.classname, self.runtime, self.prop, self.runprop]


# region PARSE_LOGCAT

def extract_num_classes(line: str) -> int:
    split = line.strip().split(' ')
    return int(split[len(split) - 1])


def parse_class_runtimes(times: list[str]) -> list[RandomWorkloadRuntime]:
    cut_strs = []
    for runtime in times:
        (before, part, after) = runtime.partition('RANDOM_WORKER: ')
        if after == '':
            print('failed to split string?? ' + before)
            continue
        cut_strs.append(after)

    runtimes: list[RandomWorkloadRuntime] = []
    for string in cut_strs:
        runtimes.append(RandomWorkloadRuntime(string))
    return runtimes


def parse_logcat_string(logcatstring: str) -> (int, list[RandomWorkloadRuntime]):
    logcat_list = logcatstring.split('\n')
    # work backwards so we have the most recent
    filtered_logcat = []
    for string in logcat_list:
        if 'RANDOM_WORKER' in string:
            filtered_logcat.append(string)

    pos = len(filtered_logcat) - 1
    while 'NUM CLASSES' not in filtered_logcat[pos]:
        pos -= 1

    latest_run = filtered_logcat[pos:]
    num_classes = extract_num_classes(latest_run[0])
    runtimes = parse_class_runtimes(latest_run[2:])

    total_time = 0
    for t in runtimes:
        total_time += t.runtime
    sleep_time = next(x for x in runtimes if 'SleepWorkload' in x.classname).runtime
    for t in runtimes:
        t.set_prop(total_time)
        t.set_run_prop(total_time - sleep_time)
    return total_time, runtimes


# endregion

def write_csv(runtimes: list[RandomWorkloadRuntime], total_time: int, output_file):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        writer.writerow(workload_runtime_csv_header)
        for t in runtimes:
            writer.writerow(t.to_arr())


class RandomWorkload(AbstractWorkload):

    @singledispatchmethod
    def __init__(self, arg):
        raise TypeError(f'unknown argument type {type(arg)}')

    @__init__.register
    def _init_with_file(self, file: str):
        self.adb = AdbHelper(enable_switch_to_root=False)
        self._read_config(file)

    @__init__.register
    def _init_with_args(self, pause_prob: float, timestep: int, num_classes: int,
                        csv_file: str = None, aut='land.erikblok.busyworker', runtime: int = None):
        pass

    def _read_config(self, file: str):
        config = ConfigParser()
        config.read(file)
        rand_conf = config['RANDOM_WORKLOAD']
        self.csv_folder = rand_conf.get('csv_output_path')
        self.csv_name = rand_conf.get('csv_name')
        self.aut = rand_conf.get('pkg_name')
        self.loop_counter = 1
        self.runtime = rand_conf.getint('runtime')
        self.warmup_runtime = rand_conf.getint(WARMUP_RUNTIME)
        self.pause_prob = rand_conf.getfloat(SLEEP_PROB)
        self.timestep = rand_conf.getint(TIMESTEP)
        self.num_classes = rand_conf.getint(NUM_CLASSES)
        if self.runtime is None or self.pause_prob is None \
                or self.timestep is None or self.num_classes is None:
            raise ValueError('Invalid config file!')

    def pre_test(self):
        pass

    def test_workload(self):
        intent = self.get_start_intent()
        intent.send_intent(self.adb)

        time.sleep(self.runtime)
        # ensure worker has been stopped!
        # never mind, this will always stop it
        self.get_stop_intent().send_intent(self.adb)

    def loop_post_test(self):
        time.sleep(1)
        logcat_str = get_logcat_for_aut(self.aut, self.adb)
        if logcat_str is None:
            return

        (total_time, runtimes) = parse_logcat_string(logcat_str)
        csv_file = f'{self.csv_folder}{self.csv_name}-{self.loop_counter}.csv'
        write_csv(runtimes=runtimes, total_time=total_time, output_file=csv_file)
        self.loop_counter += 1

    def get_start_intent(self) -> Intent:
        extras = [Extra(ExtraTypes.INT, TIMESTEP, self.timestep),
                 # Extra(ExtraTypes.INT, RUNTIME, self.runtime),
                  Extra(ExtraTypes.FLOAT, SLEEP_PROB, self.pause_prob),
                  Extra(ExtraTypes.INT, NUM_CLASSES, self.num_classes)]
        intent = Intent(activity=PACKAGE, action=Actions.STARTRANDOM, extras=extras)
        return intent

    def warmup_workload(self):
        intent = self.get_start_intent()
        intent.send_intent(self.adb)
        time.sleep(self.warmup_runtime)
        self.get_stop_intent().send_intent(self.adb)



if __name__ == "__main__":
    test = InstrumentedTest(RandomWorkload('config.ini'), 'config.ini')
    test.runtest()
