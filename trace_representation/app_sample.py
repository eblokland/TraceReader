from typing import List, Union, Set, Optional

from trace_representation.simpleperf_python_datatypes import CallChain, Symbol
from trace_representation.time_unit import TimeUnit


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


class PowerSample(object):
    """
    Class that can be used as a reference to a power sample. This way, it is known from the AppState whether
    or not the power sample was different than another AppState
    """

    def __init__(self, power: float, timestamp: TimeUnit):
        self.power = power
        self.timestamp = timestamp

    #def __eq__(self, other):
     #   if not isinstance(other, PowerSample):
      #      return False
       # return self.timestamp == other.timestamp



class PowerPeriod(object):
    """
    Accumulates the power used by samples of a function.  not useful without knowing the amount of time it ran for.
    """

    def __init__(self, local_power: Optional[PowerSample] = None, nonlocal_power: Optional[PowerSample] = None):
        """
        :param local_power:  power used by this function in *local* code
        :param nonlocal_power: power used by this function in *non-local* code
        """
        self.local_power: float = local_power.power if local_power is not None else 0.0
        self.nonlocal_power: float = nonlocal_power.power if nonlocal_power is not None else 0.0
        # if local_power is 0, then this wasn't a local sample.
        # don't add it to the list.
        self.local_power_set: Set[PowerSample] = {local_power} if local_power is not None else set()
        self.nonlocal_power_set: Set[PowerSample] = {nonlocal_power} if nonlocal_power is not None else set()

    def __iadd__(self, other):
        if not isinstance(other, PowerPeriod):
            raise TypeError("Incorrect type provided, not a PowerPeriod")
        self.local_power += other.local_power
        self.nonlocal_power += other.nonlocal_power

        self.local_power_set.update(other.local_power_set)
        self.nonlocal_power_set.update(other.nonlocal_power_set)

        return self

    def get_combined_power_set(self) -> Set[PowerSample]:
        return self.local_power_set.union(self.nonlocal_power_set)


class AppState(object):
    def __init__(self, timestamp: TimeUnit, period: TimeUnit, energy_consumed, sample: AppSample, env: EnvironmentState,
                 power: Union[PowerSample, None] = None):
        """
        :param timestamp: timestamp in whatever clock was specified, using TimeUnit
        :param period: time until next AppState
        :param energy_consumed: amount of energy consumed by this sample in joules
        :param sample: AppSample containing a stack trace (or possible multiple)
        :param env: TODO environment store
        :param power: Power being used at this time
        """
        self.sample: AppSample = sample
        self.timestamp: TimeUnit = timestamp
        self.energy_consumed: float = energy_consumed

        self.period: TimeUnit = period
        self.power: Union[PowerSample, None] = power
        self.environment: EnvironmentState = env

# def is_multithreaded(self):
#    return len(self.sample.traces) > 1
