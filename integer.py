#!/usr/bin/env python
# coding=utf-8
"""
Balanced ternary integers
=========================

This module provides for sequences of balanced ternary digits to be interpreted
and operated on as integers.  In a signed interpretation (Int), the trit values
-, 0 and + represent negative one, zero and positive one respectively.  In an
unsigned interpretation (UInt), they represent zero, one, and two -- in UInt we
are essentially using balanced ternary symbols to encode unbalanced (standard)
ternary data.

Every sequence of trits represents an integer, which is the sum of the integer
equivalent of each trit, times 3 to the power of the trit's index within the
sequence, starting from zero in the rightmost position.

For example, the signed integer trit sequence '-+0' has the integer equivalent
'i' of:

i = (-1 * 3**2) + (1 * 3**1) + (0 * 3**0)
  = (-1 * 9) + (1 * 3)
  = -9 + 3
  = -6

Whereas, the same trit sequence '-+0' as an unsigned integer has the integer
value:

i = (0 * 3**2) + (2 * 3**1) + (1 * 3**0)
  = (2 * 3) + (1 * 1)
  = 7
"""
import math
import numbers

from . import trit


class IntMixin(object):
    def __int__(self):
        return self.integer

    def __oct__(self):
        return oct(int(self))

    def __hex__(self):
        return hex(int(self))


class Int(IntMixin, trit.Trits):
    def __init__(self, trits, length=None):
        if isinstance(trits, numbers.Integral):
            if trits == 0:
                trits = [trit.TRIT_ZERO]
            else:
                integer = trits
                trits = []
                power = self.order(integer) - 1
                while power >= 0:
                    if integer == 0 or self.order(integer) <= power:
                        item = trit.TRIT_ZERO
                    elif integer < 0:
                        item = trit.TRIT_NEG
                    else:
                        item = trit.TRIT_POS
                    trits.append(item)
                    integer -= int(item) * (3 ** power)
                    power -= 1
        super(Int, self).__init__(trits, length)
        self.integer = 0
        for i in range(len(self)):
            if self[i] == trit.TRIT_ZERO:
                continue
            power = len(self) - 1 - i
            self.integer += int(self[i]) * (3 ** power)

    @staticmethod
    def order(integer):
        """Return the number of trits required to represent 'integer'."""
        return int(math.ceil(math.log(2 * abs(integer), 3)))

    def __repr__(self):
        return 'Int({})'.format(int(self))

    def __add__(self, other):
        a, b = trit.Trits.match_length(self, other)
        results = []
        carry = trit.TRIT_ZERO
        for x, y in reversed(list(zip(a, b))):
            result, carry = x.add(y, carry)
            results.append(result)
        if carry != trit.TRIT_ZERO:
            results.append(carry)
        return Int(reversed(results))


class UInt(IntMixin, trit.Trits):
    def __init__(self, trits, length=None):
        if isinstance(trits, numbers.Integral):
            if trits < 0:
                raise ValueError(
                        "Cannot instantiate an unsigned integer with "
                        "negative value {}.".format(trits))
            integer = trits
            trits = []
            while integer != 0 or len(trits) == 0:
                (integer, remain) = divmod(integer, 3)
                if remain == 0:
                    value = trit.TRIT_NEG
                elif remain == 1:
                    value = trit.TRIT_ZERO
                else:
                    value = trit.TRIT_POS
                trits.append(value)
            trits.reverse()
        if length is not None and length > len(trits):
            trits = ([trit.TRIT_NEG] * (length - len(trits))) + trits
        super(UInt, self).__init__(trits, length)
        self.integer = 0
        for i in range(len(self)):
            if self[i] == trit.TRIT_NEG:
                continue
            power = len(self) - 1 - i
            self.integer += (int(self[i]) + 1) * (3 ** power)

    def __repr__(self):
        return 'UInt({})'.format(self.integer)
