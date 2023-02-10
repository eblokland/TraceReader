from typing import IO
from entry import *


class EnvironmentLog(object):
    def __init__(self, logfile):
        if type(logfile) is str:
            logfile = open(logfile)
        lines = logfile.readlines()
        logs = map(lambda line: parse_line(line), lines)
        lastvoltage = None
        lastcurrent = None
        def lam(log):
            nonlocal lastvoltage, lastcurrent
            if type(log) is Voltage:
                lastvoltage = log
                if lastcurrent is not None:
                    return Power(lastvoltage, lastcurrent)
                else:
                    return None
            elif type(log) is Current:
                lastcurrent = log
                if lastvoltage is not None:
                    return Power(lastvoltage, lastcurrent)
                else:
                    return None
            else:
                return log

        self.logs = list(filter(lambda log: log is not None, map(lam, logs)))

    def print_logs(self):
        for log in self.logs:
            print(str(log))
