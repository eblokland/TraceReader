import math
from typing import Set, MutableSet, Union

from scipy.stats import norm

from trace_representation.simpleperf_python_datatypes import TimePeriod, EnergyPeriod, PowerPeriod


class LocalNonLocal(object):
    def __init__(self, local=0.0, non_local=0.0):
        self.local = local
        self.non_local = non_local


class ProbInterval(object):
    def __init__(self, lower=-1, upper=-1):
        self.lower = lower
        self.upper = upper

    def __str__(self):
        return '[' + str(self.lower) + ', ' + str(self.upper) + ']'


class Function(object):
    def __init__(self, addr, name):
        self.addr: int = addr  # address of function, used as primary key
        self.name_set: Set[str] = {name}  # set of all names that this function uses (it'll probably just be the one)
        self.num_leaf_samples: int = 0  # number of times this function was the top of the callchain
        self.num_samples: int = 0  # number of times this function was seen in a callchain, not counting leaf samples
        self.time: TimePeriod = TimePeriod()  # Amount of time this function was running (not accurate lol)
        self.energy: EnergyPeriod = EnergyPeriod()  # Energy attributed to this function
        self.power: PowerPeriod = PowerPeriod()
        self.children: MutableSet[Function] = set[Function]()  # Things called by this function.
        self.local_prob: float = 0  # Probability of this function being sampled (corresponds to pbbm in formula)
        self.nonlocal_prob: float = 0  # Probability of this function being found in a callchain
        self.local_runtime: float = 0  # Estimated TOTAL runtime of this function (corresponds to tbbm)
        self.nonlocal_runtime: float = 0  # Estimated time that a function (or its children)
        # called by this function will run in total
        self.local_energy_cost: float = 0  # Estimated energy cost to run this function once
        self.nonlocal_energy_cost: float = 0
        self.mean_local_power: float = 0
        self.mean_nonlocal_power: float = 0

        # prob intervals

        self.local_prob_interval: Union[ProbInterval, None] = None
        self.nonlocal_prob_interval: Union[ProbInterval, None] = None
        self.mean_local_power_interval: Union[ProbInterval, None] = None
        self.mean_nonlocal_power_interval: Union[ProbInterval, None] = None

    def post_process(self, total_samples: int, total_runtime_seconds: float):
        """
        Processes this function using information only known after running through the samples once.
        Calculates the probabilities and from that, the runtime. DOES NOT use the period for this, it is calculated
        through the probability estimation.
        :param total_samples: Number of samples taken in total
        :param total_runtime_seconds: Runtime of the program in total.
        """
        self._set_prob(total_samples)
        self._set_runtime(total_runtime_seconds)
        self._set_power()
        self._prob_interval(n=total_samples, alpha=0.05)
        self._power_interval(alpha=0.05)

    def _set_prob(self, n):
        """
        Calc local and non-local probabilities
        :param n: Number of samples in total
        """
        self.local_prob = self.num_leaf_samples / n
        self.nonlocal_prob = self.num_samples / n

    def _set_runtime(self, total_time):
        """
        Calculates the runtime from the probabilities.   Requires probabilities to be set.
        :param total_time: Total runtime of the program
        """
        self.local_runtime = self.local_prob * total_time
        self.nonlocal_runtime = self.nonlocal_prob * total_time

    def _set_power(self):
        """
        Uses the summed up local/nonlocal power to calculate mean local/nonlocal power and from that
        the local/nonlocal energy cost.
        Ignores the measured energy periods, as this is using the probabilities calculated earlier.
        """
        self.mean_local_power = (1 / self.num_leaf_samples) * self.power.local_power if self.num_leaf_samples > 0 else 0
        # (1 / self.num_samples) * self.power.nonlocal_power
        self.mean_nonlocal_power = (1 / self.num_samples) * self.power.nonlocal_power if self.num_samples > 0 else 0
        self.local_energy_cost = self.mean_local_power * self.local_runtime
        self.nonlocal_energy_cost = self.mean_nonlocal_power * self.nonlocal_runtime

    # implement equations 9 and 10 from paper
    def _prob_interval(self, n: int, alpha: float):
        """
        Calculate confidence interval for the probability estimation
        :param n: number of samples for the interval we're calculating
        :param alpha: desired alpha
        :return:
        """
        percentile = norm.ppf(1 - (alpha / 2))

        def do_prob(p_bbm: float) -> ProbInterval:
            # sanity check from section C
            # p_bbm must not be too close to 1 or 0
            if n * p_bbm < 5 or n * (1 - p_bbm) < 5:
                return ProbInterval()

            half_interval = percentile * math.sqrt((1 / n) * p_bbm * (1 - p_bbm))
            upper = p_bbm + half_interval
            lower = p_bbm - half_interval
            return ProbInterval(lower=lower, upper=upper)

        self.local_prob_interval = do_prob(self.local_prob)
        self.nonlocal_prob_interval = do_prob(self.nonlocal_prob)

    def _power_interval(self, alpha):
        """
        Calculates confidence interval for power
        :param alpha: desired alpha value
        """
        percentile = norm.ppf(1 - (alpha / 2))

        def s(pow_hat, pow_list):
            n_bbm = len(pow_list)
            pow_sum = 0.0
            for p in pow_list:
                pow_sum += (p - pow_hat) ** 2

            return math.sqrt(
                (1 / (n_bbm - 1)) * pow_sum
            )

        def intervals(pow_hat, pow_list) -> ProbInterval:

            n_bbm = len(pow_list)
            if n_bbm < 2:
                return ProbInterval()
            sqrt_n_bbm = math.sqrt(n_bbm)
            half_interval = percentile * (s(pow_hat, pow_list) / sqrt_n_bbm)
            upper = pow_hat + half_interval
            lower = pow_hat - half_interval

            return ProbInterval(lower=lower, upper=upper)

        # just double check this...
        assert self.num_leaf_samples == len(self.power.local_power_list), \
            str(self.num_leaf_samples) + ' is not ' + str(
                len(self.power.local_power_list)) + ' did you set the current multiplier correctly?'
        assert self.num_samples == len(self.power.nonlocal_power_list), \
            str(self.num_samples) + ' is not ' + str(
                len(self.power.nonlocal_power_list)) + ' did you set the current multiplier correctly?'

        self.mean_local_power_interval = intervals(self.mean_local_power, self.power.local_power_list)
        self.mean_nonlocal_power_interval = intervals(self.mean_nonlocal_power, self.power.nonlocal_power_list)

    def get_names(self):
        return ' .. '.join(self.name_set)

    def __str__(self):
        string = "Fun at " + str(self.addr) + " with names "
        for name in self.name_set:
            string += name + ' '
        string += 'with local_energy_cost: ' + str(self.mean_local_power) + ' and nonlocal energy cost ' + \
                  str(self.mean_nonlocal_power) + ' sample count ' + str(self.num_leaf_samples)
        return string
