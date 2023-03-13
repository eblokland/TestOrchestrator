import time

from simpleperf_utils import AdbHelper

from adb_helpers.Intent import Intent, Actions


class CommandLineSampler(object):
    def __init__(self):
        self.adbhelper = AdbHelper(enable_switch_to_root=False)

    def send_intent(self, intent: Intent):
        return self.adbhelper.run(adb_args=['shell'] + intent.get_args(), log_output=True, log_stderr=True)

    def start_logcat_log(self):
        return self.send_intent(Intent(action=Actions.WRITELOGCAT))

    def stop_logcat_log(self):
        return self.send_intent(Intent(action=Actions.STOPLOGCAT))

    def start_file_log(self, outfilename='log.txt', devicefiledir='/mnt/sdcard/logs/'):
        filepath = 'file://' + devicefiledir + outfilename
        intent = Intent(action=Actions.WRITEFILE, uri=filepath)
        result = self.send_intent(intent)
        if result:
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

    def pull_file(self, outfilename='log.txt', filedir='/sdcard/logs/', localname='log.txt', localpath='./'):
        filepath = filedir + outfilename
        localpath = localpath + localname
        self.adbhelper.run(['pull', filepath, localpath])
