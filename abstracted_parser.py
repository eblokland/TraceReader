import os
from copy import copy

from analysis.statistical_analysis import StatisticalAnalyzer
from parsers.parse_to_abstract import parse_to_abstract
from parsers.parser_args import ParserArgs
from analysis.single_threaded_analyzer import SingleThreadedAnalyzer
from analysis.function.function_csv_writer import write_csv
from trace_reader_utils.pickle_utils import gzip_pickle
import pickle
import gzip


def parse_single_trace(args: ParserArgs):
    (states, power_samples) = parse_to_abstract(args)
    analyzer = SingleThreadedAnalyzer(states)
    analyzer.perform_analysis()
    funs = analyzer.get_sorted_fun_list(lambda f: f.local_energy_cost, True)

    if args.pickle_functions:
        gzip_pickle(obj=analyzer.function_dict, file_name=args)
        gzip_pickle(obj=power_samples, file_name=f'{args.output_dir}{args.shared_filename}_power')
    if args.output_csv:
        write_csv(args, funs)


def parse_directory(args: ParserArgs):
    new_args = copy(args)
    directory = new_args.simpleperf_log_dir
    files = os.listdir(directory)
    for file in files:
        str_file = str(file)
        if str_file.endswith('.data'):
            shared_name = str_file.removesuffix('.data')
            new_args.shared_filename = shared_name
            if not os.path.exists(f'{new_args.environment_log_dir}{shared_name}.txt'):
                print(f'Warning, failed to find matching env log at {new_args.environment_log_dir}{shared_name}.txt ')
                continue
            parse_single_trace(new_args)


if __name__ == "__main__":
    pa = ParserArgs('./config.ini')
    if not os.path.exists(pa.output_dir):
        os.mkdir(pa.output_dir)
    parse_directory(pa) if pa.parse_dir else parse_single_trace(pa)
   #args = ParserArgs('./config.ini')
   # (states, power_samples) = parse_to_abstract(args)
   # analyzer = SingleThreadedAnalyzer(states)
   # analyzer.perform_analysis()
    #funs = analyzer.get_sorted_fun_list(lambda f: f.local_energy_cost, True)
    #if args.pickle_functions:
    #    pickle_file_name = args.output_dir + args.shared_filename + '.pickle.gz'
    #    with gzip.open(pickle_file_name, 'wb') as pickle_file:
    #        # pickle the dict so we keep the mapping to the function
    #        pickle.dump(analyzer.function_dict, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
    #    power_sample_file_name = args.output_dir + args.shared_filename + '_power'
    ##    gzip_pickle(power_samples, file_name=power_sample_file_name)
    #if args.output_csv:
    #    write_csv(args.output_dir + args.shared_filename + '.csv', funs)
