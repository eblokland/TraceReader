from typing import List

from parsers.environment_parser.EnvironmentParser import EnvironmentLog
from parsers.parser_args import ParserArgs
from parsers.perf_parser.perf_data_parser import PerfDataParser
from trace_representation.app_sample import AppState


def _get_energy_cost_of_sample(environment_log: EnvironmentLog, timestamp, period) -> (float, float):
    cur_power = environment_log.get_power_for_time(timestamp)
    power = environment_log.get_power_for_time(timestamp)
    energy_used = power * period / 1e9  # assumes that period is in nanoseconds
    return energy_used, cur_power


def parse_to_abstract(args: ParserArgs) -> List[AppState]:
    env_samples = EnvironmentLog(args)
    perf_parser = PerfDataParser(args)
    states = perf_parser.parse()
    for state in states:
        energy_cost, power = _get_energy_cost_of_sample(env_samples, state.timestamp, state.period)
        state.energy_consumed = energy_cost
        state.power = power
    return states