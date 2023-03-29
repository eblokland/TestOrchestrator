import os
from configparser import ConfigParser
from typing import Optional

from simpleperf_helpers.app_profiler import AppProfiler
from binary_cache_builder import BinaryCacheBuilder

from simpleperf_helpers.simpleperf_command import SimpleperfCommand
from test_components.test_component import TestComponent


class SimpleperfComponent(TestComponent):
    def __init__(self, config_file: str):
        self.sp_cmd = SimpleperfCommand(config_file)
        self.sp_args = self.sp_cmd.build_simpleperf_obj()
        self._read_config(config_file)
        self.profiler = AppProfiler(self.sp_args)
        self.iteration = 1
        self.perf_data_path = self.sp_args.perf_data_path.removesuffix('.data')

    def _read_config(self, cfg_file: str):
        cfg = ConfigParser()
        cfg.read(cfg_file)
        conf = cfg['CONFIG']
        self.bin_cache_path = conf.get('binarycachepath')
        self.ndk_path = conf.get('ndkpath')
        self.disable_root = conf.getboolean('disable_root')
        self.device_serial = conf.get('adb_serial')
        self.out_file_name = conf.get('outfilename')
        sp_conf = cfg['SIMPLEPERF']
        self.output_dir = sp_conf.get('simpleperfoutputpath')

    def pre_test_fun(self):
        # this does some one-time setup, like copying the simpleperf bin
        # could also compile the AUT, but I want to do this separately.
        self.profiler.prepare()

    def loop_pre_test_fun(self):
        # dirty hack to set the file name to something unique.
        # good thing everything is public in python
        self.profiler.args.perf_data_path = self.perf_data_path + f'-{self.iteration}.data'

    def test_fun(self):
        self.profiler.kill_app_process()
        self.profiler.start()

    def shutdown_fun(self):
        lines = self.profiler.stop_profiling()
        file_path = self.output_dir + self.out_file_name + f'-{self.iteration}_logs.txt'

        with open(file=file_path, mode='w') as log_file:
            log_file.writelines(lines)

    def loop_post_test_fun(self):
        self.profiler.collect_profiling_data()

        # for now, do this here.  would be better to do it in
        # post_test_fun but then need to find all the different
        # files that were output.
        self._build_bincache(self.sp_args.perf_data_path)
        self.iteration += 1

    def post_test_fun(self):
        pass

    def _build_bincache(self, perf_data_path, symfspaths=None):
        # binary cache doesn't support custom directories... just change pwd instead.
        current_dir = os.getcwd()
        if not os.path.exists(self.bin_cache_path):
            os.mkdir(self.bin_cache_path)
        os.chdir(self.bin_cache_path)
        if self.ndk_path == '':
            self.ndk_path = None
        bin_cache = BinaryCacheBuilder(ndk_path=self.ndk_path, disable_adb_root=self.disable_root)
        bin_cache.build_binary_cache(perf_data_path, symfspaths)
        os.chdir(current_dir)
