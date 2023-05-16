import os
import sys
from copy import copy, deepcopy
from typing import List, Dict

from analysis.function.function import Function
from analysis.function.function_csv_writer import write_csv
from analysis.single_threaded_analyzer import SingleThreadedAnalyzer
from parsers.parse_to_abstract import parse_to_abstract
from parsers.parser_args import ParserArgs
from trace_reader_utils.pickle_utils import gzip_pickle
from trace_representation.app_sample import AppState, PowerSample

from multiprocessing import Pool


def parse_single_trace(args: ParserArgs):
    (states, power_samples) = parse_to_abstract(args)

    funs = analyze_state_list(args, states)

    output_filepath = args.output_dir + args.shared_filename
    if args.pickle_functions:
        pickle_results(funs, power_samples, output_filepath)
    if args.output_csv:
        fun_list = sorted(list(funs.values()), key=(lambda f: f.local_energy_cost), reverse=True)
        write_csv(output_filepath, fun_list)


def analyze_state_list(args: ParserArgs, states: List[AppState]) -> Dict[int, Function]:
    analyzer = SingleThreadedAnalyzer(states, filter_dupes=args.filter_dupes)
    analyzer.perform_analysis()
    return analyzer.function_dict


def pickle_results(function_dict, power_samples, shared_file_name):
    gzip_pickle(obj=function_dict, file_name=shared_file_name)
    gzip_pickle(obj=power_samples, file_name=f'{shared_file_name}_power')


def _filter_valid_files(args: ParserArgs, filename):
    str_file = str(filename)
    if str_file.endswith('.data'):
        shared_name = str_file.removesuffix('.data')
        if not os.path.exists(f'{args.env_dir()}{shared_name}.txt'):
            print(f'Warning, failed to find matching env log at {args.env_dir()}{shared_name}.txt ')
            return False
        return True
    return False


def parse_and_merge(args: ParserArgs):
    if not args.merge_name:
        raise AttributeError(f'Need merged filename in args')

    new_args = copy(args)
    merged_list: List[AppState] = []
    merged_power_samples: List[PowerSample] = []
    files = os.listdir(args.log_dir())
    for file in filter(lambda f: _filter_valid_files(args, f), files):
        new_args.shared_filename = str(file).removesuffix('.data')
        (states, power_samples) = parse_to_abstract(new_args)
        merged_list += states
        merged_power_samples += power_samples

    funs = analyze_state_list(args, merged_list)
    output_filepath = args.output_dir + args.merge_name
    if args.pickle_functions:
        pickle_results(funs, merged_power_samples, output_filepath)
    if args.output_csv:
        fun_list = sorted(list(funs.values()), key=(lambda f: f.local_energy_cost), reverse=True)
        write_csv(output_filepath, fun_list)

def recursive_parse_directory(args: ParserArgs):

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    if not args.shared_dir:
        raise NotImplementedError
    #enforce use of shared_dir here since it's recursively looking anyway

    items = os.listdir(args.shared_dir)
    directories = [file for file in items if os.path.isdir(f'{args.shared_dir}/{file}')]
    files = [x for x in items if os.path.isfile(f'{args.shared_dir}/{x}')]
    if len(files) > 0:
        parse_directory(args, files=files)

    for dir in directories:
        newargs = deepcopy(args)
        newargs.shared_dir = f'{newargs.shared_dir}/{dir}/'
        newargs.output_dir = f'{newargs.output_dir}/{dir}/'
        recursive_parse_directory(newargs)


def parse_directory(args: ParserArgs, files: List[str] = None):
    if files is None:
        files = os.listdir(args.log_dir())

    def get_args_for_file(file: str, old_args: ParserArgs):
        file_args = deepcopy(old_args)
        file_args.shared_filename = str(file).removesuffix('.data')
        return file_args

    with Pool() as p:
        filtered_args = [(get_args_for_file(file, args)) for file in files if _filter_valid_files(args, file)]
        p.map(parse_single_trace, filtered_args)


if __name__ == "__main__":
    args = sys.argv
    pa = None
    if arlen := len(args) == 2:
        config_loc = str(args[1])
        pa = ParserArgs(cfg_file=config_loc)
    elif arlen == 1:
        config_loc = './config.ini'
        pa = ParserArgs(cfg_file=config_loc)
    else:
        pa = ParserArgs(argv=sys.argv)

    if not os.path.exists(pa.output_dir):
        os.mkdir(pa.output_dir)
    if 'merge' in pa.mode:
        parse_and_merge(pa)
    elif 'directory' in pa.mode:
        parse_directory(pa)
    elif 'single' in pa.mode:
        parse_single_trace(pa)
    elif 'recursive' in pa.mode:
        recursive_parse_directory(pa)
    else:
        print(f'unknown mode string {pa.mode}')
