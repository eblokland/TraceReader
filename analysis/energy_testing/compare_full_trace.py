import os
import csv
from functools import singledispatch
from typing import Union, Callable, Optional, List

from trace_reader_utils.pickle_utils import *

from analysis.function.function import Function


@singledispatch
def sum_full_trace(arg, function_filter) -> float:
    raise TypeError(f'Unknown type {type(arg)}')


@sum_full_trace.register
def sum_full_trace_str(pickle_file: str, function_filter: Optional[Callable[[Function], bool]] = None) -> float:
    funs = get_dict_from_pickle(pickle_file)
    return sum_full_trace(funs, function_filter)


@sum_full_trace.register
def sum_full_trace_list(funs: dict, function_filter: Optional[Callable[[Function], bool]] = None) -> float:
    if len(funs) == 0 or not isinstance(list(funs.values())[0], Function):
        raise TypeError(f'Need list of Function type, got {type(funs[0])}')

    return sum(fun.energy.local_energy for fun in funs.values() if function_filter is None or function_filter(fun))


def get_sums_from_dir(directory: str, function_filter: Optional[Callable[[Function], bool]] = None) -> List[float]:
    files = os.listdir(directory)
    sums: List[float] = []
    for file in files:
        filepath = directory + file
        try:
            trace_sum = sum_full_trace(filepath, function_filter)
            sums.append(trace_sum)
        except TypeError: #swallow any errors arising from files that don't contain a function pickle.
            pass
        except ValueError:
            pass
    return sums