from functools import singledispatch
from typing import List, Dict, Union, Optional
from scipy.stats import wilcoxon, ttest_ind

from analysis.function.Comparators.function_result import FunctionResult
from analysis.function.Comparators.test_result import TestResult
from analysis.function.function import Function


def _compare_and_calc_avg(power_list1: List[float], power_list2: List[float],
                          comparator_fun, identifier: str) -> TestResult:

    avg1 = sum(power_list1) / len(power_list1)
    avg2 = sum(power_list2) / len(power_list2)

    rank = comparator_fun(power_list1, power_list2)
    return TestResult(identifier, avg1, avg2, rank)


def compare_function_powers(x: Function, y: Function, comparator_fun,
                            existing_fun_result: FunctionResult = None, filter_dupes: bool = True) -> FunctionResult:
    local_power_rank = comparator_fun(x.get_local_power_list(filter_dupes), y.get_local_power_list(filter_dupes))
    nonlocal_power_rank = comparator_fun(x.get_nonlocal_power_list(filter_dupes), y.get_nonlocal_power_list(filter_dupes))

    comb_res = _compare_and_calc_avg(x.get_combined_power_list(filter_dupes), y.get_combined_power_list(filter_dupes),
                                     comparator_fun, 'combined power')

    results = [TestResult('local power', x.mean_local_power, y.mean_local_power, local_power_rank),
               TestResult('nonlocal power', x.mean_nonlocal_power, y.mean_nonlocal_power,
                          nonlocal_power_rank),
               comb_res,
               ]

    if existing_fun_result is None:
        existing_fun_result = FunctionResult(x, y, results)
    else:
        existing_fun_result.add_results(results)

    return existing_fun_result


def wilcoxon_power(x: Function, y: Function, filter_dupes: bool = True):
    return compare_function_powers(x, y, lambda a, b: wilcoxon(a, b), filter_dupes=filter_dupes)


def welch_power(x: Function, y: Function, filter_dupes: bool = True) -> FunctionResult:
    return compare_function_powers(x, y, lambda a, b: ttest_ind(a, b, equal_var=False), filter_dupes=filter_dupes)


def compare_dict(x: Dict[int, Function], y: Dict[int, Function], filter_dupes: bool = True) -> List[FunctionResult]:
    comp_list: List[FunctionResult] = []
    for x_fun in x.values():
        try:
            y_fun = y[x_fun.addr]
        except KeyError:
            continue
        res = welch_power(x_fun, y_fun, filter_dupes)
        comp_list.append(res)
    return comp_list


@singledispatch
def get_fun(fun, fun_dict):
    raise TypeError(f'unknown arg type {type(fun)}')


@get_fun.register
def _get_fun_by_name(name: str, fun_dict: Dict[int, Function]) -> Function:
    return next((fun for fun in fun_dict.values() if name in fun.name_set))


@get_fun.register
def _get_fun_by_id(fun_id: int, fun_dict: Dict[int, Function]) -> Function:
    return fun_dict[fun_id]


def compare_functions(fun1: Union[str, int], fun2: Union[str, int],
                      fun_dict1: Dict[int, Function], fun_dict2: Dict[int, Function],
                      filter_dupes: bool = True) -> Optional[FunctionResult]:

    try:
        func1 = get_fun(fun1, fun_dict1)
    except (StopIteration, IndexError):
        print(f'Unable to find {fun1}')
        return None
    try:
        func2 = get_fun(fun2, fun_dict2)
    except (StopIteration, IndexError):
        print(f'Unable to find {fun2}')
        return None

    return welch_power(func1, func2, filter_dupes)
