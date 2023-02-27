import math
from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import List, Dict, Any, Set
from scipy.stats import norm
from app_sample import AppState
from simpleperf_python_datatypes import EnergyPeriod, TimePeriod, PowerPeriod


class LocalNonLocal(object):
    def __init__(self, local=0.0, non_local=0.0):
        self.local = local
        self.non_local = non_local


class ProbInterval(object):
    def __init__(self, lower=-1, upper=-1):
        self.lower = lower
        self.upper = upper

    def __str__(self):
        return '[' + str(self.lower) + ', ' + str(self.upper) + ']'


class Function(object):
    def __init__(self, addr, name):
        self.addr: int = addr  # address of function, used as primary key
        self.name_set: Set[str] = {name}  # set of all names that this function uses (it'll probably just be the one)
        self.num_leaf_samples: int = 0  # number of times this function was the top of the callchain
        self.num_samples: int = 0  # number of times this function was seen in a callchain, not counting leaf samples
        self.time: TimePeriod = TimePeriod()  # Amount of time this function was running (not accurate lol)
        self.energy: EnergyPeriod = EnergyPeriod()  # Energy attributed to this function
        self.power: PowerPeriod = PowerPeriod()
        self.children: MutableSet[Function] = set[Function]()  # Things called by this function.
        self.local_prob: float = 0  # Probability of this function being sampled (corresponds to pbbm in formula)
        self.nonlocal_prob: float = 0  # Probability of this function being found in a callchain
        self.local_runtime: float = 0  # Estimated TOTAL runtime of this function (corresponds to tbbm)
        self.nonlocal_runtime: float = 0  # Estimated time that a function (or its children) called by this function will run in total
        self.local_energy_cost: float = 0  # Estimated energy cost to run this function once
        self.nonlocal_energy_cost: float = 0
        self.mean_local_power: float = 0
        self.mean_nonlocal_power: float = 0

        # prob intervals
        self.local_prob_interval: ProbInterval = ProbInterval()
        self.nonlocal_prob_interval: ProbInterval = ProbInterval()

    def post_process(self, total_samples: int, total_runtime_seconds: float):
        self._set_prob(total_samples)
        self._set_runtime(total_runtime_seconds)
        self._set_power()
        self._prob_interval(n=total_samples, alpha=0.05)

    def _set_prob(self, n):
        self.local_prob = self.num_leaf_samples / n
        self.nonlocal_prob = self.num_samples / n

    def _set_runtime(self, total_time):
        self.local_runtime = self.local_prob * total_time
        self.nonlocal_runtime = self.nonlocal_prob * total_time

    def _set_power(self):
        # we already accumulated all the sample powers

        self.mean_local_power = (1 / self.num_leaf_samples) * self.power.local_power if self.num_leaf_samples > 0 else 0
        # (1 / self.num_samples) * self.power.nonlocal_power
        self.mean_nonlocal_power = (1 / self.num_samples) * self.power.nonlocal_power if self.num_samples > 0 else 0
        self.local_energy_cost = self.mean_local_power * self.local_runtime
        self.nonlocal_energy_cost = self.mean_nonlocal_power * self.nonlocal_runtime

    # implement equations 9 and 10 from paper
    def _prob_interval(self, n: int, alpha: float):
        percentile = norm.ppf(1 - (alpha / 2))
        def do_prob(p_bbm: float) -> ProbInterval:
            # sanity check from section C
            # p_bbm must not be too close to 1 or 0
            if n * p_bbm < 5 or n * (1 - p_bbm) < 5:
                return ProbInterval()

            upper = p_bbm + percentile * math.sqrt((1 / n) * p_bbm * (1 - p_bbm))
            lower = p_bbm - percentile * math.sqrt((1 / n) * p_bbm * (1 - p_bbm))
            return ProbInterval(lower=lower, upper=upper)

        self.local_prob_interval = do_prob(self.local_prob)
        self.nonlocal_prob_interval = do_prob(self.nonlocal_prob)

    #def _power_interval(self, ):

    def __str__(self):
        string = "Fun at " + str(self.addr) + " with names "
        for name in self.name_set:
            string += name + ' '
        string += 'with local_energy_cost: ' + str(self.mean_local_power) + ' and nonlocal energy cost ' + \
                  str(self.mean_nonlocal_power) + ' sample count ' + str(self.num_leaf_samples)
        return string


class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState]):
        self._state_list = state_list
        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass
