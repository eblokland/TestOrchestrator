"""
intent.py: Helper functions to create Intents for am start-server
"""
from enum import Enum, auto
from typing import List

from simpleperf_utils import AdbHelper


class Actions(Enum):
    WRITEFILE = "land.erikblok.action.WRITETOFILE"
    WRITELOGCAT = "land.erikblok.action.WRITETOLOGCAT"
    KEEPALIVE = "land.erikblok.action.NOWRITE"
    STOPFILE = "land.erikblok.action.STOPFILE"
    STOPLOGCAT = "land.erikblok.action.STOPLOGCAT"
    NOKEEPALIVE = "land.erikblok.action.NOKEEPALIVE"

    STOPRANDOM = "land.erikblok.action.STOP_RANDOM"
    STARTRANDOM = "land.erikblok.action.START_RANDOM"
    STARTBUSY = "land.erikblok.action.START_BUSY"
    STOPBUSY = "land.erikblok.action.STOP_BUSY"


# not sure why this triggers, by docs it should not...
# noinspection PyArgumentList
class ExtraTypes(Enum):
    INT = auto()
    FLOAT = auto()
    LONG = auto()
    BOOL = auto()


class Extra(object):
    def __init__(self, extra_type, key, value):
        if extra_type == ExtraTypes.BOOL:
            self.type = '--ez'
        elif extra_type == ExtraTypes.FLOAT:
            self.type = '--ef'
        elif extra_type == ExtraTypes.LONG:
            self.type = '--el'
        elif extra_type == ExtraTypes.INT:
            self.type = '--ei'
        else:
            raise Exception("Invalid type for extra")
        self.value = value
        self.key = key

    def get_str(self):
        return self.type + ' ' + str(self.key) + ' ' + str(self.value)


class Intent(object):
    def __init__(self, activity='land.erikblok.infosamplerservice/.EnvironmentSampler', action=None, uri=None,
                 extras: List[Extra] = None):
        if extras is None:
            extras = []
        self.activity = activity
        if action is None:
            self.action = action
        elif isinstance(action, Actions):
            self.action = action.value
        else:
            raise ValueError('invalid input for action')
        self.uri = uri
        self.extras = extras

    def add_extras(self, extras: List[Extra]):
        for extra in extras:
            self.add_extra(extra)

    def add_extra(self, extra: Extra):
        if isinstance(extra, Extra):
            self.extras += extra
        else:
            raise Exception('argument not extra')

    def set_action(self, action: Actions):
        if not isinstance(action, Actions):
            raise Exception('invalid action')
        self.action = action.value

    def set_activity(self, activity):
        self.activity = activity

    def get_cmd_str(self):
        cmd_str = 'am start-foreground-service'
        if self.action:
            cmd_str += ' '
            cmd_str += '-a "' + self.action + '"'
        if self.uri:
            cmd_str += ' '
            cmd_str += '-d "' + self.uri + '"'
        if self.extras:
            for e in self.extras:
                if isinstance(e, Extra):
                    cmd_str += ' '
                    cmd_str += e.get_str()
        cmd_str += ' "'
        cmd_str += self.activity + '"'
        return cmd_str

    def get_args(self):
        return self.get_cmd_str().split()

    def send_intent(self, adb: AdbHelper = None):
        if adb is None:
            adb = AdbHelper()
        return adb.run(adb_args=['shell'] + self.get_args(), log_output=True, log_stderr=True)
