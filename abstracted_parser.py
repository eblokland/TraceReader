from EnvironmentParser import EnvironmentLog
from parser_args import ParserArgs
from perf_data_parser import PerfDataParser
from single_threaded_analyzer import SingleThreadedAnalyzer
from function_csv_writer import write_csv

if __name__ == "__main__":
    args = ParserArgs('./config.ini')
    # parse environment samples
    environment_samples = EnvironmentLog(args.environment_log_file, args)
    perf_parser = PerfDataParser(environment_samples, args)
    states = perf_parser.parse()
    analyzer = SingleThreadedAnalyzer(states)
    analyzer.perform_analysis()
    funs = analyzer.get_sorted_fun_list(lambda f: (f.local_energy_cost), True)
    pass
    if args.output_file:
        write_csv(args.output_file, funs)
    else:
        for fun in funs:
            print(str(fun) + '\n')
