from typing import List

from trace_representation.simpleperf_python_datatypes import CallChain, Symbol


class ThreadSample(object):
    """
    Sample of a single thread, with a Symbol and Callchain
    """
    def __init__(self, symbol: Symbol, trace: CallChain):
        self.symbol: Symbol = symbol
        self.trace: CallChain = trace

    def __str__(self):
        return str(self.symbol)

class AppSample(object):
    """
    Class that contains a list of ThreadSamples, corresponding to all the threads running during the sample.
    """
    def __init__(self, samples: List[ThreadSample]):
        self.samples = samples

    def get_first_sample(self) -> ThreadSample:
        return self.samples[0]


class EnvironmentState(object):
    def __init__(self):
        pass


class AppState(object):
    def __init__(self, timestamp, period, energy_consumed, sample: AppSample, env: EnvironmentState, power):
        """
        :param timestamp: raw timestamp in whatever clock was specified
        :param period: time until next AppState
        :param energy_consumed: amount of energy consumed by this sample in joules
        :param sample: AppSample containing a stack trace (or possible multiple)
        :param env: TODO environment store
        :param power: Power being used at this time
        """
        self.sample: AppSample = sample
        self.timestamp = timestamp
        self.energy_consumed = energy_consumed
        self.period = period
        self.power = power
        self.environment = env

   # def is_multithreaded(self):
    #    return len(self.sample.traces) > 1