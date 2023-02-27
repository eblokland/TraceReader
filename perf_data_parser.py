from typing import Dict, List

from simpleperf_report_lib import ReportLib, SampleStruct

from app_sample import AppState, AppSample, EnvironmentState, ThreadSample
from parser_args import ParserArgs
from EnvironmentParser import EnvironmentLog
from PerfParser import FunctionAddr
from simpleperf_python_datatypes import CallChain, Symbol


def _get_energy_cost_of_sample(environment_log: EnvironmentLog, timestamp, period) -> (float, float):
    cur_power = environment_log.get_power_for_time(timestamp)
    power = environment_log.get_power_for_time(timestamp)
    energy_used = power * period / 1e9
    return energy_used, cur_power


class PerfDataParser(object):
    def __init__(self, environment_log: EnvironmentLog, args: ParserArgs):
        self.environment_log = environment_log
        self.args = args
        self.states: List[AppState] = []

    def parse(self) -> List[AppState]:
        self.states = self._convert_to_states()
        return self.states

    def _create_report_lib(self) -> ReportLib:
        sp_report = ReportLib()
        sp_report.SetRecordFile(self.args.simpleperf_log_file)
        if self.args.trace_offcpu_mode in sp_report.GetSupportedTraceOffCpuModes():
            sp_report.SetTraceOffCpuMode(self.args.trace_offcpu_mode)
        sp_report.SetSymfs(self.args.binary_cache)
        return sp_report

    def _convert_to_states(self) -> List[AppState]:
        states: List[AppState] = []
        lib = self._create_report_lib()
        while lib.GetNextSample() is not None:
            samp = lib.GetCurrentSample()
            #TODO: make the period real instead of the fake period that i'm given
            period = samp.period
            timestamp = samp.time / 1e6 #simpleperf reports in nanoseconds, my tool in milliseconds
            energy_cost, power = _get_energy_cost_of_sample(self.environment_log, timestamp, period)

            thread_sample = ThreadSample(Symbol(lib.GetSymbolOfCurrentSample()),
                                         CallChain(lib.GetCallChainOfCurrentSample()))

            app_sample = AppSample([thread_sample])
            new_state = AppState(timestamp, period, energy_cost, app_sample, EnvironmentState(), power)

            states.append(new_state)

        return states



