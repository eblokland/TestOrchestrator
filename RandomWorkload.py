import csv
import time
from configparser import ConfigParser

from simpleperf_utils import AdbHelper
from adb_helpers.Intent import Intent, Actions, Extra, ExtraTypes
from TestRunner.TestRunner import InstrumentedTest

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'

TIMESTEP = "timestep"
RUNTIME = "runtime"
SLEEP_PROB = "sleep_prob"
NUM_THREADS = "num_threads"
WORKER_ID = "worker_id"
NUM_CLASSES = "num_classes"

workload_runtime_csv_header = ['Classname', 'Runtime (ns)', 'proportion of total', 'proportion of active']


class workload_runtime(object):
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


def extract_num_classes(line: str) -> int:
    split = line.strip().split(' ')
    return int(split[len(split) - 1])


def parse_class_runtimes(times: list[str]) -> list[workload_runtime]:
    cut_strs = []
    for time in times:
        (before, part, after) = time.partition('RANDOM_WORKER: ')
        if after == '':
            print('failed to split string?? ' + before)
            continue
        cut_strs.append(after)

    runtimes: list[workload_runtime] = []
    for str in cut_strs:
        runtimes.append(workload_runtime(str))
    return runtimes


def print_csv(runtimes: list[workload_runtime], total_time: int, output_file):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        writer.writerow(workload_runtime_csv_header)
        for t in runtimes:
            writer.writerow(t.to_arr())


def parse_logcat_string(logcatstring: str) -> (int, list[workload_runtime]):
    logcat_list = logcatstring.split('\n')
    # work backwards so we have the most recent
    filtered_logcat = []
    for str in logcat_list:
        if 'RANDOM_WORKER' in str:
            filtered_logcat.append(str)

    pos = len(filtered_logcat) - 1
    while not 'NUM CLASSES' in filtered_logcat[pos]:
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


def run_random_workload(config):
    rand_conf = config['RANDOM_WORKLOAD']
    runtime = rand_conf.getint('runtime')
    pause_prob = rand_conf.getfloat('pause_prob')
    timestep = rand_conf.getint('timestep')
    num_classes = rand_conf.getint('num_classes')

    adb = AdbHelper()
    extras = [Extra(ExtraTypes.INT, TIMESTEP, timestep),
              Extra(ExtraTypes.INT, RUNTIME, runtime),
              Extra(ExtraTypes.FLOAT, SLEEP_PROB, pause_prob),
              Extra(ExtraTypes.INT, NUM_CLASSES, num_classes)]
    intent = Intent(activity=PACKAGE, action=Actions.STARTRANDOM, extras=extras)

    intent.send_intent(adb)

    time.sleep(runtime + 1)


def post_random_workload(config):
    rand_conf = config['RANDOM_WORKLOAD']
    adb = AdbHelper(enable_switch_to_root=False)
    status, pid = adb.run_and_return_output(['shell', 'pidof', config['SIMPLEPERF'].get('aut')])
    if not status:
        print("failed to get pid")
        return

    print(pid)
    status, logcat_str = adb.run_and_return_output(
        ['shell', 'logcat', '-d', '--pid=' + str(pid)], True, True)
    if not status:
        print("something went wrong with logcat!")
        return

    (total_time, runtimes) = parse_logcat_string(logcat_str)
    csv_file = rand_conf.get('csv_output_path') + rand_conf.get('csv_name') + '.csv'
    print_csv(runtimes=runtimes, total_time=total_time, output_file=csv_file)


if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read('config.ini')
    test = InstrumentedTest(lambda: run_random_workload(cfg), 'config.ini')
    test.runtest()
    post_random_workload(cfg)
