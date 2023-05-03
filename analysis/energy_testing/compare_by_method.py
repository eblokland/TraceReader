import copy
import os
from typing import Optional, Callable, Dict, List, Any, MutableMapping, Union, Tuple

import scipy.stats as stats

from analysis.energy_testing.function_energy_sum import FunctionEnergySum
from analysis.function.function import Function
from trace_reader_utils.pickle_utils import get_dict_from_pickle


def validate_pickle(file: str) -> Optional[MutableMapping[Any, Function]]:
    try:
        f_dict = get_dict_from_pickle(file)
        if not isinstance(next(iter(f_dict.values())), Function):
            return None
        return f_dict
    except ValueError:
        return None
    except TypeError:
        return None

def _merge_by_identifier(dict: MutableMapping[Any, Function]):
    raise NotImplementedError('Implement me')


def _combine_dicts(*, target_dict: MutableMapping[Any, Function], other_dict: MutableMapping[Any, Function],
                   merge_by_identifier: bool = False) -> MutableMapping[Any, Function]:
    target_key_view = target_dict.keys()
    for (key, value) in other_dict.items():
        if key not in target_key_view:
            target_dict[copy.deepcopy(key)] = copy.deepcopy(value)
            continue
        else:
            target_fun = target_dict[key]
            target_fun += value

    if merge_by_identifier:
        _merge_by_identifier(target_dict)
    return target_dict


def _add_dict_to_sum(sum_dict: MutableMapping[Any, FunctionEnergySum],
                     other_dict: MutableMapping[Any, Union[Function, FunctionEnergySum]],
                     merge_by_identifier: bool = False) -> MutableMapping[Any, FunctionEnergySum]:
    sum_keys = sum_dict.keys()
    for (key, value) in other_dict.items():
        if key not in sum_keys:
            sum_dict[key] = FunctionEnergySum(value)
        else:
            fun_sum = sum_dict[key]
            fun_sum += value

    if merge_by_identifier:
        raise NotImplementedError(':(')

    return sum_dict


def get_function_sums_from_dicts(dicts: List[MutableMapping[Any, Function]]) -> MutableMapping[Any, Function]:
    num_dicts = len(dicts)
    if num_dicts == 0:
        return dict()

    summed_functions = copy.deepcopy(dicts[0])

    for x in dicts[1:]:
        _combine_dicts(target_dict=summed_functions, other_dict=x)

    return summed_functions


def get_function_energy_sums_from_dicts(dicts: List[MutableMapping[Any, Function]]) -> MutableMapping[
    Any, FunctionEnergySum]:

    sum_dict: Dict[Any, FunctionEnergySum] = dict()
    for d in dicts:
        _add_dict_to_sum(sum_dict, d)

    return sum_dict


def _retrieve_filtered_dicts(directory: str, function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        List[MutableMapping[Any, Function]]:

    files = os.listdir(directory)
    file_paths = [f'{directory}/{file}' for file in files]

    function_dicts = [x for file in file_paths if (x := validate_pickle(file)) is not None]

    if function_filter is not None:
        for fd in function_dicts:
            for (key, fun) in fd.items():
                if not function_filter(fun):
                    fd.pop(key)

    return function_dicts


def get_function_sums_from_dir(directory: str, function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        MutableMapping[Any, Function]:

    return get_function_sums_from_dicts(_retrieve_filtered_dicts(directory, function_filter))


def get_fes_from_dir(directory: str, function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        MutableMapping[Any, FunctionEnergySum]:

    return get_function_energy_sums_from_dicts(_retrieve_filtered_dicts(directory, function_filter))


def compare_directories_by_method(dir1: str, dir2: str,
                                  function_filter: [Optional[Callable[[Function], bool]]] = None) -> Tuple[List[
        Tuple[FunctionEnergySum, Any]], List[FunctionEnergySum]]:
    dir1_sums = get_fes_from_dir(dir1, function_filter)
    dir2_sums = get_fes_from_dir(dir2, function_filter)

    results: List[(FunctionEnergySum, FunctionEnergySum, Any)] = list()
    unmatched: List[FunctionEnergySum] = list()

    # iterate over every item from dir1, and see if it's in dir 2
    # if so, we test it, and remove from dir2
    # if not, we add it to unmatched list
    for (key, value) in dir1_sums.items():
        if key in dir2_sums:
            other = dir2_sums[key]
            results.append(value.compare(other, stats.mannwhitneyu))
            dir2_sums.pop(key)
        else:
            unmatched.append(value)

    # now, we've looked at everything in dir1, and anything left in dir2 was unmatched
    # add the dir2 ones to unmatched
    unmatched += [dir2_sums.values()]

    return results, unmatched
