# This is a sample Python script.

from test_runner.test_runner import InstrumentedTest
from test_workloads.sleep_workload import SleepWorkload

if __name__ == '__main__':
    test = InstrumentedTest(SleepWorkload(70), 'config.ini')
    test.runtest()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
