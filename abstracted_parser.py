from parsers.environment_parser.EnvironmentParser import EnvironmentLog
from parsers.parser_args import ParserArgs
from parsers.perf_parser.perf_data_parser import PerfDataParser
from Analysis.single_threaded_analyzer import SingleThreadedAnalyzer
from Analysis.function.function_csv_writer import write_csv
import pickle
import gzip




if __name__ == "__main__":
    args = ParserArgs('./config.ini')
    # parse environment samples
    environment_samples = EnvironmentLog(args.environment_log_file, args)
    perf_parser = PerfDataParser(environment_samples, args)
    states = perf_parser.parse()
    analyzer = SingleThreadedAnalyzer(states)
    analyzer.perform_analysis()
    funs = analyzer.get_sorted_fun_list(lambda f: (f.local_energy_cost), True)
    if args.pickle_functions:
        pickle_file_name = args.output_dir + args.shared_filename + '.pickle.gz'
        with gzip.open(pickle_file_name, 'wb') as pickle_file:
            #pickle the dict so we keep the mapping to the function
            pickle.dump(analyzer.function_dict, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)
    if args.output_csv:
        write_csv(args.output_dir + args.shared_filename + '.csv', funs)
    #else:
     #   for fun in funs:
      #      print(str(fun) + '\n')
