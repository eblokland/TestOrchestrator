import copy
import os
from configparser import ConfigParser
from functools import singledispatchmethod


class SimpleperfCommand(object):
    @singledispatchmethod
    def __init__(self, arg):
        raise ValueError(f"Unknown argument: {arg}")

    @__init__.register(str)
    def _init_from_string(self, string: str):
        if not os.path.isfile(string):
            # TODO: maybe try to parse the command from a string?
            raise ValueError('File not found, will not try to parse as command either')
        cfg = ConfigParser()
        cfg.read(string)
        self._init_from_cfg(self, cfg)

    @__init__.register(ConfigParser)
    def _init_from_cfg(self, cfg: ConfigParser):
        sp_conf = cfg['SIMPLEPERF']
        shared_conf = cfg['CONFIG']

        self.app = sp_conf.get('aut')
        self.events = sp_conf.get('events')
        self.freq = sp_conf.get('frequency')

        if self.app is None or self.events is None or self.freq is None:
            raise ValueError(f"Unable to find all required options!")

        self.duration = sp_conf.get('duration')
        self.do_callstack = sp_conf.getboolean('docallstack', fallback=False)
        # we may not have this option, provide a fallback to avoid value error
        self.use_dwarf = sp_conf.getboolean('usedwarf', fallback=False)

        outfile = sp_conf.get('simpleperfoutputpath')
        perf_file_name = shared_conf.get('outfilename')
        if outfile is not None and perf_file_name is not None:
            self.perf_data_path = outfile + perf_file_name + '.data'

        self.clock_id = sp_conf.get('clockid', fallback=None)
        self.trace_offcpu = sp_conf.getboolean('trace_offcpu', fallback=False)

        # TODO: support these options
        self.disable_adb_root = True
        self.native_lib_dir = None
        self.compile_java_code = None
        self.activity = None
        self.test = None
        self.log = 'info'
        self.skip_collect_binaries = True

    # clone this object into something that the google simpleperf library can use.
    # make a new one in case it does something to the object.
    def build_simpleperf_obj(self):
        newobj = copy.deepcopy(self)
        record_opts_string = ''
        if self.events is not None and self.events != '':
            record_opts_string += ' -e ' + self.events
        if self.duration is not None:
            record_opts_string += ' --duration ' + self.duration
        if self.freq is not None:
            record_opts_string += ' -f ' + self.freq
        if self.do_callstack:
            record_opts_string += ' --call-graph '
            if self.use_dwarf:
                record_opts_string += 'dwarf '
            else:
                record_opts_string += 'fp '
        if self.clock_id is not None:
            record_opts_string += ' --clockid ' + self.clock_id

        if self.trace_offcpu:
            record_opts_string += ' --trace-offcpu '
        newobj.record_options = record_opts_string
        return newobj
