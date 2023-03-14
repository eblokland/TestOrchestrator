import time

from test_workloads.abstract_workload import AbstractWorkload


class SleepWorkload(AbstractWorkload):
    def __init__(self, sleep_time_secs: int):
        self.sleep_time = sleep_time_secs

    def pre_test(self):
        pass

    def test_workload(self):
        time.sleep(self.sleep_time)

    def post_test(self):
        pass
