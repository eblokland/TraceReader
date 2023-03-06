import math
from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import List, Dict, Any, Set
from scipy.stats import norm
from app_sample import AppState
from simpleperf_python_datatypes import EnergyPeriod, TimePeriod, PowerPeriod



class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState]):
        self._state_list = state_list
        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass
