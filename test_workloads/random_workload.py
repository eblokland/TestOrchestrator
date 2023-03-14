import csv
import time
from configparser import ConfigParser

from simpleperf_utils import AdbHelper

from adb_helpers.intent import Intent, Actions, Extra, ExtraTypes
from test_runner.test_runner import InstrumentedTest
from test_workloads.abstract_workload import AbstractWorkload

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'

TIMESTEP = "timestep"
RUNTIME = "runtime"
SLEEP_PROB = "sleep_prob"
NUM_THREADS = "num_threads"
WORKER_ID = "worker_id"
NUM_CLASSES = "num_classes"

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
    def __init__(self, file):
        self.adb = AdbHelper(enable_switch_to_root=False)
        self._read_config(file)

    def _read_config(self, file: str):
        config = ConfigParser()
        config.read(file)
        self.aut = cfg['SIMPLEPERF'].get('aut')
        rand_conf = cfg['RANDOM_WORKLOAD']
        self.csv_file = rand_conf.get('csv_output_path') + rand_conf.get('csv_name') + '.csv'

        self.runtime = rand_conf.getint('runtime')
        self.pause_prob = rand_conf.getfloat('pause_prob')
        self.timestep = rand_conf.getint('timestep')
        self.num_classes = rand_conf.getint('num_classes')
        if self.runtime is None or self.pause_prob is None \
                or self.timestep is None or self.num_classes is None:
            raise ValueError('Invalid config file!')

    def pre_test(self):
        pass

    def test_workload(self):
        extras = [Extra(ExtraTypes.INT, TIMESTEP, self.timestep),
                  Extra(ExtraTypes.INT, RUNTIME, self.runtime),
                  Extra(ExtraTypes.FLOAT, SLEEP_PROB, self.pause_prob),
                  Extra(ExtraTypes.INT, NUM_CLASSES, self.num_classes)]
        intent = Intent(activity=PACKAGE, action=Actions.STARTRANDOM, extras=extras)

        intent.send_intent(self.adb)

        time.sleep(self.runtime + 1)

    def post_test(self):
        status, pid = self.adb.run_and_return_output(['shell', 'pidof', self.aut])
        if not status:
            print("failed to get pid")
            return
        print(pid)
        status, logcat_str = self.adb.run_and_return_output(
            ['shell', 'logcat', '-d', '--pid=' + str(pid)], True, True)
        if not status:
            print("something went wrong with logcat!")
            return

        (total_time, runtimes) = parse_logcat_string(logcat_str)
        write_csv(runtimes=runtimes, total_time=total_time, output_file=self.csv_file)


if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read('config.ini')
    test = InstrumentedTest(RandomWorkload('../config.ini'), '../config.ini')
    test.runtest()