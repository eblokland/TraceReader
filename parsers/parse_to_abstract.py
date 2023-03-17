from typing import List, Set, Dict

from parsers.environment_parser.EnvironmentParser import EnvironmentLog
from parsers.environment_parser.entry import Power
from parsers.parser_args import ParserArgs
from parsers.perf_parser.perf_data_parser import PerfDataParser
from trace_representation.app_sample import AppState, PowerSample
from trace_representation.time_unit import TimeUnit


def _get_energy_cost_of_sample(environment_log: EnvironmentLog, timestamp: TimeUnit, period: TimeUnit) -> (
        float, Power):
    cur_power = environment_log.get_power_for_time(timestamp)
    power = environment_log.get_power_for_time(timestamp)
    energy_used = power.data * float(period.to_seconds())
    return energy_used, cur_power


def parse_to_abstract(args: ParserArgs) -> List[AppState]:
    env_samples = EnvironmentLog(args)
    perf_parser = PerfDataParser(args)
    states = perf_parser.parse()

    encountered_power_states: Dict[Power, PowerSample] = {}

    def get_power_sample(timestamp: TimeUnit, period: TimeUnit) -> (float, PowerSample):
        energy_cost, power = _get_energy_cost_of_sample(env_samples, timestamp, period)
        if power in encountered_power_states:
            pow_samp = encountered_power_states[power]
        else:
            pow_samp = PowerSample(power.data, power.timestamp)
            encountered_power_states[power] = pow_samp

        return energy_cost, pow_samp

    for state in states:
        energy_cost, power = get_power_sample(state.timestamp, state.period)
        state.energy_consumed = energy_cost
        state.power = power
    return states
