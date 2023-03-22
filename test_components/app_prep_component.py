from configparser import ConfigParser

from simpleperf_utils import AdbHelper

from config_strings import AUT, COMPILE, APK_LOC
from test_components.test_component import TestComponent
from adb_helpers.commands import *


class AppPrepComponent(TestComponent):
    def __init__(self, cfg_file):
        self._parse_cfg_file(cfg_file)

    def _parse_cfg_file(self, cfg_file: str):
        parser = ConfigParser()
        parser.read(cfg_file)
        cfg = parser['TEST_CONFIGURATION']
        self.aut = cfg.get(AUT)
        self.compile = cfg.get(COMPILE)
        self.apk = cfg.get(APK_LOC)
        self.adb = AdbHelper()

    def pre_test_fun(self):
        install_apk(file=self.apk, grant_perms=True, adb=self.adb)
        compile_package(pkg=self.aut, mode='speed', adb=self.adb)

    def post_test_fun(self):
        uninstall_package(pkg=self.aut, adb=self.adb)

    def test_fun(self):
        pass

    def shutdown_fun(self):
        pass
