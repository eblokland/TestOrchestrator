from abc import abstractmethod, ABC
from typing import List

from adb_helpers.actions import Actions
from adb_helpers.intent import Intent

PACKAGE = 'land.erikblok.busyworker/.BusyWorkerService'


class AbstractWorkload(ABC):

    def pre_test(self):
        """
        Runs before test loop, used for any environmental setup needed.
        Not mandatory to implement
        :return:
        """
        pass

    @abstractmethod
    def warmup_workload(self):
        """
        Used as a "warmup", primarily to poke the ART to do some JIT optimizations.
        Mandatory to implement
        :return:
        """
        pass

    def loop_pre_test(self):
        """
        Runs before test workload in main loop.  Probably not necessary for workload, but provided for consistency.
        Not mandatory to implement.
        :return:
        """
        pass

    @abstractmethod
    def test_workload(self):
        """
        Primary test workload.  Should start workload, block until finished, and confirm workload is stopped somehow.
        Mandatory to implement
        :return:
        """
        pass

    def loop_post_test(self):
        """
        Runs after test in test loop.  Probably not necessary for workload, provided for consistency.
        Not mandatory to implement
        :return:
        """

    def post_test(self):
        """
        Runs after test loop.  Takes care of any tasks such as uninstalling the apk that should happen at the end of a test.
        :return:
        """
        pass

    @abstractmethod
    def get_start_intent(self) -> Intent:
        pass

    def get_stop_intent(self):
        return Intent(activity=PACKAGE, action=Actions.STOP_WORKER)
