from adb_helpers.actions import Actions
from adb_helpers.intent import Intent
from test_runner.test_runner import InstrumentedTest
from test_workloads.ab_workloads.ab_workload import ABWorkload


class ForLoopWorkload(ABWorkload):
    def _read_file_concrete(self, file: str):
        self._read_file(file, 'FOR_LOOP')

    def pre_test(self):
        pass

    def get_start_intent(self) -> Intent:
        return self._get_start_intent(action=Actions.START_FORLOOP)

    def get_short_start_intent(self) -> Intent:
        return self._get_short_start_intent(action=Actions.START_FORLOOP)


if __name__ == "__main__":
    test = InstrumentedTest(ForLoopWorkload('/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini'),
                            '/Users/erikbl/PycharmProjects/TestOrchestrator/config.ini')
    test.runtest()