import types
from configparser import ConfigParser
from app_profiler import AppProfiler
from samplers.environment_sampler import EnvironmentSampler
from device import *
from binary_cache_builder import BinaryCacheBuilder

from simpleperf_utils import AdbHelper

from simpleperf_helpers.simpleperf_command_builder import SimpleperfCommand


class InstrumentedTest(object):
    def __init__(self, testfun, cfgloc):
        self.testfun = testfun
        self.cfgloc = cfgloc
        self.cfg = ConfigParser()
        self.cfg.read(cfgloc)

    def runtest(self):
        command = SimpleperfCommand(self.cfg)
        args = command.build_simpleperf_obj()
        profiler = AppProfiler(args)
        profiler.prepare()
        samp = EnvironmentSampler(self.cfg)

        if not samp.check_installed():
            samp.install_pkg()
        if not samp.start_file_log():
            raise Exception('failed to start logger')

        adb = AdbHelper()

        print(adb.run_and_return_output(['shell', 'dumpsys', 'battery', '|', 'grep', '-i', 'charge']))
        profiler.start()
        self.testfun()
        print(adb.run_and_return_output(['shell', 'dumpsys', 'battery', '|', 'grep','-i', 'charge']))
        profiler.stop_profiling()
        samp.stop_file_log()
        profiler.collect_profiling_data()
        samp.pull_log()

        self._build_bincache(args.perf_data_path)

    def _build_bincache(self, perf_data_path, symfspaths=None):
        #binary cache doesn't support custom directories... just change pwd instead.
        current_dir = os.getcwd()
        conf = self.cfg['CONFIG']
        bin_cache_path = conf.get('binarycachepath')
        os.chdir(bin_cache_path)
        ndk_path = conf.get('ndkpath')
        disable_root = conf.getboolean('disable_root')
        if ndk_path == '':
            ndk_path = None
        bin_cache = BinaryCacheBuilder(ndk_path=ndk_path, disable_adb_root=disable_root)
        bin_cache.build_binary_cache(perf_data_path, symfspaths)
        os.chdir(current_dir)
