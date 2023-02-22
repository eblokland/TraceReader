import types
from dataclasses import dataclass
from configparser import ConfigParser

#helper data class so that I can get type hints :)
class ParserArgs:
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
        self.output_file = config.get('output_file')
        self.current_divider = config.getfloat('current_divider', 1e9)
