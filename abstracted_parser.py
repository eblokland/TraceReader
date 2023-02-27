from EnvironmentParser import EnvironmentLog
from parser_args import ParserArgs
from perf_data_parser import PerfDataParser
from single_threaded_analyzer import SingleThreadedAnalyzer

if __name__ == "__main__":
    args = ParserArgs('./config.ini')
    # parse environment samples
    environment_samples = EnvironmentLog(args.environment_log_file, args)
    perf_parser = PerfDataParser(environment_samples, args)
    states = perf_parser.parse()
    analyzer = SingleThreadedAnalyzer(states)
    analyzer.perform_analysis()
    funs = analyzer.get_sorted_fun_list(lambda f: (f.local_energy_cost), True)

    outputfun = print

    if args.output_file:
        outfile = open(args.output_file, 'w')

        outputfun = lambda string: outfile.write(str(string) + '\n')

    for fun in funs:
        outputfun(str(fun) + '\n')
