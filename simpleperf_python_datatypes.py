#python versions of simpleperf data structures.
#yes, this is very memory inefficient.  just download more ram
from typing import List

from simpleperf_report_lib import CallChainStructure, CallChainEntryStructure, SymbolStruct


class Symbol(object):
    def __init__(self, symbol: SymbolStruct):
        self.dso_name = symbol.dso_name
        self.vaddr = symbol.vaddr_in_file
        self.symbol_name = symbol.symbol_name
        self.symbol_addr = symbol.symbol_addr
        self.len = symbol.symbol_len
        #ignore mapping for now

class CallChainEntry(object):
    def __init__(self, entry: CallChainEntryStructure):
        self.ip = entry.ip
        self.symbol = Symbol(entry.symbol)


class CallChain(object):
    def __init__(self, chain : CallChainStructure):
        self.entries: List[CallChainEntry] = []
        for entry in chain.entries:
            self.entries.append(CallChainEntry(entry))


class TimePeriod(object):
    def __init__(self, local_time=0.0, accumulated_time=0.0):
        self.local_time = local_time
        self.accumulated_time = accumulated_time

    def __iadd__(self, other):
        if not isinstance(other, TimePeriod):
            raise TypeError('Object provided is not an EnergyPeriod')
        self.local_time += other.local_time
        self.accumulated_time += other.accumulated_time
        return self

    def __str__(self):
        return 'local time: ' + str(self.local_time) + ' acc time: ' + str(self.accumulated_time)


class EnergyPeriod(object):
    """
    Based on Period from annotate.py, keeps track of energy use instead of event count.
    local_energy = energy used specifically by this thing (line, fun, file)
    accumulated_energy = energy used by this thing AND any functions it calls (enzo enzo)
    """

    def __init__(self, local_energy=0.0, accumulated_energy=0.0):
        self.local_energy = local_energy
        self.accumulated_energy = accumulated_energy

    def __iadd__(self, other):
        if not isinstance(other, EnergyPeriod):
            raise TypeError('Object provided is not an EnergyPeriod')
        self.local_energy += other.local_energy
        self.accumulated_energy += other.accumulated_energy
        return self

    def __str__(self):
        return 'local energy: ' + str(self.local_energy) + ' acc energy: ' + str(self.accumulated_energy)
