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

| Trit | Signed | Unsigned |
| ---- | -----: | -------: |
|  -   |   -1   |     0    |
|  0   |    0   |     1    |
|  +   |    1   |     2    |

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

import trit


class IntMixin(object):
    def __int__(self):
        raise NotImplementedError

    def __index__(self):
        return int(self)

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
        self.integer = None

    @staticmethod
    def order(integer):
        """Return the number of trits required to represent 'integer'."""
        return int(math.ceil(math.log(2 * abs(integer), 3)))

    def is_negative(self):
        for t in self:
            if t == trit.TRIT_NEG:
                return True
            if t == trit.TRIT_POS:
                return False
        return False

    def __int__(self):
        if self.integer is None:
            self.integer = 0
            for i in range(len(self)):
                if self[i] == trit.TRIT_ZERO:
                    continue
                power = len(self) - 1 - i
                self.integer += int(self[i]) * (3 ** power)
        return self.integer

    def __abs__(self):
        """Return the absolute value of this Int."""
        for t in self.trits:
            if t == trit.TRIT_NEG:
                return -self
            elif t == trit.TRIT_POS:
                return self
        return self

    def __add__(self, other):
        """Add two Ints and return the sum as an Int.

        Obviously I could just add the integer equivalents of the two Ints
        together, and then encode the result as an Int, but that's no fun at
        all.
        """
        a, b = trit.Trits.match_length(self, other)
        results = []
        carry = trit.TRIT_ZERO
        for x, y in reversed(list(zip(a, b))):
            result, carry = x.add(y, carry)
            results.append(result)
        if carry != trit.TRIT_ZERO:
            results.append(carry)
        return Int(reversed(results))

    def __sub__(self, other):
        """Return the difference of two Ints as an Int."""
        return self.__add__(-other)

    def __mul__(self, other):
        """Return the product of two Ints as an Int."""
        result = Int([trit.TRIT_ZERO])
        # Short circuit if either operand happens to be zero.
        if self == result or other == result:
            return result
        for i in range(len(self)):
            if self[i] == trit.TRIT_ZERO:
                continue
            shift = [trit.TRIT_ZERO] * (len(self) - i - 1)
            trits = [self[i] * x for x in other] + shift
            result += Int(trits)
        return result

    def __divmod__(self, other):
        """Return the quotient and remainder of division of two Ints.

        The result is given as a tuple (quotient, remainder), both elements are
        Int objects.

        The behaviour of this function differs from that of Python's built-in
        integer division for negative numbers.  While integer division gives
        the floored quotient (rounded towards negative infinity), balanced
        ternary integer division gives the truncated quotient (rounded towards
        zero).

        Consequently, Python integer division will never return a modulus
        (remainder) with the opposite sign from the denominator, whereas
        balanced ternary integer division may do so.

        The inconsistency is unfortunate, but the whole point of a balanced
        ternary system is symmetry between the positive and negative, and I
        couldn't bring myself to break the symmetry just to conform to a
        language convention.

        >>> divmod(-5, 2)
        (-3, 1)
        >>> divmod(Int(-5), Int(2))
        (-2, -1)
        """
        if other.is_zero():
            raise ZeroDivisionError("Division of {!r} by zero.".format(self))
        # Several short-circuit opportunities:
        # 0 / x = 0
        if self.is_zero():
            return (INT_ZERO, INT_ZERO)
        # x / 1 = x
        if other == INT_ONE:
            return (self, INT_ZERO)
        # x / -1 = -x
        if other == Int([trit.TRIT_NEG]):
            return (-self, INT_ZERO)

        if other.is_negative():
            quotient, remain = self.__divmod__(-other)
            return (-quotient, remain)
        if self.is_negative():
            quotient, remain = (-self).__divmod__(other)
            return (-quotient, -remain)
        remain = Int(self)
        quotient = INT_ZERO
        while remain >= other:
            remain -= other
            quotient += INT_ONE
        return (quotient, remain)

    def __floordiv__(self, other):
        """Return the quotient of Int division.

        This is the equivalent of truncating (rounded towards zero) the
        quotient of true division, see the docs for __divmod__ for more detail.
        """
        return self.__divmod__(other)[0]

    def __mod__(self, other):
        """Return the remainder of Int division.
        
        See the docs for __divmod__ for more information.
        """
        return self.__divmod__(other)[1]


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
            trits = ([trit.TRIT_NEG] * (length - len(trits))) + list(trits)
        super(UInt, self).__init__(trits, length)
        self.integer = None

    def __int__(self):
        if self.integer is None:
            self.integer = 0
            for i in range(len(self)):
                if self[i] == trit.TRIT_NEG:
                    continue
                power = len(self) - 1 - i
                self.integer += (int(self[i]) + 1) * (3 ** power)
        return self.integer

    def __abs__(self):
        return self


INT_ZERO    = Int([trit.TRIT_ZERO])
INT_ONE     = Int([trit.TRIT_POS])
INT_NEG_ONE = Int([trit.TRIT_NEG])

UINT_ZERO    = UInt([trit.TRIT_ZERO])
UINT_ONE     = UInt([trit.TRIT_POS])
UINT_TWO     = UInt([trit.TRIT_NEG])
