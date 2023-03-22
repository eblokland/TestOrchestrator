import os
from configparser import ConfigParser

from app_profiler import AppProfiler
from binary_cache_builder import BinaryCacheBuilder

from simpleperf_helpers.simpleperf_command import SimpleperfCommand
from test_components.test_component import TestComponent


class SimpleperfComponent(TestComponent):
    def __init__(self, config_file: str):
        self.sp_args = SimpleperfCommand(config_file)
        self.profiler = AppProfiler(self.sp_args)
        self._read_config(config_file)

    def _read_config(self, cfg_file: str):
        cfg = ConfigParser()
        cfg.read(cfg_file)
        conf = cfg['CONFIG']
        self.bin_cache_path = conf.get('binarycachepath')
        self.ndk_path = conf.get('ndkpath')
        self.disable_root = conf.getboolean('disable_root')
        self.device_serial = conf.get('adb_serial')

    def pre_test_fun(self):
        self.profiler.prepare()
        self.profiler.kill_app_process()

    def post_test_fun(self):
        self.profiler.collect_profiling_data()


    def test_fun(self):
        self.profiler.kill_app_process()
        self.profiler.start()

    def shutdown_fun(self):
        self.profiler.stop_profiling()
        self._build_bincache(self.sp_args.perf_data_path)

    def _build_bincache(self, perf_data_path, symfspaths=None):
        # binary cache doesn't support custom directories... just change pwd instead.
        current_dir = os.getcwd()
        os.chdir(self.bin_cache_path)
        if self.ndk_path == '':
            self.ndk_path = None
        bin_cache = BinaryCacheBuilder(ndk_path=self.ndk_path, disable_adb_root=self.disable_root)
        bin_cache.build_binary_cache(perf_data_path, symfspaths)
        os.chdir(current_dir)
