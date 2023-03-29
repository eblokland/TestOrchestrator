from functools import singledispatchmethod
from typing import Optional, List, Any
from collections.abc import Callable

from test_components.test_component import TestComponent
from test_workloads.abstract_workload import AbstractWorkload


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

    def runtest(self):
        # execute all setup functions, these may take time
        for fun in self._pre_test_funs:
            fun()
        self._workload.pre_test()

        # perform the warmup now, this is a short workload to warm the JIT cache
        self._workload.warmup_workload()

        for i in range(0, self.iterations):

            for fun in self._loop_pre_test_funs:
                fun()

            self._workload.loop_pre_test()

            # start up all test-related services.  they should ensure that they've finished starting.
            for fun in self._test_funs:
                fun()

            # run the test workload.  it will return when it finishes.
            self._workload.test_workload()

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



