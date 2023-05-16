import argparse
from configparser import ConfigParser
from functools import singledispatchmethod


class ParserArgs:
    """
    Parameter "struct" that contains all the args needed for this tool
    """

    def __init__(self, **kwargs):
        if 'cfg_file' in kwargs:
            self._init_from_cfg(kwargs['cfg_file'])
        elif 'argv' in kwargs:
            self._init_from_argv(kwargs['argv'])
        else:
            raise NotImplementedError('didn\'t implement base kwargs yet')


    def _init_from_argv(self, argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-n', '--ndk_dir', type=str, required=True)
        parser.add_argument('-m', '--mode', type=str, default='single', choices=['single', 'directory', 'merge'])
        parser.add_argument('--filter_dupes', action='store_true')
        parser.add_argument('-i', '--input_dir', type=str, default='./')
        parser.add_argument('--shared_filename', type=str)
        parser.add_argument('--binary_cache_dir', type=str)
        parser.add_argument('--trace_offcpu_mode', type=str, default='on-cpu')
        parser.add_argument('--no_output_csv', action='store_false')
        parser.add_argument('--no_pickle_functions', action='store_false')
        parser.add_argument('-o','--output_dir', type=str, required=True)
        parser.add_argument('-c', '--current_divider', type=float, default=1e9)

        parser.parse_args(args=argv, namespace=self)
        self.source_dirs = []


    def _init_from_cfg(self, cfg_file):
        cfg = ConfigParser()
        cfg.read(cfg_file)
        config = cfg['CONFIG']
        self.ndk_dir = config.get('ndk_dir')
        #self.parse_dir = config.getboolean('parse_full_dir')
        self.merge_name = config.get('merge_name')
        self.mode = config.get('mode')
        self.environment_log_dir = config.get('environment_log_dir')
        self.filter_dupes = config.getboolean('filter_dupes', True)
        self.simpleperf_log_dir = config.get('simpleperf_log_dir')
        self.shared_filename = config.get('shared_filename')
        self.binary_cache = config.get('binary_cache_dir')
        self.source_dirs = config.get('source_dirs')
        self.trace_offcpu_mode = config.get('trace_offcpu_mode')
        self.source_dirs = config.get('source_dirs').split(';')
        self.output_csv = config.getboolean('output_csv')
        self.current_divider = config.getfloat('current_divider', 1e9)
        self.pickle_functions = config.getboolean('pickle_functions')
        self.output_dir = config.get('output_dir')
        self.shared_dir = config.get('shared_dir')

    def get_env_log_file(self):
        return f'{self.env_dir()}{self.shared_filename}.txt'

    def get_simpleperf_log_file(self):
        return f'{self.log_dir()}{self.shared_filename}.data'

    def env_dir(self):
        return self.shared_dir if self.shared_dir else self.environment_log_dir

    def log_dir(self):
        return self.shared_dir if self.shared_dir else self.simpleperf_log_dir
