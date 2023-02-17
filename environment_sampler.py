import os
from configparser import ConfigParser

from simpleperf_utils import AdbHelper
from Intent import Intent, Actions
import time


class CommandLineSampler(object):
    def __init__(self):
        self.adbhelper = AdbHelper(enable_switch_to_root=False)

    def send_intent(self, intent: Intent):
        return self.adbhelper.run(adb_args=['shell'] + intent.getArgs(), log_output=True, log_stderr=True)

    def start_logcat_log(self):
        return self.send_intent(Intent(action=Actions.WRITELOGCAT))

    def stop_logcat_log(self):
        return self.send_intent(Intent(action=Actions.STOPLOGCAT))

    def start_file_log(self,outfilename='log.txt', devicefiledir='/mnt/sdcard/logs/'):
        filepath = 'file://'+devicefiledir + outfilename
        intent = Intent(action=Actions.WRITEFILE, uri=filepath)
        result = self.send_intent(intent)
        if result:
            return True
        else:
            return False

    def stop_file_log(self):
        intent = Intent(action=Actions.STOPFILE)
        if self.send_intent(intent):
            #let's sleep here to give it some time to flush the filewriter :)
            time.sleep(0.5)
            return True
        else:
            return False

    def pull_file(self, outfilename='log.txt', filedir='/sdcard/logs/', localname='log.txt', localpath='./'):
        filepath = filedir + outfilename
        localpath = localpath + localname
        self.adbhelper.run(['pull', filepath, localpath])


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
        return self.adbhelper.run(adb_args=['shell']+intent.getArgs())

    def start_file_log(self):
        filepath = 'file://'+self.devicefiledir + self.outfilename + '.txt'
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
            #let's sleep here to give it some time to flush the filewriter :)
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

    def pull_log(self):
        args = ['pull', self.get_device_path(), self.get_local_path()]
        return self.adbhelper.run(adb_args=args)