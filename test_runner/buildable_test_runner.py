from functools import singledispatchmethod
from time import sleep
from typing import Optional, List, Any
from collections.abc import Callable

from test_components.test_component import TestComponent
from test_workloads.abstract_workload import AbstractWorkload
from device import AndroidDevice, get_device

import device


class BuildableTest(object):
    def __init__(self, workload: Optional[AbstractWorkload], iterations: int = 1):
        self._workload = workload
        self._pre_test_funs = []
        self._test_funs = []
        self._test_shutdown_funs = []
        self._post_test_funs = []
        self._loop_pre_test_funs = []
        self._loop_post_test_funs = []
        self.iterations = iterations
        self._disconnect_adb: bool = False
        self._wireless_adb_ip: Optional[str] = None
        self._device: Optional[AndroidDevice] = None

# region BUILDER_METHODS
    @singledispatchmethod
    def _add_fun(self, arg, fun_list):
        raise TypeError(f'type {type(arg)} not supported')

    @_add_fun.register(Callable)
    def _add_single_fun(self, new_fun, fun_list):
        fun_list.append(new_fun)

    @_add_fun.register(list)
    def _add_funs(self, new_funs, fun_list):
        for fun in new_funs:
            self._add_fun(fun, fun_list)

    def add_pre_test_fun(self, funs):
        self._add_fun(funs, self._pre_test_funs)
        return self

    def add_test_fun(self, funs):
        self._add_fun(funs, self._test_funs)
        return self

    def add_shutdown_fun(self, funs):
        self._add_fun(funs, self._test_shutdown_funs)
        return self

    def add_post_fun(self, funs):
        self._add_fun(funs, self._post_test_funs)
        return self

    def add_loop_post_test_fun(self, funs):
        self._add_fun(funs, self._loop_post_test_funs)
        return self

    def add_loop_pre_test_fun(self, funs):
        self._add_fun(funs, self._loop_pre_test_funs)
        return self

    def add_test_component(self, component: TestComponent):
        if not isinstance(component, TestComponent):
            raise TypeError('provided component not instance of TestComponent')

        self.add_test_fun(component.test_fun)
        self.add_post_fun(component.post_test_fun)
        self.add_shutdown_fun(component.shutdown_fun)
        self.add_pre_test_fun(component.pre_test_fun)
        self.add_loop_pre_test_fun(component.loop_pre_test_fun)
        self.add_loop_post_test_fun(component.loop_post_test_fun)
        return self

    def set_disconnect_adb(self, disconnect_adb: bool, wireless_adb_ip: Optional[str] = None):
        if not disconnect_adb and wireless_adb_ip is None:
            raise ValueError('When using disconnecting ADB, we need an IP to connect back to.')
        self._disconnect_adb = disconnect_adb
        self._wireless_adb_ip = wireless_adb_ip
        self._device = AndroidDevice(serial=self._wireless_adb_ip) if self._disconnect_adb else None
        return self
#endregion

    def runtest(self):
        # execute all setup functions, these may take time
        for fun in self._pre_test_funs:
            fun()
        self._workload.pre_test()

        # perform the warmup now, this is a short workload to warm the JIT cache
        self._workload.warmup_workload()
        sleep(120)

        for i in range(0, self.iterations):

            for fun in self._loop_pre_test_funs:
                fun()

            self._workload.loop_pre_test()

            # start up all test-related services.  they should ensure that they've finished starting.
            for fun in self._test_funs:
                fun()

            self._workload.start_test()
            # run the test workload.  it will return when it finishes.
            if self._device and self._wireless_adb_ip:
                self._device.disconnect(self._wireless_adb_ip)
                print(f'hopefully disconnected')
            self._workload.wait_for_test()
            if self._device and self._wireless_adb_ip:
                print(self._device.connect(self._wireless_adb_ip))


            self._workload.stop_test()

            # run test shutdown functions.
            for fun in self._test_shutdown_funs:
                fun()

            for fun in self._loop_post_test_funs:
                fun()

            # run post-test for workload
            self._workload.loop_post_test()

        self._workload.post_test()

        # run the rest of the post-test functions
        for fun in self._post_test_funs:
            fun()



