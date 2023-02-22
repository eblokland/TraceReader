from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import List

from app_sample import AppState
from simpleperf_python_datatypes import EnergyPeriod, TimePeriod


class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState]):
        self._state_list = state_list
        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass


class SingleThreadedAnalyzer(StatisticalAnalyzer):

    def perform_analysis(self):




class Function(object):
    def __init__(self, addr, name):
        self.addr = addr # address of function, used as primary key
        self.name_set = {name} # set of all names that this function uses (it'll probably just be the one)
        self.num_leaf_samples = 0 # number of times this function was the top of the callchain
        self.num_samples = 0 # number of times this function was seen in a callchain
        self.time = TimePeriod() # Amount of time this function was running (not accurate lol)
        self.local_energy = EnergyPeriod() # Energy attributed to this function
        self.children: List[Function] = [] # Things called by this function.


