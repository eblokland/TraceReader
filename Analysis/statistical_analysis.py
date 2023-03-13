from abc import ABC, abstractmethod
from typing import List
from trace_representation.app_sample import AppState


# Abstract class for a statistical analyzer, that will take a list of program states and *do something* with them.
class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState]):
        self._state_list = state_list
        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass
