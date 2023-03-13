import os
from configparser import ConfigParser

from simpleperf_utils import AdbHelper
from adb_helpers.Intent import Intent, Actions
import time

class EnvironmentSampler(object):
    def __init__(self, cfg: ConfigParser):
        self.adbhelper = AdbHelper(enable_switch_to_root=False)
        config = cfg['CONFIG']
        samplercfg = cfg['SAMPLER']
        self.apkloc = samplercfg.get('samplerapkloc')
        self.samplerpkg = samplercfg.get('samplerpkg')
        self.wait_timer = samplercfg.getfloat('samplerwaittimer')
        self.reinstall = samplercfg.getboolean('reinstall')
        self.devicefiledir = samplercfg.get('devicefiledir')
        self.shellfiledir = samplercfg.get('shellfiledir')
        self.outfilename = config.get('outfilename')
        self.localpath = samplercfg.get('samplerlogoutputpath')
        self.use_runas = samplercfg.getboolean('use_runas')

    def check_installed(self):
        output = self.adbhelper.run_and_return_output(adb_args=['shell', 'pm', 'list', 'packages', '-3'],
                                                      log_output=True)
        if not self.samplerpkg:
            raise Exception('sampler app package unknown')
        return self.samplerpkg in output[1]

    def install_pkg(self):
        if not self.apkloc:
            raise Exception('sampler app location unknown')
        if not os.path.isfile(self.apkloc):
            raise FileNotFoundError('didn\'t find apk')
        adb_cmd = ['install', '-g', self.apkloc]
        return self.adbhelper.run(adb_cmd)

    def send_intent(self, intent: Intent):
        return self.adbhelper.run(adb_args=['shell'] + intent.get_args())

    def start_file_log(self):
        filepath = 'file://' + self.devicefiledir + self.outfilename + '.txt'
        intent = Intent(action=Actions.WRITEFILE, uri=filepath)
        result = self.send_intent(intent)
        if result:
            time.sleep(self.wait_timer)
            return True
        else:
            return False

    def stop_file_log(self):
        intent = Intent(action=Actions.STOPFILE)
        if self.send_intent(intent):
            # let's sleep here to give it some time to flush the filewriter :)
            time.sleep(0.5)
            return True
        else:
            return False

    def start_logcat_log(self):
        return self.send_intent(Intent(action=Actions.WRITELOGCAT))

    def stop_logcat_log(self):
        return self.send_intent(Intent(action=Actions.STOPLOGCAT))

    def get_device_path(self):
        return self.shellfiledir + self.outfilename + '.txt'

    def get_local_path(self):
        return self.localpath + self.outfilename + '.txt'

    def pull_log(self, log_things: bool = False):
        def run_as():
            args = ['shell', 'run-as', self.samplerpkg, 'cat', self.devicefiledir + self.outfilename + '.txt']
            (status, out_str) = self.adbhelper.run_and_return_output(adb_args=args, log_output=log_things, log_stderr=log_things)
            if status:
                with open(self.get_local_path(), mode="w") as file:
                    file.write(out_str.strip())
            return status

        if self.use_runas:
            status = run_as()
        else:
            #we will attempt to try this normally first.
            #if that fails, fall back to a run-as thing.
            #may need to later fix the device path on run-as
            #to default to something that's not devicefiledir.
            args = ['pull', self.get_device_path(), self.get_local_path()]
            status = self.adbhelper.run(adb_args=args, log_output=log_things, log_stderr=log_things)
            if not status:
                status = run_as()

        return status
