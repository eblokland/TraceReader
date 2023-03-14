from typing import List

from simpleperf_report_lib import ReportLib

from parsers.parser_args import ParserArgs
from trace_representation.app_sample import AppState, AppSample, EnvironmentState, ThreadSample
from trace_representation.simpleperf_python_datatypes import CallChain, Symbol
from trace_representation.time_unit import TimeUnit


class PerfDataParser(object):
    """
    Class that parses a perf.data file into an intermediate representation.
    """

    def __init__(self, args: ParserArgs):
        """
        :param args: ParserArgs object
        """
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
        """
        Steps through the reportLib and creates a list of AppState objects.
        Currently only capable of using on-cpu samples, will break with off-cpu samples
        :return:
        """
        states: List[AppState] = []
        lib = self._create_report_lib()
        count = 0
        # loop steps through the samples one by one, converting them to AppStates
        # currently, only on-cpu samples are supported!
        while lib.GetNextSample() is not None:
            count += 1
            samp = lib.GetCurrentSample()
            ev = lib.GetEventOfCurrentSample()
            if 'task-clock' not in ev.name and 'cpu-clock' not in ev.name:
                print(f'Unsupported event {ev.name}, skipping')
                continue

            period = TimeUnit(nanos=samp.period)
            timestamp = TimeUnit(nanos=samp.time)  # simpleperf reports in nanoseconds, my tool in milliseconds
            # energy_cost, power = _get_energy_cost_of_sample(self.environment_log, timestamp, period)

            thread_sample = ThreadSample(Symbol(lib.GetSymbolOfCurrentSample()),
                                         CallChain(lib.GetCallChainOfCurrentSample()))

            app_sample = AppSample([thread_sample])
            new_state = AppState(timestamp, period, 0, app_sample, EnvironmentState(), 0)

            states.append(new_state)

        print(count)
        return states
