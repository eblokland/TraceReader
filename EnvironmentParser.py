from typing import IO
from entry import *
from operator import attrgetter


# standard compare: 0 if good, -1 if x < y, 1 if x > y
# if timestamp < position, return -1.
# if timestamp > position, return 1
def check_timestamp_position(timestamp, position, logs: list[Entry]):
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
def bin_search(begin, end, timestamp, logs: list[Entry]):
    # base case: we're out of options
    if begin == end:
        return logs[begin].data
    middle = begin + (int((end - begin) / 2))
    comp = check_timestamp_position(timestamp, middle, logs)
    if comp == 0:
        return logs[middle].data
    if comp == -1:
        return bin_search(begin, middle - 1, timestamp, logs)
    return bin_search(middle + 1, end, timestamp, logs)


class EnvironmentLog(object):
    def __init__(self, logfile, args: ParserArgs):
        if type(logfile) is str:
            logfile = open(logfile)
        lines = logfile.readlines()
        logs = map(lambda line: parse_line(line, args), lines)
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
        self.power_logs = list(filter(lambda log: isinstance(log, Power), self.logs))

    def print_logs(self, logs=None):
        if logs is None:
            logs = self.logs
        for log in logs:
            print(str(log))

    # binary search for timestamp
    def get_power_for_time(self, timestamp):
        return bin_search(0, len(self.power_logs) - 1, timestamp, self.power_logs)
