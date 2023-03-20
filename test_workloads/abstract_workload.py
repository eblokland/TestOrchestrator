from abc import abstractmethod, ABC

from adb_helpers.actions import Actions
from adb_helpers.intent import Intent

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'

class AbstractWorkload(ABC):

    @abstractmethod
    def pre_test(self):
        pass

    @abstractmethod
    def test_workload(self):
        pass

    @abstractmethod
    def post_test(self):
        pass

    def get_stop_intent(self):
        return Intent(activity=PACKAGE, action=Actions.STOP_WORKER)
