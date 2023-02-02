# This is a sample Python script.
import types

from utils import AdbHelper
from configparser import ConfigParser
from Intent import Intent, Actions, ExtraTypes, Extra
from app_profiler import AppProfiler
from environment_sampler import EnvironmentSampler
import time

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def simpleperfCmdBuilder(config: ConfigParser):
    newcfg = types.SimpleNamespace()
    str = ''
    cfg = config['SIMPLEPERF']
    #loc = cfg.get('simpleperfdevicelocation')
    #if loc is None:
    #    str += 'simpleperf'
    #else:
    #    str += loc
    #str += ' record '
    rawstr = cfg.get('raw')
    if rawstr is not None:
        return str + rawstr

    aut = cfg.get('aut')
    if aut is None:
        raise Exception('unknown aut, can\'t proceed')

    #str += ' --app ' + aut
    newcfg.app = aut

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
        newcfg.perf_data_path = outfile

    newcfg.record_options = str
    newcfg.disable_adb_root = True
    newcfg.native_lib_dir = None
    newcfg.compile_java_code = None
    newcfg.activity = None
    newcfg.test = None
    newcfg.log = 'info'
    newcfg.skip_collect_binaries = True
    return newcfg

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cfg = ConfigParser()
    cfg.read('config.ini')
    args = simpleperfCmdBuilder(cfg)
    #profiler = AppProfiler(args)
    #profiler.profile()
    samp = EnvironmentSampler(cfg)
    if not samp.check_installed():
        samp.install_pkg()
    if not samp.start_file_log():
        raise Exception('failed to start logger')
    time.sleep(10)
    samp.stop_file_log()
    samp.pull_log()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/




