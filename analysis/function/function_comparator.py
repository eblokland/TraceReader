from typing import List, Dict
import csv
from scipy.stats import wilcoxon, ttest_ind
from analysis.function.function import Function
import sys
from trace_reader_utils.pickle_utils import gzip_unpickle

csv_header = ['name set', 'p-value local', 'p-value nonlocal', 'local-diff', 'nonlocal-diff']


class TestResult(object):
    def __init__(self, identifier: str, val1, val2, res):
        self.identifier = identifier
        self.val1 = val1
        self.val2 = val2
        self.result = res

    def get_csv_header(self):
        return [str(self.identifier) + ' ' + 'trace1 mean', str(self.identifier) + ' trace2 mean',
                str(self.identifier) + ' p-value']

    def get_csv_fields(self):
        return [self.val1, self.val2, self.result.pvalue]


class FunctionResult(object):
    def __init__(self, func1: Function, func2: Function, results: List[TestResult]):
        self.names = func1.get_names()
        self.func1 = func1
        self.func2 = func2
        self.results = results

    def get_full_csv_header(self):
        header = ['function names', 'func1 loc samp', 'func1 nonloc samp', 'func2 loc samp', 'func2 nonloc samp']
        for r in self.results:
            header += r.get_csv_header()
        return header

    def get_csv_fields(self):
        row = [self.names, self.func1.num_leaf_samples, self.func1.num_samples, self.func2.num_leaf_samples,
               self.func2.num_samples]
        for r in self.results:
            row += r.get_csv_fields()
        return row

    def add_results(self, results: List[TestResult]):
        self.results += results

    def __iadd__(self, other):
        if not isinstance(other, FunctionResult):
            raise TypeError('incorrect other type')

        if self.names != other.names:
            raise ValueError('other needs to have same function name as this')

        self.results += other.results
        return self


def write_compare_csv(output_file: str, comp_list: List[FunctionResult]):
    with open(output_file, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', quotechar='|')
        writer.writerow(comp_list[0].get_full_csv_header())
        for entry in comp_list:
            writer.writerow(entry.get_csv_fields())


def compare_function_powers(x: Function, y: Function, comparator_fun,
                            existing_fun_result: FunctionResult = None) -> FunctionResult:
    local_power_rank = comparator_fun(x.get_local_power_list(), y.get_local_power_list())
    nonlocal_power_rank = comparator_fun(x.get_nonlocal_power_list(), y.get_nonlocal_power_list())

    results = [TestResult('local power', x.mean_local_power, y.mean_local_power, local_power_rank),
               TestResult('nonlocal power', x.mean_nonlocal_power, y.mean_nonlocal_power,
                          nonlocal_power_rank)]

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


if __name__ == "__main__":
    numargs = len(sys.argv)
    if numargs != 4:
        print('Syntax: python function_comparator.py pickle1 pickle2 outfile')
        sys.exit(0)
    trace_1 = gzip_unpickle(str(sys.argv[1]))
    trace_2 = gzip_unpickle(str(sys.argv[2]))
    if trace_1 is None or trace_2 is None:
        print('Invalid pickle files!')
        sys.exit(-1)

    if isinstance(trace_1, Dict) and isinstance(trace_2, Dict):
        result = compare_dict(trace_1, trace_2)
        write_compare_csv(str(sys.argv[3]), result)
    else:
        print('traces not dict?')
