from collections.abc import MutableSet
from typing import Dict

from simpleperf_report_lib import ReportLib, SampleStruct
from EnvironmentParser import EnvironmentLog
from annotate import Addr2Line
from configparser import ConfigParser
from parser_args import ParserArgs
from simpleperf_report_lib import SymbolStruct

from simpleperf_python_datatypes import EnergyPeriod, TimePeriod


class FunctionAddr(object):
    def __init__(self, addr, name):
        self.addr = addr
        self.name_set = {name}
        self.energy = EnergyPeriod()
        self.time = TimePeriod()

    def __str__(self):
        string = 'Function at: ' + str(self.addr) + ' containing names: \n'
        for name in self.name_set:
            string += name + '\n'
        string += 'with energy: ' + str(self.energy) + '\n'
        string += 'with time: ' + str(self.time)
        return string




class PerfParser(object):

    def __init__(self, environment_log: EnvironmentLog, args: ParserArgs):
        self.environment_log = environment_log
        self.args = args
        source_array = args.source_dirs

        self.addr2line = Addr2Line(ndk_path=args.ndk_dir, binary_cache_path=args.binary_cache, source_dirs=source_array)
        self.dso_energies = {}
        self.file_energies = {}
        # dictionary of energies.  key = function address, value = FunctionAddr object
        self.function_energies: Dict[int, FunctionAddr] = {}
        self.energy = 0.0
        self.time = 0.0

    def get_data(self):
        # add addrs to the addr2line object
        self._add_all_addrs()
        # tell addr2line to convert everything to lines
        self.addr2line.convert_addrs_to_lines()
        # generate energy costs
        self._generate_energy_costs()

    # kind of a copy of _generate_periods in annotate.py.  instead of generating sample #, I generate "periods" using energy consumption instead
    # idea is that each sample should have a cost in joules or watts or something.
    def _generate_energy_costs(self):
        lib = self._create_report_lib()
        if self.args.trace_offcpu_mode != 'on-cpu':
            raise NotImplementedError('no support for off-cpu yet...')

        samp = lib.GetNextSample()
        if samp is None:
            return
        event = lib.GetEventOfCurrentSample()
        if event.name != 'task-clock':
            raise NotImplementedError(
                'no support for ' + event.name + ' events added yet... if it\'s cpu-clock that\'s busted')
        while lib.GetCurrentSample() is not None:
            self._generate_energy_cost_of_sample(lib)
            lib.GetNextSample()

    # stealing code isn't fraud if you cite it :)
    def _generate_energy_cost_of_sample(self, lib: ReportLib):
        symbols = []

        # get all symbols that appear in the callchain of the sample
        symbols.append(lib.GetSymbolOfCurrentSample())
        callchain = lib.GetCallChainOfCurrentSample()
        for i in range(callchain.nr):
            symbols.append(callchain.entries[i].symbol)
        is_sample_used = False
        used_dso_dict = {}
        used_file_dict = {}
        # this will be a set marking used function addrs
        used_function_addr_set: MutableSet = set()
        used_line_dict = {}
        sample_energy = self._get_energy_cost_of_sample(lib)
        sample_time = self._get_time_cost_of_sample_seconds(lib)
        energy = EnergyPeriod(sample_energy, sample_energy)
        time = TimePeriod(sample_time, sample_time)

        # here symbols is the full callchain of the sample.
        # we want to add local energy + accumulated energy for the end of the callchain, and then for everything after that we add accumulated energy
        # make sure that we don't add to the same file/function/line twice, because this sample only happened once and thus shouldn't be double counted!
        # ex. if there are two functions from the same file in the callchain, we add to each function but only once to the file.
        for i, symbol in enumerate(symbols):
            """on the second symbol (if it exists), we don't want to increase the local_energy part of the energy period.
                replace the period with a new one that has no local_energy
            """
            if i == 1:
                energy = EnergyPeriod(0, sample_energy)
                time = TimePeriod(0, sample_time)
            if not self._use_symbol(symbol):
                continue
            is_sample_used = True

            self._add_dso_energy(symbol.dso_name, energy, used_dso_dict)

            sources = self.addr2line.get_sources(symbol.dso_name, symbol.vaddr_in_file)
            for source in sources:
                if source.file:
                    self._add_file_energy(source, energy, used_file_dict)
                    if source.line:
                        self._add_line_energy(source, energy, used_line_dict)

            self._add_function_energy_by_addr(energy,time, symbol, used_function_addr_set)


            # sources = self.addr2line.get_sources(symbol.dso_name, symbol.symbol_addr)
            # for source in sources:
            #   pass

            # forget this stuff, going to correlate it only by symbol_addr which is the start of the function containing instruction
            # this may be fucked up by JIT, inlining, whatever.  not going to worry about it for now, would like to attempt
            # to fix this later

            # if source.file:
            #   self._add_file_energy(source, energy, used_file_dict)
            #  if source.line:
            #     self._add_function_energy(source, energy, used_function_dict)

        if is_sample_used:
            self.energy += sample_energy
            self.time += sample_time

    def _get_energy_cost_of_sample(self, lib: ReportLib) -> float:
        sample = lib.GetCurrentSample()
        if sample is None:
            return 0.0
        power = self.environment_log.get_power_for_time(sample.time)
        # 1 watt == 1 Joule/second
        # multiply watts by seconds to get joules used.
        energy_used = power * sample.period / 1e9  # divide by 1e9 to go nanosecond -> second

        return energy_used

    def _get_time_cost_of_sample_seconds(self, lib: ReportLib) -> float:
        sample = lib.GetCurrentSample()
        if sample is None:
            return 0.0
        event = lib.GetEventOfCurrentSample()
        if 'task-clock' not in event.name:
            raise NotImplementedError('no support for anything not task-clock')
        return sample.period / 1e9 #return in seconds


    def _add_addr_for_sample(self, lib: ReportLib):
        symbols = [lib.GetSymbolOfCurrentSample()]
        callchain = lib.GetCallChainOfCurrentSample()
        for i in range(callchain.nr):
            symbols.append(callchain.entries[i].symbol)
        for symbol in symbols:
            if self._use_symbol(symbol):
                build_id = lib.GetBuildIdForPath(symbol.dso_name)
                self.addr2line.add_addr(symbol.dso_name, build_id, symbol.symbol_addr, symbol.vaddr_in_file)
                self.addr2line.add_addr(symbol.dso_name, build_id, symbol.symbol_addr, symbol.symbol_addr)

    def _add_all_addrs(self):
        # going through the lib is a one-way thing. make a new object here because we can't reuse one anyway.
        lib = self._create_report_lib()
        while lib.GetNextSample() is not None:
            self._add_addr_for_sample(lib)
        lib.Close()

    def _use_symbol(self, symbol):
        return True

    # helper function to generate a report lib out of whatever settings we were given, since
    # we will need to generate the report lib multiple times per run
    def _create_report_lib(self) -> ReportLib:
        sp_report = ReportLib()
        sp_report.SetRecordFile(self.args.simpleperf_log_file)
        sp_report.SetTraceOffCpuMode(self.args.trace_offcpu_mode)
        sp_report.SetSymfs(self.args.binary_cache)
        return sp_report

    def _add_dso_energy(self, dso_name: str, period: EnergyPeriod, used_dso_dict: Dict[str, bool]):
        if dso_name not in used_dso_dict:
            used_dso_dict[dso_name] = True
            dso_period = self.dso_energies.get(dso_name)
            if dso_period is None:
                dso_period = self.dso_energies[dso_name] = DsoPeriod(dso_name)
            dso_period.add_energy(period)

    def _add_file_energy(self, source, period, used_file_dict):
        if source.file_key not in used_file_dict:
            used_file_dict[source.file_key] = True
            file_period = self.file_energies.get(source.file)
            if file_period is None:
                file_period = self.file_energies[source.file] = FilePeriod(source.file)
            file_period.add_period(period)

    def _add_line_energy(self, source, period, used_line_dict):
        if source.line_key not in used_line_dict:
            used_line_dict[source.line_key] = True
            file_period = self.file_energies[source.file]
            file_period.add_line_period(source.line, period)

    def _add_function_energy(self, source, period, used_function_dict):
        if source.function_key not in used_function_dict:
            used_function_dict[source.function_key] = True
            file_period = self.file_energies[source.file]
            file_period.add_function_period(source.function, source.line, period)

    def _add_function_energy_by_addr(self, energy: EnergyPeriod, time: TimePeriod, symbol: SymbolStruct,
                                     used_function_addr_set: MutableSet):
        addr = symbol.symbol_addr
        if addr not in used_function_addr_set:
            used_function_addr_set.add(addr)
            if addr not in self.function_energies:
                self.function_energies[addr] = FunctionAddr(addr, symbol.symbol_name)
            function_ref = self.function_energies[addr]
            function_ref.energy += energy
            function_ref.time += time


class BaseBlockPeriod(object):
    # period for shared lib
    def __init__(self):
        self.energy = EnergyPeriod()

    def add_energy(self, energy):
        self.energy += energy


class DsoPeriod(BaseBlockPeriod):
    def __init__(self, dso_name):
        super().__init__()
        self.dso_name = dso_name


class FilePeriod(BaseBlockPeriod):
    def __init__(self, file_id):
        super().__init__()
        self.file = file_id
        self.line_dict = {}
        self.function_dict = {}

    def add_line_energy(self, line, energy):
        line_energy = self.line_dict.get(line)
        if line_energy is None:
            self.line_dict[line] = line_energy = EnergyPeriod()
        line_energy += energy

    def add_function_energy(self, function_name, function_start_line, energy):
        fun_energy = self.function_dict.get(function_name)
        if not fun_energy:
            if function_start_line is None:
                function_start_line = -1
            self.function_dict[function_name] = fun_energy = [function_start_line, EnergyPeriod()]
        fun_energy[1] += energy
