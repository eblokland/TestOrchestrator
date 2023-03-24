import sys

from test_components.app_prep_component import AppPrepComponent
from test_components.environment_sampler_component import EnvironmentSamplerComponent
from test_components.simpleperf_component import SimpleperfComponent
from test_runner.buildable_test_runner import BuildableTest
from test_workloads.ab_workloads.for_loop_workload import ForLoopWorkload
from test_workloads.ab_workloads.is_workload import ISWorkload
from test_workloads.ab_workloads.mim_workload import MIMWorkload
from test_workloads.abstract_workload import AbstractWorkload
from test_workloads.bluetooth_workload import BluetoothWorkload
from test_workloads.random_workload import RandomWorkload
from test_workloads.sensor_workload import SensorWorkload
from test_workloads.sleep_workload import SleepWorkload


def get_wl_for_string(test_str: str, config_loc: str) -> AbstractWorkload:
    test_str = test_str.lower()
    if test_str in 'bluetooth':
        return BluetoothWorkload(config_loc)
    if test_str in 'random':
        return RandomWorkload(config_loc)
    if test_str in 'sensor':
        return SensorWorkload(config_loc)
    if test_str in 'sleep':
        return SleepWorkload(config_loc)
    if test_str in 'for_loop':
        return ForLoopWorkload(config_loc)
    if test_str in 'internal_setter':
        return ISWorkload(config_loc)
    if test_str in 'mim':
        return MIMWorkload(config_loc)


def build_test(test_str: str, iterations: int, simpleperf_config: str, sampler_config: str,
               workload_conf: str, app_prep_conf: str) -> BuildableTest:
    workload = get_wl_for_string(test_str, workload_conf)
    test = BuildableTest(workload=workload, iterations=iterations). \
        add_test_component(EnvironmentSamplerComponent(sampler_config)) \
        .add_test_component(SimpleperfComponent(simpleperf_config)) \
        .add_test_component(AppPrepComponent(app_prep_conf))

    return test


def build_test_single_conf(test_str: str, conf: str, iterations: int):
    return build_test(test_str, iterations, conf, conf, conf, conf)


if __name__ == "__main__":
    args = sys.argv[1:]
    test_str = args[0]
    conf_loc = args[1]
    num_runs = int(args[2])
    if num_runs is None:
        num_runs = 1
    test = build_test_single_conf(test_str, conf_loc, num_runs)
    test.runtest()