import sys
from configparser import ConfigParser
from typing import Tuple, Optional

from test_components.app_prep_component import AppPrepComponent
from test_components.environment_sampler_component import EnvironmentSamplerComponent
from test_components.simpleperf_component import SimpleperfComponent
from test_components.simpleperf_disconnected_component import SimpleperfDisconnectedComponent
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
    else:
        raise ValueError(f'invalid string {test_str}')


def build_test(test_str: str, iterations: int, simpleperf_config: str, sampler_config: str,
               workload_conf: str, app_prep_conf: str, use_dc: bool = False, adb_ip: Optional[str] = None) -> BuildableTest:
    workload = get_wl_for_string(test_str, workload_conf)
    simp_component = SimpleperfDisconnectedComponent(simpleperf_config) if use_dc else SimpleperfComponent(simpleperf_config)
    test = BuildableTest(workload=workload, iterations=iterations). \
        add_test_component(EnvironmentSamplerComponent(sampler_config)) \
        .add_test_component(simp_component) \
        .add_test_component(AppPrepComponent(app_prep_conf)) \
        .set_disconnect_adb(use_dc, adb_ip)

    return test


def build_test_single_conf(test_str: str, conf: str, iterations: int, use_dc: bool = False, adb_ip: Optional[str] = None):
    return build_test(test_str, iterations, conf, conf, conf, conf, use_dc, adb_ip)


if __name__ == "__main__":
    args = sys.argv[1:]
    test_str = args[0]
    conf_loc = args[1]
    num_runs = int(args[2])
    cfg = ConfigParser()
    cfg.read(conf_loc)
    adb_ip = None
    use_dc = False
    if cfg.has_section('TEST_CONFIGURATION'):
        test_conf = cfg['TEST_CONFIGURATION']
        adb_ip = test_conf.get('wireless_adb_ip')
        use_dc = test_conf.getboolean('dc_adb', None)
    if num_runs is None:
        num_runs = 1
    test = build_test_single_conf(test_str, conf_loc, num_runs, use_dc, adb_ip)
    test.runtest()