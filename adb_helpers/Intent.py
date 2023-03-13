"""
Intent.py: Helper functions to create Intents for am start-server
"""
from enum import Enum, auto

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


class ExtraTypes(Enum):
    INT = auto()
    FLOAT = auto()
    LONG = auto()
    BOOL = auto()


class Extra(object):
    def __init__(self, type, key, value):
        if type == ExtraTypes.BOOL:
            self.type = '--ez'
        elif type == ExtraTypes.FLOAT:
            self.type = '--ef'
        elif type == ExtraTypes.LONG:
            self.type = '--el'
        elif type == ExtraTypes.INT:
            self.type = '--ei'
        else:
            raise Exception("Invalid type for extra")
        self.value = value
        self.key = key

    def getStr(self):
        return self.type + ' ' + str(self.key) + ' ' + str(self.value)


class Intent(object):
    def __init__(self, activity='land.erikblok.infosamplerservice/.EnvironmentSampler', action=None, uri=None,
                 extras=None):
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

    def addExtra(self, extra):
        if isinstance(extra, Extra):
            self.extras += extra
        else:
            raise Exception('argument not extra')

    def setAction(self, action):
        if not isinstance(action, Actions):
            raise Exception('invalid action')
        self.action = action.value

    def setActivity(self, activity):
        self.activity = activity

    def getCmdStr(self):
        str = 'am start-foreground-service'
        if self.action:
            str += ' '
            str += '-a "' + self.action + '"'
        if self.uri:
            str += ' '
            str += '-d "' + self.uri + '"'
        if self.extras:
            for e in self.extras:
                if isinstance(e, Extra):
                    str += ' '
                    str += e.getStr()
        str += ' "'
        str += self.activity + '"'
        return str

    def getArgs(self):
        return self.getCmdStr().split()

    def send_intent(self, adb: AdbHelper):
        return adb.run(adb_args=['shell'] + self.getArgs(), log_output=True, log_stderr=True)
