from adb_helpers.actions import Actions
from adb_helpers.intent import Intent
from test_workloads.ab_workloads.ab_workload import ABWorkload


class InternalSetterWorkload(ABWorkload):

    def _read_file_concrete(self, file: str):
        self._read_file(file, 'IS')

    def pre_test(self):
        pass

    def test_workload(self):
        pass

    def post_test(self):
        pass

    def get_start_intent(self) -> Intent:
        return self._get_start_intent(action=Actions.START_IS)
