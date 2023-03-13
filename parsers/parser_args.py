import types
from dataclasses import dataclass
from configparser import ConfigParser

class ParserArgs:
    """
    Parameter "struct" that contains all the args needed for this tool
    """
    def __init__(self, cfg_file):
        cfg = ConfigParser()
        cfg.read(cfg_file)
        config = cfg['CONFIG']
        self.ndk_dir = config.get('ndk_dir')
        self.environment_log_dir = config.get('environment_log_dir')
        self.simpleperf_log_dir = config.get('simpleperf_log_dir')
        self.shared_filename = config.get('shared_filename')
        self.environment_log_file = self.environment_log_dir + self.shared_filename + '.txt'
        self.simpleperf_log_file = self.simpleperf_log_dir + self.shared_filename + '.data'
        self.binary_cache = config.get('binary_cache_dir')
        self.source_dirs = config.get('source_dirs')
        self.trace_offcpu_mode = config.get('trace_offcpu_mode')
        self.source_dirs = config.get('source_dirs').split(';')
        self.output_csv = config.getboolean('output_csv')
        self.current_divider = config.getfloat('current_divider', 1e9)
        self.pickle_functions = config.getboolean('pickle_functions')
        self.output_dir = config.get('output_dir')
