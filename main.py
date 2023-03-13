# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from parsers.environment_parser.EnvironmentParser import EnvironmentLog
from PerfParser import PerfParser
from parsers.parser_args import ParserArgs


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print('Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = ParserArgs('./config.ini')
    # parse environment samples
    environment_samples = EnvironmentLog(args.environment_log_file, args)
    outputfun = print

    if args.output_file:
        outfile = open(args.output_file, 'w')

        outputfun = lambda string: outfile.write(str(string) + '\n')

    # open report library using simpleperf log.
    perf_parser = PerfParser(environment_samples, args)
    perf_parser.get_data()

    functions = list(perf_parser.function_energies.values())
    functions.sort(key=lambda fun_addr: (fun_addr.energy.local_energy, fun_addr.energy.accumulated_energy),
                   reverse=True)

    for fun in functions:
        for name in fun.name_set:
            if 'land.erikblok' in name:
                outputfun(str(fun) + '\n')
                continue


    outputfun(perf_parser.energy)
    outputfun(perf_parser.time)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
