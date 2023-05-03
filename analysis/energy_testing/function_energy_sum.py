import copy
from typing import Optional, Union, Set, List

from analysis.function.function import Function


class FunctionEnergySumResult(object):
    def __init__(self, sum1: "FunctionEnergySum", sum2: "FunctionEnergySum",
                 local_res, nonlocal_res, test_id):
        self.sum1 = sum1
        self.sum2 = sum2
        self.local_res = local_res
        self.nonlocal_res = nonlocal_res
        self.test_id = test_id


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
