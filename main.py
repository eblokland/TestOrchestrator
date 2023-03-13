# This is a sample Python script.
import time

from TestRunner import InstrumentedTest
# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def workload():
    time.sleep(70)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    test = InstrumentedTest(workload, 'config.ini')
    test.runtest()



# See PyCharm help at https://www.jetbrains.com/help/pycharm/




