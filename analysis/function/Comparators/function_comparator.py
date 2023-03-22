from functools import singledispatch, reduce
from typing import List, Dict, Union
import csv
from scipy.stats import wilcoxon, ttest_ind

from analysis.function.Comparators.function_result import FunctionResult
from analysis.function.Comparators.test_result import TestResult
from analysis.function.function import Function
from trace_representation.app_sample import PowerSample


def _compare_and_calc_avg(power_list1: List[float], power_list2: List[float],
                          comparator_fun, identifier: str) -> TestResult:
    def red_op(x: Union[float, int, PowerSample], y: Union[float, int, PowerSample]):
        if isinstance(x, PowerSample):
            x = x.power
        if isinstance(y, PowerSample):
            y = y.power
        return x + y

    avg1 = reduce(red_op, power_list1) / len(power_list1)
    avg2 = reduce(red_op, power_list2) / len(power_list2)

    rank = comparator_fun(power_list1, power_list2)
    return TestResult(identifier, avg1, avg2, rank)


def compare_function_powers(x: Function, y: Function, comparator_fun,
                            existing_fun_result: FunctionResult = None) -> FunctionResult:
    local_power_rank = comparator_fun(x.get_local_power_list(), y.get_local_power_list())
    nonlocal_power_rank = comparator_fun(x.get_nonlocal_power_list(), y.get_nonlocal_power_list())

    comb_res = _compare_and_calc_avg(x.get_combined_power_list(), y.get_combined_power_list(),
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


def wilcoxon_power(x: Function, y: Function):
    return compare_function_powers(x, y, lambda a, b: wilcoxon(a, b))


def welch_power(x: Function, y: Function) -> FunctionResult:
    return compare_function_powers(x, y, lambda a, b: ttest_ind(a, b, equal_var=False))


def compare_dict(x: Dict[int, Function], y: Dict[int, Function]) -> List[FunctionResult]:
    comp_list: List[FunctionResult] = []
    for x_fun in x.values():
        try:
            y_fun = y[x_fun.addr]
        except KeyError:
            continue
        res = welch_power(x_fun, y_fun)
        comp_list.append(res)
    return comp_list


@singledispatch
def get_fun(fun, fun_dict):
    raise TypeError(f'unknown arg type {type(fun)}')


@get_fun.register
def _get_fun_by_name(name: str, fun_dict: Dict[int, Function]) -> Function:
    return next((fun for fun in fun_dict.values() if name in fun.name_set), None)


@get_fun.register
def _get_fun_by_id(fun_id: int, fun_dict: Dict[int, Function]) -> Function:
    return fun_dict[fun_id]


def compare_functions(fun1: Union[str, int], fun2: Union[str, int],
                      fun_dict1: Dict[int, Function], fun_dict2: Dict[int, Function]) -> FunctionResult:

    func1 = get_fun(fun1, fun_dict1)
    func2 = get_fun(fun2, fun_dict2)
    if func1 is None or func2 is None:
        if func1 is None:
            print(f'{fun1} not found in dict!')
        if func2 is None:
            print(f'{fun2} not found in dict!')
        raise KeyError

    return welch_power(func1, func2)
