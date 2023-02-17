# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import types

from EnvironmentParser import EnvironmentLog
from PerfParser import PerfParser
from entry import *
from configparser import ConfigParser
from simpleperf_report_lib import ReportLib
from parser_args import ParserArgs


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print('Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = ParserArgs('./config.ini')
    # parse environment samples
    environment_samples = EnvironmentLog(args.environment_log_file)

    # open report library using simpleperf log.
    perf_parser = PerfParser(environment_samples, args)
    perf_parser.get_data()

    functions = list(perf_parser.function_energies.values())
    functions.sort(key=lambda fun_addr: (fun_addr.energy.local_energy, fun_addr.energy.accumulated_energy), reverse=False)


    for fun in functions:
        for name in fun.name_set:
            if 'land.erikblok' in name:
                print(str(fun) + '\n')
                continue

   # for i in range(0, 20):
    #    print(str(functions[i]) + '\n')

    print(perf_parser.energy)
    print(perf_parser.time)

    pass

    # log.print_logs(log.power_logs)
    # filteredlogs = list(filter(lambda l: isinstance(l, Current), log.raw_logs))
    # log.print_logs(filteredlogs)
    # for i in range(1, len(log.power_logs)):
    #   print(str(log.power_logs[i].time_between(log.power_logs[i-1])) + '  power: ' + str(log.power_logs[i].data))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
