from configparser import ConfigParser

from simpleperf_utils import AdbHelper

from config_strings import AUT, COMPILE, APK_LOC, INSTALL_PKG
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
        self.install_pkg = cfg.getboolean(INSTALL_PKG)
        self.compile = cfg.getboolean(COMPILE)
        self.apk = cfg.get(APK_LOC)
        self.adb = AdbHelper()

    def pre_test_fun(self):
        if self.install_pkg:
            install_apk(file=self.apk, grant_perms=True, adb=self.adb)
        if self.compile:
            compile_package(pkg=self.aut, mode='speed', adb=self.adb)

    def post_test_fun(self):
        if self.install_pkg:
            uninstall_package(pkg=self.aut, adb=self.adb)

    def test_fun(self):
        pass

    def shutdown_fun(self):
        pass
