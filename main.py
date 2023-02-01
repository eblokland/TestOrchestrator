# This is a sample Python script.
from utils import AdbHelper
from configparser import ConfigParser
from Intent import Intent, Actions, ExtraTypes, Extra

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def simpleperfCmdBuilder(config: ConfigParser):
    str = ''
    cfg = config['SIMPLEPERF']
    loc = cfg.get('simpleperfdevicelocation')
    if loc is None:
        str += 'simpleperf'
    else:
        str += loc
    str += ' record '
    rawstr = cfg.get('raw')
    if rawstr is not None:
        return str + rawstr

    aut = cfg.get('aut')
    if aut is None:
        raise Exception('unknown aut, can\'t proceed')

    str += ' --app ' + aut

    events = cfg.get('events')
    if events is not None and events != '':
        str += ' -e ' + events

    duration = cfg.get('duration')
    if duration is not None:
        str += ' --duration ' + duration

    freq = cfg.get('frequency')
    if freq is not None:
        str += ' -f ' + freq


    doCallstack = cfg.getboolean('docallstack')
    if doCallstack is not None and doCallstack:
        str += ' --call-graph '
        dwarf = cfg.getboolean('usedwarf')
        if dwarf is not None and dwarf:
            str += 'dwarf '
        else:
            str += 'fp '

    outfile = cfg.get('simpleperfoutputpath')
    if outfile is not None:
        str += ' -o ' + outfile

    return str

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('config.ini')
    print(simpleperfCmdBuilder(cfg))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/




