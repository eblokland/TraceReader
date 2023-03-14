# python versions of simpleperf data structures.
# yes, this is very memory inefficient.  just download more ram
from typing import List

from simpleperf_report_lib import CallChainStructure, CallChainEntryStructure, SymbolStruct

from trace_representation.time_unit import TimeUnit


class Symbol(object):
    """
    Symbol associated with one (TODO: or more) callchain entr(y)(ies)
    contains:
    dso_name: the name of the file the symbol is found in
    vaddr: the address of the surrounding function's beginning in the file
    symbol_name: the name of the symbol
    symbol_addr: address of the symbol itself
    len: the length of the function in the file.
    """

    def __init__(self, symbol: SymbolStruct):
        try:
            self.dso_name: str = symbol.dso_name
        except UnicodeDecodeError:
            self.dso_name: str = 'dso_decode_failed'
        self.vaddr: int = symbol.vaddr_in_file
        try:
            self.symbol_name: str = symbol.symbol_name
        except UnicodeDecodeError:
            self.symbol_name: str = 'symbol_decode_failed'
        self.symbol_addr: int = symbol.symbol_addr
        self.len: int = symbol.symbol_len
        # ignore mapping for now

    # we say that a symbol contains a given item if that item is contained in one of its names
    # or if it's equal to one of its addresses.
    # for now let's not match on substrings of addresses, that seems unnecessary
    def __contains__(self, item):
        return item in self.dso_name or item in self.symbol_name \
               or item == self.symbol_addr or item == self.vaddr

    def __str__(self):
        return self.symbol_name


class CallChainEntry(object):
    """
    Contains a single entry in a callchain, consisting of an instruction pointer address and
    a 'Symbol'
    """

    def __init__(self, entry: CallChainEntryStructure):
        self.ip: int = entry.ip
        self.symbol: Symbol = Symbol(entry.symbol)

    def __contains__(self, item):
        if item == self.ip:
            return True

        return item in self.symbol

    def __str__(self):
        return str(self.symbol)


class CallChain(object):
    """
    Contains a list of CallChainEntries associated with this CallChain
    """

    def __init__(self, chain: CallChainStructure):
        self.entries: List[CallChainEntry] = []
        for i in range(0, chain.nr):
            self.entries.append(CallChainEntry(chain.entries[i]))

    def __contains__(self, item):
        return any(item in entry for entry in self.entries)


class TimePeriod(object):
    """
    Class that represents the amount of execution time used locally and non-locally by a function
    """

    def __init__(self, local_time: TimeUnit = TimeUnit(), accumulated_time: TimeUnit = TimeUnit()):
        """
        :param local_time: Local execution time
        :param accumulated_time: non-local execution time
        """
        self.local_time = local_time
        self.accumulated_time = accumulated_time

    def __iadd__(self, other):
        if not isinstance(other, TimePeriod):
            raise TypeError('Object provided is not a TimePeriod')
        self.local_time += other.local_time
        self.accumulated_time += other.accumulated_time
        return self

    def __str__(self) -> str:
        return 'local time: ' + str(self.local_time) + ' acc time: ' + str(self.accumulated_time)


class PowerPeriod(object):
    """
    Accumulates the power used by samples of a function.  not useful without knowing the amount of time it ran for.
    """

    def __init__(self, local_power=0.0, nonlocal_power=0.0):
        """
        :param local_power:  power used by this function in *local* code
        :param nonlocal_power: power used by this function in *non-local* code
        """
        self.local_power = local_power
        self.nonlocal_power = nonlocal_power
        # if local_power is 0, then this wasn't a local sample.
        # don't add it to the list.
        self.local_power_list = [local_power] if local_power > 0 else []
        self.nonlocal_power_list = [nonlocal_power] if nonlocal_power > 0 else []

    def __iadd__(self, other):
        if not isinstance(other, PowerPeriod):
            raise TypeError("Incorrect type provided, not a PowerPeriod")
        self.local_power += other.local_power
        self.nonlocal_power += other.nonlocal_power
        self.local_power_list += other.local_power_list
        self.nonlocal_power_list += other.nonlocal_power_list
        return self


class EnergyPeriod(object):
    """
    Based on Period from annotate.py, keeps track of energy use instead of event count.
    """

    def __init__(self, local_energy=0.0, accumulated_energy=0.0):
        """
        :param local_energy: energy used specifically by this thing (line, fun, file)
        :param accumulated_energy:  energy used by this thing AND any functions it calls (and their calls etc.)
        """
        self.local_energy = local_energy
        self.accumulated_energy = accumulated_energy
        self.local_energy_list = [local_energy] if local_energy > 0 else []
        self.accumulated_energy_list = [accumulated_energy] if accumulated_energy > 0 else []

    def __iadd__(self, other):
        if not isinstance(other, EnergyPeriod):
            raise TypeError('Object provided is not an EnergyPeriod')
        self.local_energy += other.local_energy
        self.accumulated_energy += other.accumulated_energy
        self.local_energy_list += other.accumulated_energy_list
        self.accumulated_energy_list += other.accumulated_energy_list
        return self

    def __str__(self):
        return 'local energy: ' + str(self.local_energy) + ' acc energy: ' + str(self.accumulated_energy)
