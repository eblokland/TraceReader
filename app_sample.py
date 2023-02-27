from typing import List

from simpleperf_python_datatypes import CallChain, Symbol


class ThreadSample(object):
    def __init__(self, symbol: Symbol, trace: CallChain):
        self.symbol: Symbol = symbol
        self.trace: CallChain = trace

    def __str__(self):
        return str(self.symbol)

class AppSample(object):
    def __init__(self, samples: List[ThreadSample]):
        self.samples = samples

    def get_first_sample(self) -> ThreadSample:
        return self.samples[0]


class EnvironmentState(object):
    def __init__(self):
        pass


class AppState(object):
    def __init__(self, timestamp, period, energy_consumed, sample: AppSample, env: EnvironmentState, power):
        self.sample: AppSample = sample #appsample containing a stack trace (or multiple)
        self.timestamp = timestamp #timestamp in whatever clock was used
        self.energy_consumed = energy_consumed #amount of energy consumed by this sample in joules
        self.period = period #time to next State
        self.power = power
        self.environment = env #TBA environment state

    def is_multithreaded(self):
        return len(self.sample.traces) > 1