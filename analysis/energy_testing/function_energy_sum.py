import copy
from typing import Optional, Union, Set, List

from numpy import median

from analysis.function.function import Function


class FunctionEnergySumResult(object):
    def __init__(self, sum1: "FunctionEnergySum", sum2: "FunctionEnergySum",
                 local_res, nonlocal_res, test_id):
        self.sum1 = sum1
        self.sum2 = sum2
        self.local_res = local_res
        self.nonlocal_res = nonlocal_res
        self.test_id = test_id

    @staticmethod
    def get_csv_header():
        return ['Addr', 'Name_set', 'Local Energy Result',
                'Nonlocal Energy Result', 'Test Name', 'Local median 1', 'local median 2',
                'nonlocal median 1', 'nonlocal median 2']

    def get_csv_line(self):
        addr_str = f'{self.sum1.addr} - ' + str(self.sum2.addr) if self.sum1.addr != self.sum2.addr else ''
        return [addr_str, str(self.sum1.name_set.union(self.sum2.name_set)),
                str(self.local_res.pvalue), str(self.nonlocal_res.pvalue), self.test_id,
                str(median(self.sum1.local_energies)), str(median(self.sum2.local_energies)),
                str(median(self.sum1.non_local_energies)), str(median(self.sum2.non_local_energies))
                ]


class FunctionEnergySum(object):
    def __init__(self, fun: Function):
        self.addr: int = fun.addr
        self.name_set: Set[str] = copy.deepcopy(fun.name_set)
        self.local_energies: List[float] = [fun.local_energy_cost]
        self.non_local_energies: List[float] = [fun.nonlocal_energy_cost]

    def __add__(self, other: Union[Function, "FunctionEnergySum"]):
        copy_self = copy.deepcopy(self)
        copy_self += other
        return copy_self

    def __iadd__(self, other: Union[Function, "FunctionEnergySum"]):
        if not ((is_fun := isinstance(other, Function)) or
                (isinstance(other, FunctionEnergySum))):
            raise TypeError(f'Cannot add type {type(other)} to FunctionEnergySum')

        if self.addr != other.addr and other.name_set.isdisjoint(self.name_set):
            print('WARNING: adding two FunctionEnergySum/Function objects that appear disjoint.')

        self.name_set.union(other.name_set)

        if is_fun:
            # type checker isn't capable of inferring that we checked the type already
            # noinspection PyUnresolvedReferences
            self.local_energies.append(other.local_energy_cost)
            # noinspection PyUnresolvedReferences
            self.non_local_energies.append(other.nonlocal_energy_cost)
        else:
            self.local_energies += other.local_energies
            self.non_local_energies += other.non_local_energies

        return self

    def compare(self, other: "FunctionEnergySum", test: callable) -> FunctionEnergySumResult:
        return FunctionEnergySumResult(
            self,
            other,
            test(self.local_energies, other.local_energies),
            test(self.non_local_energies, other.non_local_energies),
            test.__name__
        )

    def median_local(self):
        return median(self.local_energies)

    def median_nonlocal(self):
        return median(self.non_local_energies)

    @staticmethod
    def get_csv_header():
        return [
            'Addr',
            'Name Set',
            'Median Local Energy',
            'Median Nonlocal Energy',
        ]

    def get_csv_line(self):
        return [
            str(self.addr),
            str(self.name_set),
            str(median(self.local_energies)),
            str(median(self.non_local_energies))
        ]

