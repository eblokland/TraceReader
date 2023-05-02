import os
import csv
from functools import singledispatch
from typing import Union, Callable, Optional, List

import scipy

from trace_reader_utils.pickle_utils import *

from analysis.function.function import Function


@singledispatch
def sum_full_trace(arg, function_filter) -> float:
    """
    Returns the sum of the local energy consumption of each Function in a set of Function objects.

    :param arg: Pickle file or dict containing Function objects
    :param function_filter: Optional filter, receives a Function object and returns true if it should be
        included in the sum
    :return: sum of local energy consumption of the Functions in the provided collection
    """
    raise TypeError(f'Unknown type {type(arg)}')


@sum_full_trace.register
def sum_full_trace_str(pickle_file: str, function_filter: Optional[Callable[[Function], bool]] = None) -> float:
    funs = get_dict_from_pickle(pickle_file)
    return sum_full_trace(funs, function_filter)


@sum_full_trace.register
def sum_full_trace_dict(funs: dict, function_filter: Optional[Callable[[Function], bool]] = None) -> float:
    if len(funs) == 0 or not isinstance(list(funs.values())[0], Function):
        raise TypeError(f'Need list of Function type, got {type(funs[0])}')

    return sum(fun.energy.local_energy for fun in funs.values() if function_filter is None or not function_filter(fun))


def get_sums_from_dir(directory: str, function_filter: Optional[Callable[[Function], bool]] = None) -> List[float]:
    """
    Searches a directory for files containing function dictionary pickles and returns a list of the total energy
    use of each dictionary.
    :param directory: Directory to search
    :param function_filter: Optional filter to remove functions from the list.  The filter should return true
        if the function is to be included in the sum.
    :return: A list containing the total energy consumption for each of the pickles in the directory.
    """
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


def compare_directories(dir1: str, dir2: str, function_filter: Optional[Callable[[Function], bool]] = None,
                        test: Callable = scipy.stats.mannwhitneyu):
    """
    Compares two directories with the provided test and returns the result

    :param dir1: Directory containing a set of function dict pickles
    :param dir2: Directory containing a different set of function dict pickles
    :param test: Test to execute and return the result of.  By default, scipy.stats.mannwhitneyu
    """
    dir1_sums = get_sums_from_dir(dir1, function_filter)
    dir2_sums = get_sums_from_dir(dir2, function_filter)
    return test(dir1_sums, dir2_sums)

