from typing import List

from analysis.function.Comparators.test_result import TestResult
from analysis.function.function import Function


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

    def __str__(self):
        out = f'{self.func1.get_names()} \n {self.func2.get_names()}\n'

        for r in self.results:
            out += str(r) + '\n'
        return out

