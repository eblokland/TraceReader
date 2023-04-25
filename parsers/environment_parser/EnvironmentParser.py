from functools import singledispatchmethod
from typing import List, Union

from parsers.environment_parser.entry import *
from operator import attrgetter

# standard compare: 0 if good, -1 if x < y, 1 if x > y
# if timestamp < position, return -1.
# if timestamp > position, return 1
from trace_representation.time_unit import TimeUnit


def check_timestamp_position(timestamp: TimeUnit, position, logs: list[Entry]):
    power = logs[position]
    compare = power.compare_timestamp(timestamp)

    # this will never happen but it'd be nice
    if compare == 0:
        return 0

    # current position time is greater than target time
    if compare == -1:
        # for now, return 0 if we're already at the start of the array.  maybe in future we should discard this
        # sample?
        if position <= 0:
            return 0
        # return that timestamp is less than current position
        return -1

    # from here on: current position is less than target time

    # we don't have any more logs, so return good.
    if position >= len(logs) - 1:
        return 0
    # the next log is from the future, so this is the best one.
    if logs[position + 1].timestamp > timestamp:
        return 0
    # the next log must be from before our timestamp, return that target > position
    return 1


# binary search the log list for the timestamp occurring closest to the given timestamp, but not in the future.
def bin_search(begin, end, timestamp: TimeUnit, logs: list[Power]) -> Power:
    # base case: we're out of options
    if begin == end:
        return logs[begin]
    middle = begin + (int((end - begin) / 2))
    comp = check_timestamp_position(timestamp, middle, logs)
    if comp == 0:
        return logs[middle]
    if comp == -1:
        return bin_search(begin, middle - 1, timestamp, logs)
    return bin_search(middle + 1, end, timestamp, logs)


class EnvironmentLog(object):
    @singledispatchmethod
    def __init__(self, arg):
        raise TypeError(f'Unsupported init arg type {type(arg)}')

    @__init__.register
    def _init_with_parserargs(self, args: ParserArgs):
        self._init_with_args(args.get_env_log_file(), args.current_divider)

    @__init__.register
    def _init_with_args(self, env_log: str, current_divider: Union[float, int]):
        logfile = open(env_log)
        lines = logfile.readlines()
        logs = map(lambda line: parse_line(line, current_divider), lines)
        self.raw_logs = list(logs)
        lastvoltage = None
        lastcurrent = None

        def lam(log):
            nonlocal lastvoltage, lastcurrent
            if isinstance(log, Voltage):
                if isinstance(lastvoltage, Voltage) and log.timestamp < lastvoltage.timestamp:
                    raise AssertionError('out of order processing of logs, not good')
                lastvoltage = log
                if isinstance(lastcurrent, Current):
                    return Power(lastvoltage, lastcurrent)
                else:
                    return None
            elif isinstance(log, Current):
                if isinstance(lastcurrent, Current) and log.timestamp < lastcurrent.timestamp:
                    raise AssertionError('out of order processing of logs')
                lastcurrent = log
                if isinstance(lastvoltage, Voltage):
                    return Power(lastvoltage, lastcurrent)
                else:
                    return None
            else:
                return log

        self.logs = list(filter(lambda log: log is not None, map(lam, self.raw_logs)))
        self.logs.sort(key=attrgetter('timestamp'))
        self.power_logs: List[Power] = list(filter(lambda log: isinstance(log, Power), self.logs))


    def print_logs(self, logs=None):
        if logs is None:
            logs = self.logs
        for log in logs:
            print(str(log))

    # binary search for timestamp
    def get_power_for_time(self, timestamp: TimeUnit) -> Power:
        return bin_search(0, len(self.power_logs) - 1, timestamp, self.power_logs)

    def get_power_average(self) -> float:
        """
        Get the average power draw over the whole environment log.
        :return: average power draw in Watts
        """
        start_time: TimeUnit = self.power_logs[0].timestamp
        end_time: TimeUnit = self.power_logs[-1].timestamp
        total_time: TimeUnit = end_time - start_time

        consumed_joules: float = 0
        for index, power in enumerate(self.power_logs[0:-1]):
            period: TimeUnit = self.power_logs[index + 1].timestamp - power.timestamp
            consumed_joules += power.data * float(period.to_seconds())

        avg_power = consumed_joules / float(total_time.to_seconds())
        return avg_power
