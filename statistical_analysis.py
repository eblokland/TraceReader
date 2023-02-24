from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import List, Dict, Any, Set

from app_sample import AppState
from simpleperf_python_datatypes import EnergyPeriod, TimePeriod, PowerPeriod

class LocalNonLocal(object):
    def __init__(self, local=0.0, non_local=0.0):
        self.local = local
        self.non_local = non_local

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
        self.prob: float = 0  # Probability of this function being sampled (corresponds to pbbm in formula)
        self.runtime: float = 0 # Estimated runtime of this function (corresponds to tbbm)
        self.energy_cost: float = 0 # Estimated energy cost to run this function once
        self.mean_power: float = 0

    def post_process(self, total_samples: int, total_runtime: int):
        self._set_prob(total_samples)
        self._set_runtime(total_runtime)
        self._set_power()

    def _set_prob(self, n):
        self.prob = self.num_leaf_samples / n

    def _set_runtime(self, total_time):
        self.runtime = self.prob * total_time

    def _set_power(self):
        #we already accumulated all the sample powers
        if self.num_leaf_samples == 0:
            return
        self.mean_power = (1 / self.num_leaf_samples) * self.power.local_power #+\
                         # (1 / self.num_samples) * self.power.nonlocal_power
        self.energy_cost = self.mean_power * self.runtime

    def __str__(self):
        string = "Fun at " + str(self.addr) + " with names "
        for name in self.name_set:
            string += name + ' '
        string += 'with mean_power: ' + str(self.mean_power) + ' and prob ' + str(self.prob)
        return string



class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState]):
        self._state_list = state_list
        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass
