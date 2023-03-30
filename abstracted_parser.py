import os
from copy import copy
from typing import List, Dict

from analysis.function.function import Function
from analysis.function.function_csv_writer import write_csv
from analysis.single_threaded_analyzer import SingleThreadedAnalyzer
from parsers.parse_to_abstract import parse_to_abstract
from parsers.parser_args import ParserArgs
from trace_reader_utils.pickle_utils import gzip_pickle
from trace_representation.app_sample import AppState, PowerSample


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
        if not os.path.exists(f'{args.environment_log_dir}{shared_name}.txt'):
            print(f'Warning, failed to find matching env log at {args.environment_log_dir}{shared_name}.txt ')
            return False
        return True
    return False


def parse_and_merge(args: ParserArgs):
    if not args.merge_name:
        raise AttributeError(f'Need merged filename in args')

    new_args = copy(args)
    merged_list: List[AppState] = []
    merged_power_samples: List[PowerSample] = []
    files = os.listdir(args.simpleperf_log_dir)
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


def parse_directory(args: ParserArgs):
    new_args = copy(args)
    directory = new_args.simpleperf_log_dir
    files = os.listdir(directory)
    for file in filter(lambda f: _filter_valid_files(args, f), files):
        new_args.shared_filename = str(file).removesuffix('.data')
        parse_single_trace(new_args)


if __name__ == "__main__":
    pa = ParserArgs('./config.ini')
    if not os.path.exists(pa.output_dir):
        os.mkdir(pa.output_dir)
    if 'merge' in pa.mode:
        parse_and_merge(pa)
    elif 'directory' in pa.mode:
        parse_directory(pa)
    elif 'single' in pa.mode:
        parse_single_trace(pa)
    else:
        print(f'unknown mode string {pa.mode}')
