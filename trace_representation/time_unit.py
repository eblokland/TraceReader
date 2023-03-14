import copy
import math
from decimal import *
from typing import Union


def _convert_up(input_number: int) -> (int, int):
    # Each of the units contains 1000 of the unit below it.
    # By taking advantage of this, we can use one function for converting
    # each smaller unit into the larger unit
    given_unit = input_number % 1000
    higher_unit = math.floor(input_number / 1000)
    return higher_unit, given_unit


def _convert_float_down(input_number: Union[float, Decimal]) -> (int, Union[float, Decimal]):
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

        if isinstance(seconds, float) or isinstance(seconds, Decimal):
            (seconds, new_millis) = _convert_float_down(seconds)
            millis += new_millis

        if isinstance(millis, float) or isinstance(millis, Decimal):
            millis, new_micros = _convert_float_down(millis)
            micros += new_micros

        if isinstance(micros, float) or isinstance(millis, Decimal):
            micros, new_nanos = _convert_float_down(micros)
            nanos += new_nanos

        # don't do any conversion to nanos, we'll coerce it

        self.nanos = int(nanos) + int(micros * 1000) + int(millis * 1000000) + int(seconds * 1000000000)

    def __add__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        new = copy.copy(self)
        new.nanos += other.nanos
        return new

    def __iadd__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        self.nanos += other.nanos
        return self

    def __sub__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        new = copy.copy(self)
        new.nanos -= other.nanos
        return new

    def __isub__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        self.nanos -= other.nanos
        return self

    def __eq__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        return self.nanos == other.nanos

    def __gt__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        return self.nanos > other.nanos

    def __ge__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        return self.nanos >= other.nanos

    def __lt__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        return self.nanos < other.nanos

    def __le__(self, other):
        if not isinstance(other, TimeUnit):
            raise TypeError(f'Unsupported operand type {type(other)}')
        return self.nanos <= other.nanos

    def __str__(self):
        return f"{self.nanos}"

    # convert to decimals as there is a potential loss of precision. I don't think this is a realistic issue, but if
    # some timestamp is (ex.) millis since the unix epoch, it would cause issues as it is too large to fit in a float.
    def to_seconds(self) -> Decimal:
        return Decimal(self.nanos) / Decimal(1e9)

    def to_millis(self) -> Decimal:
        return Decimal(self.nanos) / Decimal(1e6)

    def to_micros(self) -> Decimal:
        return Decimal(self.nanos) / Decimal(1e3)

    def to_nanos(self) -> int:
        return self.nanos
