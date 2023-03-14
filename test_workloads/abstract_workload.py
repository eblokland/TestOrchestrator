from abc import abstractmethod, ABC


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
