from abc import ABC, abstractmethod


class TestComponent(ABC):

    def pre_test_fun(self):
        """
        Function to be executed prior to the test loop starting.
        May be executed long before workload
        :return:
        """
        pass

    def loop_pre_test_fun(self):
        """
        Function to be executed before test within test loop.
        :return:
        """
        pass

    def test_fun(self):
        """
        Function to be executed *immediately* prior to test workload beginning
        Should be used ex. for starting up sampling
        :return:
        """
        pass

    def shutdown_fun(self):
        """
        Function to be executed *immediately* after test workload ends.
        Should be used for ex. stopping sampling.  Should not take long.
        :return:
        """
        pass

    def loop_post_test_fun(self):
        """
        Function to be executed after test end, within test loop.
        :return:
        """
        pass

    def post_test_fun(self):
        """
        Function to be executed after the test ends.  May be executed long after workload exits,
        should be used for long actions (ex. copy file)
        :return:
        """
        pass


