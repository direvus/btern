#!/usr/bin/env python
# coding=utf-8
import numbers

from . import trit


class Register(trit.Trits):
    """A fixed-length, mutable, ordered sequence of trits.

    A Register's length is set when it is created, and is fixed for the
    lifetime of the Register.  The contents of the Register within that length
    may be modified freely.
    """
    __hash__ = None

    def __init__(self, trits, length):
        if not isinstance(length, numbers.Integral):
            raise TypeError(
                    "Invalid length argument {!r}; "
                    "length must be a positive integer.".format(length))
        if length <= 0:
            raise ValueError(
                    "Invalid length argument {}; "
                    "length must be positive.".format(length))
        super(Register, self).__init__(trits, length)
        self.trits = list(self.trits)
        self.length = length

    def __str__(self):
        return ''.join([str(x) for x in self.trits])

    def __len__(self):
        return self.length

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            length = len(range(*key.indices(self.length)))
            if length != len(value):
                raise ValueError(
                        "Invalid slice assignment of {} items to {} indices; "
                        "would modify the length of the Register.".format(
                            len(value), length))
            self.trits[key] = [trit.Trit.make(x) for x in value]
        else:
            self.trits[key] = trit.Trit.make(value)

