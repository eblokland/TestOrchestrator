from configparser import ConfigParser

from app_profiler import AppProfiler
from binary_cache_builder import BinaryCacheBuilder
from device import *
from simpleperf_utils import AdbHelper

from samplers.environment_sampler import EnvironmentSampler
from simpleperf_helpers.simpleperf_command import SimpleperfCommand
from test_workloads.abstract_workload import AbstractWorkload


class InstrumentedTest(object):
    def __init__(self, workload: AbstractWorkload, cfgloc):
        self.workload = workload
        self.cfg = ConfigParser()
        self.cfg.read(cfgloc)
        self._read_config(self.cfg)

    def _read_config(self, cfg: ConfigParser):
        conf = cfg['CONFIG']
        self.bin_cache_path = conf.get('binarycachepath')
        self.ndk_path = conf.get('ndkpath')
        self.disable_root = conf.getboolean('disable_root')
        self.device_serial = conf.get('adb_serial')

    def runtest(self):
        command = SimpleperfCommand(self.cfg)
        args = command.build_simpleperf_obj()
        profiler = AppProfiler(args)
        profiler.prepare()

        self.workload.pre_test()

        samp = EnvironmentSampler(self.cfg)

        if not samp.check_installed():
            samp.install_pkg()
        if not samp.start_file_log():
            raise Exception('failed to start logger')

        adb = AdbHelper()
        if self.device_serial is not None:
            adb.serial_number = self.device_serial

        print(adb.run_and_return_output(['shell', 'dumpsys', 'battery', '|', 'grep', '-i', 'charge']))
        profiler.start()
        self.workload.wait_for_test()
        print(adb.run_and_return_output(['shell', 'dumpsys', 'battery', '|', 'grep', '-i', 'charge']))
        profiler.stop_profiling()
        samp.stop_file_log()
        self.workload.post_test()
        profiler.collect_profiling_data()
        samp.pull_log()

        self._build_bincache(args.perf_data_path)

    def _build_bincache(self, perf_data_path, symfspaths=None):
        # binary cache doesn't support custom directories... just change pwd instead.
        current_dir = os.getcwd()
        os.chdir(self.bin_cache_path)
        if self.ndk_path == '':
            self.ndk_path = None
        bin_cache = BinaryCacheBuilder(ndk_path=self.ndk_path, disable_adb_root=self.disable_root)
        bin_cache.build_binary_cache(perf_data_path, symfspaths)
        os.chdir(current_dir)
