import copy
import csv
import os
from typing import Optional, Callable, Dict, List, Any, MutableMapping, Union, Tuple

import scipy.stats as stats

from analysis.energy_testing.function_energy_sum import FunctionEnergySum, FunctionEnergySumResult
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


def _combine_dicts(*, target_dict: MutableMapping[Any, Function], other_dict: MutableMapping[Any, Function]) -> \
MutableMapping[Any, Function]:
    target_key_view = target_dict.keys()
    for (key, value) in other_dict.items():
        if key not in target_key_view:
            target_dict[copy.deepcopy(key)] = copy.deepcopy(value)
            continue
        else:
            target_fun = target_dict[key]
            target_fun += value

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

    function_dicts = [{fun_id: fun for fun_id, fun in fun_dict.items()
                       if function_filter(fun)} if function_filter is not None else fun_dict
                      for file in file_paths if (fun_dict := validate_pickle(file)) is not None]

    return function_dicts


def get_function_sums_from_dir(directory: str, function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        MutableMapping[Any, Function]:
    return get_function_sums_from_dicts(_retrieve_filtered_dicts(directory, function_filter))


def get_fes_from_dir(directory: str, function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        MutableMapping[Any, FunctionEnergySum]:
    return get_function_energy_sums_from_dicts(_retrieve_filtered_dicts(directory, function_filter))


def compare_directories_by_method(dir1: str, dir2: str,
                                  function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        Tuple[List[FunctionEnergySumResult], List[FunctionEnergySum]]:
    dir1_sums = get_fes_from_dir(dir1, function_filter)
    dir2_sums = get_fes_from_dir(dir2, function_filter)

    results: List[FunctionEnergySumResult] = list()
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
    unmatched += list(dir2_sums.values())

    return results, unmatched


def compare_directories_by_method_string(dir1: str, dir2: str,
                                         function_filter: [Optional[Callable[[Function], bool]]] = None) -> \
        Tuple[List[FunctionEnergySumResult], List[FunctionEnergySum]]:
    dir1_sums = get_fes_from_dir(dir1, function_filter)
    dir2_sums = get_fes_from_dir(dir2, function_filter)

    results: List[FunctionEnergySumResult] = list()
    unmatched: List[FunctionEnergySum] = list()

    # dir2_kvs = dir2_sums.items()

    for value in dir1_sums.values():
        matched = False
        for (key2, value2) in dir2_sums.items():
            if not value.name_set.isdisjoint(value2.name_set):
                results.append(value.compare(value2, stats.mannwhitneyu))
                dir2_sums.pop(key2)
                matched = True
                break
        if not matched:
            unmatched.append(value)

    unmatched += list(dir2_sums.values())
    return results, unmatched


def write_results_csv(directory: str, filename: str, results: List[FunctionEnergySumResult],
                      unmatched: Optional[List[FunctionEnergySum]] = None):
    filepath = f'{directory}/{filename}.csv'
    if os.path.isfile(filepath):
        raise FileExistsError(f'File {filepath} exists')

    def sort_key(result: FunctionEnergySumResult) -> float:
        return (result.sum1.median_local() + result.sum2.median_local()) / 2

    results.sort(key=sort_key, reverse=True)

    with open(filepath, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter='\t')
        writer.writerow(FunctionEnergySumResult.get_csv_header())
        for res in results:
            writer.writerow(res.get_csv_line())

    if unmatched is not None:
        unmatched_path = f'{directory}/{filename}_unmatched.csv'
        if os.path.isfile(unmatched_path):
            print('WARNING: unmatched already existed, quitting')
        else:
            with open(unmatched_path, 'w') as unmatched_csv:
                writer = csv.writer(unmatched_csv, delimiter='\t')
                writer.writerow(FunctionEnergySum.get_csv_header())
                for um_sum in unmatched:
                    writer.writerow(um_sum.get_csv_line())
