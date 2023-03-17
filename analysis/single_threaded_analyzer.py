from typing import Any, Dict, List, Callable

from analysis.function.function import Function
from analysis.statistical_analysis import StatisticalAnalyzer
from trace_representation.app_sample import AppState
from trace_representation.simpleperf_python_datatypes import TimePeriod, EnergyPeriod, CallChainEntry, Symbol, \
    PowerPeriod
from trace_representation.time_unit import TimeUnit


def _get_or_create_function(symbol: Symbol, fun_dict: Dict[Any, Function]) -> Function:
    """
    Searches for a function with the given symbol's address in the function dict.
    If it is not found, create a new one with the given symbol.
    If it is found, ensure that the symbol's name is in the function's name set, then return it.
    :param symbol: Symbol to search for
    :param fun_dict: Dictionary to search in
    :return: Function object associated with this symbol
    """
    addr = symbol.symbol_addr
    name = symbol.symbol_name
    if addr in fun_dict:
        func = fun_dict[addr]
        if name not in func.name_set:
            func.name_set.add(name)
    else:
        func = Function(addr, name)
        fun_dict[addr] = func

    return func


def _analyze_callchain_entry(entry: CallChainEntry, fun_dict: Dict[Any, Function], child_fun: Function,
                             time: TimePeriod, energy: EnergyPeriod, power: PowerPeriod, used_fun_set: set) -> Function:
    """
    Analyzes one callchain from one program state
    :param entry: CallChainEntry to analyze
    :param fun_dict: Dictionary of functions we've seen so far
    :param child_fun: Function that appears above this one in the callchain (this function's child)
    :param time: Time period associated with this program state
    :param energy: Energy period associated with this program state
    :param power: Power period associated with this program state
    :param used_fun_set: Functions we've seen *in this callchain* so far
    :return:
    """
    function = _get_or_create_function(entry.symbol, fun_dict)
    if child_fun not in function.children:
        function.children.add(child_fun)
    # For now we ignore any recursive calls to a function.
    # That means that if something appears in the callchain twice, we skip incrementing its sample count,
    # energy, power, and time.  This way we don't double attribute things that make the numbers weird.
    if function not in used_fun_set:
        used_fun_set.add(function)
        function.num_samples += 1
        function.energy += energy
        function.power += power
        function.time += time

    return function


def _analyze_state(app_state: AppState, total_time: int, function_dict: Dict[int, Function]) -> int:
    """
     "Static" function that analyzes one single program state snapshot.
    :param app_state: AppState to analyze
    :param total_time: total time that has elapsed up until this sample.
    :param function_dict: Dictionary of functions we've seen so far
    :return: The new total_time, including this state.
    """
    # get the first sample in the app_state - we aren't going to try multiple threads in this
    sample = app_state.sample.get_first_sample()
    # increment the total time by the period of the app state
    sample_runtime = app_state.period
    total_time += sample_runtime.to_nanos()

    sample_energy = app_state.energy_consumed
    sample_power = app_state.power

    # retrieve or create the function we're using
    function = _get_or_create_function(sample.symbol, function_dict)

    # function is the actual funct being executed at the time that this was running,
    # attribute its local energy and time now as well as increment its sample counter
    function.time += TimePeriod(local_time=sample_runtime, accumulated_time=sample_runtime)
    function.energy += EnergyPeriod(local_energy=sample_energy, accumulated_energy=sample_energy)
    function.power += PowerPeriod(local_power=sample_power, nonlocal_power=0)
    function.num_leaf_samples += 1

    # energy/time to be used for entries in the callchain
    non_local_time = TimePeriod(local_time=TimeUnit(), accumulated_time=sample_runtime)
    non_local_energy = EnergyPeriod(local_energy=0, accumulated_energy=sample_energy)
    non_local_power = PowerPeriod(local_power=0, nonlocal_power=sample_power)

    # for each entry in the callchain, we enter it as a child of its parent (entry after it in callchain), and attribute
    # non-local energy and runtime
    callchain = sample.trace
    child_fun = function
    used_function_set = set()
    for entry in callchain.entries:
        child_fun = _analyze_callchain_entry(entry, function_dict, child_fun, non_local_time,
                                             non_local_energy, non_local_power, used_function_set)

    return total_time


class SingleThreadedAnalyzer(StatisticalAnalyzer):
    """
    Class that will analyze a list of AppStates that, together, make up a program trace.
    This class makes a very simplifying assumption that the whole program is one thread,
    that may or may not be actively scheduled.
    """

    def __init__(self, state_list: List[AppState], begin_time: TimeUnit = None, end_time: TimeUnit = None):
        super().__init__(state_list, begin_time, end_time)
        self.function_dict: Dict[int, Function] = {}

    def perform_analysis(self):
        total_time = 0
        # each state corresponds to a single stack sample (in the single threaded analyzer)
        # if there are multiple traces in the state we just ignore them and only take the first one
        for state in self._state_list:
            total_time = _analyze_state(state, total_time, self.function_dict)

        # now we created a full list of functions!  very cool.
        # phat(bbm) = n(bbm) / n === estimated prob of bbm (or function)
        # is equal to number of function samples over total number of samples

        total_samples = len(self._state_list)
        for fun in self.function_dict.values():
            fun.post_process(total_samples, total_time / 1e9)

    def get_sorted_fun_list(self, key: Callable[[Function], Any] = lambda fun: fun.local_energy_cost, reverse=False):
        """
        Returns a sorted list of all functions in the function dictionary
        :param key: Key to sort the list by
        :param reverse: Should the list be reversed
        :return: Sorted list
        """
        fun_list = list(self.function_dict.values())
        fun_list.sort(key=key, reverse=reverse)
        return fun_list
