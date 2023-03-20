from time import sleep

from adb_helpers.actions import Actions
from adb_helpers.intent import Intent, Extra
from test_runner.test_runner import InstrumentedTest
from test_workloads.ab_workloads.ab_workload import ABWorkload

class MIMWorkload(ABWorkload):

    def _read_file_concrete(self, file: str):
        self._read_file(file, 'MIM')

    def pre_test(self):
        pass

    def get_start_intent(self) -> Intent:
        return self._get_start_intent(action=Actions.START_MIM)


if __name__ == "__main__":
    test = InstrumentedTest(MIMWorkload('/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini'), '/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini')
    test.runtest()