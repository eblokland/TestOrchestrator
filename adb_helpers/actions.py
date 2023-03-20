from enum import Enum


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
    STOP_WORKER = "land.erikblok.action.STOP_WORKER"
    START_MIM = "land.erikblok.action.START_MIM"
    START_IS = "land.erikblok.action.START_IS"
    START_FORLOOP = "land.erikblok.action.START_FORLOOP"
