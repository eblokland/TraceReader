from typing import List

from simpleperf_python_datatypes import CallChain


class AppSample(object):
    def __init__(self, traces: List[CallChain]):
        self.traces = traces


class EnvironmentState(object):
    def __init__(self):
        pass


class AppState(object):
    def __init__(self, timestamp, period, energy_consumed, sample: AppSample, env: EnvironmentState):
        self.sample = sample #appsample containing a stack trace (or multiple)
        self.timestamp = timestamp #timestamp in whatever clock was used
        self.energy_consumed = energy_consumed #amount of energy consumed by this sample in joules
        self.period = period #time to next State
        self.environment = env #TBA environment state

    def is_multithreaded(self):
        return len(self.sample.traces) > 1