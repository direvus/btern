#!/usr/bin/env python
# coding=utf-8
"""
Balanced ternary integers

This module provides for sequences of balanced ternary digits to be interpreted
and operated on as integers.  In a signed interpretation (Int), the trit values
-, 0 and + represent negative one, zero and positive one respectively.  In an
unsigned interpretation (UInt), they represent zero, one, and two.
"""
import math
import numbers

from . import trit


class Int(trit.Trits):
    def __repr__(self):
        return 'Int({})'.format(int(self))


class UInt(trit.Trits):
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
                    value = trit.NEG
                elif remain == 1:
                    value = trit.ZERO
                else:
                    value = trit.POS
                trits.append(value)
            trits.reverse()
        if length is not None and length > len(trits):
            trits = ([trit.NEG] * (length - len(trits))) + trits
        trit.Trits.__init__(self, trits, length)
        # The sequence of trits may have been trimmed to 'length' by the
        # upstream constructor, so figure out the uint value from scratch.
        self.uint = 0
        for i in range(len(self)):
            if self[i] == trit.TRITS[trit.NEG]:
                continue
            power = len(self) - 1 - i
            self.uint += (int(self[i]) + 1) * (3 ** power)

    def __int__(self):
        return self.uint

    def __repr__(self):
        return 'UInt({})'.format(self.uint)
