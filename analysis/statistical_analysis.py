from abc import ABC, abstractmethod
from typing import List

from trace_representation.app_sample import AppState
# Abstract class for a statistical analyzer, that will take a list of program states and *do something* with them.
from trace_representation.time_unit import TimeUnit


class StatisticalAnalyzer(ABC):
    def __init__(self, state_list: List[AppState], begin_time: TimeUnit = None, end_time: TimeUnit() = None):
        def keep_state(state: AppState):
            return (begin_time is None or state.timestamp >= begin_time) and (
                        end_time is None or state.timestamp <= end_time)

        if begin_time is None and end_time is None:
            self._state_list = state_list
        else:
            self._state_list = list(filter(keep_state, state_list))

        super().__init__()

    @abstractmethod
    def perform_analysis(self):
        pass
