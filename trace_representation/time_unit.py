import copy
import math
from functools import singledispatch, singledispatchmethod


def _convert_up(input_number: int) -> (int, int):
    # Each of the units contains 1000 of the unit below it.  By taking advantage of this, we can use one function for converting
    # each smaller unit into the larger unit
    given_unit = input_number % 1000
    higher_unit = math.floor(input_number / 1000)
    return higher_unit, given_unit


def _convert_float_down(input_number: float) -> (int, float):
    # Takes a float number, extracts the integer portion, and returns the remainder *1000 to be converted downwards
    # in unit.
    given_unit = int(input_number)
    remainder = (input_number % 1) * 1000
    return given_unit, remainder


class TimeUnit(object):
    """
    TimeUnit represents time internally as integer counters of nanos, micros, millis, and seconds.
    It will automatically keep track of these to prevent overflowing, and will allow combining two objects.
    """

    def __init__(self, seconds=0, millis=0, micros=0, nanos=0):

        if isinstance(seconds, float):
            (seconds, new_millis) = _convert_float_down(seconds)
            millis += new_millis

        if isinstance(millis, float):
            millis, new_micros = _convert_float_down(millis)
            micros += new_micros

        if isinstance(micros, float):
            micros, new_nanos = _convert_float_down(micros)
            nanos += new_nanos

        # don't do any conversion to nanos, we'll coerce it

        self.seconds = int(seconds)
        self.millis = int(millis)
        self.micros = int(micros)
        self.nanos = int(nanos)

        self._convert_units()

    def __add__(self, other):
        new = copy.copy(self)
        new.seconds += other.seconds
        new.millis += other.millis
        new.micros += other.micros
        new.nanos += other.nanos
        return new

    def __iadd__(self, other):
        self.seconds += other.seconds
        self.millis += other.millis
        self.micros += other.micros
        self.nanos += other.nanos
        return self

    def _convert_units(self):
        """
        Ensure that each unit aside from seconds has no more than 999
        """
        extra_micros, new_nanos = _convert_up(self.nanos)
        self.micros += extra_micros
        self.nanos = new_nanos

        extra_millis, new_micros = _convert_up(self.micros)
        self.millis += extra_millis
        self.micros = new_micros

        extra_secs, new_millis = _convert_up(self.millis)
        self.seconds += extra_secs
        self.millis = new_millis

    def to_seconds(self) -> float:
        return self.seconds + float(self.millis) / 1e3 + float(self.micros) / 1e6 + float(self.nanos) / 1e9

    def to_millis(self) -> float:
        return self.seconds * 1e3 + self.millis + float(self.micros) / 1e3 + float(self.nanos) / 1e6

    def to_micros(self) -> float:
        return self.seconds * 1e6 + self.millis * 1e3 + float(self.micros) + float(self.nanos) / 1e3

    def to_nanos(self) -> int:
        return int(self.seconds * 1e9 + self.millis * 1e6 + self.micros * 1e3 + self.nanos)
